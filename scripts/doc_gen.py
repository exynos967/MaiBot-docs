import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import config
from llm_client import HttpError, generate_text


class DocGenerator:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY (or OPENAI_API_KEY) is not set in environment variables.")

        self.__api_key = config.GEMINI_API_KEY
        self.base_url = config.BASE_URL.rstrip("/")
        self.model_name = config.MODEL_NAME
        self.api_style = config.LLM_API_STYLE
        self.docs_root = config.DOCS_ROOT
        self.show_base_url_in_logs = config.SHOW_BASE_URL_IN_LOGS

        # LLM docs are organized into modular categories (AstrBot-docs-like).
        self.categories = [
            "ai_integration",
            "design_standards",
            "messages",
            "platform_adapters",
            "plugin_system",
            "learning_system",
            "storage_utils",
        ]
        self.default_category = "design_standards"

    def _get_base_context(self) -> str:
        """递归读取 docs_root 下的 md 文件作为上下文（排除 snapshots/，并做长度限制）。"""
        if not os.path.exists(self.docs_root):
            return ""

        max_files = int(os.getenv("DOC_CONTEXT_MAX_FILES", "40") or "40")
        max_chars_per_file = int(os.getenv("DOC_CONTEXT_MAX_CHARS_PER_FILE", "2000") or "2000")
        max_total_chars = int(os.getenv("DOC_CONTEXT_MAX_TOTAL_CHARS", "40000") or "40000")

        context: List[str] = []
        total_chars = 0
        included = 0
        for root, _, files in os.walk(self.docs_root):
            if "snapshots" in root.split(os.sep):
                continue
            for filename in sorted(files):
                if not filename.endswith(".md"):
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.docs_root)
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read() or ""
                    if len(text) > max_chars_per_file:
                        text = text[:max_chars_per_file] + "\n\n...[truncated]..."
                    chunk = f"--- Doc: {rel_path} ---\n{text}"
                    if total_chars + len(chunk) > max_total_chars:
                        return "\n\n".join(context)
                    context.append(chunk)
                    total_chars += len(chunk)
                    included += 1
                    if included >= max_files:
                        return "\n\n".join(context)

        return "\n\n".join(context)

    def _mask_sensitive(self, text: str) -> str:
        if not self.__api_key:
            return text
        return (text or "").replace(self.__api_key, "***")

    def _handle_exception(self, e: Exception, context: str) -> None:
        error_msg = self._mask_sensitive(str(e))
        print(f"{context} 出错: {error_msg}")

        if isinstance(e, HttpError):
            print(f"API 诊断: 状态码={e.status_code}, 消息={error_msg}")
            if e.status_code == 401:
                print("诊断建议: API Key 无效，请检查环境变量 GEMINI_API_KEY。")
            elif e.status_code == 403:
                print("诊断建议: 权限不足或被封禁，请检查 API Key 权限或 IP 区域。")
            elif e.status_code == 429:
                print("诊断建议: 触发频率限制，请稍后再试或更换 API Key。")
            elif e.status_code >= 500:
                print("诊断建议: 上游服务端错误，请稍后重试。")

        print("提示: 如需排查连通性，可运行 `python scripts/test_api.py`。")

    def _call_llm(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        print(f"发起请求: model={self.model_name}")
        if self.show_base_url_in_logs:
            print(f"  - Base URL: {self._mask_sensitive(self.base_url)}")
        else:
            print("  - Base URL: (hidden)")
        print(f"  - API Style: {self.api_style}")
        print(f"  - Temperature: {temperature}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                return generate_text(
                    api_key=self.__api_key,
                    base_url=self.base_url,
                    model_name=self.model_name,
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_version=config.GEMINI_API_VERSION,
                    api_style=self.api_style,
                    timeout_seconds=600,
                )
            except HttpError as e:
                if e.status_code in [403, 429] and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"收到 API 错误 {e.status_code}，正在进行第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                raise e
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"请求发生异常: {self._mask_sensitive(str(e))}，正在进行第 {attempt + 1} 次重试...")
                    time.sleep(wait_time)
                    continue
                raise e

        raise RuntimeError("unreachable")

    def _extract_json(self, text: str) -> Any:
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            start_arr = text.find("[")
            end_arr = text.rfind("]")
            start_obj = text.find("{")
            end_obj = text.rfind("}")
            if start_arr != -1 and end_arr != -1 and (start_obj == -1 or start_arr < start_obj):
                json_str = text[start_arr : end_arr + 1]
            elif start_obj != -1 and end_obj != -1:
                json_str = text[start_obj : end_obj + 1]
            else:
                json_str = text
        return json.loads(json_str)

    def _extract_changed_paths(self, diff: str) -> List[str]:
        paths: List[str] = []
        if not diff:
            return paths
        for match in re.finditer(r"^diff --git a/(.+?) b/(.+?)$", diff, flags=re.MULTILINE):
            a_path = match.group(1).strip()
            b_path = match.group(2).strip()
            if a_path and a_path not in paths:
                paths.append(a_path)
            if b_path and b_path not in paths:
                paths.append(b_path)
        return paths

    def _should_skip_by_paths(self, paths: List[str]) -> bool:
        ignore_prefixes = (
            ".github/",
            ".vscode/",
            "docs/",
            "doc/",
            "website/",
            "web/",
            "dashboard/",
            "frontend/",
            "front/",
            "ui/",
            "assets/",
        )
        ignore_exact = {
            "README.md",
            "README.zh.md",
            "CHANGELOG.md",
            "pnpm-lock.yaml",
            "package-lock.json",
            "yarn.lock",
            "package.json",
        }
        ignore_suffixes = (
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".lock",
        )

        def is_ignored(path: str) -> bool:
            p = (path or "").lstrip("./")
            if p in ignore_exact:
                return True
            if p.startswith(ignore_prefixes):
                return True
            if p.endswith(ignore_suffixes):
                return True
            if p.endswith((".vue", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".less", ".html")):
                return True
            return False

        if paths and all(is_ignored(p) for p in paths):
            return True
        if paths and all(
            p.endswith((".vue", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".less", ".html")) for p in paths
        ):
            return True
        return False

    def should_update_docs(self, commit_message: str, diff: str) -> bool:
        changed_paths = self._extract_changed_paths(diff)
        if changed_paths and self._should_skip_by_paths(changed_paths):
            print("AI filtering skipped: only non-dev-doc relevant paths changed.")
            return False

        system_instruction = "你是一个文档维护助手，只能根据给定的 Commit Message 和 Diff 做判断。"
        prompt = f"""
你是一个文档维护助手。请判断以下代码变更（Commit/PR）是否会影响第三方开发者（插件/适配器/接口调用方），从而需要更新开发文档。

Commit Message:
{commit_message}

Diff Snippet:
{diff[:2000]}

规则：
1. 仅当变更影响对外契约（如对外 API、事件/消息模型、配置 schema、插件/适配器接口、兼容性与对外行为）时，才需要更新文档。
2. 如果只是内部重构、WebUI/前端细节、日志/注释、CI 配置、测试用例、纯格式调整，通常不需要更新文档。

请仅回答 "YES" 或 "NO"（可以在 YES 后面附带 1 句极短理由/证据）。
"""
        try:
            result = self._call_llm(prompt, system_instruction=system_instruction, temperature=0, max_tokens=10).strip().upper()
            return "YES" in result
        except Exception as e:
            self._handle_exception(e, "AI filtering")
            return False

    def _preprocess_diff(self, diff: str) -> str:
        line_count = diff.count("\n")
        if line_count < 500:
            return diff

        print(f"检测到变更量较大 ({line_count} 行)。正在生成技术摘要以供 AI 分析...")
        system_instruction = "你是一个专业的技术摘要生成器，擅长将冗长的代码 Diff 转换为紧凑的技术摘要。"
        summary_prompt = f"""
你是一个资深系统架构师。以下是一个巨大的代码变更 Diff。
由于 Diff 过长，请你将其压缩为一个**高密度的技术摘要**。

要求：
1. 必须保留所有新增/修改的类名、接口定义、重要方法签名、新增配置项。
2. 清晰描述数据流或调用链路的变化。
3. 剔除样板代码、简单导入变化、纯格式调整。

--- Diff ---
{diff[:30000]}
"""
        try:
            summary = self._call_llm(summary_prompt, system_instruction=system_instruction, temperature=0.2)
            return f"[Large Diff Summary]\n{summary}\n\n[Note: Original diff was {line_count} lines and was summarized.]"
        except Exception as e:
            self._handle_exception(e, "summarizing diff")
            return diff[:10000]

    def _validate_change(self, change: Dict, processed_diff: str, commit_message: str) -> Optional[str]:
        action = (change.get("action") or "").strip().lower()
        if action not in {"create", "update", "noop"}:
            return "action must be one of: create/update/noop"

        if action == "noop":
            return None

        file_name = (change.get("file_name") or "").strip()
        if not file_name.endswith(".md"):
            return "file_name must end with .md"
        if action == "create" and file_name == "index.md":
            return "file_name must not be index.md for create"
        if any(x in file_name for x in ["/", "\\", ".."]):
            return "file_name must be a plain filename (no path)"

        target_category = (change.get("target_category") or "").strip()
        if action == "create":
            if target_category not in self.categories:
                return f"target_category must be one of: {', '.join(self.categories)}"

        content = change.get("content")
        if not isinstance(content, str) or not content.strip():
            return "content must be a non-empty string"
        if not content.lstrip().startswith("---"):
            return "content must start with YAML frontmatter ('---')"

        evidence = change.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 2:
            return "evidence must be a list with at least 2 items"

        haystack = f"{commit_message}\n{processed_diff}"
        matched = 0
        for item in evidence:
            if not isinstance(item, str):
                continue
            token = item.strip().strip("`")
            if token and token in haystack:
                matched += 1
        if matched < 2:
            return "evidence items must appear in commit message or diff"

        return None

    def _validate_bootstrap_item(self, item: Dict, repo_context: str) -> Optional[str]:
        file_name = (item.get("file_name") or "").strip()
        if not file_name.endswith(".md"):
            return "file_name must end with .md"
        if file_name == "index.md":
            return "file_name must not be index.md"
        if any(x in file_name for x in ["/", "\\", ".."]):
            return "file_name must be a plain filename (no path)"

        target_category = (item.get("target_category") or "").strip()
        if not target_category:
            return "target_category is required"
        if target_category not in self.categories:
            return f"target_category must be one of: {', '.join(self.categories)}"

        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            return "content must be a non-empty string"
        if not content.lstrip().startswith("---"):
            return "content must start with YAML frontmatter ('---')"

        required_sections = ("## 概述", "## 目录/结构", "## 适用范围", "## 变更影响分析")
        for sec in required_sections:
            if sec not in content:
                return f"content must include section: {sec}"

        evidence = item.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 2:
            return "evidence must be a list with at least 2 items"

        matched = 0
        for ev in evidence:
            if not isinstance(ev, str):
                continue
            token = ev.strip().strip("`")
            if token and token in repo_context:
                matched += 1
        if matched < 2:
            return "evidence items must appear in provided repo context"

        return None

    def generate_bootstrap_docs(self, repo_context: str) -> List[Dict]:
        """基于仓库结构与 README 的快照生成初始文档（用于首次建档/重建基线）。"""
        base_context = self._get_base_context()
        today = datetime.now().strftime("%Y-%m-%d")
        categories_str = ", ".join(self.categories)
        repo_name = config.REPO_NAME
        branch = config.UPSTREAM_BRANCH

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
你是一个高级软件工程师和技术文档专家。你的任务是为 `{repo_name}` 的 `{branch}` 分支生成**初始**开发文档（按模块分组，面向 AI/RAG）。

