---
title: 插件系统与 API 框架
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 提供了一个高度解耦的插件系统，允许开发者扩展机器人的功能。插件通常通过 `_manifest.json` 声明元数据，并通过事件/命令/组件等机制与主程序交互，覆盖数据库、表情、LLM、工具链桥接等扩展能力。

## 目录/结构
- `plugins/`: 插件存放根目录。
- `plugins/hello_world_plugin/`: 基础插件示例，包含 `_manifest.json` 和 `plugin.py`。
- `plugins/ChatFrequency/`、`plugins/emoji_manage_plugin/`、`plugins/MaiBot_MCPBridgePlugin/`: 其他示例插件（含 MCP 桥接能力）。
- `docs-src/plugins/api/`: 对外 API 的文档入口（如 `chat-api.md`, `database-api.md`, `llm-api.md` 等）。
- `src/plugin_system/`: 插件运行时实现（加载、注册与分发）
  - `src/plugin_system/core/plugin_manager.py`: 插件加载与生命周期管理（启动时会被调用，例如 `src/main.py` 中 `plugin_manager.load_all_plugins()`）。
  - `src/plugin_system/core/component_registry.py`: 组件/命令注册中心（消息处理侧会通过它查找命令）。
  - `src/plugin_system/core/events_manager.py`: 事件分发（例如启动阶段 `EventType.ON_START`）。
- `plugins/MaiBot_MCPBridgePlugin/`: 实现了 MCP（Model Context Protocol）桥接功能，增强了工具链集成。

## 适用范围与边界
- **适用范围**: 适用于开发新功能插件、集成第三方工具或修改现有插件逻辑。
- **边界**:
  - 插件的权限控制和沙箱机制细节需要以源码/配置进一步验证。
  - 对外 API 的“文档化契约”以 `docs-src/plugins/api/` 为准；而实际可调用能力与行为需以 `src/plugin_system/apis/` 与相关实现为准。

## 变更影响分析
- API 的变动会直接影响依赖该接口的所有插件兼容性（建议配套迁移说明与回归）。
- 插件加载机制（`plugin_manager`）的修改可能影响系统启动速度和稳定性。
- 命令/事件分发（`component_registry` / `events_manager`）的规则变化可能改变插件副作用与拦截行为。
