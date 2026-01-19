---
title: 插件 API 参考手册
last_updated: 2026-01-19
---

## 概述
apis 模块作为插件系统的中心化门面层（facade layer），为插件开发者提供了与核心机器人功能（如聊天管理、数据库 CRUD、LLM 生成、消息发送等）交互的标准化高级接口。它通过抽象内部复杂逻辑为 get_all_streams、db_query 和 text_to_stream 等函数，旨在确保系统的稳定性并降低开发门槛。

## 目录/结构
当前模块包含以下核心 API 文件：
- `src/plugin_system/apis/chat_api.py`: 提供聊天流查询与过滤功能，核心组件为 ChatManager。
- `src/plugin_system/apis/database_api.py`: 提供基于 Peewee 模型的通用数据库操作接口 `db_query`。
- `src/plugin_system/apis/generator_api.py`: 核心回复生成接口 `generate_reply`，由 ReplyerManager 管理。
- `src/plugin_system/apis/send_api.py`: 消息发送接口，如 `text_to_stream`，内部使用 UniversalMessageSender 处理多平台分发。
- `src/plugin_system/apis/plugin_register_api.py`: 提供插件注册装饰器 `register_plugin`。
- `src/plugin_system/apis/component_manage_api.py`: 管理组件（命令、动作、工具等）的生命周期与元数据。

## 适用范围
本手册适用于所有基于 MaiBot 开发的插件。开发者可通过以下核心接口实现功能：
- **注册插件**: 使用 `@register_plugin` 装饰器。
- **数据库交互**: 通过 `db_query` 进行数据的增删改查。
- **触发生成**: 使用 `generate_reply` 调用 LLM 生成逻辑。
- **发送消息**: 使用 `text_to_stream` 发送文本或流式消息。

## 变更影响分析
- **数据安全**: `db_query` 允许直接操作模型且缺乏严格的数据类型验证，插件传递错误数据可能导致系统异常。
- **状态风险**: 隐式访问内部管理器（如 get_chat_manager）若处理不当，可能导致全局状态损坏。
- **异步调用**: 如 `globally_disable_component` 等异步 API 必须在插件代码中被正确 await，否则将产生静默失败。

## 证据
- `db_query`
- `generate_reply`
- `src/plugin_system/apis/chat_api.py`