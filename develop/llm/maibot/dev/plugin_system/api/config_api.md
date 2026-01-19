---
last_updated: 2026-01-19
---

# 配置 API 文档

## 概述
`config_api` 模块为插件提供了标准化的配置访问接口。该模块允许插件安全地读取全局配置以及插件自身的私有配置，支持通过点分隔符（dot notation）进行嵌套属性或键值的访问，并内置了异常处理机制以确保插件运行的稳定性。

## API 列表

### 1. get_global_config
- **功能**: 从全局配置对象中安全地获取指定键的值。
- **函数签名**: `get_global_config(key: str, default: Any = None) -> Any`
- **参数说明**:
    - `key`: 字符串类型，支持嵌套访问（如 `"section.key"`），大小写敏感。
    - `default`: 可选，当配置项不存在时返回的默认值。
- **返回**: 返回对应的配置项内容或 `default` 值。

### 2. get_plugin_config
- **功能**: 从插件提供的配置字典中获取特定键的值。
- **函数签名**: `get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any`
- **参数说明**:
    - `plugin_config`: 插件的配置字典对象。
    - `key`: 字符串类型，支持嵌套访问（如 `"db.host"`）。
    - `default`: 可选，当配置项不存在时返回的默认值。
- **返回**: 返回对应的配置项内容或 `default` 值。

## 调用约定
1. **路径格式**: 访问嵌套配置时，必须使用 `.` 作为分隔符。
2. **异常处理**: API 内部捕获了所有访问异常（如 `KeyError`），并在获取失败时通过 `logger` 记录警告信息，随后返回 `default` 参数指定的值。
3. **隔离性**: 插件应优先使用 `get_global_config` 读取全局共享信息，使用 `get_plugin_config` 处理插件私有逻辑。

## 变更影响分析
- **安全性**: 通过封装 `getattr` 和字典访问，避免了插件直接操作全局配置对象可能带来的副作用。
- **健壮性**: 统一的 `try-except` 结构保证了即使配置文件结构发生变化，插件也不会因为读取某个不存在的键而直接崩溃。

## 证据
- 源码位置: `src/plugin_system/apis/config_api.py`
- 函数定义: `def get_global_config(key: str, default: Any = None) -> Any:`
- 函数定义: `def get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any:`