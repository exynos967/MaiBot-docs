---
title: "LLM Generator API"
last_updated: 2026-01-19
---

## 概述
LLM Generator API 是 MaiBot 插件系统的核心组件之一，主要负责暴露机器人的回复生成引擎。通过该 API，开发者可以让插件利用系统底层的 LLM 驱动引擎（包括 PFC 规划与回复架构）来产生回复内容。该功能主要通过 `src/plugin_system/apis/generator_api.py` 中的 `generate_reply` 异步函数实现。

## 目录/结构
该 API 属于 `src/plugin_system/apis` 模块，相关核心文件与组件包括：
- **src/plugin_system/apis/generator_api.py**: 包含 `generate_reply` 函数，是调用回复生成引擎的主要入口。
- **src/plugin_system/apis/llm_api.py**: 提供底层模型生成请求支持，定义了 `LLMRequest` 与 `TaskConfig` 等配置类。
- **相关依赖**: 依赖于 `src.chat.message_receive.chat_stream` 提供的聊天流上下文。

## 适用范围
- **插件扩展**: 适用于需要自定义逻辑但仍想复用机器人核心生成能力的插件。
- **回复逻辑定制**: 插件可以通过传入特定的 `action_data` 和 `chat_stream` 来干预或触发 LLM 生成过程。
- **标准化接入**: 作为插件系统与系统核心回复引擎之间的抽象层，确保插件开发的标准化。

## 变更影响分析
- **平台适配性**: 部分 API 默认参数（如平台标识）在多处硬编码为 "qq"。在非 QQ 平台使用时，开发者需显式传递参数以避免逻辑错误。
- **兼容性负担**: 回复生成逻辑中包含较多向下兼容处理，内部逻辑相对复杂，升级核心引擎时需关注参数传递的一致性。
- **测试挑战**: 由于 API 设计依赖 `get_chat_manager()` 和 `plugin_manager` 等全局单例，进行单元测试时可能需要较大工作量的 Mock 操作。

## 证据
- `generate_reply(chat_stream, chat_id, action_data, ...)`
- `src/plugin_system/apis/generator_api.py`
