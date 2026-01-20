---
 last_updated: 2026-01-19 
---
 
 # 快速上手与系统启动 
 
 ## 概述 
 MaiBot 采用双进程管理架构，以确保核心服务的稳定运行。引导程序位于根目录的 `bot.py`，它负责协调守护进程 (Runner) 与工作进程 (Worker)。当 Worker 进程执行业务逻辑并返回特定的重启码时，Runner 会自动重新拉起服务。系统初始化核心由 `src/main.py` 中的 `MainSystem` 类驱动。 
 
 ## 目录/结构 
 - `bot.py`: 启动入口，包含多进程管理、EULA 协议校验 (`check_eula`) 及守护进程逻辑。 
 - `src/main.py`: 系统初始化中心，负责 `MainSystem` 的实例化、异步任务调度及插件加载。 
 - `Dockerfile`: 提供基于 `python:3.13-slim` 的多阶段构建流程。 
 - `.env`: 环境配置文件，支持从 `template/template.env` 自动生成。 
 
 ## 适用范围 
 适用于 MaiBot 服务的初次部署、环境变量配置、容器化运行以及对进程重启机制的理解。 
 
 ## 变更影响分析 
 - **进程标识**: 系统通过环境变量 `MAIBOT_WORKER_PROCESS` 识别当前是否为工作进程。 
 - **自动重启**: Worker 进程返回 `RESTART_EXIT_CODE` (42) 时，Runner 会自动重启 Worker。 
 - **初始化时序**: `MainSystem.initialize()` 采用异步并发方式加载组件，单一关键组件失败可能导致整体流程挂起。 
 
 ## 证据 
 - `is_worker = os.environ.get("MAIBOT_WORKER_PROCESS") == "1"` 
 - `RESTART_EXIT_CODE = 42` 
 - `from src.main import MainSystem` 
 - `async def initialize(self)`
