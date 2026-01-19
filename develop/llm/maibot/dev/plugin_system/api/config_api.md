---
last_updated: 2026-01-19
---

## 概述

`config_api.py` 模块是 MaiBot 插件系统的核心组件之一，旨在为插件提供安全、标准化的配置读取接口。它支持通过命名空间（点号分隔符）访问嵌套的全局配置以及插件私有配置，确保了配置访问的隔离性与只读安全性。

## API 列表

### 1. get_global_config

从系统全局配置中安全地获取指定键的值。

- **函数签名**: `get_global_config(key: str, default: Any = None) -> Any`
- **参数说明**:
    - `key`: 字符串类型。支持嵌套访问，例如 `"section.subsection.key"`。大小写敏感。
    - `default`: 可选。若配置项不存在，则返回此默认值。
- **返回**: 配置项的值或默认值。

### 2. get_plugin_config

从插件自身的配置字典或对象中提取特定配置项。

- **函数签名**: `get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any`
- **参数说明**:
    - `plugin_config`: 插件的配置字典。
    - `key`: 字符串类型。支持嵌套访问，例如 `"database.host"`。
    - `default`: 可选。若配置项不存在，则返回此默认值。
- **返回**: 配置项的值或默认值。

## 调用约定

1. **嵌套访问**: 开发者应使用点号 `.` 作为层级分隔符来访问深层配置，API 内部会自动解析路径。
2. **异常处理**: 当指定的键不存在时，API 不会抛出异常，而是记录一条警告日志并返回 `default` 参数指定的值。
3. **只读性**: 插件应仅通过此 API 读取配置，不应尝试通过此接口修改全局状态。

## 变更影响分析

- **兼容性**: 该 API 封装了对 `global_config` 的直接访问，如果底层配置结构发生变化，只需在 API 层进行适配，而无需修改所有插件代码。
- **安全性**: 通过 `hasattr` 和 `isinstance` 检查，防止了因非法键名导致的程序崩溃。

## 证据

- **源码位置**: `src/plugin_system/apis/config_api.py`
- **关键定义**: `def get_global_config(key: str, default: Any = None) -> Any:`
- **关键定义**: `def get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any:`