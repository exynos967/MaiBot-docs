---
last_updated: 2026-01-19 
---

# Unified Message Client 

## 概述 
`MessageClient` 是 `maim_message` 库中用于构建统一消息客户端的核心类。作为主入口点（Main entry point for unified message clients），它封装了底层的通信细节，支持 WebSocket 和 TCP 模式的消息交互。 

## 目录/结构 
- **src/maim_message/api.py**: 包含 `MessageClient` 类及其基于 `BaseMessageHandler` 的核心分发逻辑。 
- **src/maim_message/client_base.py**: 提供客户端网络连接的基础实现架构。 
- **src/maim_message/connection_interface.py**: 定义了连接层抽象接口。 

## 适用范围 
该组件适用于需要高性能、双事件循环架构的消息处理场景。它集成了异步网络驱动器，并支持通过 `MessageConverter` 在 Legacy API 和现代 `APIMessageBase` 格式之间进行标准化转换。 

## 变更影响分析 
`MessageClient` 位于 `src/maim_message/api.py`，是公开 API 表面的重要组成部分。其内部实现的任何变更将直接影响客户端连接管理、心跳机制及消息处理回调的注册逻辑。此外，由于其依赖 `ClientNetworkDriver` 处理 I/O，底层网络逻辑的修改也需同步验证。 

## 证据 
- "Main entry point for unified message clients." 
- "MessageClient"
