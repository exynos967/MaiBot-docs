---
title: 核心架构与前额叶 (PFC) 决策系统
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 的核心逻辑基于模拟生物大脑的结构，其中 `PFC` (Prefrontal Cortex，前额叶) 负责高层决策、行为规划和对话状态管理。它不只是简单的问答，而是通过观察环境并规划动作来模拟“生命体”行为。

## 目录/结构
核心逻辑位于 `src/chat/brain_chat/PFC/` 目录下：
- `pfc.py`: 决策中枢，协调各个组件。
- `action_planner.py`: 行为规划器，决定何时说话及使用何种动作。
- `conversation.py` & `conversation_info.py`: 管理对话上下文与元数据。
- `message_storage.py`: 负责消息的持久化与检索。
- `chat_states.py`: 维护当前的聊天状态机。

## 适用范围与边界
- **适用范围**: 适用于处理 QQ 群聊等复杂交互场景下的逻辑判断与回复生成。
- **边界**: 具体的消息解析与协议适配（如 NapCat）不在此模块，需配合 `src/chat/` 其他组件使用。具体的 LLM 调用细节需要以源码验证。

## 变更影响分析
作为系统的“大脑”，对 PFC 目录下的任何修改都会直接影响机器人的回复逻辑、响应频率以及行为模式。修改 `action_planner.py` 可能会导致机器人过度活跃或反应迟钝。