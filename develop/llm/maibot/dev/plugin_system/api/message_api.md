---
title: 消息 API (Message API)
last_updated: 2026-01-19
---

## 概述
`message_api.py` 模块为插件系统提供了标准化的消息处理接口。它封装了对底层数据库消息记录的查询、统计以及格式化操作，支持按时间戳、聊天会话 ID 和用户 ID 进行多维度筛选。该模块旨在简化插件开发者获取历史上下文和处理消息文本的流程。

## API 列表

### 1. 消息查询接口
- `get_messages_by_time(start_time, end_time, limit, limit_mode, filter_mai)`: 获取指定时间段内的全局消息。
- `get_messages_by_time_in_chat(chat_id, start_time, end_time, ...)`: 获取特定会话在指定时间段内的消息，支持过滤命令和机器人消息。
- `get_recent_messages(chat_id, hours, limit, ...)`: 获取指定会话最近 N 小时内的消息记录。
- `get_messages_before_time_in_chat(chat_id, timestamp, limit, ...)`: 获取指定会话在某一时间点之前的历史消息。

### 2. 消息统计接口
- `count_new_messages(chat_id, start_time, end_time)`: 统计指定会话在特定时间段内产生的新消息总数。
- `count_new_messages_for_users(chat_id, start_time, end_time, person_ids)`: 统计特定用户在会话中产生的新消息数。

### 3. 格式化与过滤接口
- `build_readable_messages_to_str(messages, ...)`: 将消息对象列表转换为人类可读的字符串，支持时间戳模式切换和长消息截断。
- `filter_mai_messages(messages)`: 移除消息列表中的机器人自身消息。
- `get_person_ids_from_messages(messages)`: (Async) 从消息列表中提取不重复的用户 ID 列表。

## 调用约定
- **参数类型**: 时间戳参数必须为 `int` 或 `float` 类型；`chat_id` 必须为非空字符串。
- **排序模式**: `limit_mode` 参数接受 `'latest'` (默认，获取最近记录) 或 `'earliest'` (获取最早记录)。
- **异步处理**: 涉及详细信息构建或用户 ID 提取的函数（如 `build_readable_messages_with_details`）为异步函数，调用时需使用 `await`。

## 变更影响分析
- **数据模型**: 该 API 依赖 `DatabaseMessages` 数据模型，若数据库表结构变更，需同步更新 `src/common/data_models/database_data_model.py`。
- **工具类依赖**: 核心查询逻辑封装在 `src.chat.utils.chat_message_builder` 中，API 层主要负责参数校验与业务逻辑封装。
- **机器人判定**: 过滤逻辑通过 `is_bot_self` 实现，确保了跨平台（如 WebUI 与聊天平台）判定的一致性。

## 证据
- 源码文件 `src/plugin_system/apis/message_api.py` 定义了完整的消息处理函数集。
- 函数 `get_messages_by_time_in_chat` 证明了系统支持基于 `chat_id` 和时间戳的复合查询。
- 函数 `build_readable_messages_to_str` 证明了系统提供了将数据库模型转换为可读文本的标准化路径。