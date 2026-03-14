---
title: "Quick Start Guide"
last_updated: 2026-01-19
---

## 概述
Maim Message 是一个专门的 Python 消息处理库，为 WebSocket 和 TCP 通信提供统一接口。它采用双层架构，支持现代 'API-Server' 版本，并提供 MessageBase 和 APIMessageBase 之间的标准化双向转换，优化了双事件循环架构下的表现。

## 目录/结构
本指南主要涉及以下组件与示例文件：
- **核心配置函数**：`create_server_config` 和 `create_client_config`。
- **示例文件**：
  - `examples/quick_start.py`：基础连接演示。
  - `examples/external_library_example.py`：展示包含 ChatServer 实现的复杂集成。
- **主要入口**：
  - `MessageServer` (src/maim_message/api.py)
  - `MessageClient` (src/maim_message/api.py)

## 适用范围
适用于需要快速上手 Maim Message 库进行服务器和客户端开发的工程人员。该文档重点介绍了如何通过工厂函数初始化 `WebSocketServer` 和 `WebSocketClient`，并利用 `register_custom_handler` 注册应用特定的消息类型。

## 变更影响分析
- **导入约束**：必须遵循模块化导入路径，例如从 `maim_message.server` 或 `maim_message.client` 导入。直接从根模块导入将导致 ImportError。
- **安全性风险**：示例中提供的 `ssl_verify=False` 仅用于开发调试，严禁直接复制到生产环境。
- **传输协议**：目前示例主要覆盖 WebSocket 传输，TCP 模式的具体实现需参考源码中的 TCPServerConnection。

## 证据
- `create_client_config`：用于初始化连接到特定服务器的客户端配置。
- `create_server_config`：用于初始化包含身份验证和消息回调的服务器配置。
- `examples/external_library_example.py`：提供了 ChatServer 的复杂实现参考。
