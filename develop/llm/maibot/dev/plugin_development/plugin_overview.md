---
title: Plugin System Overview
last_updated: 2026-01-19
---

## 概述
MaiBot 插件系统是一个统一的开发与管理框架，集成了核心基类（Plugin/Action/Command/Tool）、丰富的底层 API 接口以及标准化的数据模型。该系统作为开发者扩展 MaiBot 功能的基础，负责协调插件的注册、配置、消息处理及外部交互。

## 目录/结构
插件系统核心组件分布如下：
- src/plugin_system/base/: 包含 BasePlugin, BaseAction, BaseCommand, BaseTool 等核心基类，以及 ConfigField 和 ConfigLayout 配置组件。
- src/plugin_system/apis/: 提供 ChatManager (chat_api), generate_reply (generator_api), db_query (database_api) 以及 register_plugin 注册装饰器。
- src/plugin_system/utils/: 包含 ManifestValidator 负责插件清单校验。

## 适用范围
本指南适用于以下开发活动：
- 使用 register_plugin 装饰器进行新插件的注册与集成。
- 通过 ChatManager 接口进行聊天记录查询和群组管理。
- 调用 generator_api 接入 LLM 驱动的回复生成引擎。
- 利用 database_api 进行基于 Peewee 模型的数据库 CRUD 操作。

## 变更影响分析
- 核心架构风险：src/plugin_system/base 中的插件基类变动具有全局性影响，可能导致现有插件无法加载或运行。
- 依赖一致性：系统高度依赖 src.common.data_models 中的模型，任何底层模型的微调均需同步更新插件系统导出层。

## 证据
- class PluginBase(ABC):
- src/plugin_system/__init__.py