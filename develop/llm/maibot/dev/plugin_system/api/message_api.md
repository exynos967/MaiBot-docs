---
title: 消息 API (Message API)
last_updated: 2026-01-19
---

## 概述

`message_api` 模块为插件系统提供标准化的消息查询、计数及格式化功能。该模块封装了底层数据库操作，允许插件开发者以统一的接口获取历史消息、统计新消息数量，并将原始消息数据转换为可读的文本格式。

## API 列表

### 消息查询

- **get_messages_by_time_in_chat**
  - **说明**: 获取指定聊天中指定时间范围内的消息。
  - **签名**: `get_messages_by_time_in_chat(chat_id: str, start_time: float, end_time: float, limit: int = 0, limit_mode: str = "latest", filter_mai: bool = False, filter_command: bool = False, filter_intercept_message_level: Optional[int] = None) -> List[DatabaseMessages]`

- **get_recent_messages**
  - **说明**: 获取指定聊天中最近一段时间（默认 24 小时）的消息。
  - **签名**: `get_recent_messages(chat_id: str, hours: float = 24.0, limit: int = 100, limit_mode: str = "latest", filter_mai: bool = False) -> List[DatabaseMessages]`

- **get_messages_before_time_in_chat**
  - **说明**: 获取指定聊天中指定时间戳之前的消息。
  - **签名**: `get_messages_before_time_in_chat(chat_id: str, timestamp: float, limit: int = 0, filter_mai: bool = False, filter_intercept_message_level: Optional[int] = None) -> List[DatabaseMessages]`

### 消息计数

- **count_new_messages**
  - **说明**: 计算指定聊天中从开始时间到结束时间的新消息数量。
  - **签名**: `count_new_messages(chat_id: str, start_time: float = 0.0, end_time: Optional[float] = None) -> int`

### 消息格式化与处理

- **build_readable_messages_to_str**
  - **说明**: 将消息列表构建成可读的字符串。
  - **签名**: `build_readable_messages_to_str(messages: List[DatabaseMessages], replace_bot_name: bool = True, timestamp_mode: str = "relative", read_mark: float = 0.0, truncate: bool = False, show_actions: bool = False) -> str`

- **filter_mai_messages**
  - **说明**: 从消息列表中移除机器人自身的消息。
  - **签名**: `filter_mai_messages(messages: List[DatabaseMessages]) -> List[DatabaseMessages]`

## 调用约定

1. **时间戳**: 所有时间参数（如 `start_time`, `end_time`, `timestamp`）均应使用 Unix 时间戳（`float` 或 `int`）。
2. **标识符**: `chat_id` 必须为非空字符串，否则会抛出 `ValueError`。
3. **数量限制**: `limit` 参数设为 `0` 时表示不限制返回数量。当 `limit > 0` 时，`limit_mode` 可选 `'earliest'`（最早）或 `'latest'`（最新）。
4. **异步支持**: 部分格式化函数（如 `build_readable_messages_with_details`）为异步函数，需使用 `await` 调用。

## 变更影响分析

- **数据模型依赖**: 该 API 强依赖于 `src.common.data_models.database_data_model.DatabaseMessages`。如果数据库消息模型发生变更，此 API 的返回结构将受到直接影响。
- **底层工具依赖**: 模块内部大量调用了 `src.chat.utils.chat_message_builder` 中的底层函数。底层工具的逻辑变更（如消息过滤规则）会透传至此 API。
- **机器人识别**: `filter_mai_messages` 依赖 `is_bot_self` 函数，该函数支持多平台（包括 WebUI）的机器人身份识别。

## 证据

- **证据 1**: 源码文件 `src/plugin_system/apis/message_api.py` 定义了核心查询接口 `get_messages_by_time_in_chat` (第 54 行)。
- **证据 2**: 源码文件 `src/plugin_system/apis/message_api.py` 提供了消息格式化工具 `build_readable_messages_to_str` (第 348 行)，并明确了其参数如 `replace_bot_name` 和 `timestamp_mode`。