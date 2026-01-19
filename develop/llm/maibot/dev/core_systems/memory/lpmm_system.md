---
title: Long-term Personal Memory (LPMM)
last_updated: 2026-01-19
---

## 概述
长期个人记忆 (Long-term Personal Memory, LPMM) 系统是 MaiBot 的核心组件，负责管理知识图谱 (KG) 和检索增强生成 (RAG)。该系统集成了基于 FAISS 的向量检索与基于图论的 Personalized PageRank (PPR) 算法，通过 EmbeddingStore 管理段落、实体及关系的向量化存储，旨在提升 AI 回复的上下文相关性与长期记忆能力。

## 目录/结构
本系统主要分布在以下目录：
- **src/chat/knowledge/**: 核心知识库实现，包含：
  - `embedding_store.py`: 负责 FAISS 索引操作与向量持久化。
  - `kg_manager.py`: 维护知识图谱连接、同义词边及 PPR 排序。
  - `ie_process.py`: 处理信息抽取 (IE)，利用 LLM 提取实体和 RDF 三元组。
  - `lpmm_ops.py`: 封装增量添加、检索及清空功能的公开 API 类 `LPMMOperations`。
  - `qa_manager.py`: 协调向量库与知识图谱的联合检索类 `QAManager`。
- **src/memory_system/**: 记忆管理与检索工具，包含：
  - `chat_history_summarizer.py`: 实现聊天记录的异步主题识别与压缩摘要。
  - `memory_retrieval.py`: 通过 ReAct Agent 驱动的记忆检索流程。

## 适用范围
- **系统初始化**: 通过 `lpmm_start_up` 函数在启动时加载数据。
- **插件扩展**: 插件可通过 `ChatManager` 或 `LPMMOperations` 访问长期记忆能力。
- **检索优化**: 可配置 `rag_synonym_threshold` 和 `qa_ppr_damping` 以调整检索精度。

## 变更影响分析
- **模型一致性**: 若更换嵌入模型，`EmbeddingStore` 存储的向量将失效，系统会触发一致性校验。
- **性能波动**: 随着知识图谱节点增加，执行 PPR 算法可能引入检索延迟。
- **并发冲突**: 多线程获取 Embedding 时依赖同步包装，在高并发场景下可能存在事件循环冲突风险。

## 证据
- `Long-term Personal Memory (LPMM)`
- `src/chat/knowledge/embedding_store.py`
- `class LPMMOperations:`
- `async def get_knowledge(self, question: str, limit: int = 5)`