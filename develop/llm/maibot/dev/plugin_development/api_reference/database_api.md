---
title: "Database and Persistence API"
last_updated: 2026-01-19 
---

## 概述 

MaiBot 提供了一套标准化的数据库抽象层 API，旨在为插件开发者提供简便的持久化存储能力。该 API 封装在 `src/plugin_system/apis/database_api.py` 中，作为插件系统与底层核心组件之间的抽象层，确保了数据库操作的标准化与隔离性。 

## 目录/结构 

- **主要接口文件**: `src/plugin_system/apis/database_api.py` 
- **核心功能**: 提供基于 Peewee 模型的异步 CRUD 操作接口。 
- **依赖项**: 
  - `peewee`: 用于对象关系映射。 
  - `src.common.logger`: 系统统一日志服务。 

## 适用范围 

该 API 适用于所有通过 `register_plugin` 注册的插件。开发者可以通过以下核心函数与数据库交互： 

- **db_query**: 通用的数据库 CRUD 异步接口。 
  - **定义位置**: `src/plugin_system/apis/database_api.py` 
  - **支持参数**: 包括模型类 (`model_class`)、数据 (`data`)、查询类型 (`query_type`)、过滤器 (`filters`)、结果限制 (`limit`) 及排序规则 (`order_by`)。 

## 变更影响分析 

- **数据一致性**: `db_query` 使用动态 `getattr` 获取模型字段。若插件传递的模型类与数据库实际定义不符，会引发异常。 
- **异步性**: 所有数据库查询均为异步函数，必须在 `async` 上下文中使用。 
- **模型依赖**: 插件开发者需参考 `src/common/` 中的 Peewee 模型定义以正确构建查询。 

## 证据 

- `src/plugin_system/apis/database_api.py` 
- `db_query(model_class, data, query_type, filters, limit, order_by, single_result)`
