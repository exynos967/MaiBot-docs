---
title: Chat Flow Management: HeartFlow and BrainChat
last_updated: 2026-01-19
---

## 概述
MaiBot 的核心聊天逻辑由 HeartFlow 和 BrainChat 两种主要流管理模块构成。系统采用规划-回复（planning-replying）架构，通过 PFC（前额叶皮层）逻辑实现复杂的会话决策。BrainChat 专注于私聊场景下的 ReAct 模式决策，而 HeartFlow 则针对群聊环境优化了频率控制与消息处理流程。

## 目录/结构
- **src/chat/brain_chat/**: 核心决策与私聊循环实现。包含 `brain_chat.py` (生命周期管理) 与 `brain_planner.py` (LLM 动作规划)。
- **src/chat/heart_flow/**: 包含群聊协调器 `heartflow.py`、会话处理器 `heartFC_chat.py`、以及 `frequency_control.py` (频率控制) 等组件。

## 适用范围
- **BrainChatting**: 位于 `src/chat/brain_chat/brain_chat.py`，管理私聊会话的完整生命周期（观察、等待、回复、状态转换）。它利用 `BrainPlanner` 解析 LLM 的 JSON 指令来执行 `reply` 或 `complete_talk` 等动作。
- **HeartFChatting**: 位于 `src/chat/heart_flow/heartFC_chat.py`，负责协调群聊中的动作规划与执行，并处理提及（mention）状态。
- **Heartflow**: 顶层协调器，通过 `get_or_create_heartflow_chat` 方法根据 `chat_id` 的属性动态分配 `BrainChatting` 或 `HeartFChatting` 实例。

## 变更影响分析
- **决策准确性**: `BrainPlanner` 依赖特定的 ReAct Prompt 结构。若 LLM 无法输出有效的 JSON，系统会强制执行 `complete_talk` 动作导致会话非预期中断。
- **回复频率调节**: `FrequencyControl` 模块将调节倍率限制在 0.1 至 5.0 之间。调整 `global_config.chat.planner_smooth` 会直接影响规划周期之间的休眠时间。
- **并发与任务安全**: `_main_chat_loop` 的异常捕获机制设置为 3 秒后重启。若出现持续性逻辑错误，可能引发任务频繁重启。此外，`CycleDetail` 的序列化深度被限制在 5 以防止递归错误。

## 证据
- `class BrainChatting:`
- `class HeartFChatting:`
- `self.action_planner = BrainPlanner(chat_id=self.stream_id, action_manager=self.action_manager)`
- `src/chat/heart_flow/heartFC_chat.py`