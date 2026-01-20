---
last_updated: 2026-01-19
---

# 配置 API

## 概述
`config_api` 模块为插件提供了标准化的配置读取接口。它允许插件安全地访问全局配置 (`global_config`) 以及插件自身的私有配置字典，支持通过命名空间路径（点号分隔）进行深层属性访问。

## API 列表

### get_global_config
- **描述**: 从全局配置中安全地获取一个值。建议插件使用此方法读取全局配置以确保隔离性。
- **函数签名**: `get_global_config(key: str, default: Any = None) -> Any`
- **参数说明**: 
  - `key`: 字符串类型，支持点号分隔的嵌套路径（如 `section.subsection.key`），大小写敏感。
  - `default`: 可选，当配置项不存在时返回的默认值。
- **返回值**: 配置值或默认值。

### get_plugin_config
- **描述**: 从指定的插件配置字典中获取值。
- **函数签名**: `get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any`
- **参数说明**: 
  - `plugin_config`: 插件自带的配置字典。
  - `key`: 字符串类型，支持点号分隔的嵌套路径。
  - `default`: 可选，配置不存在时的回退值。
- **返回值**: 配置值或默认值。

## 调用约定
1. **路径访问**: 使用 `.` 作为分隔符访问嵌套配置。
2. **安全性**: 函数内部捕获了异常并会通过 `logger.warning` 记录失败信息，不会直接抛出异常导致插件崩溃。
3. **只读性**: 此 API 仅供读取配置，不提供修改配置的功能。

## 变更影响分析
- **扩展性**: 嵌套键值的支持使得配置结构可以灵活调整而无需更改代码逻辑。
- **稳定性**: 统一的异常处理机制增强了系统的健壮性。

## 证据
- 源码位置: `src/plugin_system/apis/config_api.py`
- 函数定义: `def get_global_config(key: str, default: Any = None) -> Any:`
- 函数定义: `def get_plugin_config(plugin_config: dict, key: str, default: Any = None) -> Any:`
