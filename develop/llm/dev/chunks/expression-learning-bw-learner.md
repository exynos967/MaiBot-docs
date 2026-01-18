---
title: 表达学习与黑话挖掘 (BW Learner)
type: feature
status: experimental
last_updated: 2026-01-18
related_base: 
---

## 概述
`bw_learner` 模块是 MaiBot 实现“进化”的关键。它通过监控群聊消息，学习用户的说话风格、挖掘特定群聊的“黑话”（Jargon），并进行自我反思和表达优化，使机器人的回复更贴近真实人类。

## 目录/结构
- `src/bw_learner/expression_learner.py`: 表达学习的核心逻辑。
- `src/bw_learner/jargon_miner.py`: 负责从历史消息中提取高频或特殊词汇（黑话）。
- `src/bw_learner/message_recorder.py`: 记录用于学习的原始语料。
- `src/bw_learner/expression_reflector.py`: 评估学习到的表达是否符合设定。

## 适用范围与边界
- **适用范围**: 涉及机器人语气模仿、词汇量自动扩充以及群聊文化适应性功能。
- **边界**: 学习频率和语料过滤算法的细节（如如何避免学习违规词汇）需要补充信息或以源码验证。

## 变更影响分析
- 修改 `jargon_miner.py` 的阈值可能导致机器人开始使用大量无关词汇或无法识别核心黑话。
- `expression_learner.py` 的逻辑变更会直接影响机器人的“性格”演变过程。