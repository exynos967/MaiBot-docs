---
title: LLM 接入与 Model Client 抽象
type: feature
status: stable
last_updated: 2026-01-18
related_base:
---

## 概述
MaiBot 将“模型提供方（OpenAI/Gemini 等）”与“业务侧调用（对话/工具/嵌入/语音）”解耦：业务侧只关心统一的 `BaseClient` 能力与配置的 `ModelInfo`，从而支持多提供商切换、负载均衡与工具调用。

## 目录/结构
- **模型配置定义**：
  - `src/config/api_ada_configs.py`：`APIProvider`、`ModelInfo`、任务配置等数据结构。
  - `src/config/config.py`：加载 `model_config`，并将提供商/模型配置组织为可索引结构（细节以源码为准）。
- **Client 抽象与注册**：
  - `src/llm_models/model_client/base_client.py`：`BaseClient` 抽象、`APIResponse`/`UsageRecord`、`ClientRegistry`（注册/缓存客户端）。
  - `src/llm_models/model_client/__init__.py`：根据 `model_config.api_providers` 的 `client_type` 动态导入对应实现（例如 openai/gemini）。
- **提供商实现**：
  - `src/llm_models/model_client/openai_client.py`
  - `src/llm_models/model_client/gemini_client.py`
- **统一请求入口（业务侧更常用）**：
  - `src/llm_models/utils_model.py`：`LLMRequest`，提供 `generate_response_async` / `get_embedding` / `audio` 等统一调用路径，并记录用量到数据库（具体策略以源码为准）。
- **消息/工具载荷结构**：
  - `src/llm_models/payload_content/message.py`：`MessageBuilder`/`Message`
  - `src/llm_models/payload_content/tool_option.py`：`ToolOption`/`ToolCall`

## 适用范围与边界
- **适用范围**：需要接入新模型提供商、调整模型任务分配、或理解工具调用/推理字段在系统中的流转时。
- **边界**：PFC/对话侧如何构造 prompt、如何选择任务模型与重试策略属于更上层业务逻辑，需结合 `src/chat/` 与具体配置文件一并验证。

## 变更影响分析
- 调整 `BaseClient`/`APIResponse` 的字段或签名，会影响所有提供商实现与调用方（风险高，建议先全局检索引用并做回归）。
- 新增提供商通常需要：实现 `BaseClient` + 通过 `ClientRegistry` 注册 + 在配置中新增对应 `APIProvider.client_type`。
- 工具调用/响应解析逻辑变更会直接影响插件工具链与对话行为（可能引入不可预期的 side-effect）。
