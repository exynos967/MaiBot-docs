---
title: 核心架构：前额叶皮层 (PFC) 与行为规划
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 的核心对话逻辑采用“类大脑”分层结构，其中 `PFC`（Prefrontal Cortex，前额叶）负责高层决策、行为规划与对话状态管理。该模块旨在让机器人具备更接近“类人”的决策能力，而非简单的关键词匹配。

## 目录/结构
核心逻辑位于 `src/chat/brain_chat/PFC/`：
- `pfc.py`：PFC 主控，串联观察、规划、回复生成等流程。
- `action_planner.py`：行为规划（是否回复、回复方式/动作等）。
- `chat_observer.py` / `observation_info.py`：对外界输入进行观察/结构化，形成可用于决策的数据。
- `conversation.py` / `conversation_info.py`：会话上下文与元信息管理。
- `reply_generator.py` / `reply_checker.py`：回复生成与校验/过滤（边界策略以源码为准）。
- `message_storage.py`：PFC 内部的消息存储与检索（与 `src/chat/message_receive/storage.py` 的收发侧存储是不同层级）。
- `chat_states.py`：对话状态机与状态切换。

## 适用范围与边界
- **适用范围**: 适用于理解 MaiBot 如何决定回复时机、如何维护长期对话上下文，以及高层决策的主要边界。
- **边界**:
  - 消息协议适配与统一消息封装不在此模块，主要位于 `src/chat/message_receive/`，并依赖 `maim_message` 提供的统一消息类型。
  - LLM 的请求与多提供商适配主要位于 `src/llm_models/`（例如 `model_client/`、`utils_model.py`）。

## 变更影响分析
对 `src/chat/brain_chat/PFC/` 的修改会直接影响：回复时机、频率、风格与上下文保持能力。尤其是：
- 修改 `action_planner.py` 可能导致机器人过度活跃或反应迟钝。
- 修改 `conversation.py` / `message_storage.py` 可能影响“长期记忆/上下文”一致性与检索命中率。
- 修改 `reply_generator.py` / `reply_checker.py` 可能改变输出质量与安全边界（建议配套做回归验证）。
