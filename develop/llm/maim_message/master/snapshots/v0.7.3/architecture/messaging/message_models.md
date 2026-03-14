---
title: "Message Models and Segments"
last_updated: 2026-01-19
---

## 概述

本文档定义了 Maim Message 库中现代 API-Server Version 的核心消息模型。这些模型专门为双事件循环架构进行了优化，构成了跨 WebSocket 和 TCP 通信的标准化数据交换基础。核心组件包括 APIMessageBase 消息类及其组成部分 Seg（消息段）。

## 目录/结构

该模块位于 `src/maim_message/message`，作为 API-Server Version 消息架构的主入口，通过 `__init__.py` 统一导出了定义在 `api_message_base.py` 中的关键数据结构：

- **APIMessageBase**: 主要消息类，用于现代 API 版本的核心数据承载。
- **Seg**: 消息段，代表通信协议中的基础消息片段。
- **BaseMessageInfo**: 包含消息基础元数据的数据结构。
- **GroupInfo**: 针对群组相关消息上下文的元数据结构。
- **UserInfo**: 针对用户相关消息上下文的元数据结构。

## 适用范围

适用于所有使用现代 API-Server Version 架构的场景，包括统一的 WebSocket 和 TCP 通信。这些模型通过 `MessageConverter` 实现与 Legacy API 模型（MessageBase）之间的标准化双向转换，确保了新旧协议的兼容性。

## 变更影响分析

- **依赖风险**: `src/maim_message/message` 作为一个 Facade（门面），高度依赖于 `src/maim_message/api_message_base.py`。父模块结构的任何变动都可能导致此导出层失效。
- **架构一致性**: 修改 APIMessageBase 或 Seg 的结构将直接影响 `MessageConverter` 的转换逻辑以及 `MessageServer` 与 `MessageClient` 的消息处理流程。

## 证据

- API-Server Version Message Module - 最新消息格式和组件
- APIMessageBase,         # 主要消息类（原ServerMessageBase）
- Seg
