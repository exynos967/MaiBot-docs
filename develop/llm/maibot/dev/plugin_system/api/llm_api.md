---
last_updated: 2026-01-19
---

# LLM API 文档

## 概述
`llm_api` 模块是 MaiBot 插件系统提供的核心接口之一，旨在为插件开发者提供标准化的 LLM（大语言模型）交互能力。该模块封装了底层的模型请求逻辑，支持模型配置获取、基础文本生成、工具调用（Tool Call）以及基于消息工厂的复杂对话生成。

## API 列表

### 1. get_available_models
- **功能**: 获取系统中所有可用的模型任务配置。
- **签名**: `def get_available_models() -> Dict[str, TaskConfig]`
- **返回值**: 返回一个字典，Key 为模型配置名称，Value 为 `TaskConfig` 对象。

### 2. generate_with_model
- **功能**: 使用指定的模型配置进行异步文本生成。
- **签名**: `async def generate_with_model(prompt: str, model_config: TaskConfig, request_type: str = "plugin.generate", temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Tuple[bool, str, str, str]`
- **返回值**: `(是否成功, 生成内容, 推理过程, 模型名称)`。

### 3. generate_with_model_with_tools
- **功能**: 支持工具调用的模型生成接口。
- **签名**: `async def generate_with_model_with_tools(prompt: str, model_config: TaskConfig, tool_options: List[Dict[str, Any]] | None = None, ...) -> Tuple[bool, str, str, str, List[ToolCall] | None]`
- **返回值**: 相比基础生成，额外返回 `List[ToolCall]` 列表。

### 4. generate_with_model_with_tools_by_message_factory
- **功能**: 通过消息工厂函数构建上下文，支持更复杂的对话逻辑。
- **签名**: `async def generate_with_model_with_tools_by_message_factory(message_factory: Callable[[BaseClient], List[Message]], model_config: TaskConfig, ...) -> Tuple[bool, str, str, str, List[ToolCall] | None]`

## 调用约定
1. **异步调用**: 所有生成类接口均为 `async` 函数，必须使用 `await` 关键字调用。
2. **配置获取**: 建议先通过 `get_available_models()` 获取合法的 `TaskConfig` 对象，再传递给生成函数。
3. **错误处理**: 接口内部已封装 `try-except`，若失败会返回 `False` 状态位及错误信息，开发者应检查返回值的第一个布尔元素。

## 变更影响分析
- **模型配置变更**: 若 `src/config/api_ada_configs.py` 中的 `TaskConfig` 结构发生变化，将直接影响此 API 的参数类型。
- **底层请求库**: 该 API 依赖 `src.llm_models.utils_model.LLMRequest`，底层请求逻辑的修改会改变生成行为（如超时、重试机制）。

## 证据
- `src/plugin_system/apis/llm_api.py`: 定义了 `async def generate_with_model` 函数，明确了返回值为 `Tuple[bool, str, str, str]`。
- `src/plugin_system/apis/llm_api.py`: 定义了 `def get_available_models() -> Dict[str, TaskConfig]`，展示了如何从 `model_config.model_task_config` 提取配置。