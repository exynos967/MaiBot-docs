---
last_updated: 2026-01-19
---

# 配置 API 文档

## 概述
`config_api` 模块是插件系统的核心组件之一，旨在为插件提供安全、隔离且支持嵌套访问的配置读取功能。该模块封装了对全局配置和插件私有配置的访问逻辑，确保插件开发者能够以统一的方式获取所需参数。

## API 列表

### 1. get_global_config
- **功能描述**: 从全局配置（`global_config`）中安全地获取指定键的值。
- **函数签名**: `get_global_config(key: str, default: Any = None) -> Any`
- **参数说明**:
  - `key`: 字符串类型。支持命名空间式访问，如 `"section.subsection.key"`。大小写敏感。
  - `default`: 可选。当配置键不存在时返回的默认值。
- **返回**: 返回对应的配置项内容或 `default` 值。

### 2. get_plugin_config
- **功能描述**: 从插件特定的配置字典中获取值，同样支持嵌套访问。
- **函数签名**: `get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any`
- **参数说明**:
  - `plugin_config`: 插件自身的配置字典对象。
  - `key`: 字符串类型。支持点号分隔的嵌套键名。
  - `default`: 可选。当配置键不存在时返回的默认值。
- **返回**: 返回对应的配置项内容或 `default` 值。

## 调用约定
- **路径分隔符**: 必须使用点号 `.` 作为嵌套层级的分隔符。
- **只读性**: 插件应通过此 API 读取配置，而非直接修改 `global_config` 对象，以维持系统稳定性。
- **异常处理**: API 内部已实现 `try-except` 块。若键路径无效，系统会记录一条警告日志（`logger.warning`）并返回 `default` 参数指定的值，不会抛出中断性异常。

## 变更影响分析
- **隔离性**: 通过 `get_global_config` 访问配置，确保了插件与底层配置实现之间的解耦。
- **健壮性**: 嵌套访问逻辑支持 `dict` 索引和 `getattr` 两种方式，能够兼容不同结构的配置对象。

## 证据
- **源码位置**: `src/plugin_system/apis/config_api.py`
- **核心定义**: 源码中定义了 `def get_global_config(key: str, default: Any = None) -> Any:` 以及 `def get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any:` 两个关键函数。