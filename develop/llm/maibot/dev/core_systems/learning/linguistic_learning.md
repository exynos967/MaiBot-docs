---
title: Linguistic Learning and Jargon Mining
last_updated: 2026-01-19
---

## 概述
MaiBot 的语言学习系统主要位于 `src/bw_learner` 路径下，核心功能是从聊天记录中自动提取用户语言风格（Expression）与专业术语（Jargon）。该系统通过 `MessageRecorder` 协调消息流，并利用 AI 自动化校验（Auto-check）或人工反馈机制（Reflection）来确保学习内容的准确性与安全性，使机器人在后续对话中能够模拟特定风格。

## 目录/结构
系统涉及的主要文件与类包括：
- `src/bw_learner/expression_learner.py`: 实现 `ExpressionLearner` 类，负责从消息中学习风格特征。
- `src/bw_learner/jargon_miner.py`: 实现 `JargonMiner` 类，负责术语挖掘及含义推断。
- `src/bw_learner/expression_selector.py`: 实现 `ExpressionSelector`，根据语境匹配已学习的表达方式。
- `src/bw_learner/expression_auto_check_task.py`: 定义 AI 风格校验任务。
- `src/bw_learner/jargon_explainer.py`: 提供术语的上下文含义解释。

## 适用范围
学习系统通过 `expression_groups` 变量配置聊天室共享规则，并由 `expression_self_reflect` 开关控制是否启用自动检查。术语挖掘（Jargon Mining）在检测到术语达到特定出现阈值（如 2, 4, 8, 24 次）后，将尝试使用 LLM 推断含义。通过 `expression_checked_only` 配置，可以强制机器人仅使用通过审核的表达方式。

## 变更影响分析
- **资源成本**: 频繁的风格挖掘与校验任务涉及多次 LLM 请求，需关注 API 消耗成本。
- **数据安全**: 学习过程存在习得不当内容的风险，系统通过 `ExpressionAutoCheckTask` 进行安全准则过滤。
- **并发性能**: 核心模块使用 `asyncio.Lock` 缓解任务处理中的并发风险。
- **底层依赖**: 模块深度依赖 `src.common.database.database_model.Expression` 和 `Jargon` 数据模型进行存储。

## 证据
- "src/bw_learner/expression_learner.py"
- "src/bw_learner/jargon_miner.py"