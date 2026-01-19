---
title: Chat API
last_updated: 2026-01-19
---

## 概述
`chat_api` 模块是插件系统提供的核心接口，专门负责聊天信息的查询和管理。它封装了对底层 `ChatStream` 的访问逻辑，允许插件开发者通过标准化的方式获取群聊或私聊的上下文信息、统计数据及流状态。

## API 列表

### ChatManager 静态方法
- **get_all_streams(platform)**: 获取指定平台的所有聊天流。支持通过 `SpecialTypes.ALL_PLATFORMS` 获取全平台数据。
- **get_group_streams(platform)**: 筛选并获取所有群聊流。
- **get_private_streams(platform)**: 筛选并获取所有私聊流。
- **get_group_stream_by_group_id(group_id, platform)**: 根据群组 ID 和平台标识符精确查找聊天流。
- **get_private_stream_by_user_id(user_id, platform)**: 根据用户 ID 和平台标识符精确查找私聊流。
- **get_stream_type(chat_stream)**: 识别流类型，返回 `"group"`、`"private"` 或 `"unknown"`。
- **get_stream_info(chat_stream)**: 提取流的详细元数据，包括 `stream_id`、`platform`、`group_id`、`user_id` 等。
- **get_streams_summary()**: 返回当前系统内各类聊天流的统计摘要字典。

### 模块级便捷函数
模块提供了与 `ChatManager` 静态方法同名的便捷函数（如 `get_all_streams`），支持直接调用。

## 调用约定
1. **导入方式**: 推荐使用 `from src.plugin_system.apis import chat_api`。
2. **平台参数**: `platform` 参数默认为 `"qq"`。若需跨平台操作，必须传入 `SpecialTypes.ALL_PLATFORMS`。
3. **异常处理**: API 内部实现了类型检查，若 `group_id` 或 `platform` 类型不符，会抛出 `TypeError`；若 ID 为空则抛出 `ValueError`。

## 变更影响分析
- **依赖关系**: 该 API 强依赖于 `src.chat.message_receive.chat_stream`。如果 `ChatStream` 对象的 `group_info` 或 `user_info` 结构发生变化，`get_stream_info` 和 `get_stream_type` 的逻辑需同步调整。
- **扩展性**: `SpecialTypes` 枚举为未来支持更多特殊筛选逻辑预留了空间。

## 证据
- 源码定义：`src/plugin_system/apis/chat_api.py` 中定义了 `class ChatManager:` 及其静态方法。
- 核心逻辑：`get_group_stream_by_group_id` 方法通过遍历 `get_chat_manager().streams.items()` 并校验 `stream.group_info` 来实现查找。