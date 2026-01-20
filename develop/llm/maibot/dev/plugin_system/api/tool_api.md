---
title: "工具 API 文档"
last_updated: 2026-01-19
---

## 概述

`tool_api.py` 是 MaiBot 插件系统的核心 API 之一，主要负责管理和导出工具（Tool）实例及定义。它作为插件系统与外部调用者（如 LLM 生成逻辑或 Chat 逻辑）之间的桥梁，提供了获取工具实例及检索 LLM 可用的工具定义列表的功能。

## API 列表

### 1. get_tool_instance

- **功能**: 根据工具名称获取特定的工具实例。
- **函数签名**: `get_tool_instance(tool_name: str, chat_stream: Optional["ChatStream"] = None) -> Optional[BaseTool]`
- **参数说明**:
  - `tool_name`: 字符串类型，代表工具的唯一标识名称。
  - `chat_stream`: 可选的聊天流对象，用于在工具实例化时传递当前会话上下文。
- **返回值**: 返回 `BaseTool` 子类的实例；若未找到对应的工具，则返回 `None`。
- **逻辑描述**: 该方法通过 `component_registry` 检索工具及其对应的插件配置，并完成实例化。

### 2. get_llm_available_tool_definitions

- **功能**: 获取所有对 LLM 开放的工具定义，用于模型调用决策。
- **函数签名**: `get_llm_available_tool_definitions()`
- **返回值**: 返回一个列表，每个元素为包含工具名称和定义的元组：`List[Tuple[str, Dict[str, Any]]]`。
- **逻辑描述**: 通过 `component_registry.get_llm_available_tools()` 获取可用工具类，并调用其 `get_tool_definition()` 方法提取标准定义格式。

## 调用约定

1. **上下文传递**: 建议在插件内部调用 `get_tool_instance` 时传入 `chat_stream`，以确保工具能够访问特定的会话属性。
2. **类型检查**: 该模块利用 `TYPE_CHECKING` 避免与 `ChatStream` 的循环导入，调用方应确保已安装相关基础库依赖。
3. **注册依赖**: 所有工具必须先通过系统注册机制注入到 `component_registry` 中，否则此 API 将无法定位到相关资源。

## 变更影响分析

- **注册中心依赖**: 本 API 高度依赖 `src.plugin_system.core.component_registry`。若注册逻辑变更，将直接导致工具检索失败。
- **LLM 集成**: `get_llm_available_tool_definitions` 的输出格式由 `BaseTool.get_tool_definition()` 决定。若修改工具定义结构，需同步更新 LLM 的 Prompt 构造逻辑。

## 证据

- 源码位置: `src/plugin_system/apis/tool_api.py`
- 关键函数: `def get_tool_instance(tool_name: str, chat_stream: Optional["ChatStream"] = None) -> Optional[BaseTool]:` 证实了工具实例获取的入口及参数要求。
- 关键类引入: `from src.plugin_system.base.base_tool import BaseTool` 证实了工具必须继承自统一的基类。
- 关键调用: `llm_available_tools = component_registry.get_llm_available_tools()` 证实了对底层注册中心的依赖关系。
