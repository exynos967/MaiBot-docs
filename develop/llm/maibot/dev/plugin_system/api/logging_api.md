---
title: Logging API
last_updated: 2026-01-19
---

## 概述
Logging API 是插件系统提供的标准日志接口模块。它通过封装并导出核心日志工具，为插件提供统一的日志记录能力，确保插件日志与系统主日志格式保持一致。

## API 列表

### get_logger
- **功能描述**: 获取系统预设的日志记录器实例。
- **导出方式**: 通过 `__all__` 显式导出。
- **原始定义**: 引用自 `src.common.logger`。

## 调用约定
插件应通过 `src.plugin_system.apis.logging_api` 导入该函数。由于该模块使用了 `__all__` 限制，建议直接导入所需符号。

```python
from src.plugin_system.apis.logging_api import get_logger

logger = get_logger()
logger.info("Plugin initialized")
```

## 变更影响分析
- **接口稳定性**: 该 API 属于导出型接口，其稳定性取决于 `src.common.logger` 的实现。
- **兼容性**: 任何对 `get_logger` 返回值类型或参数签名的修改都会直接影响所有调用此 API 的插件。

## 证据
1. 源码文件位置：`src/plugin_system/apis/logging_api.py`。
2. 导出声明：代码中明确定义了 `__all__ = ["get_logger"]`，限定了对外暴露的接口。