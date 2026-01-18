---
title: 核心架构与通信接口规范
type: refactor
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
本库采用接口驱动设计，通过 `ConnectionInterface` 定义了统一的通信行为。架构上支持“客户端”与“服务器”两种角色，旨在解耦平台适配器与核心逻辑服务。

## 目录/结构
### 1. 通信接口 (connection_interface.py)
- **ConnectionInterface**: 基础接口，定义 `start`, `stop`, `send_message`。
- **ServerConnectionInterface**: 扩展 `broadcast_message`。
- **ClientConnectionInterface**: 扩展 `connect` 与 `is_connected` 状态检查。

### 2. 消息处理基类 (BaseMessageHandler)
- 提供 `register_message_handler` 与 `register_custom_message_handler`。
- 支持异步任务管理与后台任务清理（`background_tasks`）。

## 适用范围与边界
- **适用范围**: 规范所有基于 WebSocket 或 TCP 的通信实现类。
- **边界**: 接口定义不限制底层传输协议的具体实现细节（如 websockets vs aiohttp）。

## 变更影响分析
- **初始建档**: 引入了统一的 `BaseMessageHandler` 以减少代码冗余。后续新增通信模式（如 Webhook）必须继承此接口规范以确保兼容性。