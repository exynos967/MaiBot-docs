---
title: LLM 载荷与多模态消息构建
last_updated: 2026-01-19
---

## 概述
该文档定义了如何构建发送给大语言模型（LLM）的载荷内容，包括文本、图像及工具调用结构。通过使用结构化的 Builder 模式和数据模型（如 MessageBuilder 和 RespFormat），确保发送给模型的数据符合多模态交互要求。

## 目录/结构
核心组件位于 `src/llm_models/payload_content` 目录中：
- `src/llm_models/payload_content/message.py`: 包含 MessageBuilder、Message 和 RoleType，用于管理对话消息和角色。
- `src/llm_models/payload_content/resp_format.py`: 包含 RespFormat 类，用于处理响应格式和 JSON Schema 生成。
- `src/llm_models/payload_content/tool_option.py`: 包含 ToolOptionBuilder 和 ToolCall，用于描述和构建工具调用及参数。

## 适用范围
- **角色定义**: 支持 System, User, Assistant, Tool 四种对话角色。
- **多模态内容**: 支持文本及主流图片格式（jpg, jpeg, png, webp, gif）。
- **工具集成**: 提供流式构建工具（函数）调用项及其参数定义的能力。

## 变更影响分析
- **图片支持**: 图片格式校验通过 `SUPPORTED_IMAGE_FORMATS` 硬编码实现，若供应商增加格式支持需手动更新。
- **性能风险**: `_link_definitions` 递归处理 JSON Schema 中的 $defs 字段，在处理极深嵌套结构时可能存在性能风险。
- **数据一致性**: 文档建议通过 Builder 进行初始化，代码层面未强制禁止直接实例化可能导致数据状态不一致。

## 证据
- class MessageBuilder
- class ToolCall
- src/llm_models/payload_content/resp_format.py