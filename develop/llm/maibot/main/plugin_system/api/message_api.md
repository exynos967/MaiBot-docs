---
last_updated: 2026-01-19
---

# 消息 API (message_api.py)

## 概述
消息API模块 (`src.plugin_system.apis.message_api`) 为插件提供了一套标准化的接口，用于从数据库中检索历史消息、统计消息频率以及对消息内容进行可读化格式化。该模块封装了底层的数据库查询逻辑，并提供了多维度的过滤功能（如过滤机器人自身消息、过滤命令消息等）。

## API 列表
### 消息检索
- **get_messages_by_time**: `get_messages_by_time(start_time: float, end_time: float, limit: int = 0, limit_mode: str = "latest", filter_mai: bool = False) -> List[DatabaseMessages]`
- **get_messages_by_time_in_chat**: 获取指定聊天会话内的时间段消息。支持 `filter_command` 和 `filter_intercept_message_level` 参数。
- **get_recent_messages**: `get_recent_messages(chat_id: str, hours: float = 24.0, limit: int = 100, ...)` 获取指定聊天最近小时数内的消息。
- **get_messages_before_time**: 获取指定时间戳之前的历史记录。

### 统计与计算
- **count_new_messages**: `count_new_messages(chat_id: str, start_time: float = 0.0, end_time: Optional[float] = None) -> int`

### 格式化工具
- **build_readable_messages_to_str**: 将 `DatabaseMessages` 列表转换为格式化的可读字符串。支持 `replace_bot_name`、`timestamp_mode` 等显示设置。
- **filter_mai_messages**: 显式过滤掉由机器人（Mai）发送的消息。

## 调用约定
1. **导入方式**: 推荐使用 `from src.plugin_system.apis import message_api`。
2. **异常处理**: 当参数不合法（如 `chat_id` 为空、`limit` 为负数或时间戳非数字）时，API 将抛出 `ValueError`。
3. **数据模型**: 返回的消息对象类型为 `List[DatabaseMessages]`。

## 变更影响分析
- **兼容性**: 该 API 统一了多平台下的机器人身份判定逻辑（通过 `is_bot_self`），在跨平台插件开发中更具鲁棒性。
- **性能**: 查询接口支持 `limit` 和 `limit_mode`（latest/earliest），大规模数据查询时应合理设置限制以避免内存溢出。

## 证据
- 源码中定义了 `def get_messages_by_time_in_chat` 并包含详细的 `ValueError` 校验逻辑。
- 源码中提供了 `build_readable_messages_to_str` 函数，通过调用 `build_readable_messages` 实现消息到字符串的转换。
