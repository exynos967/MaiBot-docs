import argparse
import os
import shutil
import sys
from typing import Dict, List

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

    def _write_snapshot_indexes(self) -> None:
        snapshots_root = os.path.join(self.docs_root, "snapshots")
        if not os.path.isdir(snapshots_root):
            return

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
            index_lines.append(f"- [{v}](/develop/llm/main/snapshots/{v}/)")
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
        print("=== MaiBot 文档自动化同步开始 ===")
        try:
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
        print("=== MaiBot 文档自动化同步完成 ===")

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

                if latest_update.get("type") == "release":
                    tag_name = latest_update.get("tag_name")
                    pr_title = f"docs({branch}): 归档版本 {tag_name}"
                    pr_body = f"🚀 检测到 `{config.REPO_NAME}` 新版本发布：`{tag_name}`。\n\n本 PR 自动创建了该版本的文档快照（仅 LLM 自动维护部分）。"
                else:
                    sha = (latest_update.get("sha") or "")[:7]
                    pr_title = f"docs({branch}): 自动同步提交 {sha}"
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
    args = parser.parse_args()

    controller = MainController()
    controller.run(force_latest=args.force_latest)

