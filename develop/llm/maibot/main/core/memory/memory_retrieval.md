---
title: 智能记忆检索与摘要
last_updated: 2026-01-19
---

## 概述
该模块实现了 MaiBot 的记忆系统，其核心功能是将分散的聊天消息通过 ChatHistorySummarizer 按话题打包压缩存储。同时，利用基于 ReAct 架构的智能记忆检索工具链（通过 MemoryRetrievalToolRegistry 注册），该系统能自动执行两阶段查询：生成问题并驱动 Agent 寻找答案，为回复生成提供精准的上下文增强。

## 目录/结构
- **src/memory_system/chat_history_summarizer.py**: 定义了 class ChatHistorySummarizer，负责累积、识别并压缩聊天话题，使用 TopicCache 管理进行中的话题状态。
- **src/memory_system/memory_retrieval.py**: 包含核心入口 build_memory_retrieval_prompt，负责构建检索 Prompt 并通过 _react_agent_solve_question 执行思考循环。
- **src/memory_system/memory_utils.py**: 提供 parse_questions_json 和 parse_datetime_to_timestamp 等辅助工具，利用 json_repair 处理不规则 JSON。
- **src/memory_system/retrieval_tools/**: 包含具体的工具实现，如 search_chat_history（历史搜索）、query_person_info（用户信息）及 query_words（黑话查询）。

## 适用范围
- **聊天历史检索**: 通过关键词、参与人及时间范围在数据库中搜索历史记录。
- **用户信息查询**: 模糊查询用户记忆点和画像信息。
- **术语解释**: 查询未知词汇、缩写或黑话的含义。
- **上下文增强**: 在 LLM 生成回复前，通过多轮工具调用补充背景资料。

## 变更影响分析
- **Token 成本**: ReAct Agent 的迭代受 global_config.memory.max_agent_iterations 限制，过度思考可能导致高昂的 Token 消耗。
- **解析稳定性**: 话题识别与问题提取依赖 LLM 产生的 JSON 质量，若 json_repair 无法修复则可能导致检索失败。
- **搜索限制**: 搜索聊天记录超过 15 条时会强制转为关键词统计，且 query_person_info 的相似度过滤阈值为 0.5。
- **数据安全**: 全局记忆检索受 global_config.memory.global_memory_blacklist 的平台/ID 黑名单隔离机制限制。

## 证据
- MemoryRetrievalToolRegistry
- class ChatHistorySummarizer
- query_person_info
- search_chat_history
- async def _react_agent_solve_question
- src/memory_system/retrieval_tools/tool_registry.py