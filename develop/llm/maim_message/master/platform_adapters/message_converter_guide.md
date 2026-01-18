---
title: 消息格式转换与适配指南
type: improvement
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
`MessageConverter` 是连接 Legacy 插件系统与新版 API-Server 的桥梁。它提供了标准化的双向转换逻辑，确保不同版本的组件可以无缝协作。

## 目录/结构
### 1. 接收场景 (Receive)
- **to_api_receive**: 将 Legacy 消息转换为 API 格式，将 `user_info` 映射至 `sender_info`。
- **from_api_receive**: 反向转换。

### 2. 发送场景 (Send)
- **to_api_send**: 将 Legacy 消息转换为 API 格式，将 `user_info` 映射至 `receiver_info`。
- **from_api_send**: 反向转换。

## 适用范围与边界
- **适用范围**: 仅用于 `MessageBase` 与 `APIMessageBase` 之间的转换。
- **边界**: 转换过程中若缺少 `api_key` 或 `platform` 等必要字段，将抛出异常或需要手动补充。

## 变更影响分析
- **初始建档**: 解决了 v2.0+ 版本引入后，旧版插件无法直接处理新版消息的问题。开发者应优先使用场景化方法（receive/send）而非通用私有方法。