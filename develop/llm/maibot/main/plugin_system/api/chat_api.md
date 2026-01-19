---
last_updated: 2026-01-19
---

# Chat API 文档

## 概述

`chat_api.py` 模块专门负责插件系统中聊天信息的查询与管理。该模块采用了标准 Python 包设计模式，提供了 `ChatManager` 类以及一系列模块级别的便捷函数，用于获取、筛选和统计跨平台的聊天流（ChatStream）。

## API 列表

### 1. 获取聊天流列表
- `get_all_streams(platform="qq") -> List[ChatStream]`
  获取所有聊天流。参数 `platform` 支持字符串或 `SpecialTypes.ALL_PLATFORMS`。
- `get_group_streams(platform="qq") -> List[ChatStream]`
  仅获取群聊类型的聊天流。
- `get_private_streams(platform="qq") -> List[ChatStream]`
  仅获取私聊类型的聊天流。

### 2. 精确查找聊天流
- `get_group_stream_by_group_id(group_id, platform="qq") -> Optional[ChatStream]`
  根据群 ID 查找对应的群聊流。
- `get_private_stream_by_user_id(user_id, platform="qq") -> Optional[ChatStream]`
  根据用户 ID 查找对应的私聊流。

### 3. 信息获取与统计
- `get_stream_type(chat_stream: ChatStream) -> str`
  返回聊天流类型，结果为 "group"、"private" 或 "unknown"。
- `get_stream_info(chat_stream: ChatStream) -> Dict[str, Any]`
  获取详细信息字典，包含 `stream_id`、`platform`、`type` 及 ID/名称等信息。
- `get_streams_summary() -> Dict[str, int]`
  返回系统内聊天流的统计摘要（总数、群聊数、私聊数、QQ 流数）。

## 调用约定

1. **导入方式**：
   - 推荐导入模块：`from src.plugin_system.apis import chat_api`
   - 或导入管理器类：`from src.plugin_system.apis.chat_api import ChatManager as chat`
2. **平台参数**：默认平台通常为 `"qq"`。若需获取所有平台的流，请使用 `SpecialTypes.ALL_PLATFORMS`。
3. **异常处理**：API 内部会检查参数类型，若 `group_id` 或 `user_id` 类型不匹配将抛出 `TypeError`；若 ID 为空则可能抛出 `ValueError`。

## 变更影响分析

- **类型安全**：API 强制要求 `ChatStream` 实例及字符串 ID 的类型校验，修改底层 `ChatStream` 结构可能导致 `get_stream_info` 返回的字段发生变化。
- **平台扩展**：新增聊天平台时，需在调用处显式指定 `platform` 字符串或确保其逻辑能被 `ALL_PLATFORMS` 覆盖。

## 证据

- **源码位置**：`src/plugin_system/apis/chat_api.py` 包含了 `ChatManager` 类的完整定义。
- **关键签名**：`def get_all_streams(platform: Optional[str] | SpecialTypes = "qq") -> List[ChatStream]` 证明了默认参数与类型约束。