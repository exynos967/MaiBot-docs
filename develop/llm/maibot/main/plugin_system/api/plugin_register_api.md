---
title: 插件注册 API
last_updated: 2026-01-19
---

## 概述

该模块提供了 `register_plugin` 装饰器，用于将插件类注册到全局插件管理器中。它负责验证插件类的有效性（如继承关系和命名规范），并记录插件的类定义及物理文件路径，以便后续由插件管理器统一进行实例化。

## API 列表

### register_plugin(cls)

- **功能**: 插件注册装饰器。
- **参数**: 
  - `cls`: 需要注册的插件类。
- **返回**: 原始类 `cls`。
- **异常**: 
  - `ValueError`: 如果插件名称 `plugin_name` 包含非法字符 "."，则抛出此异常。

## 调用约定

1. **继承要求**: 被装饰的类必须是 `BasePlugin` 的子类。
2. **属性要求**: 类必须包含 `plugin_name` 属性。
3. **命名规范**: `plugin_name` 不能包含点号 (".")，建议使用下划线。
4. **路径识别**: 装饰器会自动通过 `pyproject.toml` 定位项目根目录，并计算插件相对于模块的路径。

## 变更影响分析

- **全局状态**: 该 API 会修改 `src.plugin_system.core.plugin_manager.plugin_manager` 中的 `plugin_classes` 和 `plugin_paths` 字典。
- **日志记录**: 会使用 `plugin_manager` 命名空间的 logger 记录注册成功或失败的日志。
- **项目结构依赖**: 注册逻辑高度依赖项目根目录下存在的 `pyproject.toml` 文件。

## 证据

- 在 `src/plugin_system/apis/plugin_register_api.py` 中定义了 `def register_plugin(cls):` 函数。
- 源码中明确检查了 `issubclass(cls, BasePlugin)` 以及 `plugin_name` 是否包含 "."。