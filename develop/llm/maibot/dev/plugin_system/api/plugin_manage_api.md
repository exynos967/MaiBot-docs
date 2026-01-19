---
last_updated: 2026-01-19
---

# 插件管理 API

## 概述
`src/plugin_system/apis/plugin_manage_api.py` 提供了一组标准接口，用于在运行时动态管理 MaiBot 的插件。这些 API 封装了核心 `plugin_manager` 的功能，支持插件的列表查询、路径获取、动态加载、卸载、重新加载以及目录扫描等操作。

## API 列表

### 1. `list_loaded_plugins()`
- **功能**: 获取当前已加载的所有插件名称。
- **返回**: `List[str]` - 插件名称列表。

### 2. `list_registered_plugins()`
- **功能**: 获取所有已注册（发现）的插件名称。
- **返回**: `List[str]` - 插件名称列表。

### 3. `get_plugin_path(plugin_name: str)`
- **功能**: 获取指定插件所在目录的绝对路径。
- **参数**: `plugin_name` (str) - 插件名称。
- **返回**: `str` - 路径字符串。
- **异常**: 若插件不存在则抛出 `ValueError`。

### 4. `remove_plugin(plugin_name: str)`
- **功能**: 异步卸载指定插件。
- **参数**: `plugin_name` (str) - 插件名称。
- **返回**: `bool` - 卸载是否成功。

### 5. `reload_plugin(plugin_name: str)`
- **功能**: 异步重新加载指定插件。
- **参数**: `plugin_name` (str) - 插件名称。
- **返回**: `bool` - 重载是否成功。

### 6. `load_plugin(plugin_name: str)`
- **功能**: 加载指定的插件类。
- **返回**: `Tuple[bool, int]` - (是否成功, 影响的数量)。

### 7. `add_plugin_directory(plugin_directory: str)`
- **功能**: 向系统添加一个新的插件搜索目录。
- **返回**: `bool` - 添加是否成功。

### 8. `rescan_plugin_directory()`
- **功能**: 重新扫描已注册的目录以发现并加载新插件。
- **返回**: `Tuple[int, int]` - (成功加载数, 失败数)。

## 调用约定
- **异步性**: `remove_plugin` 和 `reload_plugin` 是异步函数 (`async def`)，调用时必须使用 `await` 关键字并在异步上下文中运行。
- **延迟导入**: 所有函数内部均采用 `from src.plugin_system.core.plugin_manager import plugin_manager` 的延迟导入方式，以避免循环引用。

## 变更影响分析
- **核心耦合**: 该文件高度依赖 `src.plugin_system.core.plugin_manager`。如果核心管理器的接口发生变化，此处的封装层必须同步更新。
- **扩展性**: `add_plugin_directory` 允许动态扩展插件源，适用于 WebUI 远程安装插件后的自动热加载场景。

## 证据
- `src/plugin_system/apis/plugin_manage_api.py`: `async def remove_plugin(plugin_name: str) -> bool:` 证明了卸载操作的异步性质。
- `src/plugin_system/apis/plugin_manage_api.py`: `def get_plugin_path(plugin_name: str) -> str:` 及其中的 `raise ValueError` 逻辑，证明了路径查询的错误处理机制。