---
last_updated: 2026-01-19
---

# 工具 API (Tool API)

## 概述
本模块提供了与插件系统工具（Tools）交互的核心 API 接口。其主要功能包括根据工具名称获取经过初始化的工具实例，以及导出供大语言模型（LLM）调用的工具定义列表。

## API 列表

### 1. get_tool_instance
获取指定名称的公开工具实例。

- **签名**: `get_tool_instance(tool_name: str, chat_stream: Optional["ChatStream"] = None) -> Optional[BaseTool]`
- **参数说明**:
    - `tool_name`: 目标工具的注册名称。
    - `chat_stream`: 可选的聊天流对象，用于在工具执行时传递会话上下文。
- **返回**: 返回一个继承自 `BaseTool` 的工具类实例。如果组件注册表中不存在该工具，则返回 `None`。

### 2. get_llm_available_tool_definitions
获取所有已注册且 LLM 可用的工具定义。

- **签名**: `get_llm_available_tool_definitions()`
- **返回**: 一个包含元组的列表 `List[Tuple[str, Dict[str, Any]]]`，每个元组包含工具名称及其通过 `get_tool_definition()` 获取的定义字典。

## 调用约定
- **实例化逻辑**: `get_tool_instance` 会从 `component_registry` 中检索工具的元数据（`tool_info`）及插件配置（`plugin_config`），并将其连同 `chat_stream` 一起注入工具类的构造函数。
- **依赖关系**: 该 API 强依赖于 `src.plugin_system.core.component_registry` 进行组件检索，以及 `src.plugin_system.base.base_tool.BaseTool` 作为基类约定。

## 变更影响分析
- **注册表变更**: 如果 `component_registry` 中的 `get_component_info` 或 `get_component_class` 接口发生变化，此模块将无法正确加载工具。
- **工具基类协议**: `get_llm_available_tool_definitions` 依赖于工具类必须实现 `get_tool_definition()` 静态方法或类方法。

## 证据
- 接口定义见 `src/plugin_system/apis/tool_api.py`。
- 函数实现参考 `get_tool_instance` 以及其内部对 `component_registry` 的调用。
- 导出逻辑参考 `get_llm_available_tool_definitions` 函数。