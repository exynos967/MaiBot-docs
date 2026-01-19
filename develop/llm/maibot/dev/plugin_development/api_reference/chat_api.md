---
title: Chat API Reference
last_updated: 2026-01-19
---

## 概述
Chat API 是 MaiBot 插件系统的核心公共接口，主要由 `ChatManager` 类提供支持。它是插件查询聊天上下文、管理聊天流（Chat Streams）以及获取群组信息的首要途径。通过该 API，开发者可以实现对聊天记录的过滤、检索及统计摘要功能，而无需直接操作底层复杂的数据库或协议逻辑。

## 目录/结构
该 API 模块位于 `src/plugin_system/apis` 目录下，核心定义文件为：
- `src/plugin_system/apis/chat_api.py`: 包含核心类 `ChatManager`，负责群聊和私聊流的查询、过滤及统计摘要。

## 适用范围
- **插件开发者**：用于在自定义插件中获取对话历史或群组元数据。
- **系统扩展**：为新的消息处理流提供标准化的信息访问接口。

## 变更影响分析
- **平台默认值**：API 的默认平台参数在多处硬编码为 "qq"，在进行跨平台（如 Telegram 或 Discord）开发时，开发者必须显式传递平台标识以避免逻辑错误。
- **依赖项**：该 API 高度依赖 `src.chat.message_receive.chat_stream` 及 `maim_message`。底层数据模型的变更将直接影响 `ChatManager` 的查询结果。
- **测试挑战**：由于 API 设计高度依赖全局单例（如 `get_chat_manager()`），在编写单元测试时可能需要大量的 Mock 操作。

## 证据
- `src/plugin_system/apis/chat_api.py` 
- `class ChatManager: """聊天管理器 - 专门负责聊天信息的查询和管理"""`