注意：你只能基于下面提供的“仓库信息”与“现有文档”，输出**概括性、可验证**的文档。若缺少细节，请明确写“需要以源码验证/需要补充信息”，不要猜测接口。

--- 可用分类 ---
{categories_str}

--- 仓库信息（快照） ---
{repo_context}

--- 现有文档（可能为空） ---
{base_context}

--- 输出要求 ---
1) 只输出一个 JSON 数组（最多 12 项），每一项是一个对象，仅包含这些 key：
   - target_category: 必须为可用分类之一
   - file_name: 纯文件名，以 .md 结尾，禁止包含路径/..，且不能是 index.md
   - content: Markdown，必须以 YAML frontmatter 开头，且至少包含以下章节：
       - ## 概述
       - ## 目录/结构（可用任意标题，但要清晰描述目录/模块）
       - ## 适用范围与边界（标题中必须包含“适用范围”）
       - ## 变更影响分析（初始建档也需要此章节）
   - evidence: 字符串数组（至少 2 条），每条必须能在“仓库信息（快照）”中找到原样子串（建议使用路径/文件名/目录名/README 中的专有名词）
   - reason: 1 句理由（为什么需要这些文档作为初始基线）
2) frontmatter 字段必须包含：
   ---
   title: (简洁标题)
   type: (feature | improvement | refactor)
   status: (stable | experimental)
   last_updated: {today}
   related_base: (可为空)
   ---
