---
title: Built-in Plugins Reference
last_updated: 2026-01-19
---

## 概述
本文档基于 MaiBot 框架提供的内置插件及开发示例，旨在指导开发者掌握插件开发模式。重点参考了 src/plugins/built_in/plugin_management 及 plugins/hello_world_plugin 的实现，涵盖了动作 (Actions)、命令 (Commands)、工具 (Tools) 和事件处理器 (EventHandlers) 的标准化设计方式。

## 目录/结构
- **插件管理内置插件 (Internal Management)**
  - 路径：`src/plugins/built_in/plugin_management/`
  - 核心类：`PluginManagementPlugin`, `ManagementCommand`
  - 职责：负责插件的动态加载、卸载及权限控制（`/pm` 指令）。
- **Hello World 示例插件 (Demonstration)**
  - 路径：`plugins/hello_world_plugin/`
  - 核心类：`HelloWorldPlugin`, `HelloAction`, `TimeCommand`, `CompareNumbersTool`, `ForwardMessages`
  - 职责：展示如何利用 `src.plugin_system` 的 APIs 实现消息监听、LLM 交互及配置管理。

## 适用范围
本文档适用于所有需要扩展 MaiBot 功能的开发者。开发者需遵循 `src/plugin_system/base/` 定义的基类规范，并可通过 `src/plugin_system/apis/` 中的 `ChatManager`、`generate_reply` 和 `register_plugin` 进行功能开发。

## 变更影响分析
- **核心功能影响**：对 `src/plugins/built_in/plugin_management/plugin.py` 的修改将影响全局插件生命周期管理（load/unload）及权限列表 `plugin.permission` 的验证。
- **参考实现影响**：`plugins/hello_world_plugin/plugin.py` 作为官方开发范本，其结构的调整会影响新开发者对 `BasePlugin` 注册及 `available_for_llm` 等元数据定义的理解。
- **依赖项**：部分组件如 `TestCommand` 强依赖 `src.plugin_system.apis.generator_api`，若 LLM 生成器服务不可用，该功能将受限。

## 证据
- class HelloWorldPlugin(BasePlugin):
- class ManagementCommand(BaseCommand):