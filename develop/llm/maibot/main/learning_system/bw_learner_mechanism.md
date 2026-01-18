---
title: 表达学习与黑话挖掘系统规范
type: feature
status: experimental
last_updated: 2026-01-18
related_base: 
---

## 概述
`bw_learner` 模块负责从聊天记录中提取语言风格、特定句式（Expressions）以及黑话（Jargon）。通过 `ExpressionLearner` 和 `JargonMiner`，机器人能够模仿用户的说话方式并理解社群特有的缩写或俚语。

## 目录/结构
主要组件位于 `src/bw_learner/`：
- `expression_learner.py`: 核心学习类，通过 `learn_style_prompt` 提取 `situation` 和 `style`。
- `jargon_miner.py`: 负责黑话的提取与含义推断（Inference），支持基于上下文或仅基于词条的推断。
- `learner_utils.py`: 提供消息过滤、相似度计算等通用工具。
- `expression_auto_check_task.py`: 自动检查已学习表达的合规性与适用性。

## 适用范围与边界
- **适用范围**: 提升机器人在特定群聊环境下的拟人化程度。
- **边界**: 学习过程受 `bot_config.toml` 中的 `expression` 配置约束（如 `expression_checked_only`）。单字黑话通常会被过滤。

## 变更影响分析
修改提取逻辑或 Prompt（如 `learn_style_prompt`）会影响语料库的质量。若 `jargon_miner` 的推断逻辑变更，可能导致机器人对特定词汇的误解。