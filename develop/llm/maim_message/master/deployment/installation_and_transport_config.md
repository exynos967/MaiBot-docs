---
title: 安装、传输协议与安全配置
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
`maim_message` 支持多种传输模式，包括标准的 WebSocket (ws/wss) 和实验性的纯 TCP 模式。环境要求 Python 3.10+。

## 目录/结构
### 1. 安装方式
- 稳定版: `pip install maim_message`
- 开发版: `pip install -e .` (需克隆源码)

### 2. 传输模式配置
- **WebSocket (Default)**: 支持 `ssl_certfile` 和 `ssl_keyfile` 开启 WSS。
- **TCP (Experimental)**: 通过 `mode='tcp'` 启用，URL 格式为 `tcp://host:port`。

### 3. 核心依赖
- FastAPI/Uvicorn (服务端)
- websockets/aiohttp (客户端)
- cryptography (安全支持)

## 适用范围与边界
- **适用范围**: 适用于生产环境部署及本地开发调试。
- **边界**: TCP 模式目前标记为实验性，不建议在对稳定性要求极高的生产环境中使用。

## 变更影响分析
- **初始建档**: 记录了 v0.6.4 版本引入的 WSS 支持配置方式。SSL 证书路径在 `RouteConfig` 中需通过 `ssl_verify` 明确指定。