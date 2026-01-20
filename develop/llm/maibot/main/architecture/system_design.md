---
last_updated: 2026-01-19
---

## 概述
MaiBot 采用双进程守护架构，主要由 Runner 进程和 Worker 进程组成。Runner 进程（通过 `run_runner_process` 管理）充当守护进程，负责启动并监控 Worker 进程。当 Worker 进程以特定退出码（如 42）终止时，Runner 会自动将其重启，从而提高系统的可用性。

## 目录/结构
- `bot.py`: 项目入口，实现了 `run_runner_process` 和 `raw_main` 引导逻辑，并处理 `EULA` 协议校验。
- `src/main.py`: 定义了核心类 `MainSystem`，它是 Worker 进程的核心控制器，负责异步任务调度、插件加载（via `plugin_manager`）及 WebUI 的初始化。
- `Dockerfile`: 定义了基于 `python:3.13-slim` 的多阶段构建流程。

## 适用范围
该架构设计适用于需要长时间运行且具备自愈能力的 Bot 系统。其范围涵盖：
- 基于 `MAIBOT_WORKER_PROCESS` 环境变量的进程角色区分。
- 使用 `subprocess.Popen` 进行 Worker 进程的生命周期管理。
- 跨组件的任务协调，包括 `chat_bot` 消息处理和异步任务维护。

## 变更影响分析
- **进程逻辑**: 修改 `RESTART_EXIT_CODE`（当前为 42）将直接改变系统的重启触发条件。
- **初始化风险**: `bot.py` 中的 `check_eula` 函数在 Docker 等非交互环境下若触发阻塞式 `input()` 可能导致启动死锁。
- **清理流程**: 系统的优雅停机由 `graceful_shutdown` 负责，但 `Runner` 进程中使用 `os._exit()` 可能会导致某些资源清理逻辑被跳过。
- **部署约束**: 容器化构建强依赖于 `uv` 工具及同级目录下的 `MaiMBot-LPMM` 资源。

## 证据
- `RESTART_EXIT_CODE = 42`
- `class MainSystem:`
- `run_runner_process`
- `is_worker = os.environ.get("MAIBOT_WORKER_PROCESS") == "1"`
