---
title: "Planner and Replier Monitoring"
last_updated: 2026-01-19
---

## 概述
MaiBot 的监控系统是一个用于实时查看和分析机器人内部推理过程（Planner & Replier）的集成工具。它允许管理员追踪 PFC（前额叶皮层）的规划细节、执行的 Actions 列表以及 Replier 的最终输出耗时。该系统基于 WebUI 架构，通过 FastAPI 后端解析本地存储的 JSON 日志文件，并由 React 前端组件进行可视化展示。

## 目录/结构
系统的核心代码分布在以下路径：
- **后端 API (`src/webui/api/`)**:
  - `planner.py`: 定义了 `get_planner_overview` 和 `get_chat_plan_logs` 等接口，用于处理 `logs/plan` 路径下的日志。
  - `replier.py`: 定义了 `get_replier_overview` 和 `get_chat_reply_logs` 接口，处理 `logs/reply` 路径下的回复日志。
- **前端路由 (`dashboard/src/routes/monitor/`)**:
  - `index.tsx`: 包含 `PlannerMonitorPage` 组件，作为监控页面的统一入口。
  - `planner-monitor.tsx`: 实现 `PlannerMonitor` 组件，用于展示任务规划的推理过程及 Action 统计。
  - `replier-monitor.tsx`: 实现 `ReplierMonitor` 组件，专注于模型响应耗时和生成结果。
  - `use-monitor.ts`: 提供 `useAutoRefresh` 和 `useChatNameMap` 等通用 Hook。

## 适用范围
本规范适用于 MaiBot WebUI 的开发者与运维人员，用于维护和扩展以下功能：
- 实时监控机器人计划执行的 reasoning 预览。
- 回溯特定 `chat_id` 下的推理日志详情 (`PlanLogDetail`)。
- 统计模型在回复生成过程中的性能耗时 (`overall_ms`)。

## 变更影响分析
- **存储路径**: 监控逻辑依赖于 `PLAN_LOG_DIR` 和 `REPLY_LOG_DIR` 的硬编码路径（如 `logs/plan`）。若修改日志存储策略，需同步更新 `src/webui/api/planner.py`。
- **性能负载**: 由于当前实现通过解析文件名提取 `parse_timestamp_from_filename`，大量日志积压可能导致 `get_planner_overview` 的响应延迟。
- **并发与安全**: 直接基于 `chat_id` 拼接路径可能存在风险，且在大并发访问下，频繁的磁盘 I/O 需进一步优化。

## 证据
- `class PlanLogDetail(BaseModel):` (定义于 `src/webui/api/planner.py`)
- `dashboard/src/routes/monitor/planner-monitor.tsx` (前端计划器监控实现文件)
