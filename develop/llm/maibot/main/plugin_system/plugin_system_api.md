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
  - `plugins/ChatFrequency/`、`plugins/emoji_manage_plugin/`: 其他示例插件。
- **运行时实现**: `src/plugin_system/`（插件加载、事件/命令注册与分发）
  - `src/plugin_system/core/plugin_manager.py`: 插件加载与生命周期管理（启动时会被调用，例如 `src/main.py` 中 `plugin_manager.load_all_plugins()`）。
  - `src/plugin_system/core/component_registry.py`: 组件/命令注册中心（消息处理侧会通过它查找命令）。
  - `src/plugin_system/core/events_manager.py`: 事件分发（例如启动阶段 `EventType.ON_START`）。
- **API 定义**: 参考 `docs-src/plugins/api/`，包括 `chat-api.md`, `database-api.md`, `llm-api.md` 等。

## 适用范围与边界
- **适用范围**: 适用于功能扩展、第三方服务接入及自定义指令开发。
- **边界**:
  - 插件的权限控制与沙箱隔离机制需要以源码/配置进一步验证。
  - 对外 API 的“文档化契约”以 `docs-src/plugins/api/` 为准；而实际可调用能力与行为需以 `src/plugin_system/apis/` 与相关实现为准。

## 变更影响分析
插件系统的 API 变更会影响所有已安装插件的兼容性；新增 API 需确保在 `src/` 核心代码中有对应实现与回归验证。尤其是：
- `component_registry` 的匹配/注册规则变化会直接影响命令触发与组件注入。
- `events_manager` 的事件类型/顺序变化可能改变插件副作用（例如启动时注册、消息前置处理等）。
