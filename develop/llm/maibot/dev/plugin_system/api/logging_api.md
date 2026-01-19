---
title: Logging API
last_updated: 2026-01-19
---

## 概述
Logging API 是插件系统提供的标准日志接口，旨在为插件开发者提供统一的日志记录能力。该接口通过重新导出底层通用日志模块实现，确保插件日志格式与系统保持一致。

## API 列表
### get_logger
- **描述**: 获取一个日志记录器实例。
- **导出符号**: `get_logger`
- **来源**: `src.common.logger`

## 调用约定
插件应当通过 `src.plugin_system.apis.logging_api` 导入 `get_logger` 函数，而不是直接引用底层 `common` 模块，以确保符合插件系统的解耦规范。

## 变更影响分析
- 该文件作为 `src.common.logger` 的代理层。如果底层日志系统的初始化逻辑或接口发生变化，所有通过此 API 调用日志的插件将受到直接影响。
- `__all__` 显式声明了导出接口，确保了 API 的可见性边界，任何未在 `__all__` 中列出的符号将不被视为公共 API。

## 证据
- 源码文件路径: `src/plugin_system/apis/logging_api.py`
- 导出声明: `__all__ = ["get_logger"]`