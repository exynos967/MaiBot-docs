import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

from config import config
from doc_gen import DocGenerator
from monitor import GitHubMonitor


class MainController:
    def __init__(self):
        self.monitor = GitHubMonitor()
        self.doc_gen = DocGenerator()
        self.updated_files = set()
        self.ai_changes = []
        self.docs_root = config.DOCS_ROOT
        self.bootstrap_mode = False

    def _get_llm_max_context_chars(self) -> int:
        raw = os.getenv("LLM_MAX_CONTEXT_CHARS") or os.getenv("BOOTSTRAP_MAX_CONTEXT_CHARS") or "120000"
        try:
            return max(8000, int(raw))
        except Exception:
            return 120000

    def _get_bootstrap_max_pages(self) -> int:
        raw = os.getenv("BOOTSTRAP_MAX_PAGES") or "60"
        try:
            return max(1, int(raw))
        except Exception:
            return 60

    def _clone_upstream_repo(self, dest_dir: str, *, branch: str, head_sha: str = "") -> str:
        """Clone upstream repo (shallow) to a local directory for bootstrap scanning."""
        repo_name = (config.REPO_NAME or "").strip()
        if not repo_name:
            raise ValueError("REPO_NAME is empty")

        repo_url = f"https://github.com/{repo_name}.git"
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        os.makedirs(os.path.dirname(dest_dir), exist_ok=True)

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, dest_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to clone {repo_url}@{branch}: {e}") from e

        if head_sha:
            try:
                subprocess.run(
                    ["git", "-C", dest_dir, "checkout", head_sha],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )
            except Exception:
                # Best-effort: HEAD should normally match the API-reported head sha.
                pass

        return dest_dir

    def _iter_upstream_files(self, repo_dir: str) -> List[str]:
        """List all files in repo_dir applying user-specified bootstrap filters."""
        exclude_dir_names = {
            ".git",
            ".github",
            ".devcontainer",
            "changelogs",
            "depends-data",
        }
        exclude_exts = {".md", ".toml", ".yaml", ".yml"}

        included: List[str] = []
        for root, dirnames, filenames in os.walk(repo_dir):
            dirnames[:] = [d for d in dirnames if d not in exclude_dir_names]

            for filename in filenames:
                name_lower = filename.lower()
                if name_lower == "license" or name_lower.startswith("license."):
                    continue
                if name_lower.endswith("ignore"):
                    continue

                ext = os.path.splitext(filename)[1].lower()
                if ext in exclude_exts:
                    continue

                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, repo_dir).replace(os.sep, "/")
                included.append(rel_path)

        return sorted(set(included))

    def _group_files_by_dir(self, file_paths: List[str]) -> Dict[str, List[str]]:
        grouped: Dict[str, List[str]] = {}
        for path in file_paths or []:
            p = (path or "").strip().replace("\\", "/").lstrip("./")
            if not p:
                continue
            dir_path = os.path.dirname(p).replace("\\", "/") or "."
            grouped.setdefault(dir_path, []).append(p)

        for k in list(grouped.keys()):
            grouped[k] = sorted(set(grouped[k]))

        return dict(sorted(grouped.items(), key=lambda kv: kv[0]))

    def _is_binary_file(self, abs_path: str) -> bool:
        try:
            with open(abs_path, "rb") as f:
                head = f.read(4096)
            return b"\x00" in head
        except Exception:
            return True

    def _read_text_file_parts(self, repo_dir: str, rel_path: str, *, part_chars: int) -> List[str]:
        abs_path = os.path.join(repo_dir, rel_path)
        if self._is_binary_file(abs_path):
            return []

        parts: List[str] = []
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                while True:
                    chunk = f.read(part_chars)
                    if not chunk:
                        break
                    parts.append(chunk)
        except Exception:
            return []
        return parts

    def _build_directory_chunks(
        self,
        *,
        repo_dir: str,
        dir_path: str,
        files: List[str],
        repo_map_text: str,
        max_context_chars: int,
    ) -> List[Dict[str, Any]]:
        fixed_overhead = 12000 + len(repo_map_text) + len(dir_path) * 4
        budget = max(2000, max_context_chars - fixed_overhead)
        part_chars = max(2000, int(budget * 0.7))

        file_blocks: List[Tuple[str, int, int, str]] = []
        for rel_path in files:
            parts = self._read_text_file_parts(repo_dir, rel_path, part_chars=part_chars)
            if not parts:
                continue
            total = len(parts)
            for idx, text in enumerate(parts, start=1):
                file_blocks.append((rel_path, idx, total, text))

        chunks: List[Dict[str, Any]] = []
        current_lines: List[str] = []
        current_files: List[str] = []
        current_len = 0

        def flush() -> None:
            nonlocal current_lines, current_files, current_len
            if not current_lines:
                return
            chunks.append({"files": sorted(set(current_files)), "files_block": "\n".join(current_lines).strip() + "\n"})
            current_lines = []
            current_files = []
            current_len = 0

        for rel_path, part_index, part_total, text in file_blocks:
            block_lines = [
                f"--- File: {rel_path} (part {part_index}/{part_total}) ---",
                "```text",
                text.rstrip("\n"),
                "```",
                "",
            ]
            block_text = "\n".join(block_lines)
            if len(block_text) > budget and text:
                # As a safety valve, hard-split oversized parts.
                split_size = max(1000, int(budget * 0.6))
                start = 0
                while start < len(text):
                    sub = text[start : start + split_size]
                    sub_lines = [
                        f"--- File: {rel_path} (part {part_index}/{part_total}, sub {start // split_size + 1}) ---",
                        "```text",
                        sub.rstrip("\n"),
                        "```",
                        "",
                    ]
                    sub_text = "\n".join(sub_lines)
                    if current_len + len(sub_text) > budget and current_lines:
                        flush()
                    current_lines.extend(sub_lines)
                    current_files.append(rel_path)
                    current_len += len(sub_text)
                    start += split_size
                continue

            if current_len + len(block_text) > budget and current_lines:
                flush()

            current_lines.extend(block_lines)
            current_files.append(rel_path)
            current_len += len(block_text)

        flush()

        # Add a small header per chunk (after packing, so we know the files list).
        for idx, ch in enumerate(chunks, start=1):
            header = [
                f"Directory: {dir_path}",
                f"Chunk: {idx}/{len(chunks)}",
                "Files in this chunk:",
            ]
            for p in ch["files"]:
                header.append(f"- {p}")
            header.append("")
            ch["files_block"] = "\n".join(header) + ch["files_block"]

        return chunks

    def _read_repo_file_text(self, repo_dir: str, rel_path: str, *, max_bytes: int) -> str:
        abs_path = os.path.join(repo_dir, rel_path)
        try:
            with open(abs_path, "rb") as f:
                raw = f.read(max_bytes + 1)
        except Exception:
            return ""

        # Skip binary-ish blobs
        if b"\x00" in raw:
            return ""

        truncated = len(raw) > max_bytes
        if truncated:
            raw = raw[:max_bytes]

        text = raw.decode("utf-8", errors="replace")
        if truncated:
            text += "\n\n...[truncated]..."
        return text

    def _extract_top_level_signatures(self, rel_path: str, text: str, *, max_lines: int = 80) -> List[str]:
        if not rel_path.endswith(".py"):
            return []

        sigs: List[str] = []
        for line in (text or "").splitlines():
            if not line:
                continue
            if line.startswith(("def ", "async def ", "class ")):
                sigs.append(line.rstrip())
                if len(sigs) >= max_lines:
                    break
        return sigs

    def _select_bootstrap_files(self, tree_paths: List[str], max_files: int = 12) -> List[str]:
        """从仓库文件树中挑选少量“高信号”文件，供 bootstrap 生成更具体的文档上下文。"""
        paths = [p.strip().lstrip("./") for p in (tree_paths or []) if p and p.strip()]

        def is_text_like(p: str) -> bool:
            suffixes = (".py", ".json", ".ini", ".cfg", ".txt", ".sh", ".env")
            return p.endswith(suffixes)

        selected: List[str] = []

        # Plugin system API surface (public contract)
        for p in paths:
            if len(selected) >= max_files:
                return selected[:max_files]
            if p.startswith("src/plugin_system/apis/") and p.endswith(".py") and is_text_like(p):
                selected.append(p)

        def add_first_match(pred) -> None:
            for p in paths:
                if p in selected:
                    continue
                if not is_text_like(p):
                    continue
                if pred(p):
                    selected.append(p)
                    return

        # Architecture / core loop hints
        add_first_match(lambda p: "/chat/brain_chat/PFC/" in p and p.endswith("pfc.py"))
        add_first_match(lambda p: "/chat/brain_chat/PFC/" in p and p.endswith("action_planner.py"))

        # Learning system hints
        add_first_match(lambda p: "/bw_learner/" in p and p.endswith("expression_learner.py"))
        add_first_match(lambda p: "/bw_learner/" in p and p.endswith("jargon_miner.py"))

        # Plugin/adapters hints
        add_first_match(lambda p: "/plugins/" in p and p.endswith("_manifest.json"))
        add_first_match(lambda p: "/plugins/" in p and p.endswith("plugin.py"))
        add_first_match(lambda p: "/adapter" in p.lower() and p.endswith(".py"))

        # If still not enough, pick a few representative src python files.
        for p in paths:
            if len(selected) >= max_files:
                break
            if p in selected:
                continue
            if not is_text_like(p):
                continue
            if p.startswith("src/") and p.endswith(".py"):
                selected.append(p)

        return selected[:max_files]

    def _build_repo_context(self, *, head_sha: str, repo_dir: str, tree_paths: List[str]) -> str:
        """Build bootstrap context by scanning the whole repo with strict filters (no upstream docs/config noise)."""
        max_total_chars = int(
            os.getenv("LLM_MAX_CONTEXT_CHARS")
            or os.getenv("BOOTSTRAP_MAX_CONTEXT_CHARS", "120000")
            or "120000"
        )
        max_file_bytes = int(os.getenv("BOOTSTRAP_MAX_FILE_BYTES", "60000") or "60000")
        max_sig_lines = int(os.getenv("BOOTSTRAP_MAX_SIG_LINES_PER_FILE", "60") or "60")

        # Summarize tree by top-level entries.
        top_level: Dict[str, List[str]] = {}
        for p in tree_paths:
            top = (p.split("/", 1)[0] or "").strip()
            top_level.setdefault(top, []).append(p)

        lines: List[str] = []
        total_chars = 0

        def add(line: str) -> bool:
            nonlocal total_chars
            line = line.rstrip("\n")
            if total_chars + len(line) + 1 > max_total_chars:
                return False
            lines.append(line)
            total_chars += len(line) + 1
            return True

        add(f"Repo: {config.REPO_NAME}")
        add(f"Branch: {config.UPSTREAM_BRANCH}")
        if head_sha:
            add(f"Head: {head_sha}")
        add("")
        add("Bootstrap filters (upstream scan):")
        add("- Exclude dirs: .devcontainer/, .github/, changelogs/, depends-data/")
        add("- Exclude files: *.md, *.toml, *.yaml, *.yml, *ignore, LICENSE")
        add("")
        add("Top-level entries (file count):")
        for k in sorted(top_level.keys()):
            if not add(f"- {k}: {len(top_level[k])}"):
                add("...(truncated due to context size limit)...")
                return "\n".join(lines)
        add("")
        add(f"Included files: {len(tree_paths)}")
        add("")

        add("All included file paths:")
        for p in tree_paths:
            if not add(f"- {p}"):
                add("...(truncated file list due to context size limit)...")
                break

        selected_files = self._select_bootstrap_files(tree_paths, max_files=12)
        file_snippets: List[Tuple[str, str]] = []
        for p in selected_files:
            text = self._read_repo_file_text(repo_dir, p, max_bytes=max_file_bytes)
            if not text.strip():
                continue
            file_snippets.append((p, text))

        if file_snippets:
            add("")
            add("Selected file snippets (for deeper verification):")
            for p, text in file_snippets:
                if not add(f"--- File: {p} ---"):
                    add("...(truncated snippets due to context size limit)...")
                    break
                add("```text")
                for ln in text.splitlines():
                    if not add(ln):
                        add("...[truncated]...")
                        break
                add("```")

        add("")
        add("Extracted top-level Python signatures (partial index):")
        for p in tree_paths:
            if not p.endswith(".py"):
                continue
            text = self._read_repo_file_text(repo_dir, p, max_bytes=max_file_bytes)
            sigs = self._extract_top_level_signatures(p, text, max_lines=max_sig_lines)
            if not sigs:
                continue
            if not add(f"--- {p} ---"):
                add("...(truncated signature index due to context size limit)...")
                break
            for sig in sigs:
                if not add(sig):
                    add("...(truncated signature index due to context size limit)...")
                    break

        return "\n".join(lines)

    def _compact_repo_map(self, repo_map: Dict) -> Dict:
        if not isinstance(repo_map, dict):
            return {}
        return {
            "repo": repo_map.get("repo"),
            "branch": repo_map.get("branch"),
            "generated_at": repo_map.get("generated_at"),
            "summary": repo_map.get("summary"),
            "module_groups": (repo_map.get("module_groups") or [])[:30],
            "public_surfaces": (repo_map.get("public_surfaces") or [])[:60],
            "doc_group_suggestions": (repo_map.get("doc_group_suggestions") or [])[:40],
            "limitations": repo_map.get("limitations"),
            "evidence": (repo_map.get("evidence") or [])[:20],
        }

    def _build_dir_briefs(self, dir_summaries: List[Dict]) -> List[Dict]:
        by_dir: Dict[str, Dict] = {}
        for item in dir_summaries or []:
            if not isinstance(item, dict):
                continue
            dir_path = str(item.get("dir") or "").strip()
            if not dir_path:
                continue
            agg = by_dir.setdefault(
                dir_path,
                {"dir": dir_path, "files": set(), "summary": [], "public": set(), "evidence": set()},
            )

            for p in item.get("files") or []:
                if isinstance(p, str) and p.strip():
                    agg["files"].add(p.strip())
            summary = (item.get("summary") or "").strip()
            if summary:
                agg["summary"].append(summary)

            for contract in item.get("public_contracts") or []:
                if not isinstance(contract, dict):
                    continue
                name = (contract.get("name") or "").strip()
                if name:
                    agg["public"].add(name)

            for ev in item.get("evidence") or []:
                if isinstance(ev, str) and ev.strip():
                    agg["evidence"].add(ev.strip())

        briefs: List[Dict] = []
        for dir_path in sorted(by_dir.keys()):
            agg = by_dir[dir_path]
            briefs.append(
                {
                    "dir": dir_path,
                    "files_count": len(agg["files"]),
                    "public_contracts": sorted(agg["public"])[:30],
                    "summary": "\n".join(agg["summary"])[:1600],
                    "evidence": sorted(agg["evidence"])[:20],
                }
            )
        return briefs

    def _generate_plugin_api_docs(self, *, repo_dir: str, repo_map: Dict) -> None:
        apis_dir = os.path.join(repo_dir, "src", "plugin_system", "apis")
        if not os.path.isdir(apis_dir):
            return

        target_category = "plugin_system/api"
        os.makedirs(os.path.join(self.docs_root, target_category), exist_ok=True)

        generated: List[str] = []
        for filename in sorted(os.listdir(apis_dir)):
            if not filename.endswith(".py"):
                continue
            if filename == "__init__.py":
                continue
            module_rel = f"src/plugin_system/apis/{filename}"
            module_text = self._read_repo_file_text(repo_dir, module_rel, max_bytes=200000)
            if not module_text.strip():
                continue

            md_name = filename[:-3] + ".md"
            page = self.doc_gen.generate_plugin_api_doc_page(
                repo_map=repo_map,
                module_path=module_rel,
                module_text=module_text,
                target_category=target_category,
                file_name=md_name,
            )
            if not page:
                continue
            out_path = self.doc_gen.write_markdown(
                target_category=target_category,
                file_name=md_name,
                content=page["content"],
            )
            self.updated_files.add(out_path)
            generated.append(md_name)

        if not generated:
            return

        index_lines = [
            f"# 插件系统 API（{config.UPSTREAM_BRANCH}）",
            "",
            "这里按源码模块拆分维护插件系统 API 文档（LLM 自动生成）。",
            "",
            "## 模块列表",
            "",
        ]
        for md_name in generated:
            stem = md_name[:-3]
            index_lines.append(f"- [{stem}](./{stem})")
        index_lines.append("")

        index_path = os.path.join(self.docs_root, target_category, "index.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines))
        self.updated_files.add(index_path)

    def _write_snapshot_indexes(self) -> None:
        snapshots_root = os.path.join(self.docs_root, "snapshots")
        if not os.path.isdir(snapshots_root):
            return

        docs_route_prefix = "/" + self.docs_root.strip("/").replace(os.sep, "/")

        versions = sorted(
            [d for d in os.listdir(snapshots_root) if os.path.isdir(os.path.join(snapshots_root, d))],
            reverse=True,
        )

        index_lines = [
            "# 文档快照",
            "",
            f"这里存放按 `{config.REPO_NAME}` 的 Tag 归档的文档快照（仅 `{self.docs_root}`）。",
            "",
        ]
        for v in versions:
            index_lines.append(f"- [{v}]({docs_route_prefix}/snapshots/{v}/)")
        index_lines.append("")

        index_path = os.path.join(snapshots_root, "index.md")
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines))
        self.updated_files.add(index_path)

    def handle_release(self, update: Dict) -> None:
        tag_name = update.get("tag_name")
        if not tag_name:
            return

        if not config.ENABLE_SNAPSHOTS:
            return

        snapshot_path = os.path.join(self.docs_root, "snapshots", tag_name)
        docs_path = self.docs_root

        print(f"🚀 检测到新版本发布：{tag_name}。正在创建文档快照...")

        if not os.path.exists(docs_path):
            print(f"⚠️ 警告：{docs_path} 不存在。跳过快照创建。")
            return

        os.makedirs(os.path.join(self.docs_root, "snapshots"), exist_ok=True)
        if os.path.exists(snapshot_path):
            print(f"⚠️ 警告：快照目录 {snapshot_path} 已存在。将执行覆盖。")
            shutil.rmtree(snapshot_path)

        os.makedirs(snapshot_path, exist_ok=True)

        try:
            for item in os.listdir(docs_path):
                if item == "snapshots":
                    continue
                src_item = os.path.join(docs_path, item)
                dst_item = os.path.join(snapshot_path, item)
                if os.path.isdir(src_item):
                    shutil.copytree(src_item, dst_item)
                else:
                    shutil.copy2(src_item, dst_item)

            print(f"✅ 快照已创建至 {snapshot_path}")

            for root, _, files in os.walk(snapshot_path):
                for file in files:
                    self.updated_files.add(os.path.join(root, file))

            self._write_snapshot_indexes()
        except Exception as e:
            print(f"❌ 创建快照时出错：{e}")

    def handle_commit(self, update: Dict, force: bool = False) -> None:
        sha = update.get("sha", "unknown")
        message = update.get("message", "")
        diff = update.get("diff", "")

        print(f"📝 正在分析提交 {sha[:7]}...")
        try:
            if force or self.doc_gen.should_update_docs(message, diff):
                print(f"✨ AI 决定为提交 {sha[:7]} 更新文档。")
                result = self.doc_gen.generate_doc_update(message, diff)
                if result:
                    file_path = result["file_path"]
                    self.updated_files.add(file_path)
                    self.ai_changes.append(result)
            else:
                print(f"ℹ️ AI 决定无需为提交 {sha[:7]} 更新文档。")
        except Exception as e:
            print(f"❌ 处理提交 {sha[:7]} 时出错：{e}")

    def run(self, force_latest: bool = False) -> None:
        print("=== LLM 文档自动化同步开始 ===")
        try:
            if self.bootstrap_mode:
                head_sha = self.monitor.get_head_sha()
                max_context_chars = self._get_llm_max_context_chars()
                max_pages = self._get_bootstrap_max_pages()
                repo_context = ""
                repo_map: Dict = {}
                dir_summaries: List[Dict] = []
                with tempfile.TemporaryDirectory(
                    prefix=f"upstream-{config.REPO_NAME.replace('/', '-')}-{config.UPSTREAM_BRANCH}-"
                ) as tmp_dir:
                    repo_dir = os.path.join(tmp_dir, "repo")
                    self._clone_upstream_repo(repo_dir, branch=config.UPSTREAM_BRANCH, head_sha=head_sha)
                    tree_paths = self._iter_upstream_files(repo_dir)

                    # Stage 1: RepoMap
                    repo_context = self._build_repo_context(head_sha=head_sha, repo_dir=repo_dir, tree_paths=tree_paths)
                    repo_map = self.doc_gen.generate_repo_map(repo_context)
                    repo_map = self._compact_repo_map(repo_map)

                    # Stage 2: Recursive per-directory analysis (direct files only; no descendant duplication)
                    dir_to_files = self._group_files_by_dir(tree_paths)
                    repo_map_text = str(repo_context)
                    try:
                        import json as _json

                        repo_map_text = _json.dumps(repo_map or {}, ensure_ascii=False)
                    except Exception:
                        repo_map_text = str(repo_map or "")

                    for dir_path, files in dir_to_files.items():
                        chunks = self._build_directory_chunks(
                            repo_dir=repo_dir,
                            dir_path=dir_path,
                            files=files,
                            repo_map_text=repo_map_text,
                            max_context_chars=max_context_chars,
                        )
                        chunk_total = len(chunks) or 1
                        for idx, ch in enumerate(chunks, start=1):
                            analysis = self.doc_gen.analyze_directory_chunk(
                                repo_map=repo_map,
                                dir_path=dir_path,
                                chunk_index=idx,
                                chunk_total=chunk_total,
                                files_block=ch["files_block"],
                            )
                            if analysis:
                                dir_summaries.append(analysis)

                latest_tag = self.monitor.get_latest_tag_name() if config.ENABLE_SNAPSHOTS else ""
                self.monitor.save_state({"last_commit_sha": head_sha, "last_tag": latest_tag})

                # Stage 3: Generate docs from directory summaries (modular plan -> pages)
                dir_briefs = self._build_dir_briefs(dir_summaries)
                plan = self.doc_gen.generate_bootstrap_doc_plan(
                    repo_map=repo_map,
                    dir_briefs=dir_briefs,
                    max_pages=max_pages,
                )

                if plan:
                    for spec in plan:
                        page = self.doc_gen.generate_bootstrap_doc_page(
                            repo_map=repo_map,
                            dir_summaries=dir_summaries,
                            spec=spec,
                        )
                        if not page:
                            continue
                        file_path = self.doc_gen.write_markdown(
                            target_category=page["target_category"],
                            file_name=page["file_name"],
                            content=page["content"],
                        )
                        self.updated_files.add(file_path)
                        self.ai_changes.append(
                            {
                                "file_path": file_path,
                                "action": "create",
                                "title": spec.get("title") or page.get("file_name") or "",
                            }
                        )
                else:
                    # Fallback: keep the original single-pass bootstrap behavior.
                    created = self.doc_gen.generate_bootstrap_docs(repo_context)
                    for item in created:
                        file_path = item.get("file_path")
                        if file_path:
                            self.updated_files.add(file_path)
                            self.ai_changes.append(item)

                # Stage 4: Plugin system API docs (LLM per module)
                with tempfile.TemporaryDirectory(
                    prefix=f"upstream-api-{config.REPO_NAME.replace('/', '-')}-{config.UPSTREAM_BRANCH}-"
                ) as api_tmp:
                    api_repo = os.path.join(api_tmp, "repo")
                    self._clone_upstream_repo(api_repo, branch=config.UPSTREAM_BRANCH, head_sha=head_sha)
                    self._generate_plugin_api_docs(repo_dir=api_repo, repo_map=repo_map)

                self.output_summary([{"type": "bootstrap", "sha": head_sha}])
                return

            updates, new_state = self.monitor.check_for_updates(force_latest=force_latest)
            if not updates:
                print("🏁 未发现新变更。退出。")
                return

            processed_updates: List[Dict] = []
            for update in updates:
                if update.get("type") == "release":
                    self.handle_release(update)
                    processed_updates.append(update)
                elif update.get("type") == "commit":
                    self.handle_commit(update, force=force_latest)
                    processed_updates.append(update)

            self.monitor.save_state(new_state)
            print("💾 状态记录已更新。")
            self.output_summary(processed_updates)
        except Exception as e:
            print(f"💥 主循环出现严重错误：{e}")
            sys.exit(1)
        print("=== LLM 文档自动化同步完成 ===")

    def output_summary(self, updates: List[Dict]) -> None:
        if not self.updated_files:
            print("📝 没有文件被创建或更新。")
            return

        print("\n" + "=" * 20 + " 总结 " + "=" * 20)
        print(f"总计更新文件数: {len(self.updated_files)}")
        for f in sorted(self.updated_files):
            print(f"- {f}")

        if os.getenv("GITHUB_ACTIONS") == "true":
            github_output = os.getenv("GITHUB_OUTPUT")
            if github_output:
                latest_update = updates[-1] if updates else {}
                branch = config.UPSTREAM_BRANCH
                repo_slug = (config.REPO_NAME.split("/")[-1] if config.REPO_NAME else "repo").strip() or "repo"

                if latest_update.get("type") == "bootstrap":
                    head_sha = (latest_update.get("sha") or "")[:7]
                    pr_title = f"docs({repo_slug}@{branch}): 初始化 LLM 文档基线"
                    pr_body = (
                        f"🧱 基于 `{config.REPO_NAME}`@`{branch}` 的当前代码快照生成初始 LLM 文档分块。\n\n"
                        + (f"Head: `{head_sha}`\n\n" if head_sha else "")
                    )
                elif latest_update.get("type") == "release":
                    tag_name = latest_update.get("tag_name")
                    pr_title = f"docs({repo_slug}@{branch}): 归档版本 {tag_name}"
                    pr_body = f"🚀 检测到 `{config.REPO_NAME}` 新版本发布：`{tag_name}`。\n\n本 PR 自动创建了该版本的文档快照（仅 LLM 自动维护部分）。"
                else:
                    sha = (latest_update.get("sha") or "")[:7]
                    pr_title = f"docs({repo_slug}@{branch}): 自动同步提交 {sha}"
                    pr_body = f"📝 基于 `{config.REPO_NAME}`@`{branch}` 提交 `{latest_update.get('sha', '')}` 自动更新文档。\n\n"

                    if self.ai_changes:
                        pr_body += "### 🤖 AI 改动分析\n"
                        for change in self.ai_changes:
                            action_str = "创建" if change.get("action") == "create" else "更新"
                            pr_body += f"- **{action_str}** `{change.get('file_path')}`: {change.get('title')}\n"
                        pr_body += "\n"

                with open(github_output, "a", encoding="utf-8") as f:
                    f.write("has_updates=true\n")
                    f.write(f"files_count={len(self.updated_files)}\n")
                    f.write(f"pr_title={pr_title}\n")
                    f.write("pr_body<<EOF\n")
                    f.write(f"{pr_body}\n")
                    f.write("\n**更新文件列表**：\n")
                    for file in sorted(self.updated_files):
                        f.write(f"- {file}\n")
                    f.write("EOF\n")

            print("[GHA] has_updates=true")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MaiBot Docs Automation")
    parser.add_argument("--force-latest", action="store_true", help="Force sync with the latest commit")
    parser.add_argument("--bootstrap", action="store_true", help="Generate initial docs baseline from repo snapshot")
    args = parser.parse_args()

    controller = MainController()
    controller.bootstrap_mode = bool(args.bootstrap)
    controller.run(force_latest=args.force_latest)
