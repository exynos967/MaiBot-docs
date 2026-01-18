---
title: 插件清单与组件定义规范
type: feature
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 插件系统通过 `_manifest.json` 文件定义插件元数据与功能组件。插件可以作为动作提供者（action_provider）或命令组件集成到系统中。

## 目录/结构
插件结构示例（参考 `src/plugins/built_in/emoji_plugin/`）：
- `_manifest.json`: 包含 `name`, `version`, `plugin_info` 等字段。
- `plugin_info.components`: 定义插件提供的组件，如 `type: "action"`。
- `plugin.py`: 插件逻辑实现入口。

## 适用范围与边界
- **适用范围**: 适用于所有存放在 `plugins/` 目录下的扩展模块。
- **边界**: 内置插件（`is_built_in: true`）通常具有更高的集成权限。插件的 API 调用需遵循 `docs-src/plugins/api/` 中的定义。

## 变更影响分析
清单文件格式的变更会导致旧版插件无法加载。修改 `plugin_type` 会影响插件在决策流（如 PFC）中的调用方式。