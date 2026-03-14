# maim_message 开发文档（master · LLM 自动维护）

本区域由 GitHub Actions 定时从 `Mai-with-u/maim_message` 的 `master` 分支拉取变更，并通过 LLM 增量维护为“模块化分组文档”。

## 导航

- 本区域不预置固定分类；首次 bootstrap 会由 LLM 基于仓库结构自动生成分组目录与文档。
- 生成后的分组会自动出现在左侧侧边栏（Sidebar）中。
- 若上游存在 Tag 且工作流启用快照，将自动生成 `snapshots/` 并出现在侧边栏中。

## 说明

- 该区域仅包含自动维护内容；如需修订请通过文档仓库 PR。
- 快照仅对稳定分支生成（当上游存在 Tag 时），便于回溯历史版本的自动文档。
