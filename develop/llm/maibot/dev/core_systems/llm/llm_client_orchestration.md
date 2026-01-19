---
title: LLM Client and Payload Management
last_updated: 2026-01-19
---

## 概述
MaiBot 的 LLM 客户端编排系统提供了一套健壮的请求协调层，通过 `LLMRequest` 实现多策略模型选择（如负载均衡与随机策略）、自动重试机制以及故障时的模型自动切换。该系统通过统一的 `BaseClient` 抽象层支持多种提供商（如 Gemini 和 OpenAI），并集成了 Token 使用记录、图片压缩以及推理内容（CoT）解析功能。

## 目录/结构
- `src/llm_models/`: 核心编排逻辑与工具类。
    - `utils_model.py`: 包含 `LLMRequest` 类及 `generate_response_async` 等核心接口。
    - `utils.py`: 实现 `LLMUsageRecorder` 使用记录器与 `compress_messages` 消息压缩工具。
    - `exceptions.py`: 定义模型异常层次结构与错误码映射。
- `src/llm_models/model_client/`: 具体模型供应商的客户端实现。
    - `base_client.py`: 定义 `BaseClient` 接口规范与 `ClientRegistry` 注册表。
    - `gemini_client.py`: 处理 Gemini 特有的思考预算与安全设置。
    - `openai_client.py`: 实现基于 OpenAI 兼容接口的响应解析与工具调用。

## 适用范围
本规范适用于 MaiBot 内部所有涉及 LLM 交互的模块，主要包括：
- 通过 `generate_response_async` 进行异步文本响应生成。
- 使用 `get_embedding` 获取文本向量用于 RAG 系统。
- 调用 `compress_messages` 优化包含多媒体内容的 Payload，防止触发 413 错误。
- 插件系统通过 `generator_api.py` 间接调用的所有生成任务。

## 变更影响分析
- **核心编排层**：修改 `LLMRequest` 的 `selection_strategy` 或重试逻辑将影响全系统的模型调用效率与稳定性。
- **客户端抽象**：`BaseClient` 接口的任何变更都要求 `GeminiClient` 与 `OpenaiClient` 进行同步更新。
- **数据持久化**：`LLMUsageRecorder` 依赖于 `src.common.database.database_model.LLMUsage`，其字段变更会影响 Token 成本统计。
- **负载优化**：`img_target_size` 的调整会改变图片压缩阈值，进而影响视觉模型的请求成功率。

## 证据
- "class LLMRequest:"
- "class BaseClient(ABC):"
- "src/llm_models/utils_model.py"