---
title: System Configuration and TOML Persistence
last_updated: 2026-01-19
---

## 概述
MaiBot 的配置管理系统集中于 `src/config` 目录，采用 TOML 格式作为持久化存储媒介。该系统通过 Python dataclasses 提供了类型安全的运行时访问，涵盖了从机器人人格设定到复杂的 LLM 任务分配等各项参数。

## 目录/结构
- `src/config/config_base.py`: 核心基类 `ConfigBase` 提供了基于反射的递归转换逻辑，支持将嵌套的 TOML 字典结构解析为强类型的 Python 对象。
- `src/config/config.py`: 定义了主加载函数 `load_config` 和 `api_ada_load_config`，用于初始化 `bot_config.toml` 与 `model_config.toml`。
- `src/config/api_ada_configs.py`: 包含 `ModelTaskConfig`，负责定义 planner（规划者）、replyer（回复者）和 tool_use（工具使用）等不同任务的模型选择逻辑。
- `src/config/official_configs.py`: 管理 `ChatConfig`（上下文大小、回复频率）和 `LPMMKnowledgeConfig`（长短期记忆与 RAG 搜索权重）。

## 适用范围
该系统适用于 MaiBot 的全局行为配置，包括机器人的多平台默认设置（如 'qq'）、API 供应商凭证验证、以及长短期个人记忆（LPMM）的模式切换（classic 或 agent）。

## 变更影响分析
- **配置自动迁移**：系统通过 `MMC_VERSION` 识别版本，并利用 `update_config` 自动合并模板变更，同时保留用户的注释和自定义值。
- **运行时风险**：若 TOML 中缺少必填字段，`load_config` 将触发 `ValueError` 导致程序退出；`APIProvider` 亦会强制检查 `api_key` 和 `base_url` 的有效性。
- **类型系统局限**：`ConfigBase` 目前仅支持 `Optional`（T | None）类型，不支持复杂的 `Union` 类型（例如 `float | str`）。

## 证据
- `global_config = load_config(config_path=os.path.join(CONFIG_DIR, "bot_config.toml"))`
- `MMC_VERSION = "0.13.0-snapshot.1"`