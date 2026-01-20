---
last_updated: 2026-01-19
---
## 概述
描述 BrainChatting 的 observe-act 循环机制。该模块实现了基于 Think-Act-Observe 循环的核心决策逻辑，由 BrainChatting 类协调聊天流的生命周期。

## 目录/结构
- src/chat/brain_chat/brain_chat.py: 包含 BrainChatting 类，负责 orchestrates 循环、消息观察与行动执行，其中核心逻辑位于 _main_chat_loop。
- src/chat/brain_chat/brain_planner.py: 包含 BrainPlanner 类，利用 LLM 进行 ReAct 模式下的规划与动作决策。

## 适用范围
该文档适用于 src/chat/brain_chat 目录，主要涵盖 BrainChatting 类的启动逻辑 (start) 及 BrainPlanner 类的规划逻辑 (plan)。

## 变更影响分析
- **解析依赖**：高度依赖 LLM 输出的 JSON 格式，若解析失败（如 JSON 损坏）将默认执行 'complete_talk' 动作。
- **API 消耗**：如果循环休眠时间（0.1s）或等待逻辑配置不当，可能导致 API 调用频率过高。
- **配置影响**：涉及 global_config.chat.max_context_size 上下文限制及 model_config.model_task_config.planner 模型指定。

## 证据
- async def _main_chat_loop(self)
- class BrainChatting
- class BrainPlanner
