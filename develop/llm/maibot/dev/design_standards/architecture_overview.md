---
title: 核心架构：前额叶皮层 (PFC) 与行为规划
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 的核心决策逻辑位于 `src/chat/brain_chat/PFC`（Pre-Frontal Cortex），模拟生物大脑的前额叶功能。它负责对话状态管理、行为规划（Action Planning）以及消息的观察与发送。该模块旨在让机器人表现出“类人”的决策能力，而非简单的关键词匹配。

## 目录/结构
- `src/chat/brain_chat/PFC/pfc.py`: 核心调度器，整合观察与行动。
- `src/chat/brain_chat/PFC/action_planner.py`: 负责规划机器人下一步的动作（如说话、沉默、使用表情）。
- `src/chat/brain_chat/PFC/conversation.py`: 管理对话上下文与会话逻辑。
- `src/chat/brain_chat/PFC/message_storage.py`: 负责消息的持久化与检索。
- `src/chat/brain_chat/PFC/chat_states.py`: 定义对话的不同状态机。

## 适用范围与边界
- **适用范围**: 适用于理解 MaiBot 如何处理输入消息、如何决定回复时机以及如何维护长期对话记忆。
- **边界**: 具体的消息协议适配（如 QQ 协议）不在此模块处理，需通过适配器层接入。具体的 LLM 调用逻辑需以源码验证其封装深度。

## 变更影响分析
- 修改 `action_planner.py` 将直接改变机器人的交互频率和语气风格。
- `message_storage.py` 的变更可能影响 RAG（检索增强生成）的效率和历史记忆的准确性。