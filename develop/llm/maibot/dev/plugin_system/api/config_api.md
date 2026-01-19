---
last_updated: 2026-01-19
---

# 配置 API 文档

## 概述
`config_api` 模块为插件系统提供了统一的配置读取接口。它支持从全局配置或插件私有配置中安全地获取值，并支持通过命名空间（点分隔符）进行嵌套访问，确保了配置访问的隔离性与只读安全性。

## API 列表

### 1. get_global_config
**功能**：从全局配置中安全地获取一个值。
- **签名**: `get_global_config(key: str, default: Any = None) -> Any`
- **参数**:
    - `key`: 命名空间式配置键名，支持嵌套访问（如 `"section.key"`），大小写敏感。
    - `default`: 可选。如果配置项不存在，则返回此默认值。
- **返回**: 配置值或指定的默认值。

### 2. get_plugin_config
**功能**：从插件特定的配置字典中获取值。
- **签名**: `get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any`
- **参数**:
    - `plugin_config`: 插件自身的配置字典。
    - `key`: 配置键名，支持嵌套访问（如 `"database.host"`），大小写敏感。
    - `default`: 可选。如果配置项不存在，则返回此默认值。
- **返回**: 配置值或指定的默认值。

## 调用约定
1. **嵌套访问**：所有 `key` 参数均支持使用 `.` 作为分隔符来访问深层嵌套的配置项。
2. **异常处理**：函数内部已封装 `try-except` 块。若键名不存在，系统会记录警告日志并返回 `default` 值，不会直接抛出异常中断插件运行。
3. **只读性**：插件应仅通过此 API 读取配置，不应尝试通过此接口修改全局配置对象。

## 变更影响分析
- **配置结构依赖**：由于 API 依赖于 `src.config.config.global_config` 的结构，若全局配置的属性名发生变更，使用 `get_global_config` 的插件需同步更新 `key` 字符串。
- **日志监控**：配置获取失败时会触发 `config_api` 标签的警告日志，便于运维排查插件配置缺失问题。

## 证据
- **源码位置**: `src/plugin_system/apis/config_api.py` 定义了核心逻辑。
- **函数定义**: 源码中明确定义了 `def get_global_config(key: str, default: Any = None) -> Any:` 以及 `def get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any:`。