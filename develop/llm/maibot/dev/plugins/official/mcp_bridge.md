---
title: "MCP Bridge: Model Context Protocol Integration"
last_updated: 2026-01-19
---

## 概述
MCP桥接插件（MCPBridgePlugin）是 MaiBot 系统中用于实现模型上下文协议（Model Context Protocol）的高性能扩展模块。它充当 MaiBot 与外部工具、资源及提示模板之间的桥梁。该插件具备完善的稳定性保障机制，如断路器（CircuitBreaker）、智能心跳和自动重连。它支持两种主要的调用架构：Workflow（预定义的硬流程）和 ReAct（由 LLM 自主决策的软流程）。

## 目录/结构
该插件的核心代码位于 `plugins/MaiBot_MCPBridgePlugin` 目录下，主要结构包括：
- `plugins/MaiBot_MCPBridgePlugin/plugin.py`: 包含主插件类 `MCPBridgePlugin`，负责生命周期管理、工具注册及权限校验。
- `plugins/MaiBot_MCPBridgePlugin/mcp_client.py`: 实现 `MCPClientManager` 和 `MCPClientSession`，管理与服务器的低级通信（Stdio/SSE/HTTP）。
- `plugins/MaiBot_MCPBridgePlugin/tool_chain.py`: 包含 `ToolChainManager`，负责管理和执行用户自定义的 Workflow。
- `plugins/MaiBot_MCPBridgePlugin/_manifest.json`: 插件的配置元数据。
- `plugins/MaiBot_MCPBridgePlugin/requirements.txt`: 列出必要的依赖项，如 `mcp>=1.0.0`。

## 适用范围
此插件适用于需要通过标准化协议扩展模型能力的场景，特别是：
1. 连接遵循 Claude Desktop mcpServers 规范的外部服务器。
2. 在 MaiBot 中通过 `/mcp` 管理命令进行工具链导出或服务器重连。
3. 将 MCP 工具作为软流程集成到系统的记忆检索 Agent 中。
4. 实现基于变量替换（如 `${prev}`）的多步骤自动化工作流。

## 变更影响分析
- **稳定性与性能**: 引入了 `CircuitBreaker` 断路器防止故障蔓延，并使用 `ToolCallCache`（基于 LRU 算法）优化重复调用的开销。
- **调用歧义**: 在软硬流程共存的双轨架构下，同名工具可能引起 LLM 的调用歧义，需注意工具命名规范。
- **资源隔离**: 使用 Stdio 模式时需考虑本地进程环境的安全性与资源隔离问题。

## 证据
- `class MCPBridgePlugin(BasePlugin):` 为插件定义的主类。
- `plugins/MaiBot_MCPBridgePlugin/core/claude_config.py` 定义了核心服务器配置路径。
