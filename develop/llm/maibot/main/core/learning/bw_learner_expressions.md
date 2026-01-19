---
title: 黑话与表达方式自动化学习
last_updated: 2026-01-19
---

## 概述
src/bw_learner 模块实现了从聊天记录中自动化学习语言表达方式（Expression）与黑话（Jargon）的核心逻辑。该模块利用 LLM 提取对话的情境与风格，并支持通过自动任务或人工反思进行质量验证，旨在提升机器人的个性化回复能力。

## 目录/结构
- **expression_learner.py**: 定义了 ExpressionLearner 类，包含核心方法 learn_and_store，负责提取 (situation, style) 对。
- **jargon_miner.py**: 负责挖掘黑话并追踪其出现频率。
- **expression_selector.py**: 定义了 ExpressionSelector 类，包含 select_suitable_expressions 方法，用于语境匹配。
- **jargon_explainer.py**: 识别对话中的黑话并提供解释。
- **expression_auto_check_task.py**: 定时执行 ExpressionAutoCheckTask 任务，利用 LLM 进行自动质量评估。
- **message_recorder.py**: 统一的消息分发入口，管理学习触发的时间窗口与消息量。

## 适用范围
- **自动化风格提取**: 适用于从多轮对话中分析并学习特定的表达习惯。
- **黑话处理**: 适用于识别语境中的非标准词汇并推断其含义。
- **语境化回复生成**: 支持根据当前 chat_info 和语境从已学习库中检索最佳匹配项。

## 变更影响分析
- **存储与查询**: 修改 Expression.select().where(~Expression.checked) 等查询逻辑会影响待审核列表的处理。
- **配置变更**: 调整 global_config.expression.expression_auto_check_interval 会直接改变 LLM 调用频率及 Token 消耗量。
- **逻辑触发**: 学习过程受限于 message_recorder.py 中定义的最小消息数量（30条）和最小时间间隔（60秒）。
- **数据安全**: 若 person_name_filter 失效，可能会意外学习并存储包含隐私信息的表达方式。

## 证据
- ExpressionLearner.learn_and_store
- ExpressionSelector.select_suitable_expressions
- jargon_miner.py
- Expression.select().where(~Expression.checked)