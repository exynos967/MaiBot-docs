---
title: "Introduction to Maim Message"
last_updated: 2026-01-19
---

## 概述
Maim Message 是一个专门的 Python 消息处理库，提供 WebSocket 和 TCP 通信的统一接口。它采用双层架构（dual-layer architecture），同时支持传统的旧版消息模型和现代的 "API-Server" 版本，并针对双事件循环进行了架构优化。

## 目录/结构
- **核心消息与转换 (Core Messaging & Conversion)**: 包含 `src/maim_message/api_message_base.py` (APIMessageBase) 和 `src/maim_message/converter.py`。
- **连接 API 层 (Connection API Layer)**: 包含 `src/maim_message/api.py` (MessageServer, MessageClient) 和 `src/maim_message/connection_interface.py`。
- **WebSocket 客户端基础设施**: 包含 `src/maim_message/client/` 路径下的网络驱动程序及 `src/maim_message/client_ws_api.py`。
- **安全与工具**: 涉及 `src/maim_message/crypto.py` 中的 X25519/ChaCha20Poly1305 加密实现。

## 适用范围
该库适用于需要高性能、加密通信且需兼容旧版协议的 Python 项目。其公共接口（Public Surfaces）涵盖了支持 'ws' 或 'tcp' 模式的 MessageServer，以及用于单连接场景的 WebSocketClient。

## 变更影响分析
- **架构升级**: 引入 MessageConverter 提供 MessageBase 与 APIMessageBase 之间的标准化双向转换，确保了 Legacy API 组件的延续性。
- **底层网络**: ClientNetworkDriver 作为纯网络 I/O 层，其变更将直接影响所有基于 WebSocket 的客户端连接管理。
- **构建元数据**: 依据 `setup.py` 配置，项目当前版本为 0.6.4，要求 Python 3.9 及以上环境。

## 证据
- Maim Message is a specialized Python message handling library
- dual-layer architecture supporting both legacy message models and a modern 'API-Server' version