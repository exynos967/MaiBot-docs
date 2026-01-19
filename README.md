# MaiBot 文档（LLM 自动维护）

本仓库使用 [VitePress](https://vitepress.dev/) 构建站点，用于将以下仓库的代码变更沉淀为可浏览的开发文档（LLM 自动生成/更新），并按“仓库/分支”隔离维护：

- `Mai-with-u/MaiBot`（`main` / `dev`）
- `Mai-with-u/maim_message`（`master`）

## 内容结构

- `develop/llm/maibot/main/`：跟踪上游 `MaiBot:main`（可按 Tag 归档快照）
- `develop/llm/maibot/dev/`：跟踪上游 `MaiBot:dev`（仅维护当前态）
- `develop/llm/maim_message/master/`：跟踪上游 `maim_message:master`（可按 Tag 归档快照；若上游无 Tag 则不会生成）

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

本仓库包含 3 条 GitHub Actions 工作流，用于从上游同步变更并通过 LLM 增量维护开发文档：

- `MaiBot:main` → `develop/llm/maibot/main/`（检测到新 Tag 时归档快照到 `develop/llm/maibot/main/snapshots/<tag>/`）
- `MaiBot:dev` → `develop/llm/maibot/dev/`（仅维护“当前态”，不做快照归档）
- `maim_message:master` → `develop/llm/maim_message/master/`（可选快照：上游存在 Tag 时才会归档）

LLM 配置通过 GitHub Secrets/Vars 提供（不会写入仓库）：

### Secrets（敏感/凭据）

在仓库 `Settings → Secrets and variables → Actions → Secrets` 配置：

- `OPENAI_API_KEY`（可选：使用 OpenAI/兼容接口时）
- `GEMINI_API_KEY`（可选：使用 Gemini 接口时；脚本会优先取 `GEMINI_API_KEY`，否则回退到 `OPENAI_API_KEY`）
- `OPENAI_API_BASE`（可选：OpenAI/兼容接口 Base URL）
- `BASE_URL`（可选：Gemini 或其他 Base URL；脚本会优先取 `BASE_URL`，否则回退到 `OPENAI_API_BASE`）
- `MODEL_NAME`（必填：模型名，例如 `gpt-4o-mini` / `gemini-1.5-flash`）
- `LLM_MAX_CONTEXT_CHARS`（可选：bootstrap 扫描阶段的上下文预算；不填默认 `120000`）

> 注：`GITHUB_TOKEN` 为 GitHub Actions 自带，不需要手动创建 Secret。

### Vars（非敏感配置）

在仓库 `Settings → Secrets and variables → Actions → Variables` 配置：

- `GEMINI_API_VERSION`（可选，默认 `v1beta`）
- `LLM_API_STYLE`（可选，默认 `auto`；可设为 `openai`/`gemini` 强制风格）
- `SYNC_LOOKBACK_HOURS`（可选，默认 `6`）
- `LLM_STRUCTURED_OUTPUT`（可选，默认 `1`；OpenAI 风格接口启用 `response_format: json_schema`，不支持会自动降级）
- `LLM_MAX_OUTPUT_TOKENS`（可选，默认空；**单一控制旋钮**：统一决定各阶段的 `max_tokens`。不填则各阶段使用内置默认值）

> 你也可以把 `LLM_STRUCTURED_OUTPUT` / `LLM_MAX_OUTPUT_TOKENS` 放在 Secrets 里，但需要同步把 3 个 workflow 的读取从 `vars.*` 改为 `secrets.*`。

首次建档（可选）：

- 如果你希望先生成一批“初始基线文档”，可以在 Actions 页面手动触发对应工作流并勾选 `bootstrap=true`。
  - 3 条工作流互相独立，生成结果不会混在一起。
