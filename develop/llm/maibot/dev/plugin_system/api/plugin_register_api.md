---
title: 插件注册 API
last_updated: 2026-01-19
---

## 概述

`plugin_register_api.py` 模块提供了插件系统的核心注册机制。通过 `register_plugin` 装饰器，开发者可以将自定义的插件类注册到全局的 `plugin_manager` 中。该 API 负责验证插件类的合法性、检查命名规范，并自动解析插件的物理路径以便后续加载。

## API 列表

### `register_plugin(cls)`

这是一个类装饰器，用于注册插件类。

- **参数**:
    - `cls`: 待注册的插件类。必须是 `BasePlugin` 的子类。
- **返回**:
    - 返回原始类 `cls`（无论注册是否成功）。
- **异常**:
    - `ValueError`: 当 `plugin_name` 包含非法字符 `.` 时抛出。

## 调用约定

1. **继承要求**: 被装饰的类必须继承自 `src.plugin_system.base.base_plugin.BasePlugin`。
2. **属性要求**: 插件类必须定义 `plugin_name` 属性。
3. **命名限制**: `plugin_name` 字符串中严禁包含点号 `.`，建议使用下划线 `_`。
4. **环境要求**: 项目根目录下必须存在 `pyproject.toml` 文件，否则 API 无法正确解析插件的绝对路径。

## 变更影响分析

- **注册时机**: 该 API 仅负责注册类定义和路径，不会立即实例化插件。实例化由插件管理器在后续生命周期中负责。
- **路径解析**: 路径解析依赖于 `__module__` 属性和 `pyproject.toml` 的位置。如果项目结构发生重大变化（如移动了根目录标识文件），将导致插件路径解析失败。
- **错误处理**: 如果类不是 `BasePlugin` 的子类，API 会记录错误日志并跳过注册逻辑，但不会中断程序运行。

## 证据

### 证据 1: 装饰器定义与类型检查
在 `src/plugin_system/apis/plugin_register_api.py` 中：
```python
def register_plugin(cls):
    from src.plugin_system.core.plugin_manager import plugin_manager
    from src.plugin_system.base.base_plugin import BasePlugin
    # ...
    if not issubclass(cls, BasePlugin):
        logger.error(f"类 {cls.__name__} 不是 BasePlugin 的子类")
        return cls
```

### 证据 2: 命名校验与注册逻辑
在 `src/plugin_system/apis/plugin_register_api.py` 中：
```python
    plugin_name: str = cls.plugin_name  # type: ignore
    if "." in plugin_name:
        logger.error(f"插件名称 '{plugin_name}' 包含非法字符 '.'，请使用下划线替代")
        raise ValueError(f"插件名称 '{plugin_name}' 包含非法字符 '.'，请使用下划线替代")
    # ...
    plugin_manager.plugin_classes[plugin_name] = cls
    plugin_manager.plugin_paths[plugin_name] = str(Path(root_path, *splitted_name).resolve())
```