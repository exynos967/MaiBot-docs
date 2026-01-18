---
title: 插件系统架构与 API 规范
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 提供了一个高度解耦的插件系统，允许开发者通过标准 API 扩展功能。插件支持事件驱动和组件化管理，涵盖了从消息处理到外部工具（如 MCP 桥接）的集成。

## 目录/结构
- **插件存放**: `plugins/` 目录下，每个插件通常包含 `_manifest.json` 和 `plugin.py`。
- **示例插件**: 
  - `plugins/hello_world_plugin/`: 基础插件示例。
  - `plugins/MaiBot_MCPBridgePlugin/`: 集成 MCP (Model Context Protocol) 的高级插件。
- **API 定义**: 参考 `docs-src/plugins/api/`，包括 `chat-api.md`, `database-api.md`, `llm-api.md` 等。

## 适用范围与边界
- **适用范围**: 适用于功能扩展、第三方服务接入及自定义指令开发。
- **边界**: 插件的权限控制与沙箱隔离机制需要补充信息。具体的 API 参数定义需要以 `docs-src/plugins/api/` 中的 Markdown 文件为准进行验证。

## 变更影响分析
插件系统的 API 变更会影响所有已安装插件的兼容性。新增 API 需确保在 `src/` 核心代码中有对应的实现支持。