---
title: PFC (Prefrontal Cortex) 决策架构规范
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 的核心决策逻辑模拟生物前额叶（PFC）功能，负责对话目标的分析、行动规划（Action Planning）以及观察环境状态。该系统使机器人能够根据上下文动态决定是回复、倾听、检索知识还是结束对话。

## 目录/结构
核心逻辑位于 `src/chat/brain_chat/PFC/`：
- `pfc.py`: 包含 `GoalAnalyzer` 类，利用 LLM 分析对话历史并设定 `goal` 与 `reasoning`。
- `action_planner.py`: 包含 `ActionPlanner` 类，定义了 `PROMPT_INITIAL_REPLY` 和 `PROMPT_FOLLOW_UP` 等决策模板。
- `observation_info.py` & `conversation_info.py`: 封装当前对话的观察数据与历史状态。
- `pfc_utils.py`: 提供 JSON 解析等辅助工具。

## 适用范围与边界
- **适用范围**: 适用于所有基于 `brain_chat` 模式的私聊与群聊决策流。
- **边界**: 具体的动作执行（如发送消息）由 `message_sender.py` 负责，PFC 仅负责逻辑层面的“规划”。

## 变更影响分析
修改 `action_planner.py` 中的 Prompt 模板或 `ActionPlanner.plan` 方法将直接改变机器人的交互频率、回复倾向（如是否容易“屏蔽”用户）以及对上下文的理解深度。