---
title: "LLM API 接口文档"
last_updated: 2026-01-19
---

## 概述
LLM API 模块为插件系统提供与大语言模型交互的能力。其核心职责是封装底层模型客户端逻辑，提供简化的接口用于模型配置检索、基础文本生成、推理过程输出以及带工具调用的复杂任务处理。

## API 列表
- **get_available_models() -> Dict[str, TaskConfig]**
  - 获取当前系统中所有有效的 TaskConfig 模型配置。
- **generate_with_model(prompt, model_config, ...)**
  - 异步接口，使用指定配置生成回复。返回 (是否成功, 生成内容, 推理过程, 模型名称)。
- **generate_with_model_with_tools(...)**
  - 异步接口，支持传递工具选项(tool_options)，并返回可能的 ToolCall 列表。
- **generate_with_model_with_tools_by_message_factory(...)**
  - 进阶异步接口，接受一个 Callable 消息工厂函数，允许插件根据客户端特性动态构建 Message 列表。

## 调用约定
1. 开发者应通过 `get_available_models()` 检索到的配置对象作为生成函数的入参。
2. 所有的生成方法均采用 `async` 异步模式，必须配合 `await` 使用。
3. 生成结果的首个返回值为布尔值，用于指示请求是否成功，失败时生成内容通常包含错误详细说明。

## 变更影响分析
- 该模块直接依赖 `src.llm_models.utils_model.LLMRequest` 进行请求封装。
- 接口统一返回了 `reasoning_content`（推理内容），便于支持具有思考过程的模型，调用方需注意对应的解包逻辑。

## 证据
- 见源码 `src/plugin_system/apis/llm_api.py`。
- 核心定义：`def get_available_models() -> Dict[str, TaskConfig]:`。
- 核心定义：`async def generate_with_model(prompt: str, model_config: TaskConfig, ...)`。
