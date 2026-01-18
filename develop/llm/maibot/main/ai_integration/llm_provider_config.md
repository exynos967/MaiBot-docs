---
title: 多模型提供商与任务配置规范
type: improvement
status: stable
last_updated: 2026-01-18
related_base: 
---

## 概述
MaiBot 支持多模型提供商集成，通过统一的 `LLMRequest` 接口调用不同厂商的 API。配置采用提供商（Providers）与模型（Models）分离的设计，支持负载均衡与随机选择策略。

## 目录/结构
配置参考 `template/model_config_template.toml`：
- `[[api_providers]]`: 定义 API 基础地址、密钥、客户端类型（如 `openai`, `gemini`）及超时重试参数。
- `[[models]]`: 定义具体模型标识符、价格统计及额外参数（如 `enable_thinking`）。
- `[model_task_config]`: 按任务类型分配模型组，包括 `utils` (基础组件), `replyer` (回复生成), `planner` (决策规划), `vlm` (视觉) 等。

## 适用范围与边界
- **适用范围**: 核心代码中所有通过 `LLMRequest` 发起的异步请求。
- **边界**: 具体的流式输出支持需在模型配置中通过 `force_stream_mode` 显式指定。

## 变更影响分析
修改 `model_task_config` 中的模型列表或温度参数将影响对应任务的响应质量与成本。新增提供商需确保其符合 `openai` 或 `gemini` 的客户端协议。