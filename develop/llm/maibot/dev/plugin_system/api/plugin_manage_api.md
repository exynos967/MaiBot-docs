---
title: 插件管理 API
last_updated: 2026-01-19
---

## 概述

`plugin_manage_api.py` 模块提供了一组用于管理插件生命周期的核心 API。这些接口允许开发者列出、加载、卸载、重新加载插件，以及管理插件目录。该模块作为 `plugin_manager` 的上层封装，简化了插件系统的交互。

## API 列表

### 1. list_loaded_plugins
- **描述**: 列出所有当前已加载的插件。
- **签名**: `list_loaded_plugins() -> List[str]`
- **返回值**: 当前加载的插件名称列表。

### 2. list_registered_plugins
- **描述**: 列出所有已注册（发现）的插件。
- **签名**: `list_registered_plugins() -> List[str]`
- **返回值**: 已注册的插件名称列表。

### 3. get_plugin_path
- **描述**: 获取指定插件的绝对路径。
- **签名**: `get_plugin_path(plugin_name: str) -> str`
- **异常**: 若插件不存在，抛出 `ValueError`。

### 4. remove_plugin (异步)
- **描述**: 卸载指定的插件。
- **签名**: `async remove_plugin(plugin_name: str) -> bool`
- **注意**: 必须在异步环境中调用。

### 5. reload_plugin (异步)
- **描述**: 重新加载指定的插件。
- **签名**: `async reload_plugin(plugin_name: str) -> bool`
- **注意**: 必须在异步环境中调用。

### 6. load_plugin
- **描述**: 加载指定的插件类。
- **签名**: `load_plugin(plugin_name: str) -> Tuple[bool, int]`
- **返回值**: `(是否成功, 成功或失败的个数)`。

### 7. add_plugin_directory
- **描述**: 向系统添加新的插件搜索目录。
- **签名**: `add_plugin_directory(plugin_directory: str) -> bool`

### 8. rescan_plugin_directory
- **描述**: 重新扫描插件目录以发现并加载新插件。
- **签名**: `rescan_plugin_directory() -> Tuple[int, int]`
- **返回值**: `(成功加载数量, 失败数量)`。

## 调用约定

1. **同步与异步**: `remove_plugin` 和 `reload_plugin` 是异步函数（`async`），调用时需使用 `await`。其余函数为同步函数。
2. **异常处理**: `get_plugin_path` 在找不到插件时会抛出 `ValueError`，建议在调用处进行捕获。
3. **内部依赖**: 所有 API 均依赖于 `src.plugin_system.core.plugin_manager.plugin_manager` 实例。

## 变更影响分析

- **扩展性**: 通过 `add_plugin_directory` 可以动态扩展插件来源。
- **稳定性**: 插件的卸载与重载通过异步接口处理，需确保调用链支持异步，否则可能导致阻塞或运行时错误。
- **一致性**: 所有的插件操作均通过单例 `plugin_manager` 进行，保证了状态的一致性。

## 证据

- **证据 1**: `src/plugin_system/apis/plugin_manage_api.py` 中定义了异步卸载接口：
  ```python
  async def remove_plugin(plugin_name: str) -> bool:
      # ...
      return await plugin_manager.remove_registered_plugin(plugin_name)
  ```
- **证据 2**: `src/plugin_system/apis/plugin_manage_api.py` 中定义了获取路径及异常处理逻辑：
  ```python
  def get_plugin_path(plugin_name: str) -> str:
      # ...
      if plugin_path := plugin_manager.get_plugin_path(plugin_name):
          return plugin_path
      else:
          raise ValueError(f"插件 '{plugin_name}' 不存在。")
  ```