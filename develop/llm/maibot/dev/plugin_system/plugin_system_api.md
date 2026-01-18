---
title: 插件系统与 API 框架
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 提供了一个高度解耦的插件系统，允许开发者扩展机器人的功能。插件通过 `_manifest.json` 进行定义，并支持多种 API 调用，包括数据库、表情管理、LLM 接口等。

## 目录/结构
- `plugins/`: 插件存放根目录。
- `plugins/hello_world_plugin/`: 基础插件示例，包含 `_manifest.json` 和 `plugin.py`。
- `docs-src/plugins/api/`: 详细记录了各类 API，如 `chat-api.md`, `database-api.md`, `llm-api.md`。
- `plugins/MaiBot_MCPBridgePlugin/`: 实现了 MCP（Model Context Protocol）桥接功能，增强了工具链集成。

## 适用范围与边界
- **适用范围**: 适用于开发新功能插件、集成第三方工具或修改现有插件逻辑。
- **边界**: 插件的权限控制和沙箱机制细节需要以源码验证。目前已知插件通过 `_manifest.json` 声明元数据。

## 变更影响分析
- API 的变动（如 `src/plugins/api/` 下定义的接口）会直接导致依赖该接口的所有插件失效。
- 插件加载机制的修改可能影响系统启动速度和稳定性。