3) 尽量覆盖多个分类（至少 4 个不同分类）；文档尽量短（每篇不超过 200 行），用于后续增量迭代完善。
"""

        created: List[Dict] = []
        try:
            raw_response = self._call_llm(prompt, system_instruction=system_instruction, temperature=0.2, max_tokens=4096)
            result = self._extract_json(raw_response)
            items = result if isinstance(result, list) else [result]

            for item in items:
                if not isinstance(item, dict):
                    continue
                validation_error = self._validate_bootstrap_item(item, repo_context)
                if validation_error:
                    print(f"Bootstrap AI output validation failed: {validation_error}")
                    continue

                change = {
                    "action": "create",
                    "target_category": item.get("target_category") or self.default_category,
                    "file_name": item.get("file_name"),
                    "content": item.get("content"),
                }
                file_path = self._apply_change(change)
                if file_path:
                    title = item.get("file_name") or ""
                    content = item.get("content") or ""
                    for line in content.splitlines():
                        if line.startswith("title:"):
                            title = line.replace("title:", "").strip()
                            break
                    created.append({"file_path": file_path, "action": "create", "title": title})
        except Exception as e:
            self._handle_exception(e, "Bootstrap 生成")

        return created

    def generate_doc_update(self, commit_message: str, diff: str) -> Optional[Dict]:
        base_context = self._get_base_context()
        processed_diff = self._preprocess_diff(diff)
        today = datetime.now().strftime("%Y-%m-%d")
        categories_str = ", ".join(self.categories)
        repo_name = config.REPO_NAME
        branch = config.UPSTREAM_BRANCH

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得引入 Diff/Summary 中不存在的符号或行为。"
        prompt = f"""
