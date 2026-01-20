---
last_updated: 2026-01-19
---

# 插件系统核心开发指南

## 概述

MaiBot 插件系统核心框架负责统一导出插件开发所需的基础类、类型定义、API 模块和数据模型。它通过 `BasePlugin` 等基类定义了插件的标准行为，并利用 `register_plugin` 提供了核心的插件注册与加载机制，整合了消息、数据库、配置及大模型相关的各类子系统接口。

## 目录/结构

- **src/plugin_system**: 框架导出层，整合了 `BasePlugin`、`register_plugin`、`BaseAction`、`ManifestValidator` 以及 `chat_api` 等公共接口。
- **src/plugin_system/base**: 架构基础定义目录，包含以下关键组件：
    - `BasePlugin`: 插件顶层实现类，聚合功能组件并调用注册中心。
    - `BaseAction`: 动作组件基类，提供 `execute` 抽象方法及 `send_text`/`send_image` 通信接口。
    - `BaseCommand`: 基于正则表达式匹配的命令组件基类。
    - `BaseEventHandler`: 支持多种系统级事件（如 `ON_MESSAGE`, `ON_PLAN`）的监听器基类。
    - `BaseTool`: 供 LLM 调用的 Function Call 工具组件基类。
    - `PluginBase`: 生命周期管理器，负责清单加载、配置迁移及 Schema 生成。
    - 配置系统: 包含 `ConfigField`、`ConfigSection` 与 `ConfigLayout` 等用于界面渲染的元数据结构。

## 适用范围

本规范适用于所有 MaiBot 插件的开发，包括但不限于动作（Action）、指令（Command）、系统事件处理以及工具集成。开发者在继承上述基类时，应遵循框架定义的生命周期与消息处理协议。

## 变更影响分析

- **依赖项关联**: 框架深度依赖 `src.common.data_models` 下的数据库、信息与 LLM 数据模型，相关模块的路径变更将直接导致系统级导出失败。
- **注册限制**: 组件名称（如 `action_name`）严禁包含 `.` 字符，否则会导致注册失败并抛出 `ValueError`。
- **配置迁移风险**: 目前自动迁移逻辑仅支持 `.toml` 格式。若插件配置的 Schema 发生重大不兼容变更，可能会导致用户配置回退至默认值。
- **硬性约束**: 插件包内必须包含 `_manifest.json` 文件，缺失该文件将导致初始化时抛出 `FileNotFoundError`。

## 证据

- `manifest_file_name: str = "_manifest.json"`
- `raise ValueError(f"Action名称 '{name}' 包含非法字符 '.'，请使用下划线替代")`
