---
title: "异步任务管理与本地存储"
last_updated: 2026-01-19
---

## 概述
本文档详细说明了 `src/manager` 目录下的核心管理机制，主要包括支持生命周期管理的异步任务框架以及基于本地 JSON 文件的轻量级持久化键值对存储管理器。

## 目录/结构
- `src/manager/async_task_manager.py`: 包含 `AsyncTaskManager` 和 `AsyncTask` 类，负责管理异步任务的添加、冲突替换、执行监控及批量终止。
- `src/manager/local_store_manager.py`: 包含 `LocalStoreManager` 类，提供基于 JSON 的同步文件持久化接口，并导出全局单例 `local_storage`。

## 适用范围
- **异步任务管理**: 开发者可通过继承 `AsyncTask` 实现业务逻辑，并利用 `AsyncTaskManager.add_task` 启动。支持配置启动前等待（`wait_before_start`）及循环执行间隔（`run_interval`）。
- **轻量级存储**: 适用于简单的配置或状态持久化。通过 `local_storage` 单例进行操作，设置值时会自动同步至路径为 `data/local_store.json` 的文件。

## 变更影响分析
- **潜在阻塞**: `LocalStoreManager` 使用同步 `json.dump/load` 读写文件，在处理大容量数据时可能导致异步事件循环被阻塞。
- **并发冲突**: 目前缺乏跨进程或跨实例的文件锁保护，多处同时写入可能引发数据覆盖或损坏。
- **资源释放**: `stop_and_wait_all_tasks` 方法对每个任务设置了 10.0s 的取消超时限制，无法及时响应取消信号的任务可能导致系统关闭时资源未完全清理。
- **启动延迟**: 调用 `add_task` 替换已存在的同名任务时，会因为阻塞等待旧任务取消而导致最高 5 秒的新任务启动延迟。

## 证据
- `class AsyncTaskManager`
- `class LocalStoreManager`
- `local_storage = LocalStoreManager("data/local_store.json")`
- `async def stop_and_wait_all_tasks(self):`
