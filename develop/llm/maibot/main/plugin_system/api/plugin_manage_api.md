---
last_updated: 2026-01-19
---

## 概述
本文档描述了位于 `src/plugin_system/apis/plugin_manage_api.py` 中的插件管理 API。该模块提供了查询、加载、卸载、重载插件以及管理插件扫描目录的公共接口。

## API 列表
- `list_loaded_plugins() -> List[str]`: 返回当前已加载插件的名称列表。
- `list_registered_plugins() -> List[str]`: 返回所有已注册插件的名称列表。
- `get_plugin_path(plugin_name: str) -> str`: 获取指定插件的绝对路径；若插件不存在则抛举 `ValueError`。
- `async remove_plugin(plugin_name: str) -> bool`: 异步卸载指定插件，返回操作结果。
- `async reload_plugin(plugin_name: str) -> bool`: 异步重新加载指定插件。
- `load_plugin(plugin_name: str) -> Tuple[bool, int]`: 加载指定插件类，返回是否成功及加载的数量。
- `add_plugin_directory(plugin_directory: str) -> bool`: 向系统添加新的插件搜索路径。
- `rescan_plugin_directory() -> Tuple[int, int]`: 重新扫描插件目录，返回成功和失败的插件计数。

## 调用约定
- **异步支持**: `remove_plugin` 与 `reload_plugin` 是协程函数，调用时必须使用 `await` 关键字。
- **异常机制**: `get_plugin_path` 接口在未找到匹配插件时会显式抛出 `ValueError`。
- **内部实现**: 此 API 层采用延迟导入（Lazy Import）模式访问 `src.plugin_system.core.plugin_manager`，以减少初始导入开销。

## 变更影响分析
- 由于 API 是对 `plugin_manager` 的封装，底层管理器的接口变动需同步调整此处的参数和返回类型。
- 异步接口的引入要求调用方代码块也必须在异步事件循环中运行。

## 证据
- 接口定义位于文件: `src/plugin_system/apis/plugin_manage_api.py`
- 异步卸载签名: `async def remove_plugin(plugin_name: str) -> bool:`
- 异常处理逻辑: `raise ValueError(f"插件 '{plugin_name}' 不存在。")`