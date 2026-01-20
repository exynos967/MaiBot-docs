---
title: "Introduction to MaiBot"
last_updated: 2026-01-19
---

## 概述
MaiBot 是一个先进的 AI 驱动多平台机器人框架，具有复杂的插件生态系统。该框架采用双进程架构（Runner/Worker），以实现高效的监控与重启机制。其核心架构基于 planning-replying 循环（BrainChat/PFC），并强调通过长期个人记忆（LPMM）系统进行深度的记忆管理。

## 目录/结构
- **bot.py**: 系统入口，负责 Runner/Worker 双进程初始化及监控。
- **src/chat/**: 核心聊天逻辑，包含 PFC（前额叶皮层）规划及 HeartFlow/BrainChat 流程管理。
- **src/plugin_system/**: 插件基础设施，定义了 Action、Command、Tool 基类及标准化 API（如 ChatManager）。
- **src/memory_system/ & src/chat/knowledge/**: 记忆与知识系统，管理 LPMM、知识图谱及 RAG 相关组件。
- **src/webui/**: 基于 FastAPI 和 React 的后台管理界面，用于监控日志及配置机器人行为。

## 适用范围
- **多平台机器人开发**: 提供统一的 API 表面，支持包括 QQ 在内的多平台集成。
- **高级智能体构建**: 适用于需要复杂逻辑规划（PFC）和长期记忆（LPMM）能力的场景。
- **插件式功能扩展**: 开发者可通过标准化装饰器 `register_plugin` 快速扩展功能模块。

## 变更影响分析
- **系统生命周期**: 修改 `bot.py` 中的 `run_runner_process` 或 `RESTART_EXIT_CODE` (42) 将直接影响进程守护与故障自愈逻辑。
- **插件生态**: `src/plugin_system/apis/` 下的 API 变动将对所有已注册插件产生破坏性影响，特别是 `register_plugin` 装饰器。
- **部署构建**: `Dockerfile` 中包含 `lpmm-builder` 编译步骤，若涉及 LPMM 或 Cython 相关代码变更，需重新执行多阶段构建流程。

## 证据
- "MaiBot is an advanced AI-driven multi-platform bot framework featuring a sophisticated plugin ecosystem"
- "dual-process architecture (Runner/Worker)"
- "RESTART_EXIT_CODE = 42"
- "is_worker = os.environ.get(\"MAIBOT_WORKER_PROCESS\") == \"1\""
