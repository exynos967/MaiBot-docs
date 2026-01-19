---
title: 回复生成器 API (Generator API)
last_updated: 2026-01-19
---

## 概述

`generator_api.py` 模块是插件系统与核心回复逻辑之间的桥梁。它提供了一组标准化的函数，用于获取回复器实例、生成基于上下文的回复、重写现有回复以及对文本进行拟人化处理（如自动分割和模拟错别字）。该模块封装了 `ReplyerManager` 和具体的 `Replyer` 实现，简化了插件调用 LLM 生成内容的流程。

## API 列表

### 1. get_replyer
获取回复器对象。优先通过 `chat_stream` 获取，若无则通过 `chat_id` 查找。
- **签名**: `def get_replyer(chat_stream: Optional[ChatStream] = None, chat_id: Optional[str] = None, request_type: str = "replyer") -> Optional[DefaultReplyer | PrivateReplyer]`
- **返回**: 回复器实例或 `None`。

### 2. generate_reply
异步生成回复。这是最核心的 API，支持动作数据解析、工具调用开关和拟人化配置。
- **签名**: `async def generate_reply(chat_stream, chat_id, action_data, ..., enable_tool=False, enable_splitter=True, ...)`
- **返回**: `Tuple[bool, Optional["LLMGenerationDataModel"]]`。包含成功标志和 LLM 生成的数据模型。

### 3. rewrite_reply
异步重写回复。用于对已有的原始回复进行润色或调整语气。
- **签名**: `async def rewrite_reply(chat_stream, reply_data, chat_id, raw_reply, ...)`
- **返回**: `Tuple[bool, Optional["LLMGenerationDataModel"]]`。

### 4. process_human_text
将纯文本处理为 `ReplySetModel`，应用消息分割和错字生成逻辑。
- **签名**: `def process_human_text(content: str, enable_splitter: bool, enable_chinese_typo: bool) -> Optional[ReplySetModel]`

### 5. generate_response_custom
根据自定义 Prompt 生成原始字符串响应。
- **签名**: `async def generate_response_custom(chat_stream, chat_id, request_type, prompt) -> Optional[str]`

## 调用约定

1. **参数优先级**: 在调用 `get_replyer` 或 `generate_reply` 时，应优先提供 `chat_stream` 对象。如果 `chat_stream` 和 `chat_id` 均为空，将抛出 `ValueError`。
2. **异步处理**: `generate_reply`、`rewrite_reply` 和 `generate_response_custom` 均为异步函数，必须使用 `await` 调用。
3. **数据模型**: `generate_reply` 返回的 `LLMGenerationDataModel` 包含了原始输出 (`content`)、处理后的输出 (`processed_output`) 以及封装好的 `reply_set`。

## 变更影响分析

- **日志记录**: 该 API 内部集成了 `PlanReplyLogger.log_reply`，所有通过此接口生成的回复都会被自动记录到回复日志中。
- **异常处理**: 模块内部捕获了 `UserWarning` 以支持生成中断，并捕获了通用 `Exception` 以防止插件崩溃，但在 `chat_id` 缺失时会主动抛出 `ValueError`。
- **拟人化处理**: 默认启用 `enable_splitter` 和 `enable_chinese_typo`，这会影响最终输出的消息条数和文本正确性。

## 证据

- **证据 1 (函数定义)**: `src/plugin_system/apis/generator_api.py` 中定义了 `get_replyer` 函数：
  ```python
  def get_replyer(
      chat_stream: Optional[ChatStream] = None,
      chat_id: Optional[str] = None,
      request_type: str = "replyer",
  ) -> Optional[DefaultReplyer | PrivateReplyer]:
  ```
- **证据 2 (核心逻辑)**: `src/plugin_system/apis/generator_api.py` 中的 `generate_reply` 异步函数实现了回复生成与日志记录：
  ```python
  async def generate_reply(
      # ... 参数列表 ...
  ) -> Tuple[bool, Optional["LLMGenerationDataModel"]]:
      # ... 获取 replyer 并调用 generate_reply_with_context ...
      success, llm_response = await replyer.generate_reply_with_context(...)
  ```