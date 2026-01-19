---
title: 发送 API (Send API)
last_updated: 2026-01-19
---

## 概述
`send_api.py` 模块是插件系统的核心通信接口，专门负责向不同的聊天流（Chat Stream）发送多媒体消息。该模块封装了底层消息构建逻辑，支持文本、表情包、图片、指令以及复杂的混合消息集（ReplySet），并提供模拟打字状态和引用回复等高级功能。

## API 列表

### 基础发送接口
- **text_to_stream(text, stream_id, ...)**: 向指定流发送纯文本消息。支持设置 `typing`（模拟打字）和 `reply_message`（引用回复）。
- **emoji_to_stream(emoji_base64, stream_id, ...)**: 发送 Base64 编码的表情包消息。
- **image_to_stream(image_base64, stream_id, ...)**: 发送 Base64 编码的图片消息。
- **command_to_stream(command, stream_id, ...)**: 向流发送特定指令或结构化命令数据。

### 高级发送接口
- **custom_to_stream(...)**: 通用接口，支持自定义 `message_type`（如 video, file）和内容。
- **custom_reply_set_to_stream(reply_set, stream_id, ...)**: 发送混合型消息集。该接口会遍历 `ReplySetModel` 中的内容，并调用内部解析器将其转换为对应的消息段（Seg）。

## 调用约定
1. **异步支持**：所有公共 API 均为 `async` 函数，必须在异步上下文中通过 `await` 调用。
2. **标识符依赖**：推荐使用 `stream_id` 作为目标标识，系统会通过 `get_chat_manager().get_stream(stream_id)` 检索目标流。
3. **引用回复**：若需实现引用回复，需同时设置 `set_reply=True` 并传入有效的 `DatabaseMessages` 对象作为 `reply_message`。
4. **数据存储**：默认情况下 `storage_message=True`，发送的消息会自动持久化到数据库。

## 变更影响分析
- **核心逻辑耦合**：所有公共接口最终均调用私有函数 `_send_to_target`。对该私有函数的修改将直接影响所有发送行为。
- **类型扩展**：新增消息类型（如语音、转发消息）需同步更新 `_parse_content_to_seg` 解析逻辑，以确保 `ReplySetModel` 能正确转换。
- **依赖项**：该模块强依赖于 `UniversalMessageSender` 和 `maim_message` 协议库，底层协议变更可能导致发送失败。

## 证据
- **源码位置**：`src/plugin_system/apis/send_api.py` 定义了 `async def text_to_stream` 等公共函数。
- **内部实现**：`_send_to_target` 函数中使用了 `UniversalMessageSender().send_message` 来执行最终的投递动作。