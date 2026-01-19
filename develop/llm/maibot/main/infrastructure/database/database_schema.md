---
title: 数据库模型与持久化
last_updated: 2026-01-19
---

## 概述
本文档记录了 MaiBot 系统的数据库架构与数据持久化规范。系统采用 Peewee ORM 框架，并以 SQLite 作为基础存储介质，涵盖了从消息记录到用户信息、LLM 统计等核心业务数据的表结构定义。

## 目录/结构
- `src/common/database/`: 提供数据库持久层核心逻辑。
  - `database.py`: 配置全局数据库实例 `db` (SqliteDatabase)，支持 WAL 模式。
  - `database_model.py`: 定义 ORM 模型类，包含 `BaseModel` 及具体的业务表结构。
- `src/common/data_models/`: 定义系统核心 Python 数据模型。
  - `database_data_model.py`: 包含用于业务交互的 `DatabaseMessages` 模型。
  - `message_data_model.py`: 包含 `ReplyContent` 与 `ReplySetModel`。

## 适用范围
本规范涉及以下具体模型及组件：
- **持久化模型 (src/common/database/database_model.py)**: 
  - `ChatStreams`: 会话流记录。
  - `Messages`: 具体的聊天消息内容及 NLP 处理后的元数据。
  - `PersonInfo`: 维护用户信息及个人印象总结。
  - `LLMUsage`: 记录 API 调用的 Token 消耗与成本。
  - `Emoji`: 管理表情包资产与使用频率。
- **核心操作**: `initialize_database` 负责自动初始化表结构、添加缺失字段及同步字段约束。

## 变更影响分析
- **数据安全性**: 在执行 `_fix_table_constraints` 过程中通过 DROP 和 CREATE 重建表来修改约束，若备份失败可能存在数据丢失风险。
- **维护性**: `DatabaseMessages.flatten` 方法依赖硬编码的键名，在新增或修改类字段时必须手动更新。
- **性能限制**: 约束同步逻辑在大数据量场景下可能导致明显的初始化延迟。

## 证据
- `class DatabaseMessages`
- `initialize_database`
- `src/common/database/database_model.py`
- `class BaseModel(Model):`