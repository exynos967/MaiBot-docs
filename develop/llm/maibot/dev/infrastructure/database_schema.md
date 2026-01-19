---
title: Core Database Models and Migrations
last_updated: 2026-01-19
---

## 概述
MaiBot 采用基于 Peewee ORM 的 SQLite 数据库作为持久化存储的基础设施。该模块位于 src/common/database 目录下，负责管理对话流、消息内容、LLM 资源消耗以及记忆检索过程的数据持久化，并包含一套用于同步字段约束的自动化迁移机制。

## 目录/结构
- src/common/database/database.py: 提供全局数据库连接配置，包括启用 WAL 模式、配置 64MB 缓存以及设置同步级别。
- src/common/database/database_model.py: 定义了核心 ORM 模型（如 ChatStreams, Messages, LLMUsage, Jargon, ThinkingBack）以及数据库初始化与同步函数。

## 适用范围
该文档适用于维护 MaiBot 核心架构、监控 LLM 接口调用量、审计对话消息历史以及进行数据库性能优化的开发人员。

## 变更影响分析
- 性能与安全平衡: 为了提升写入性能，synchronous 被设置为 0 (OFF)，这在系统异常断电时可能增加数据库损坏的风险。
- 迁移风险: sync_field_constraints 函数通过备份表方式修复 SQLite 约束，在大规模数据量下进行架构变更可能导致较长的迁移停机时间。
- 跨数据库支持: 当前实现高度依赖 SQLite 的 PRAGMA 机制，若需迁移至 PostgreSQL 等数据库，需重写底层同步逻辑。

## 证据
- class BaseModel(Model):
- def initialize_database(sync_constraints=False):