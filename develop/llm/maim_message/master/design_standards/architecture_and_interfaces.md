---
title: 系统架构与通信接口设计
type: refactor
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
库采用接口驱动设计，通过 `ConnectionInterface` 定义了统一的通信行为。系统分为 Legacy API（基于 `Router`）和 API-Server API（基于 `WebSocketClient/Server`）两套并行架构，支持异步 I/O 和多任务管理。

## 目录/结构
- **接口层 (`connection_interface.py`)**:
    - `ConnectionInterface`: 定义 `start`, `stop`, `send_message`。
    - `ServerConnectionInterface`: 扩展 `broadcast_message`。
- **处理层 (`api.py`)**:
    - `BaseMessageHandler`: 提供消息分发逻辑，支持 `custom_message_handlers`。
- **驱动层 (`client_ws_connection.py`)**:
    - `ClientNetworkDriver`: 纯网络 I/O 层，负责 WebSocket 连接生命周期及重连。

## 适用范围与边界
- **适用范围**: 开发者扩展新通信协议（如 TCP）或自定义消息处理器时需遵循此规范。
- **边界**: `BaseMessageHandler` 仅处理逻辑分发，不直接操作 Socket。网络异常由 `NetworkEvent` 向上抛出。

## 变更影响分析
引入 `ClientNetworkDriver` 后，业务逻辑与网络 I/O 实现了解耦。自定义处理器需注意 `asyncio.Task` 的生命周期管理，基类已提供 `_create_handler_task` 进行追踪。