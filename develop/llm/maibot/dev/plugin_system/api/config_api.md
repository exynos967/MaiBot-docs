---
last_updated: 2026-01-19
---

# Config API

## 概述
`config_api.py` 模块是插件系统的一部分，专门用于提供配置读取和用户信息获取的功能。它封装了对全局配置和插件特定配置的访问逻辑，支持通过嵌套路径安全地检索配置项，旨在为插件开发者提供一致且隔离的配置访问接口。

## API 列表

### get_global_config
- **定义**: `def get_global_config(key: str, default: Any = None) -> Any` 
- **功能**: 从全局配置对象 `global_config` 中安全地获取配置值。
- **参数说明**: 
  - `key`: 字符串类型。支持使用 "." 分隔的嵌套路径（例如 "section.key"）。
  - `default`: 若键名不存在或发生异常时返回的默认值，默认为 `None`。
- **返回**: 对应的配置值或默认值。

### get_plugin_config
- **定义**: `def get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any` 
- **功能**: 从指定的插件配置字典中获取值。
- **参数说明**: 
  - `plugin_config`: 字典类型。传入的插件配置上下文。
  - `key`: 字符串类型。支持嵌套键访问。
  - `default`: 配置不存在时的回退值。
- **行为**: 该函数兼容字典 key 访问及对象属性访问。

## 调用约定
- **路径表示法**: 嵌套访问必须使用命名空间格式，如 `"section.subsection.key"`。系统会通过 `key.split(".")` 自动解析层级。
- **大小写敏感**: 配置键名是大小写敏感的。
- **错误处理**: 访问失败时，API 会通过 `get_logger("config_api")` 记录警告日志并返回 `default`，不会中断插件执行流。

## 变更影响分析
- **解耦设计**: 插件通过此 API 访问配置而非直接操作 `global_config` 对象，确保了配置的只读性和系统全局状态的稳定性。
- **兼容性**: 增加嵌套支持（`key.split(".")`）使得配置结构可以平滑扩展，而无需修改插件的调用代码。

## 证据
- 源码 `src/plugin_system/apis/config_api.py` 明确包含：`def get_global_config(key: str, default: Any = None) -> Any:`。
- 源码 `src/plugin_system/apis/config_api.py` 中逻辑：`keys = key.split(".")` 证实了支持嵌套路径的设计。
- 导入声明：`from src.config.config import global_config` 确认了全局配置的来源。
