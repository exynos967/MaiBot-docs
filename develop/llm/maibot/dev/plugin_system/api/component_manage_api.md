---
title: 组件管理 API
last_updated: 2026-01-19
---

## 概述

组件管理 API 提供了对插件及其内部组件（Action, Command, Tool, EventHandler）的查询与状态管理功能。该模块支持全局范围和特定消息流（Stream）范围的组件启用与禁用操作。

## API 列表

### 插件信息查询
- `get_all_plugin_info()`: 获取所有已注册插件的详细信息。
- `get_plugin_info(plugin_name: str)`: 获取指定名称插件的信息。

### 组件查询
- `get_component_info(component_name, component_type)`: 获取特定类型组件的详细信息。
- `get_components_info_by_type(component_type)`: 获取指定类型的所有组件。
- `get_enabled_components_info_by_type(component_type)`: 获取指定类型且当前处于启用状态的组件。
- `get_registered_action_info(action_name)`: 获取 Action 注册信息。
- `get_registered_command_info(command_name)`: 获取 Command 注册信息。
- `get_registered_tool_info(tool_name)`: 获取 Tool 注册信息。
- `get_registered_event_handler_info(event_handler_name)`: 获取 EventHandler 注册信息。

### 组件状态管理
- `globally_enable_component(component_name, component_type)`: 全局启用组件。
- `globally_disable_component(component_name, component_type)`: **(异步)** 全局禁用组件。
- `locally_enable_component(component_name, component_type, stream_id)`: 在指定消息流中启用组件。
- `locally_disable_component(component_name, component_type, stream_id)`: 在指定消息流中禁用组件。
- `get_locally_disabled_components(stream_id, component_type)`: 获取指定消息流中被禁用的组件列表。

## 调用约定

1. **异步调用限制**：`globally_disable_component` 函数被定义为 `async`，调用时必须使用 `await` 关键字，且需在异步上下文中执行。
2. **类型安全**：调用涉及组件类型的 API 时，必须传入 `ComponentType` 枚举值。
3. **局部管理**：局部启用/禁用操作依赖于 `stream_id`，这通常对应于具体的聊天会话或频道 ID。

## 变更影响分析

1. **扩展性**：若增加新的组件类型，需在 `locally_enable_component`、`locally_disable_component` 及 `get_locally_disabled_components` 的 `match` 语句中增加对应的处理分支。
2. **依赖关系**：该 API 层封装了 `component_registry` 和 `global_announcement_manager` 的逻辑，底层实现的变更会直接影响此 API 的行为。

## 证据

- **证据 1**: `src/plugin_system/apis/component_manage_api.py` 中定义了异步禁用函数：`async def globally_disable_component(component_name: str, component_type: ComponentType) -> bool:`
- **证据 2**: `src/plugin_system/apis/component_manage_api.py` 中展示了基于 `stream_id` 的局部管理逻辑：`def locally_enable_component(component_name: str, component_type: ComponentType, stream_id: str) -> bool:`