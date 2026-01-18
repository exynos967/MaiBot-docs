---
title: 平台适配器客户端集成
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
适配器作为客户端连接到 MaimCore。Legacy 模式使用 `Router` 管理多平台连接；API-Server 模式使用 `WebSocketClient` 配合 `ClientConfig` 实现单连接或多连接隔离。

## 目录/结构
- **配置管理**:
    - `ClientConfig`: 包含 URL、API Key、SSL 配置及心跳参数。
    - `create_client_config`: 便捷构造函数。
- **客户端实现**:
    - `WebSocketClient`: 支持自动重连、心跳检测及自定义消息处理。
    - `WebSocketMultiClient`: 用于需要同时维护多个身份连接的场景。
- **路由逻辑**:
    - `Router` (Legacy): 通过 `TargetConfig` 映射不同平台的 WebSocket 地址。

## 适用范围与边界
- **适用范围**: 外部机器人平台（QQ、微信、Discord 等）接入 MaimBot 生态。
- **边界**: 客户端需自行处理平台特有的鉴权，`maim_message` 仅提供 `x-apikey` 和 `x-platform` 的 Header 传输机制。

## 变更影响分析
新版客户端强制要求 `api_key`。若从旧版 `Router` 迁移，需将 `TargetConfig` 转换为 `ClientConfig`，并注意 `on_message` 回调签名的变化。