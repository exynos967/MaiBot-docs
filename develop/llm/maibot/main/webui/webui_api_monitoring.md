---
title: "WebUI 后端监控 API"
last_updated: 2026-01-19
---

## 概述
WebUI 监控 API 模块基于 FastAPI 构建，主要用于系统规划器 (Planner) 和回复器 (Replier) 组件的状态监控。该模块提供了查询日志、分页检索以及查看具体日志详情的端点，支持管理后台对机器人运行逻辑进行深度审计。

## 目录/结构
- src/webui/api/planner.py: 提供规划器活动概览 (get_planner_overview) 及分页日志检索 (get_chat_plan_logs)。
- src/webui/api/replier.py: 提供回复器日志概览 (get_replier_overview) 及分页日志检索 (get_chat_reply_logs)。
- src/webui/webui_server.py: 包含 WebUIServer 服务器入口类。
- src/webui/auth.py: 提供统一认证逻辑 verify_auth_token_from_cookie_or_header。
- src/webui/routers/system.py: 系统级管理路由。

## 适用范围
主要用于 MaiBot 管理后台，允许管理员监控存储在 logs/plan (PLAN_LOG_DIR) 和 logs/reply (REPLY_LOG_DIR) 目录下的 JSON 日志文件，并支持根据文件名解析时间戳进行排序。

## 变更影响分析
- **安全性**: 直接访问文件系统的接口（如 get_log_detail）若未对 chat_id 或 filename 进行严格校验，可能存在路径穿越风险。
- **性能**: 在大规模日志目录下进行内容过滤搜索时，性能会随着文件数量增加而线性下降。
- **认证机制**: 依赖 verify_auth_token_from_cookie_or_header 确保只有授权用户能访问敏感的系统日志。

## 证据
- WebUIServer
- get_chat_plan_logs
- src/webui/routers/system.py
- verify_auth_token_from_cookie_or_header
