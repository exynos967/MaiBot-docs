---
title: Docker 容器化部署与环境配置
type: improvement
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 推荐使用 Docker 进行容器化部署，通过 `docker-compose` 协调核心引擎（Core）、适配器（Adapters）及辅助工具（如 NapCat, SQLite-Web）。

## 目录/结构
部署相关文件：
- `Dockerfile`: 采用多阶段构建，包含 `lpmm-builder` 阶段编译 `quick_algo` 等依赖。
- `docker-compose.yml`: 定义了 `maim-bot-core`, `maim-bot-adapters`, `maim-bot-napcat` 等服务及其网络、卷挂载关系。
- `template/bot_config_template.toml`: 基础运行配置，包含 `personality`, `chat`, `memory` 等模块设置。

## 适用范围与边界
- **适用范围**: 生产环境的快速部署与多服务协同。
- **边界**: 数据库默认使用 SQLite（`MaiBot.db`）。LPMM 编译依赖 `build-essential` 和 `python3.13-slim`。

## 变更影响分析
修改 `docker-compose.yml` 中的卷挂载路径可能导致数据丢失或配置无法读取。`requirements.txt` 的更新需重新构建镜像以生效。