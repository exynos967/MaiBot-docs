---
title: "Frequency API"
last_updated: 2026-01-19
---

## 概述
Frequency API 用于管理特定会话的发言频率控制参数。它封装了底层频率控制管理器的功能，允许插件查询当前会话的发言分值，并动态调整发言频率的系数。

## API 列表
- **get_current_talk_value(chat_id: str) -> float**: 计算特定会话当前的实际发言分值。其逻辑为：获取该会话的调整系数并乘以全局配置中的基础发言值 (`global_config.chat.get_talk_value(chat_id)`)。
- **set_talk_frequency_adjust(chat_id: str, talk_frequency_adjust: float) -> None**: 为指定的 `chat_id` 设置发言频率调整系数。
- **get_talk_frequency_adjust(chat_id: str) -> float**: 获取指定会话当前的发言频率调整系数。

## 调用约定
1. 插件调用时必须提供有效的 `chat_id` 字符串。
2. `talk_frequency_adjust` 应当为浮点数类型。
3. 所有操作均通过 `frequency_control_manager` 进行状态维护。

## 变更影响分析
- 该 API 强依赖于 `src.chat.heart_flow.frequency_control.frequency_control_manager`。
- `get_current_talk_value` 的结果受 `global_config` 基础配置与动态调整系数的共同影响，配置项的缺失或修改将直接改变计算结果。

## 证据
- 接口定义位于：`src/plugin_system/apis/frequency_api.py`
- 核心逻辑证据 1: `def get_current_talk_value(chat_id: str) -> float:`
- 核心逻辑证据 2: `frequency_control_manager.get_or_create_frequency_control(chat_id).set_talk_frequency_adjust(talk_frequency_adjust)`
