---
title: "Protocol Security and Encryption"
last_updated: 2026-01-19
---

## 概述
Maim Message 采用专门的加密安全层来保护消息帧。该层基于 X25519 和 ChaCha20Poly1305 加密技术，确保 WebSocket 和 TCP 通信在现代 API-Server 架构下的安全性。

## 目录/结构
以下是与安全协议相关的主要文件及组件：
- `src/maim_message/crypto.py`: 核心加密逻辑实现。
  - `CryptoManager`: 负责管理密钥交换（X25519）和消息帧的加解密（ChaCha20Poly1305）。
- `src/maim_message/ws_config.py`: 包含安全相关的配置项。
  - `ServerConfig`: 支持 SSL 证书及认证回调。
  - `ClientConfig`: 定义 API Key 等认证参数。

## 适用范围
本安全协议适用于：
- `MessageServer`: 支持 WebSocket 和 TCP 模式的统一消息服务器。
- `MessageClient` / `WebSocketClient`: 用于单连接或多连接场景的现代消息客户端。
- 通讯过程中涉及的所有加密消息帧处理。

## 变更影响分析
- **连接稳定性**: `CryptoManager` 的加密握手是连接建立的关键环节。若握手失败，将直接导致连接无法建立。
- **依赖项**: 方案依赖于 `cryptography` 第三方库。
- **框架集成**: 加密逻辑通过 `CryptoManager` 实现，直接影响 `src/maim_message/crypto.py` 中定义的帧创建与解析逻辑。

## 证据
- "X25519/ChaCha20Poly1305 encryption"
- "src/maim_message/crypto.py"
- "实现 X25519 握手及消息帧的加密（ChaCha20Poly1305）与解密。"
