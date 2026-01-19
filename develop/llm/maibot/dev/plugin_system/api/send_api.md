---
title: 发送 API (send_api)
last_updated: 2026-01-19
---

## 概述

`send_api` 模块是插件系统的核心组件之一，专门负责向不同的聊天流（Chat Stream）发送多种类型的消息。该 API 封装了底层消息构建与发送逻辑，支持文本、图片、表情包、命令以及复杂的混合消息集。其设计原则是简化插件开发者对消息下发的处理，支持通过 `stream_id` 进行精准投递。

## API 列表

所有 API 均为异步函数，返回 `bool` 值表示发送状态。

- **text_to_stream(text, stream_id, ...)**: 发送纯文本消息。支持模拟打字等待 (`typing`) 和引用回复 (`set_reply`)。
- **emoji_to_stream(emoji_base64, stream_id, ...)**: 发送表情包消息，内容需为 Base64 编码字符串。
- **image_to_stream(image_base64, stream_id, ...)**: 发送图片消息，内容需为 Base64 编码字符串。
- **command_to_stream(command, stream_id, ...)**: 向目标流发送特定指令（字符串或字典格式）。
- **custom_to_stream(message_type, content, stream_id, ...)**: 通用接口，支持发送视频、文件等自定义类型的消息。
- **custom_reply_set_to_stream(reply_set, stream_id, ...)**: 发送包含多个 `ReplyContent` 的 `ReplySetModel` 对象，支持混合类型消息和转发节点。

## 调用约定

1. **导入方式**: 推荐使用 `from src.plugin_system.apis import send_api`。
2. **定位参数**: 推荐使用 `stream_id` 作为目标标识，系统会自动查找对应的聊天流并关联平台信息。
3. **引用回复**: 若设置 `set_reply=True`，必须提供 `reply_message`（`DatabaseMessages` 类型对象）作为被引用的锚点。
4. **消息存储**: 默认 `storage_message=True`，会将发送的消息持久化到数据库中。

## 变更影响分析

- **数据模型依赖**: 依赖 `src.common.data_models` 下的 `DatabaseMessages`、`ReplySetModel` 和 `ReplyContent`。若这些模型发生破坏性变更，此 API 的转换逻辑需同步更新。
- **底层发送器**: 本模块依赖 `UniversalMessageSender` 实现最终下发。如果底层通信协议或发送逻辑重构，需确保 `_send_to_target` 内部生成的 `MessageSending` 对象符合新规范。
- **新增消息类型**: 若需支持新的消息媒介（如地理位置），需在 `_parse_content_to_seg` 函数中增加对应的转换分支。

## 证据

- **源码位置**: `src/plugin_system/apis/send_api.py` 包含了完整的消息转换与发送逻辑。
- **关键函数**: `async def _send_to_target` 是所有发送行为的统一入口，负责构建 `MessageSending` 对象并调用 `message_sender.send_message`。
- **数据处理**: `_parse_content_to_seg` 函数定义了如何将 `ReplyContentType` 枚举值映射为 `Seg` (Message Segment) 结构，涵盖了 `TEXT`、`IMAGE`、`EMOJI`、`FORWARD` 等类型。