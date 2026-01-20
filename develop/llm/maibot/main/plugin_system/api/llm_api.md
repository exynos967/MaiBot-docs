---
title: "LLM API 插件开发文档"
last_updated: 2026-01-19
---

## 概述
LLM API 模块 (`src/plugin_system/apis/llm_api.py`) 提供了插件系统与大语言模型（LLM）交互的标准化接口。该模块封装了底层的 LLMRequest 请求逻辑，支持模型发现、基础文本生成以及基于工具调用的复杂交互模式。

## API 列表

### 1. get_available_models
- **描述**: 获取系统当前所有可用的模型任务配置。
- **签名**: `def get_available_models() -> Dict[str, TaskConfig]`
- **返回值**: 以模型名称为键，`TaskConfig` 对象为值的字典。

### 2. generate_with_model
- **描述**: 异步生成内容的基本接口。
- **签名**: `async def generate_with_model(prompt: str, model_config: TaskConfig, request_type: str = "plugin.generate", temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Tuple[bool, str, str, str]`
- **返回值**: `(是否成功, 生成的内容, 推理内容, 模型名称)`。

### 3. generate_with_model_with_tools
- **描述**: 支持工具调用（Tool Call）的生成接口。
- **签名**: `async def generate_with_model_with_tools(prompt: str, model_config: TaskConfig, tool_options: List[Dict[str, Any]] | None = None, ...)`
- **返回值**: `(是否成功, 内容, 推理, 模型名, 工具调用列表)`。

### 4. generate_with_model_with_tools_by_message_factory
- **描述**: 使用消息工厂函数构建对话上下文的生成接口。
- **签名**: `async def generate_with_model_with_tools_by_message_factory(message_factory: Callable[[BaseClient], List[Message]], ...)`

## 调用约定
- **异步性**: 所有生成相关接口均为 `async` 函数，必须在异步上下文中被 `await` 调用。
- **错误处理**: 接口通过返回元组的第一个 `bool` 元素指示执行结果，而非仅抛出异常。若失败，第二个元素将包含错误信息。
- **配置传递**: 建议先调用 `get_available_models()` 获取有效的 `TaskConfig` 实例后再发起生成请求。

## 变更影响分析
- **类型依赖**: 本 API 强依赖于 `src.config.api_ada_configs.TaskConfig`。若配置类结构发生变化，需同步更新解析逻辑。
- **异步性能**: 大批量并发调用时应注意协程调度，避免阻塞主线程。

## 证据
- 模块路径：`src/plugin_system/apis/llm_api.py` 提供了核心 API 实现。
- 接口定义：源码中 `async def generate_with_model_with_tools` 明确支持 `tool_options` 参数，用于处理插件工具链请求。
