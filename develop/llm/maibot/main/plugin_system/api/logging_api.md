---
last_updated: 2026-01-19
---

# Logging API

## 概述
`logging_api` 模块是插件系统的日志接口，通过从底层公共日志组件导出获取日志记录器的函数，为插件提供统一的日志输出能力。

## API 列表
- `get_logger`: 该函数导出自 `src.common.logger`，用于初始化或获取一个日志记录器实例。

## 调用约定
插件开发者可以通过该模块的导出列表进行引用：
```python
from src.plugin_system.apis.logging_api import get_logger
```

## 变更影响分析
该模块作为一个转发层，其稳定性高度依赖于 `src.common.logger` 模块。如果底层 `get_logger` 的签名发生变化，将直接影响插件系统的日志调用。

## 证据
- 源码中明确导入了底层组件：`from src.common.logger import get_logger`
- 源码通过 `__all__` 显式对外暴露接口：`__all__ = ["get_logger"]`
