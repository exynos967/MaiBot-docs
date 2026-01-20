---
last_updated: 2026-01-19
---

## 概述
`frequency_api.py` 模块为插件系统提供了用于管理和查询会话发言频率的核心接口。通过该 API，开发者可以获取当前经过频率控制调整后的说话分值，或动态修改会话的频率权重，从而精确控制机器人的发言积极性。

## API 列表
- **get_current_talk_value(chat_id: str) -> float**
  - 功能：计算当前会话的实际说话分值。
  - 逻辑：通过获取当前频率调整系数并乘以全局配置中的基础分值计算得出。
- **set_talk_frequency_adjust(chat_id: str, talk_frequency_adjust: float) -> None**
  - 功能：设置指定会话的发言频率调整系数。
- **get_talk_frequency_adjust(chat_id: str) -> float**
  - 功能：查询指定会话当前的发言频率调整系数。

## 调用约定
1. **入参要求**：`chat_id` 必须为字符串类型；`talk_frequency_adjust` 必须为浮点数。
2. **依赖关系**：该 API 内部调用 `frequency_control_manager` 进行状态维护，并读取 `global_config.chat` 中的配置。

## 变更影响分析
- **频率控制策略**：修改这些函数会直接影响机器人回复的频率阈值判断。
- **配置依赖**：`get_current_talk_value` 的返回值直接受 `global_config.chat.get_talk_value(chat_id)` 的返回结果影响。
- **状态持久化**：所有的调整均通过 `frequency_control_manager` 进行管理，修改逻辑需注意管理器的生命周期。

## 证据
- 模块路径：`src/plugin_system/apis/frequency_api.py`
- 接口定义：`def get_current_talk_value(chat_id: str) -> float:`
- 内部实现：`frequency_control_manager.get_or_create_frequency_control(chat_id).set_talk_frequency_adjust(talk_frequency_adjust)`
