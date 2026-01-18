# MaiBot 文档（LLM 自动维护）

本仓库使用 [VitePress](https://vitepress.dev/) 构建站点，用于将以下仓库的代码变更沉淀为可浏览的开发文档（LLM 自动生成/更新），并按“仓库/分支”隔离维护：

- `Mai-with-u/MaiBot`（`main` / `dev`）
- `Mai-with-u/maim_message`（`master` / `dev`）

## 内容结构

- `develop/llm/maibot/main/`：跟踪上游 `MaiBot:main`（可按 Tag 归档快照）
- `develop/llm/maibot/dev/`：跟踪上游 `MaiBot:dev`（仅维护当前态）
- `develop/llm/maim_message/master/`：跟踪上游 `maim_message:master`（可按 Tag 归档快照；若上游无 Tag 则不会生成）
- `develop/llm/maim_message/dev/`：跟踪上游 `maim_message:dev`（仅维护当前态）

## 本地开发

### 本地部署要求
使用Nodejs安装对应依赖

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm docs:dev

# 构建生产版本
pnpm docs:build

# 预览生产版本
pnpm docs:preview
```

## 自动化同步（LLM 增量维护）

本仓库包含 4 条 GitHub Actions 工作流，用于从上游同步变更并通过 LLM 增量维护开发文档：

- `MaiBot:main` → `develop/llm/maibot/main/`（检测到新 Tag 时归档快照到 `develop/llm/maibot/main/snapshots/<tag>/`）
- `MaiBot:dev` → `develop/llm/maibot/dev/`（仅维护“当前态”，不做快照归档）
- `maim_message:master` → `develop/llm/maim_message/master/`（可选快照：上游存在 Tag 时才会归档）
- `maim_message:dev` → `develop/llm/maim_message/dev/`（仅维护“当前态”，不做快照归档）

LLM 配置通过 GitHub Secrets/Vars 提供（不会写入仓库）：

- `GEMINI_API_KEY`（或 `OPENAI_API_KEY`）
- `BASE_URL`（或 `OPENAI_API_BASE`）
- `MODEL_NAME`
- 可选：`LLM_API_STYLE`、`GEMINI_API_VERSION`、`SYNC_LOOKBACK_HOURS`

首次建档（可选）：

- 如果你希望先生成一批“初始基线文档”，可以在 Actions 页面手动触发对应工作流并勾选 `bootstrap=true`。
  - 4 条工作流互相独立，生成结果不会混在一起。
