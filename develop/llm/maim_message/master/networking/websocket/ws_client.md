---
last_updated: 2026-01-19
---

# WebSocket Client Implementation

## 概述
WebSocketClient 是 Maim Message 框架中专为单连接场景设计的现代化消息客户端实现。该组件是 "API-Server" 版本架构的核心部分，利用底层网络驱动器 (ClientNetworkDriver) 处理低级别的网络 I/O、连接状态维护以及自动重连机制。它与 MessageConverter 协作，支持 APIMessageBase 格式的消息处理。

## 目录/结构
- `src/maim_message/client/`: 模块导出入口，通过 `__init__.py` 重新导出 WebSocketClient 和 ClientConfig。
- `src/maim_message/client_ws_api.py`: 核心类 `WebSocketClient` 的定义位置。
- `src/maim_message/client_ws_connection.py`: 负责 WebSocket 底层连接逻辑及状态机。
- `src/maim_message/client_base.py`: 提供客户端基础抽象，由 WebSocketClient 继承。
- `src/maim_message/ws_config.py`: 定义了客户端配置类 `ClientConfig` 及配置创建工具 `create_client_config`。

## 适用范围
- 适用于需要高可靠 WebSocket 通信的单连接应用场景。
- 支持基于双事件循环（dual event loops）架构优化的高并发处理。
- 适用于需要自动处理连接生命周期和重连逻辑的客户端开发。

## 变更影响分析
- **导出一致性**: `src/maim_message/client/__init__.py` 依赖父模块的子模块（如 `client_ws_api.py`），需警惕循环依赖风险。
- **配置契约**: 对 `ClientConfig` 的任何修改都会直接影响 `WebSocketClient` 和 `WebSocketMultiClient` 的初始化行为。
- **网络驱动**: `ClientNetworkDriver` 作为 I/O 层不处理业务逻辑，其接口变更将影响连接层与业务层的解耦稳定性。

## 证据
- "WebSocketClient",          # 单连接客户端（主要使用）
- Specialized modern WebSocket client for single-connection scenarios.