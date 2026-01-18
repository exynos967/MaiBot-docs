# MaiBot 文档

本仓库为 MaiBot 的官方文档。MaiBot 是一个智能聊天机器人，专为 QQ 群设计，具有基于 LLM 的对话能力、记忆系统和情感表达功能。

## 关于文档

此文档站点使用 [VitePress](https://vitepress.dev/) 构建，涵盖了安装、部署、配置以及开发（未完成） MaiBot 所需的所有内容。

## 文档部分

### 文档目录

- **安装指南**
    提供标准版和新手友好版的安装步骤，帮助用户快速上手。

- **API 参考（未完成）**
    详细介绍 MaiBot 提供的 API 接口及其使用方法。

- **部署方法**
    涵盖多种部署方式，包括 Docker、Linux、Windows 和群晖 NAS。

- **常见问题解答和故障排除**
    收录常见问题及其解决方案，帮助用户排查和解决问题。

- **文件结构和配置**
    说明项目的文件结构及配置方法，便于用户自定义和扩展。

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

本仓库包含两条 GitHub Actions 工作流，用于从 `Mai-with-u/MaiBot` 同步变更并通过 LLM 增量维护开发文档：

- `develop/llm/main/`：跟踪上游 `main` 分支；并在检测到新 Tag 时归档快照到 `develop/llm/main/snapshots/<tag>/`（仅归档 LLM 自动维护部分）。
- `develop/llm/dev/`：跟踪上游 `dev` 分支；仅维护“当前态”，不做快照归档。

LLM 配置通过 GitHub Secrets/Vars 提供（不会写入仓库）：

- `GEMINI_API_KEY`（或 `OPENAI_API_KEY`）
- `BASE_URL`（或 `OPENAI_API_BASE`）
- `MODEL_NAME`
- 可选：`LLM_API_STYLE`、`GEMINI_API_VERSION`、`SYNC_LOOKBACK_HOURS`

首次建档（可选）：

- 如果你希望先生成一批“初始基线文档”，可以在 Actions 页面手动触发工作流并勾选 `bootstrap=true`。
  - `main` / `dev` 两条工作流分别执行，生成结果不会混在一起。
