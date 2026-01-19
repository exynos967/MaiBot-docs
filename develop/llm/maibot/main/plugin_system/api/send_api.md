---
last_updated: 2026-01-19
---

## 概述
`send_api` 模块位于 `src/plugin_system/apis/send_api.py`，是插件系统发送消息的核心接口。它封装了底层消息发送逻辑，支持异步发送文本、图片、表情、指令以及自定义类型的消息到指定的聊天流（stream_id）。

## API 列表
- **text_to_stream**: 异步发送文本消息。支持打字态模拟（typing）和引用回复（set_reply）。
- **emoji_to_stream**: 发送 Base64 编码的表情包。
- **image_to_stream**: 发送 Base64 编码的图片消息。
- **command_to_stream**: 向指定流发送特定指令（command）。
- **custom_to_stream**: 通用接口，支持发送 video、file 等自定义 `message_type`。
- **custom_reply_set_to_stream**: 发送包含多个回复内容的混合消息集（ReplySetModel）。

## 调用约定
1. **标识符映射**: 开发者需持有 `stream_id`。系统通过 `get_chat_manager().get_stream(stream_id)` 获取目标流对象。
2. **异步语义**: 所有 API 均为 `async` 函数，必须使用 `await` 关键字调用。
3. **数据模型**: 引用回复功能依赖 `DatabaseMessages` 对象，由 `db_message_to_message_recv` 转换为内部消息格式。

## 变更影响分析
- **统一入口**: 所有公共 API 最终均调用内部函数 `_send_to_target`，这确保了日志记录（show_log）、数据库存储（storage_message）和消息分发逻辑的高度一致性。
- **扩展性**: `Seg` 结构和 `UniversalMessageSender` 的使用使得增加新消息类型（如混合消息 `seglist`）对上层 API 影响较小。

## 证据
- `src/plugin_system/apis/send_api.py`: 该文件定义了所有导出接口。
- `async def _send_to_target(...)`: 位于源码第 48 行，是所有发送功能的统一实现核心。