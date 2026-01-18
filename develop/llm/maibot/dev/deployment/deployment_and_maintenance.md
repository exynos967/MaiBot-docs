---
title: 部署配置与环境初始化
type: improvement
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 支持 Docker 化部署，并提供了详细的配置模板。系统依赖 Python 3.10+ 环境，通过 `uv` 或 `pip` 管理依赖。配置分为机器人基础配置和模型配置两部分。

## 目录/结构
- `Dockerfile` & `docker-compose.yml`: 容器化部署定义。
- `template/bot_config_template.toml`: 机器人运行参数模板（如令牌、权限、基础行为）。
- `template/model_config_template.toml`: LLM 模型接入配置（如 API Key、模型名称、温度等）。
- `requirements.txt` & `uv.lock`: 依赖项定义。
- `scripts/run.sh`: 启动脚本。

## 适用范围与边界
- **适用范围**: 适用于初次部署、环境迁移以及调整机器人全局参数。
- **边界**: 具体的环境变量优先级（`.env` vs `toml`）需要以源码验证。目前已知存在 `template.env`。

## 变更影响分析
- `bot_config_template.toml` 的结构变化需要同步更新部署文档，否则会导致新用户启动失败。
- 依赖项（`requirements.txt`）的更新可能引入与旧版 Python 环境的兼容性问题。