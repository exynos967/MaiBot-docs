---
title: 频率控制 API
last_updated: 2026-01-19
---

## 概述
`frequency_api` 模块为插件系统提供了管理会话发言频率的接口。通过该 API，插件可以查询计算后的发言分值，或者直接获取与设置特定会话的发言频率调整系数（Adjust Value）。

## API 列表

### get_current_talk_value
- **描述**: 获取指定会话当前的实际发言分值。
- **函数签名**: `get_current_talk_value(chat_id: str) -> float`
- **实现逻辑**: 该值由会话的频率调整系数（talk_frequency_adjust）乘以全局配置中的基础发言值（global_config.chat.get_talk_value）计算得出。

### set_talk_frequency_adjust
- **描述**: 设置指定会话的发言频率调整系数。
- **函数签名**: `set_talk_frequency_adjust(chat_id: str, talk_frequency_adjust: float) -> None`
- **实现逻辑**: 通过 `frequency_control_manager` 更新指定 `chat_id` 的调整参数。

### get_talk_frequency_adjust
- **描述**: 获取指定会话当前的发言频率调整系数。
- **函数签名**: `get_talk_frequency_adjust(chat_id: str) -> float`

## 调用约定
1. **参数要求**: `chat_id` 需为有效的会话标识字符串；`talk_frequency_adjust` 应为浮点数。
2. **自动初始化**: 接口内部调用 `get_or_create_frequency_control`，若会话控制对象不存在会自动创建。
3. **依赖关系**: 本 API 依赖于 `src.chat.heart_flow.frequency_control` 模块进行状态管理。

## 变更影响分析
- **状态持久性**: 调整系数的修改会立即作用于 `frequency_control_manager` 维护的内存状态，影响后续的发言频率判定。
- **配置联动**: `get_current_talk_value` 的输出受 `global_config` 影响，若全局配置中的发言基础值发生变化，该 API 的返回值将同步改变。

## 证据
- 源码位置 `src/plugin_system/apis/frequency_api.py` 中定义了 `get_current_talk_value(chat_id: str) -> float`，其逻辑包含 `frequency_control_manager.get_or_create_frequency_control(chat_id).get_talk_frequency_adjust() * global_config.chat.get_talk_value(chat_id)`。
- 源码位置 `src/plugin_system/apis/frequency_api.py` 中定义了 `set_talk_frequency_adjust(chat_id: str, talk_frequency_adjust: float) -> None`，直接操作了频率控制管理器的设置接口。