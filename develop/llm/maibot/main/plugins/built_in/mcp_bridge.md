---
title: "MCP 协议桥接插件"
last_updated: 2026-01-19
---

## 概述
MaiBot_MCPBridgePlugin 实现了 MCP (Model Context Protocol) 协议的桥接功能，旨在将外部工具、资源和提示模板集成到 MaiBot。该插件采用双轨制架构，支持 Workflow 硬流程与 ReAct 软流程，并包含智能心跳检测、断路器保护机制（CircuitBreaker）、基于 LRU 策略的工具调用缓存（ToolCallCache）以及权限管理系统（PermissionChecker）。该插件支持 stdio、SSE 和 HTTP 等多种传输协议。

## 目录/结构
- `plugins/MaiBot_MCPBridgePlugin/`: 插件主目录。
  - `plugin.py`: 包含 `MCPBridgePlugin` 类，负责插件生命周期管理、工具动态注册及 WebUI 配置映射。
  - `mcp_client.py`: 包含 `MCPClientManager` 和 `CircuitBreaker`，负责管理服务器连接、心跳监测及熔断机制。
  - `tool_chain.py`: 包含 `ToolChainManager`，处理 Workflow 工具链的解析与执行。
- `plugins/MaiBot_MCPBridgePlugin/core/`:
  - `claude_config.py`: 包含 `parse_claude_mcp_config` 和 `ClaudeMcpServer` 数据类，用于解析 Claude 桌面风格的 MCP 配置。

## 适用范围
- **工具与资源集成**: 通过 `mcp_status` 查询服务器状态，利用 `mcp_read_resource` 读取外部资源内容。
- **提示词模板**: 使用 `mcp_get_prompt` 获取并解析 MCP 服务器提供的提示词。
- **自动化工作流**: 通过 `chains_list` 配置 Workflow 硬流程以按序执行工具链。
- **智能 Agent**: 启用 `react_enabled` 将 MCP 工具集成到 ReAct Agent 中由 LLM 自主调用。

## 变更影响分析
- **配置解析**: 必须遵循 `ClaudeMcpServer` 的配置规范，`parse_claude_mcp_config` 支持 `stdio`, `sse`, `http` 等协议，配置无效时会抛出 `ClaudeConfigError`。
- **性能优化**: 启用的 `cache_enabled` 可通过 `ToolCallCache` 减少幂等工具的重复网络请求。
- **安全性**: `stdio` 传输模式依赖本地进程，需通过 `PermissionChecker` 实施细粒度的权限控制。
- **鲁棒性**: `CircuitBreaker` 机制在检测到连续调用失败时会自动熔断，防止系统响应堆积。

## 证据
- `class MCPBridgePlugin(BasePlugin)`
- `plugins/MaiBot_MCPBridgePlugin/mcp_client.py`
- `def parse_claude_mcp_config(config_json: str) -> List[ClaudeMcpServer]`
- `class CircuitBreaker`
