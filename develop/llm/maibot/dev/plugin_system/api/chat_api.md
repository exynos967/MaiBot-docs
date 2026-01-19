---
title: 聊天管理 API (Chat API)
last_updated: 2026-01-19
---

## 概述
聊天 API 模块 (`src/plugin_system/apis/chat_api.py`) 专门用于查询和管理 MaiBot 系统中的聊天流（ChatStream）。它提供了对群聊、私聊流的过滤、检索以及统计功能，是插件系统与底层消息流交互的核心接口。该模块支持多平台筛选，默认主要面向 QQ 平台。

## API 列表
### 1. 聊天流查询
- `get_all_streams(platform)`: 获取指定平台的所有活跃聊天流。
- `get_group_streams(platform)`: 仅获取群聊类型的聊天流。
- `get_private_streams(platform)`: 仅获取私聊类型的聊天流。
- `get_group_stream_by_group_id(group_id, platform)`: 根据群 ID 精确查找聊天流对象。
- `get_private_stream_by_user_id(user_id, platform)`: 根据用户 ID 精确查找私聊流。

### 2. 流属性与元数据
- `get_stream_type(chat_stream)`: 识别流类型，返回 "group"、"private" 或 "unknown"。
- `get_stream_info(chat_stream)`: 提取流的详细信息字典，包含 stream_id、平台、群组名、用户昵称等。

### 3. 统计功能
- `get_streams_summary()`: 返回全局聊天流统计摘要，包括总流数、各类型流总数以及 QQ 平台占比。

## 调用约定
- **导入模式**: 开发者可使用 `from src.plugin_system.apis import chat_api` 调用模块级便捷函数，或通过 `from src.plugin_system.apis.chat_api import ChatManager` 调用静态方法。
- **平台筛选**: 参数 `platform` 默认值为 `"qq"`。若需获取所有平台的流，应传入 `SpecialTypes.ALL_PLATFORMS`。
- **错误处理**: 方法内部对 `group_id` 或 `user_id` 进行非空与类型检查，不符合要求时抛出 `TypeError` 或 `ValueError`。若底层管理器获取失败，将返回空结果并记录 Error 日志。

## 变更影响分析
- **核心耦合**: 依赖 `src.chat.message_receive.chat_stream` 中的 `get_chat_manager` 和 `ChatStream` 类。若核心聊天流逻辑重构，此 API 层需更新。
- **跨平台扩展**: 目前逻辑硬编码了对 `platform == "qq"` 的默认支持，新增平台时需确保 `stream.platform` 字段与查询参数一致。
- **性能注意**: `get_all_streams` 类方法通过遍历 `get_chat_manager().streams` 实现，在大规模并发会话场景下可能存在遍历开销。

## 证据
- 源码定义: `src/plugin_system/apis/chat_api.py` 中定义了 `class ChatManager:` 以及与之对应的模块级便捷函数。
- 接口签名: `get_all_streams(platform: Optional[str] | SpecialTypes = "qq") -> List[ChatStream]` 明确了平台过滤逻辑。