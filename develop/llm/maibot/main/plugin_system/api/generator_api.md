---
last_updated: 2026-01-19
---

# 回复器 API (generator_api)

## 概述
`generator_api.py` 模块是插件系统中核心的回复生成接口。它封装了对不同类型回复器（群组/私聊）的获取、文本生成、回复重写以及拟人化处理逻辑。该模块采用标准 Python 包设计模式，旨在为插件开发者提供统一的 LLM 交互入口。

## API 列表

### 1. get_replyer
- **功能**: 获取回复器对象实例。
- **签名**: `def get_replyer(chat_stream, chat_id, request_type="replyer")`
- **返回值**: `Optional[DefaultReplyer | PrivateReplyer]`

### 2. generate_reply
- **功能**: 生成回复内容，包含 LLM 调用、消息分割、错字处理及日志记录。
- **签名**: `async def generate_reply(chat_stream, chat_id, action_data, ...)`
- **返回值**: `Tuple[bool, Optional[LLMGenerationDataModel]]`

### 3. rewrite_reply
- **功能**: 对已有回复内容进行重写。
- **签名**: `async def rewrite_reply(chat_stream, reply_data, chat_id, ...)`
- **返回值**: `Tuple[bool, Optional[LLMGenerationDataModel]]`

### 4. process_human_text
- **功能**: 将原始文本处理为更拟人化的格式（应用分割器和错字生成）。
- **签名**: `def process_human_text(content, enable_splitter, enable_chinese_typo)`
- **返回值**: `Optional[ReplySetModel]`

## 调用约定
1. **标识参数**: 调用 `get_replyer` 或 `generate_reply` 时，`chat_stream` 与 `chat_id` 至少需提供一个，否则会抛出 `ValueError`。
2. **异步执行**: 主要生成接口（`generate_reply`, `rewrite_reply`, `generate_response_custom`）均为异步函数，必须使用 `await` 调用。
3. **数据模型**: 返回的 `LLMGenerationDataModel` 包含生成的原始 `content`、处理后的 `processed_output` 以及 `reply_set`。

## 变更影响分析
- **集中化逻辑**: 所有通过插件触发的回复生成均依赖此模块。修改此处的 `process_llm_response` 或日志逻辑将直接影响所有回复插件的行为。
- **依赖管理**: 该 API 依赖 `replyer_manager` 进行实例管理，确保了回复器单例的高效复用。

## 证据
- 见 `src/plugin_system/apis/generator_api.py` 中的函数签名：`def get_replyer(chat_stream: Optional[ChatStream] = None, chat_id: Optional[str] = None, request_type: str = "replyer")`
- 见 `src/plugin_system/apis/generator_api.py` 模块文档说明：`success, reply_set, _ = await generator_api.generate_reply(chat_stream, action_data, reasoning)`
