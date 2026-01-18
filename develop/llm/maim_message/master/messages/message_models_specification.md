---
title: 消息模型定义与 Seg 结构规范
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
`maim_message` 提供了两套并行的消息模型：Legacy 版本的 `MessageBase` 和 API-Server 版本的 `APIMessageBase`。两者均基于 `Seg` (Segment) 概念实现多媒体内容的标准化表达，支持文本、图片、表情等多种片段的嵌套与组合。

## 目录/结构
### 1. 核心片段 (Seg)
- **type**: 片段类型（如 `text`, `image`, `seglist`, `at`, `reply`）。
- **data**: 具体内容。`seglist` 类型时，data 为 `List[Seg]`。

### 2. Legacy 消息结构 (MessageBase)
- **message_info**: 包含 `platform`, `message_id`, `user_info`, `group_info` 等元数据。
- **message_segment**: 顶层 `Seg` 对象。

### 3. API-Server 消息结构 (APIMessageBase)
- **message_dim**: 包含 `api_key` 和 `platform`，用于多租户隔离。
- **message_info**: 包含 `sender_info`, `receiver_info` 等更详细的路由信息。

## 适用范围与边界
- **适用范围**: 适用于 MaimBot 生态内所有组件（适配器、核心、插件）间的数据交换。
- **边界**: 本模块仅负责消息的序列化与结构定义，不涉及具体的自然语言处理逻辑。

## 变更影响分析
- **初始建档**: 确立了从 Legacy 向 API-Server 版本演进的结构差异。开发者在从 v0.1.x 升级至 v0.6.x+ 时，需注意 `MessageDim` 字段的强制性要求。