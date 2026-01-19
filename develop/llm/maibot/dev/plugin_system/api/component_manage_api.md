---
last_updated: 2026-01-19
---

# 组件管理 API

## 概述

组件管理 API (`component_manage_api.py`) 是 MaiBot 插件系统的核心接口之一，用于查询插件信息以及管理各类组件（Action, Command, Tool, EventHandler）的状态。该 API 支持全局范围的状态切换，也支持针对特定消息流（stream_id）的局部状态控制。

## API 列表

### 插件信息查询
- `get_all_plugin_info() -> Dict[str, PluginInfo]`: 获取系统中所有已加载插件的详细信息。
- `get_plugin_info(plugin_name: str) -> Optional[PluginInfo]`: 获取指定名称插件的信息。

### 组件信息查询
- `get_component_info(component_name, component_type) -> Optional[Union[CommandInfo, ActionInfo, EventHandlerInfo]]`: 获取特定类型组件的详细信息。
- `get_components_info_by_type(component_type) -> Dict`: 获取指定类型的所有组件信息。
- `get_enabled_components_info_by_type(component_type) -> Dict`: 获取指定类型中当前处于启用状态的组件信息。
- `get_registered_action_info(action_name)` / `get_registered_command_info(command_name)` / `get_registered_tool_info(tool_name)` / `get_registered_event_handler_info(event_handler_name)`: 针对特定组件类型的快捷查询接口。

### 状态管理
- `globally_enable_component(component_name, component_type) -> bool`: 在全局范围内启用指定组件。
- `async globally_disable_component(component_name, component_type) -> bool`: 在全局范围内禁用指定组件（注意：此接口为异步函数）。
- `locally_enable_component(component_name, component_type, stream_id) -> bool`: 在指定的会话流中启用组件。
- `locally_disable_component(component_name, component_type, stream_id) -> bool`: 在指定的会话流中禁用组件。
- `get_locally_disabled_components(stream_id, component_type) -> list[str]`: 获取特定会话流中被禁用的组件列表。

## 调用约定

1. **异步调用**: `globally_disable_component` 是该模块中唯一的异步方法，调用时必须使用 `await` 关键字。
2. **类型安全**: 调用查询或管理方法时，必须传入正确的 `ComponentType` 枚举值（如 `ComponentType.ACTION`, `ComponentType.COMMAND` 等）。
3. **局部控制**: 局部启用/禁用方法依赖于 `global_announcement_manager`，主要用于处理特定群聊或私聊中的功能开关。

## 变更影响分析

- **注册表依赖**: 该 API 高度依赖 `src.plugin_system.core.component_registry`。如果注册表结构发生变化，此 API 的查询结果将直接受影响。
- **管理器依赖**: 局部管理功能依赖 `global_announcement_manager`。如果消息流 ID 的生成逻辑或存储逻辑变更，局部禁用功能可能失效。

## 证据

- **源码位置**: `src/plugin_system/apis/component_manage_api.py` 明确定义了所有上述管理接口。
- **异步定义**: 源码中 `async def globally_disable_component` 证实了禁用操作的异步特性。
- **局部逻辑**: `locally_enable_component` 函数内部通过 `match component_type` 逻辑分发至 `global_announcement_manager` 的不同方法。