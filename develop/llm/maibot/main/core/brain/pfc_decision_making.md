---
title: "PFC 前额叶决策系统"
last_updated: 2026-01-19
---

## 概述
PFC (Pre-Frontal Cortex) 模块是 MaiBot 对话系统的核心决策层，负责维护对话状态、规划行动步（Action Planning）、设定对话目标、生成并校验回复。该系统采用组件化设计，通过核心循环实现自主对话逻辑。

## 目录/结构
该模块由以下核心源码文件组成：
- src/chat/brain_chat/PFC/pfc_manager.py: 单例模式的对话管理器，管理 Conversation 实例生命周期。
- src/chat/brain_chat/PFC/action_planner.py: 包含 ActionPlanner 类，负责根据上下文决策行动。
- src/chat/brain_chat/PFC/conversation.py: 驱动 PFC 思考与行动的核心循环实现。
- src/chat/brain_chat/PFC/reply_checker.py: 包含 check 方法，用于回复内容的逻辑与人设校验。
- src/chat/brain_chat/PFC/waiter.py: 管理默认超时阈值 DESIRED_TIMEOUT_SECONDS。

## 适用范围
适用于对话系统中的高级逻辑规划。利用 PFCManager 的 get_or_create_conversation 接口可初始化对话流。系统支持包括回复、等待、调取知识或结束对话在内的多种行动规划（Action Planning）。

## 变更影响分析
- **决策性能**: LLM 决策延迟或 pfc_utils.py 中的 get_items_from_json 解析失败可能导致对话卡顿。
- **并发一致性**: 在规划阶段（Conversation._check_new_messages_after_planning）若有新消息并发进入，可能导致生成的回复内容过时。
- **校验逻辑**: 生成的回复如与历史相似或不符人设，将被 ReplyChecker 打回，需注意 retry_count 的处理。

## 证据
- class ActionPlanner
- class PFCManager
- src/chat/brain_chat/PFC/pfc_manager.py
