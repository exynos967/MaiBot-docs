---
title: 聊天 API (Chat API)
last_updated: 2026-01-19
---

## 概述

`chat_api` 模块是插件系统提供的专门负责聊天信息查询与管理的接口。它封装了对底层 `ChatStream`（聊天流）的操作，支持开发者获取群聊、私聊流信息，并进行平台筛选或统计。该模块采用标准 Python 包设计模式，提供类方法与便捷函数两种调用方式。

## API 列表

### 1. 流获取接口
- **get_all_streams(platform)**: 获取所有聊天流。支持通过 `platform` 字符串或 `SpecialTypes.ALL_PLATFORMS` 筛选。
- **get_group_streams(platform)**: 仅获取群聊类型的聊天流。
- **get_private_streams(platform)**: 仅获取私聊类型的聊天流。
- **get_group_stream_by_group_id(group_id, platform)**: 根据群组 ID 精确获取聊天流。
- **get_private_stream_by_user_id(user_id, platform)**: 根据用户 ID 精确获取私聊流。

### 2. 流属性与信息接口
- **get_stream_type(chat_stream)**: 返回聊天流类型，取值为 `"group"`、`"private"` 或 `"unknown"`。
- **get_stream_info(chat_stream)**: 获取聊天流的详细信息字典，包含 `stream_id`、`platform`、`type` 以及关联的群组或用户信息。

### 3. 统计接口
- **get_streams_summary()**: 返回当前系统中各类聊天流的数量统计摘要。

## 调用约定

### 导入方式
开发者可以通过以下两种方式引入 API：
```python
# 方式一：直接导入模块
from src.plugin_system.apis import chat_api

# 方式二：导入管理器类并重命名
from src.plugin_system.apis.chat_api import ChatManager as chat
```

### 参数约束
- **platform**: 默认为 `"qq"`。若需跨平台获取，必须传入 `SpecialTypes.ALL_PLATFORMS`。
- **类型检查**: API 内部会对 `platform`、`group_id`、`user_id` 进行严格的类型校验（`isinstance`），若类型不符将抛出 `TypeError`。
- **空值处理**: `group_id` 和 `user_id` 不能为空字符串，否则抛出 `ValueError`。

## 变更影响分析

- **依赖关系**: 该 API 强依赖于 `src.chat.message_receive.chat_stream` 模块中的 `ChatStream` 类和 `get_chat_manager` 函数。如果底层聊天管理器的 `streams` 结构发生变化，此 API 将直接受影响。
- **扩展性**: `SpecialTypes` 枚举为未来增加更多筛选逻辑（如特定平台组）预留了空间。
- **异常处理**: API 内部封装了 `try-except` 块并记录日志，查询失败时通常返回空列表或 `None`，不会导致插件进程直接崩溃。

## 证据

### 证据 1：核心管理器类定义
源码位置：`src/plugin_system/apis/chat_api.py`
```python
class ChatManager:
    """聊天管理器 - 专门负责聊天信息的查询和管理"""

    @staticmethod
    def get_all_streams(platform: Optional[str] | SpecialTypes = "qq") -> List[ChatStream]:
        # ... 逻辑实现 ...
```

### 证据 2：平台筛选逻辑与枚举使用
源码位置：`src/plugin_system/apis/chat_api.py`
```python
if platform == SpecialTypes.ALL_PLATFORMS or stream.platform == platform:
    streams.append(stream)
```