---
title: 配置、数据库与记忆系统（存储与工具）
type: feature
status: stable
last_updated: 2026-01-18
related_base:
---

## 概述
MaiBot 的“存储与工具”主要覆盖三类能力：配置文件加载与更新、SQLite 数据库存储、以及面向对话的记忆检索/总结工具。这些能力为 PFC/思维流/插件系统提供持久化与可观测性基础。

## 目录/结构
- 配置系统
  - `src/config/config.py`：定义总配置 `Config`，并提供 `update_config()` / `update_model_config()` 等模板合并与更新逻辑。
  - `src/config/official_configs.py`：各子配置数据结构（包含 `MaimMessageConfig` 等）。
  - `template/`：配置模板目录（例如 `template/*.toml`，用于生成/更新本地 `config/`）。
- SQLite 数据库（Peewee）
  - `src/common/database/database.py`：SQLite 连接点（`data/MaiBot.db`），并设置 WAL 等 pragmas。
  - `src/common/database/database_model.py`：表模型（例如 `ChatStreams`、`LLMUsage`、`Emoji`、`Messages` 等，按需查阅）。
  - `src/common/message_repository.py`：围绕消息表的查询/计数等仓储操作（供上层模块复用）。
- 记忆系统
  - `src/memory_system/`：记忆检索、历史总结与辅助工具（例如 `memory_retrieval.py`、`chat_history_summarizer.py`、`memory_utils.py`）。

## 适用范围与边界
- **适用范围**：需要理解配置从模板如何演进、排查数据库/记忆检索相关问题、或实现新的持久化能力时。
- **边界**：
  - 具体配置文件（`config/*.toml`）通常属于运行时产物，字段默认值与意义应以模板与 `official_configs.py` 为准。
  - 记忆系统与 PFC/消息流的耦合点需要结合调用方一起阅读（例如消息何时入库、何时触发检索）。

## 变更影响分析
- 配置结构变更需要兼容旧配置迁移（否则会导致启动失败或行为偏移）。
- 数据库表结构/索引变更会影响历史数据可用性与查询性能（需要迁移策略）。
- 记忆检索策略的改动会直接影响回复的一致性与“上下文召回”质量，建议配套做对话回归样例验证。
