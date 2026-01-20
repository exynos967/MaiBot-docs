---
title: "Knowledge Graph and RAG Retrieval"
last_updated: 2026-01-19
---

## 概述
MaiBot 的长期个人记忆 (LPMM) 系统通过整合 FAISS 向量检索与基于图论的知识图谱 (KG) 管理，实现了高效的检索增强生成 (RAG)。该系统利用 Personalized PageRank (PPR) 算法优化上下文排序，提升问答质量。

## 目录/结构
- src/chat/knowledge/__init__.py: 系统初始化入口，负责启动 EmbeddingManager 和 KGManager 并加载本地数据。
- src/chat/knowledge/embedding_store.py: 封装 FAISS 索引操作，管理段落、实体、关系三种类型的向量存储。
- src/chat/knowledge/kg_manager.py: 维护实体与文段间的图连接关系，实现 PPR 排序算法及增量图构建。
- src/chat/knowledge/qa_manager.py: QAManager 核心类，负责协调向量库与知识图谱执行联合检索 (kg_search)。
- src/chat/knowledge/lpmm_ops.py: 面向插件系统的公开 API 类 LPMMOperations，封装增删改查功能。
- src/chat/knowledge/ie_process.py: 信息抽取处理器 (IEProcess)，利用大模型提取实体和 RDF 三元组。

## 适用范围
本规格适用于 src/chat/knowledge/ 目录下的所有模块，主要用于处理 MaiBot 的长期记忆存储、知识检索以及基于 LLM 的信息抽取流程。

## 变更影响分析
- 检索性能：当知识图谱节点数过多时，执行 Personalized PageRank (PPR) 算法可能引入显著的检索延迟。
- 模型一致性：若更换嵌入模型，EmbeddingStore 会通过校验字符串拦截，导致本地已存储向量失效。
- 检索模式：可以通过 enable_ppr 配置项切换纯向量检索与图优化检索模式。

## 证据
- Personalized PageRank (PPR)
- src/chat/knowledge/__init__.py
