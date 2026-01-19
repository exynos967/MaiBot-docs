---
title: 平台适配：基于 maim_message 的统一消息与回传
type: feature
status: stable
last_updated: 2026-01-18
related_base:
---

## 概述
MaiBot 通过 `maim_message` 依赖库将不同平台的消息统一为标准结构（`BaseMessageInfo`/`Seg` 等），在此基础上实现接收、处理与回传。仓库内的“平台适配”更多体现为：**在统一消息之上做路由与策略**，而非直接处理某个平台协议。

## 目录/结构
- 统一消息类型（来自依赖库）在代码中被频繁引用：
  - `src/chat/message_receive/message.py`：`from maim_message import Seg, UserInfo, BaseMessageInfo, MessageBase`
  - `src/chat/message_receive/bot.py`：`from maim_message import UserInfo, Seg, GroupInfo`
- 平台标识与维度：
  - `BaseMessageInfo.platform`、`group_info`、`user_info` 用于区分来源平台与会话维度（MaiBot 会将 group/user id 规范化为字符串，见 `ChatBot.message_process()`）。
- 回传与 fallback：
  - `src/chat/message_receive/message.py`：发送消息时可走 `get_global_api().send_message(...)`；若配置启用，可能通过 API Server 做 fallback（例如 `global_config.maim_message.enable_api_server`）。

## 适用范围与边界
- **适用范围**：需要新增/调整平台路由、统一消息字段处理、或排查“某平台消息收不到/发不回去”问题时。
- **边界**：
  - 平台协议实现（例如 QQ/NapCat 等）不在本仓库直接实现，通常由 `maim_message` 或其下游适配器承担。
  - 不同平台能力差异（富文本、图片、转发、撤回等）需要结合实际平台与依赖库实现验证。

## 变更影响分析
- 统一消息字段的改动（platform/group/user/message_id 等）会影响会话路由、插件触发范围以及存储键设计。
- 回传链路的改动（API Server / WebUI / legacy 发送方式）可能导致消息丢失、重复或跨平台错投，建议做多平台回归。
