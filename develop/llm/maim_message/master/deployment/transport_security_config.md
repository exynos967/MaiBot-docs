---
title: 传输协议与安全配置指南
type: improvement
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
`maim_message` 支持多种传输协议（WS, WSS, TCP）及安全认证机制。生产环境建议开启 SSL/TLS 加密及 API Key 认证。

## 目录/结构
- **传输模式**:
    - `ws`: 标准 WebSocket。
    - `wss`: 加密 WebSocket，需配置 `ssl_certfile` 和 `ssl_keyfile`。
    - `tcp`: 实验性纯 TCP 支持（`mode='tcp'`）。
- **安全配置**:
    - `ConnectionConfig`: 支持 `ssl_verify`, `ssl_ca_certs` 等细粒度控制。
    - `enable_token`: 服务端可选的 Token 验证开关。

## 适用范围与边界
- **适用范围**: 系统部署、内网穿透及跨网络安全通信配置。
- **边界**: TCP 模式目前标记为实验性（experimental），在生产环境中应优先使用 WebSocket。SSL 证书路径需为绝对路径或相对于执行目录的有效路径。

## 变更影响分析
启用 SSL 后，客户端必须在 `RouteConfig` 或 `ClientConfig` 中正确配置 `ssl_verify`。若证书自签名，需分发 CA 证书至客户端，否则连接将因握手失败而重连。