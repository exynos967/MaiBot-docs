---
last_updated: 2026-01-19
---

# Tool API

## 概述
Tool API 是插件系统提供的核心接口之一，主要负责管理和获取系统中注册的工具（Tool）实例及其定义。它充当了组件注册表（component_registry）与外部调用者（如 LLM 规划器或插件逻辑）之间的桥梁，支持根据工具名称动态实例化工具，并为大语言模型提供可用的工具描述列表。

## API 列表

### 1. get_tool_instance
获取指定名称的公开工具实例。

- **函数签名**: `get_tool_instance(tool_name: str, chat_stream: Optional["ChatStream"] = None) -> Optional[BaseTool]`
- **参数说明**:
  - `tool_name`: 字符串类型，工具的唯一标识名称。
  - `chat_stream`: 可选的 `ChatStream` 对象，用于向工具实例传递当前的聊天上下文信息。
- **返回值**: 返回 `BaseTool` 的子类实例；若工具未注册或不存在，则返回 `None`。
- **内部逻辑**: 该函数会从 `component_registry` 获取工具的配置信息和类定义，并完成实例化。

### 2. get_llm_available_tool_definitions
获取所有标记为 LLM 可用的工具定义列表，通常用于构建 Prompt 中的 Tools 字段。

- **函数签名**: `get_llm_available_tool_definitions()`
- **返回值**: `List[Tuple[str, Dict[str, Any]]]`。返回一个列表，每个元素是一个包含工具名称和工具定义字典（通过 `get_tool_definition()` 获取）的元组。

## 调用约定
1. **上下文传递**: 在处理具体聊天请求时，建议传入 `chat_stream` 参数，以便工具能够访问会话状态。
2. **类型检查**: 返回的工具实例继承自 `BaseTool`，调用者应确保在使用前检查实例是否为 `None`。
3. **注册依赖**: 此 API 强依赖于 `src.plugin_system.core.component_registry` 的状态，只有在插件加载并注册完成后才能获取到对应的工具。

## 变更影响分析
- **组件注册表变更**: 如果 `component_registry` 的接口（如 `get_component_info` 或 `get_llm_available_tools`）发生变动，此 API 模块需要同步更新。
- **工具基类变更**: `BaseTool` 构造函数的签名变更（如 `plugin_config` 或 `chat_stream` 的处理方式）将直接影响 `get_tool_instance` 的实例化逻辑。
- **LLM 定义格式**: `get_llm_available_tool_definitions` 依赖于工具类实现的 `get_tool_definition()` 方法，若定义格式改变，将影响 LLM 的识别效果。

## 证据
- `src/plugin_system/apis/tool_api.py`: 包含了 `get_tool_instance` 函数的定义，展示了如何通过 `component_registry` 获取 `tool_class` 并实例化。
- `src/plugin_system/apis/tool_api.py`: 包含了 `get_llm_available_tool_definitions` 函数，展示了其通过调用 `tool_class.get_tool_definition()` 来收集工具描述。