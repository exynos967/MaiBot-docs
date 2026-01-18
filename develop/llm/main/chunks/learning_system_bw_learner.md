---
title: 表达学习与黑话挖掘系统 (bw_learner)
type: feature
status: experimental
last_updated: 2026-01-18
related_base: 
---

## 概述
`bw_learner` 是 MaiBot 实现“拟人化”和“进化”的关键模块。它通过分析聊天记录，学习用户的说话风格、黑话（Jargon）以及表达习惯，从而使机器人的回复更贴近特定群聊的氛围。

## 目录/结构
位于 `src/bw_learner/` 目录：
- `expression_learner.py`: 核心学习逻辑，负责提取表达方式。
- `jargon_miner.py` & `jargon_explainer.py`: 黑话挖掘与解释工具。
- `message_recorder.py`: 记录原始消息用于后续分析。
- `reflect_tracker.py`: 跟踪学习效果与反思过程。

## 适用范围与边界
- **适用范围**: 提升机器人在特定社群中的融入感，实现个性化语料积累。
- **边界**: 该系统依赖于大量的历史聊天数据。具体的学习算法（如是否涉及本地微调或仅为 Prompt 增强）需要以源码验证。

## 变更影响分析
该模块的变更会影响机器人语料库的积累质量。如果学习逻辑出现偏差，可能会导致机器人模仿不当言论或产生语序混乱。