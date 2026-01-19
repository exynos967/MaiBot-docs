---
last_updated: 2026-01-19
---

## 概述
本文档描述了插件系统中的组件管理 API。该模块位于 `src/plugin_system/apis/component_manage_api.py`，提供了一系列用于查询插件元数据、组件注册信息以及控制组件（Command, Action, Tool, EventHandler）启用状态的接口。系统支持全局控制与基于 `stream_id` 的局部控制。

## API 列表

### 插件信息查询
- **get_all_plugin_info()**: 返回所有已加载插件的信息字典。
- **get_plugin_info(plugin_name: str)**: 获取指定名称插件的 `PluginInfo` 对象。

### 组件信息检索
- **get_component_info(component_name, component_type)**: 获取指定类型组件的详细信息。
- **get_components_info_by_type(component_type)**: 批量获取指定类型的所有组件信息。
- **get_enabled_components_info_by_type(component_type)**: 仅获取当前已启用的组件信息。
- **特定查询接口**: 
    - `get_registered_action_info(action_name)`
    - `get_registered_command_info(command_name)`
    - `get_registered_tool_info(tool_name)`
    - `get_registered_event_handler_info(event_handler_name)`

### 状态管理接口
- **globally_enable_component(component_name, component_type)**: 全局启用组件。
- **globally_disable_component(component_name, component_type)**: **(异步)** 全局禁用组件。
- **locally_enable_component(component_name, component_type, stream_id)**: 在特定消息流中启用组件。
- **locally_disable_component(component_name, component_type, stream_id)**: 在特定消息流中禁用组件。
- **get_locally_disabled_components(stream_id, component_type)**: 查询特定消息流中被禁用的组件列表。

## 调用约定
1. **异步约束**: `globally_disable_component` 是异步函数，必须在异步上下文中调用。
2. **类型检查**: 调用组件相关 API 时，需传入 `src.plugin_system.base.component_types.ComponentType` 枚举值。
3. **局部流控制**: 局部启用/禁用方法依赖 `stream_id` 参数，通过 `global_announcement_manager` 维护状态。

## 变更影响分析
- **依赖关系**: 该模块作为外部接口层，内部通过延迟导入（Local Import）连接到 `component_registry` 和 `global_announcement_manager`，降低了模块间的耦合度。
- **扩展性**: 所有的组件操作都基于 `ComponentType` 进行分发，新增组件类型时需要同步更新 `locally_enable_component` 等方法的 `match` 分支。

## 证据
- **src/plugin_system/apis/component_manage_api.py**: 函数 `async def globally_disable_component` 明确使用了 `async` 关键字。
- **src/plugin_system/apis/component_manage_api.py**: 在 `locally_enable_component` 函数中，使用了 Python 3.10 的 `match component_type:` 语法对 `ComponentType.ACTION`, `COMMAND`, `TOOL`, `EVENT_HANDLER` 进行分支处理。