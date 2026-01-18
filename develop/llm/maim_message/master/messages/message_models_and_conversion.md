---
title: 消息模型与转换规范
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
`maim_message` 核心提供两套消息模型：Legacy 版本的 `MessageBase` 和 API-Server 版本的 `APIMessageBase`。两者均通过 `Seg` (Segment) 结构实现多媒体内容的标准化表达。`MessageConverter` 负责在不同场景下（接收/发送）进行双向转换。

## 目录/结构
- **核心组件**:
    - `Seg`: 消息片段，支持 `text`, `image`, `seglist` 等类型。
    - `APIMessageBase`: 包含 `MessageDim` (API Key/平台)、`BaseMessageInfo`、`Seg`。
    - `MessageConverter`: 提供 `to_api_receive`, `to_api_send` 等静态方法。
- **元数据结构**:
    - `GroupInfo`: 群组标识与名称。
    - `UserInfo`: 用户标识、昵称及群名片。
    - `MessageDim`: 租户隔离的核心，包含 `api_key` 和 `platform`。

## 适用范围与边界
- **适用范围**: 适用于所有 MaimBot 生态组件的消息序列化与跨版本兼容。
- **边界**: `MessageConverter` 必须明确区分“接收场景”与“发送场景”，以正确映射 `sender_info` 和 `receiver_info`。源码中 `MessageDim` 是 API-Server 版本的强制要求。

## 变更影响分析
从 Legacy 迁移至 API-Server 版本时，需通过 `MessageConverter` 处理 `api_key` 的注入。直接操作字典可能导致 `Seg` 嵌套结构解析失败，建议始终使用 `from_dict` 方法。