---
title: Logging API
last_updated: 2026-01-19
---

## 概述

Logging API 是插件系统提供的标准日志记录接口。它通过封装底层日志模块，为插件开发者提供统一的日志获取方式，确保插件日志格式与系统整体保持一致。

## API 列表

### get_logger

- **功能描述**: 获取一个日志记录器（Logger）实例。
- **导出位置**: `src/plugin_system/apis/logging_api.py`
- **原始来源**: `src.common.logger.get_logger`

## 调用约定

1. **导入方式**: 开发者应从 `src.plugin_system.apis.logging_api` 导入所需函数。
2. **导出限制**: 该模块通过 `__all__` 显式导出了 `get_logger` 符号，建议仅使用已导出的接口。

## 变更影响分析

- **兼容性**: 当前 API 仅作为 `src.common.logger.get_logger` 的转发层。如果底层 `src.common.logger` 的签名发生变化，此 API 将直接受到影响。
- **扩展性**: 目前仅支持获取日志对象，未来可能在此层增加针对插件的日志过滤或格式化逻辑。

## 证据

- **源码文件**: `src/plugin_system/apis/logging_api.py` 中定义了 API 的导出逻辑。
- **导出声明**: 源码中明确包含 `__all__ = ["get_logger"]`，确立了该 API 的公开访问权限。