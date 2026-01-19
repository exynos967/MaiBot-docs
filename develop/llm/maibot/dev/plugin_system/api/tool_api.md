---
title: 工具 API 文档
last_updated: 2026-01-19
---

## 概述

`tool_api.py` 模块提供了插件系统中工具（Tool）组件的核心访问接口。它允许系统根据工具名称获取具体的工具实例，并为大语言模型（LLM）提供可用的工具定义列表。该模块深度集成于 `component_registry`，负责协调插件配置与工具类的实例化。

## API 列表

### 1. get_tool_instance

获取公开工具的实例。

- **函数签名**: `get_tool_instance(tool_name: str, chat_stream: Optional["ChatStream"] = None) -> Optional[BaseTool]`
- **参数说明**:
    - `tool_name`: 目标工具的唯一标识名称。
    - `chat_stream`: 可选参数，用于传递当前聊天的上下文流信息。
- **返回值**: 返回 `BaseTool` 的子类实例；若未找到对应的工具定义或类，则返回 `None`。
- **内部逻辑**: 
    1. 从 `component_registry` 获取工具信息及所属插件配置。
    2. 获取工具对应的类定义。
    3. 返回初始化后的工具实例：`tool_class(plugin_config, chat_stream)`。

### 2. get_llm_available_tool_definitions

获取所有可供 LLM 使用的工具定义列表。

- **函数签名**: `get_llm_available_tool_definitions()`
- **返回值**: `List[Tuple[str, Dict[str, Any]]]`。每个元素为一个元组，包含工具名称及其对应的 JSON Schema 定义。
- **内部逻辑**: 遍历 `component_registry` 中标记为 LLM 可用的工具，并调用各工具类的 `get_tool_definition()` 静态方法。

## 调用约定

1. **上下文传递**: 在处理对话请求时，建议传入 `chat_stream` 参数，以便工具能够访问会话状态。
2. **异常处理**: 由于该 API 可能返回 `None`，调用方必须对返回值进行空值检查。
3. **依赖关系**: 该 API 依赖于 `src.plugin_system.core.component_registry` 的正确初始化。

## 变更影响分析

- **扩展性**: 新增工具只需在插件中注册为 `ComponentType.TOOL` 即可通过此 API 访问。
- **兼容性**: 修改 `BaseTool` 的构造函数签名将直接影响 `get_tool_instance` 的实例化逻辑。
- **性能**: `get_llm_available_tool_definitions` 会触发所有可用工具的定义生成，建议在工具数量极多时关注其执行效率。

## 证据

- **证据 1**: `src/plugin_system/apis/tool_api.py` 中定义了 `get_tool_instance` 函数，展示了如何通过 `component_registry` 获取 `tool_info` 和 `tool_class` 并返回实例。
- **证据 2**: `src/plugin_system/apis/tool_api.py` 中的 `get_llm_available_tool_definitions` 函数通过 `llm_available_tools.items()` 迭代并调用 `tool_class.get_tool_definition()` 来构建返回列表。