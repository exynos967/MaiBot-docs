---
title: 消息接收与处理流水线（message_receive）
type: feature
status: stable
last_updated: 2026-01-18
related_base:
---

## 概述
MaiBot 在 `src/chat/message_receive/` 中实现“统一消息接收 → 预处理 → 分发 → 发送/存储”的流水线。该层的目标是把不同平台/协议输入统一为 `MessageRecv` 等内部对象，并与插件系统、思维流（heart_flow）等上层逻辑衔接。

## 目录/结构
- `src/chat/message_receive/bot.py`
  - `ChatBot.message_process()`：核心入口（对 message_data 做规范化、过滤、事件触发、命令识别、分发等）。
  - 使用 `component_registry.find_command_by_text()` 识别命令并执行 `BaseCommand`（插件命令体系）。
- `src/chat/message_receive/message.py`
  - `Message` / `MessageRecv`：基于 `maim_message` 的 `BaseMessageInfo`/`Seg` 构造统一消息对象，并对富文本段做递归处理。
  - 包含发送逻辑与 WebUI / API Server fallback（如启用）。
- `src/chat/message_receive/chat_stream.py`
  - `ChatStream`：将消息按群/会话维度组织为 stream，并提供 chat manager（具体路由策略以源码为准）。
- `src/chat/message_receive/storage.py`
  - `MessageStorage`：收发侧的消息持久化/ID 回写等（与 PFC 内部的 `PFC/message_storage.py` 不同层级）。
- `src/chat/message_receive/uni_message_sender.py`
  - `UniversalMessageSender`：管理消息注册、即时处理、发送与存储，并维护思考状态（接口以源码为准）。

## 适用范围与边界
- **适用范围**：接入新平台、调整消息过滤/路由规则、或编写与消息流强相关的插件（命令/事件）时。
- **边界**：
  - 平台协议/事件的底层接入细节大量依赖 `maim_message`（如 `Seg`、`BaseMessageInfo`），该仓库只处理统一后的 message_data。
  - 更上层的“决策/回复生成”位于 `src/chat/brain_chat/` 与 `src/chat/heart_flow/` 等模块，需要联合阅读验证。

## 变更影响分析
- 修改 `MessageRecv` 的解析或 segment 处理，会影响所有消息类型（文本/图片/转发）与下游的 prompt/记忆记录。
- 修改 `ChatBot.message_process()` 的分发顺序（过滤→事件→命令→思维流）会改变插件拦截行为与机器人的整体交互体验。
- 修改发送侧 fallback（WebUI/API Server）可能引入跨平台回传失败或消息重复，需要配套做端到端验证。
