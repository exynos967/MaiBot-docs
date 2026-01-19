---
last_updated: 2026-01-19
---

# Generator API

## 概述
`generator_api.py` 是 MaiBot 插件系统的核心回复生成接口模块。它封装了底层回复器（Replyer）的复杂逻辑，为插件开发者提供了一套标准化的异步接口，用于生成、重写以及拟人化处理机器人回复。该 API 支持上下文感知、工具调用（Tool Use）、消息分割以及错字生成等特性。

## API 列表

### 1. get_replyer
- **功能**: 获取回复器实例。
- **签名**: `def get_replyer(chat_stream: Optional[ChatStream] = None, chat_id: Optional[str] = None, request_type: str = "replyer") -> Optional[DefaultReplyer | PrivateReplyer]`
- **说明**: 内部通过 `replyer_manager` 管理实例。必须提供 `chat_stream` 或 `chat_id`。

### 2. generate_reply
- **功能**: 生成完整的机器人回复。
- **签名**: `async def generate_reply(chat_stream, chat_id, action_data, ...)`
- **返回**: `Tuple[bool, Optional["LLMGenerationDataModel"]]`。返回包含执行状态和 LLM 生成数据的元组。
- **特性**: 支持 `enable_tool`（工具调用）、`enable_splitter`（消息分割）和 `enable_chinese_typo`（错字模拟）。

### 3. rewrite_reply
- **功能**: 对已有回复内容进行重写。
- **签名**: `async def rewrite_reply(chat_stream, reply_data, chat_id, raw_reply, reason, ...)`
- **说明**: 用于根据特定原因（reason）或回复对象（reply_to）调整回复语气。

### 4. process_human_text
- **功能**: 拟人化文本处理。
- **签名**: `def process_human_text(content: str, enable_splitter: bool, enable_chinese_typo: bool) -> Optional[ReplySetModel]`
- **说明**: 将单一字符串转换为符合拟人化配置的 `ReplySetModel` 对象。

## 调用约定
1. **异步性**: 主要生成接口（`generate_reply`, `rewrite_reply`）均为 `async` 函数，调用时需使用 `await`。
2. **参数优先级**: 在同时提供 `chat_stream` 和 `chat_id` 时，API 优先使用 `chat_stream` 获取上下文。
3. **错误处理**: 接口内部封装了异常捕获，若生成失败通常返回 `False` 或 `None`，并记录错误日志。

## 变更影响分析
- **数据模型依赖**: 该 API 强依赖于 `LLMGenerationDataModel` 和 `ReplySetModel`。若这些数据模型的结构发生变化，插件层解析返回值的逻辑需同步更新。
- **回复器扩展**: 新增回复器类型（如特定平台的 Generator）需在 `replyer_manager` 中注册，方可被 `get_replyer` 正确识别。

## 证据
- 源码位置: `src/plugin_system/apis/generator_api.py`
- 关键定义: `async def generate_reply(` 见源码中关于回复生成 API 函数的定义。
- 关键定义: `def get_replyer(` 见源码中关于回复器获取 API 函数的定义。