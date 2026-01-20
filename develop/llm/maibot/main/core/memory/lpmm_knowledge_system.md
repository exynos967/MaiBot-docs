---
title: "LPMM 长期个性化记忆模块"
last_updated: 2026-01-19
---

## 概述
Mai-LPMM（长期个性化记忆模块）是 MaiBot 用于知识库与记忆管理的核心组件。该系统通过 `src/chat/knowledge/ie_process.py` 提供的接口，利用 LLM 进行非结构化文本的实体抽取（NER）与 RDF 三元组提取。它结合了基于 FAISS 的向量数据库（由 `EmbeddingManager` 管理）与基于 NetworkX 风格的知识图谱（由 `KGManager` 管理），通过个性化 PageRank（PPR）算法实现检索增强生成（RAG）。

## 目录/结构
- `src/chat/knowledge/embedding_store.py`: 定义了 `EmbeddingManager` 和 `EmbeddingStore`，负责向量索引的持久化、多线程生成与 Top-K 检索。
- `src/chat/knowledge/kg_manager.py`: 负责增量构建知识图谱（`KGManager.build_kg`），包括实体、段落及同义词关系的建立。
- `src/chat/knowledge/qa_manager.py`: 通过 `QAManager.get_knowledge` 协调检索流程，结合相似度得分进行动态知识切片返回。
- `src/chat/knowledge/ie_process.py`: 提供 `info_extract_from_str` 函数，处理从文本到结构化 RDF 的提取逻辑。
- `src/chat/knowledge/__init__.py`: 提供系统启动入口 `lpmm_start_up`。

## 适用范围
- 适用于非结构化数据的结构化转换与长期存储。
- 适用于需要深度语义关联（KG）与文本相似度（Vector DB）相结合的个性化问答系统。

## 变更影响分析
- **数据一致性**: 更换嵌入模型需考虑 `check_embedding_model_consistency` 带来的异常风险。
- **并发性能**: 批量生成 Embedding 采用多线程模型，受 `lpmm_knowledge.max_embedding_workers` 配置影响。
- **构建成本**: `KGManager` 中的同义词自动连接操作（`_synonym_connect`）可能在高负载下消耗大量计算资源。

## 证据
- `EmbeddingManager.store_new_data_set`
- `KGManager.build_kg`
- `src/chat/knowledge/ie_process.py`
