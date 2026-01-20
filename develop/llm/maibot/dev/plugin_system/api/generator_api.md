---
last_updated: 2026-01-19
---

# 回复生成器 API (Generator API)

## 概述
Generator API 模块位于 `src/plugin_system/apis/generator_api.py`，是 MaiBot 插件系统中负责 LLM 回复生成的标准接口。该模块封装了底层的回复器管理逻辑，允许开发者通过简单的异步函数调用，在插件逻辑中触发高度定制化的回复生成流程，支持拟人化处理（错字、消息分割）以及复杂的上下文引用。

## API 列表

### 1. get_replyer
获取指定会话的回复器实例。
- **函数签名**: `get_replyer(chat_stream: Optional[ChatStream] = None, chat_id: Optional[str] = None, request_type: str = "replyer") -> Optional[DefaultReplyer | PrivateReplyer]`
- **功能**: 根据 `ChatStream` 或 `chat_id` 自动识别群组或私聊环境，并返回对应的回复器对象。使用 `replyer_manager` 进行单例维护。

### 2. generate_reply
核心异步接口，用于生成完整的 LLM 回复。
- **函数签名**: `async def generate_reply(...) -> Tuple[bool, Optional["LLMGenerationDataModel"]]`
- **关键参数**:
  - `chat_stream`: 当前聊天流对象。
  - `think_level`: 思考深度等级。
  - `enable_splitter`: 是否允许将长回复分割成多条消息。
  - `enable_chinese_typo`: 是否启用模拟真人错字的功能。
- **返回**: 一个包含成功标志和 `LLMGenerationDataModel` 的元组。该模型包含原始 Prompt、生成内容及其处理后的回复集合（`reply_set`）。

### 3. rewrite_reply
重写现有回复内容。
- **函数签名**: `async def rewrite_reply(raw_reply: str, reason: str, ...)`
- **功能**: 基于上下文对已有的 `raw_reply` 进行润色或逻辑调整。

### 4. generate_response_custom
发送原始 Prompt 并获取纯文本响应。
- **函数签名**: `async def generate_response_custom(prompt: str, ...)`
- **功能**: 绕过复杂的回复模板，直接与底层的 LLM 进行对话。

## 调用约定
1. **导入方式**: 推荐使用 `from src.plugin_system.apis import generator_api`。
2. **异步执行**: 除 `get_replyer` 和 `process_human_text` 外，其余生成类接口均为 `async`，必须使用 `await` 调用。
3. **日志记录**: 该 API 会自动调用 `PlanReplyLogger.log_reply` 进行系统审计，开发者无需手动记录 LLM 损耗。

## 变更影响分析
- **架构稳定性**: 该模块作为插件与核心 Chat 逻辑的隔离层，其接口签名变更将直接影响所有依赖自主生成回复的插件。
- **依赖项**: 紧密依赖 `src.chat.replyer` 下的 Generator 实现以及 `ReplyerManager`。
- **扩展性**: 通过 `extra_info` 参数，插件可以向 LLM 注入临时的上下文信息，而不改变原有的记忆逻辑。

## 证据
- **源码定义 1**: `src/plugin_system/apis/generator_api.py` 中定义了 `def get_replyer(chat_stream: Optional[ChatStream] = None, chat_id: Optional[str] = None, request_type: str = "replyer")`。
- **源码定义 2**: `src/plugin_system/apis/generator_api.py` 中核心逻辑位于 `async def generate_reply`，并在函数结束前调用了 `PlanReplyLogger.log_reply` 进行日志记录。
