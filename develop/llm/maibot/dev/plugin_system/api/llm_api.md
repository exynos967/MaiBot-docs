---
title: LLM API 插件接口文档
last_updated: 2026-01-19
---

## 概述

`llm_api` 模块为插件系统提供了与大语言模型（LLM）交互的标准接口。它封装了底层的模型请求逻辑，支持获取可用模型配置、基础文本生成、工具调用（Tool Call）以及基于消息工厂的复杂对话生成。

## API 列表

### 1. get_available_models
- **功能**: 获取当前系统中所有可用的模型配置。
- **签名**: `def get_available_models() -> Dict[str, TaskConfig]`
- **返回值**: 返回一个字典，Key 为模型标识符，Value 为 `TaskConfig` 对象。

### 2. generate_with_model
- **功能**: 使用指定的模型配置生成内容。
- **签名**: `async def generate_with_model(prompt: str, model_config: TaskConfig, request_type: str = "plugin.generate", temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Tuple[bool, str, str, str]`
- **返回值**: `(是否成功, 生成内容, 推理过程, 模型名称)`。

### 3. generate_with_model_with_tools
- **功能**: 支持工具调用的模型生成接口。
- **签名**: `async def generate_with_model_with_tools(prompt: str, model_config: TaskConfig, tool_options: List[Dict[str, Any]] | None = None, ...) -> Tuple[bool, str, str, str, List[ToolCall] | None]`
- **返回值**: `(是否成功, 生成内容, 推理过程, 模型名称, 工具调用列表)`。

### 4. generate_with_model_with_tools_by_message_factory
- **功能**: 通过消息工厂构建消息列表，并支持工具调用的高级生成接口。
- **签名**: `async def generate_with_model_with_tools_by_message_factory(message_factory: Callable[[BaseClient], List[Message]], model_config: TaskConfig, ...) -> Tuple[bool, str, str, str, List[ToolCall] | None]`
- **返回值**: `(是否成功, 生成内容, 推理过程, 模型名称, 工具调用列表)`。

## 调用约定

1. **异步调用**: 除 `get_available_models` 外，所有生成接口均为 `async` 函数，必须使用 `await` 调用。
2. **配置获取**: 建议先通过 `get_available_models()` 获取合法的 `TaskConfig` 对象，再传递给生成函数。
3. **异常处理**: 接口内部已封装 `try-except` 块。若调用失败，元组的首个元素（布尔值）将返回 `False`，且错误信息会记录在日志中并作为内容返回。

## 变更影响分析

- **模型配置变更**: 若 `src/config/api_ada_configs.py` 中的 `TaskConfig` 结构发生变化，将直接影响此 API 的参数类型和返回值解析。
- **底层请求逻辑**: 此 API 依赖 `src.llm_models.utils_model.LLMRequest`。如果 `generate_response_async` 的签名变更，此模块需同步更新。

## 证据

- **证据 1**: `src/plugin_system/apis/llm_api.py` 中定义了 `get_available_models` 函数，通过遍历 `model_config.model_task_config` 获取配置。
- **证据 2**: `src/plugin_system/apis/llm_api.py` 中的 `generate_with_model` 函数签名明确要求 `model_config: TaskConfig` 参数，并返回 `Tuple[bool, str, str, str]`。