你是一个高级软件工程师和技术文档专家。你的任务是维护 `{repo_name}` 的 `{branch}` 分支开发文档（按模块分组，面向 AI/RAG）。

--- 当前分类结构 ---
所有文档必须归入以下分类之一：
{categories_str}

--- 上下文（现有文档） ---
{base_context}

--- 当前变更（Diff or Summary） ---
{processed_diff}

--- Commit Message ---
{commit_message}

--- 任务要求 ---
0. 禁止编造：只允许描述上面 Diff/Summary 中可以直接佐证的变更。
1. 判断操作：
   - 若变更不影响第三方开发者（对外契约/行为未变），返回 action: \"noop\" 并给出 reason（1 句）。
   - 全新对外契约/行为：action 为 \"create\"。
   - 对现有文档的显著修订：action 为 \"update\"。
2. 证据约束（必须满足，否则用 noop）：
   - 必须提供 evidence 数组（至少 2 条），每条为原样字符串（建议使用文件路径/符号名），且必须能在 Diff/Summary 或 Commit Message 中找到。
3. 生成内容规范：
   - Markdown 必须以 YAML frontmatter 开头：
     ---
     title: (简洁的功能名称)
     type: (feature | improvement | refactor)
     status: (stable | experimental)
     last_updated: {today}
     related_base: (关联基础文档文件名，可为空)
     ---
   - 必须包含一个名为 \"## 变更影响分析\" 的区块，说明边界情况/兼容性/最佳实践。
4. 输出格式：
   - 只能返回 JSON 对象，且只能包含这些 key：action, target_category, file_name, content, evidence, reason

--- 示例输出结构 ---
{{
  \"action\": \"create\",
  \"target_category\": \"design_standards\",
  \"file_name\": \"new_feature.md\",
  \"content\": \"---\\ntitle: ...\\n...\\n---\\n\\n## 概述\\n...\\n## 关键实现\\n...\\n## 变更影响分析\\n...\",\n  \"evidence\": [\"path/to/file.py\", \"ClassName.method\"],\n  \"reason\": \"\"\n}}
"""
        try:
            raw_response = self._call_llm(prompt, system_instruction=system_instruction, temperature=0.2)
            result = self._extract_json(raw_response)
            validation_error = self._validate_change(result, processed_diff, commit_message)
            if validation_error:
                if (result.get("action") or "").strip().lower() == "noop":
                    print(f"AI returned noop: {result.get('reason', '').strip()}")
                    return None
                print(f"AI output validation failed: {validation_error}")
                return None

            if (result.get("action") or "").strip().lower() == "noop":
                print(f"AI returned noop: {result.get('reason', '').strip()}")
                return None

            file_path = self._apply_change(result)
            if file_path:
                title = result.get("file_name") or ""
                content = result.get("content") or ""
                for line in content.splitlines():
                    if line.startswith("title:"):
                        title = line.replace("title:", "").strip()
                        break
                return {"file_path": file_path, "action": result.get("action"), "title": title}
            return None
        except Exception as e:
            self._handle_exception(e, "AI 生成")
            return None

    def _apply_change(self, change: Dict) -> Optional[str]:
        action = (change.get("action") or "").strip().lower()
        target_category = (change.get("target_category") or self.default_category).strip()
        file_name = (change.get("file_name") or "").strip()
        content = change.get("content")

        if not file_name or not isinstance(content, str) or not content.strip():
            print("Invalid change format from AI.")
            return None

        if target_category not in self.categories:
            print(f"Warning: Category {target_category} not defined. Using default.")
            target_category = self.default_category

        file_path: Optional[str] = None
        if action == "update":
            for cat in self.categories:
                potential_path = os.path.join(self.docs_root, cat, file_name)
                if os.path.exists(potential_path):
                    file_path = potential_path
                    break
            if not file_path:
                print(f"警告：请求更新 {file_name} 但未找到。将回退到创建操作。")
                action = "create"

        if action == "create" or not file_path:
            file_path = os.path.join(self.docs_root, target_category, file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"已应用文档{action}：{file_path}")
        return file_path
