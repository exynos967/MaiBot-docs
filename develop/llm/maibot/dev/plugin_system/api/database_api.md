---
last_updated: 2026-01-19
---

## 概述
`database_api.md` 模块为插件开发者提供了一套基于 Peewee ORM 的通用数据库操作接口。该 API 封装了增、删、改、查等核心逻辑，允许开发者直接通过模型类（Model Class）与底层数据库交互，而无需手动编写 SQL 语句或复杂的查询逻辑。

## API 列表

### 1. db_query
**功能**：执行通用的数据库操作，支持多种查询类型。
- **参数**：
  - `model_class`: Peewee 模型类。
  - `data`: 可选，用于创建或更新的数据字典。
  - `query_type`: 字符串，可选 `"get"`, `"create"`, `"update"`, `"delete"`, `"count"`。
  - `filters`: 字典，键为字段名，值为匹配值。
  - `limit`: 整数，限制结果数量。
  - `order_by`: 列表，字段名前缀 `-` 表示降序。
  - `single_result`: 布尔值，是否只返回单个结果。
- **返回**：根据 `query_type` 返回列表、字典、整数或 `None`。

### 2. db_save
**功能**：保存数据到数据库（执行 Upsert 逻辑）。
- **参数**：
  - `model_class`: Peewee 模型类。
  - `data`: 要保存的数据。
  - `key_field`: 用于匹配现有记录的字段名。
  - `key_value`: 用于匹配的字段值。
- **行为**：若匹配到记录则更新，否则创建。

### 3. db_get
**功能**：`db_query` 的简化版本，专门用于数据检索。
- **参数**：与 `db_query` 的检索参数一致。

### 4. store_action_info
**功能**：专门用于将插件 Action 的执行信息记录到 `ActionRecords` 表中，用于记忆和上下文追踪。

## 调用约定
1. **异步调用**：本模块所有 API 均为 `async` 函数，必须使用 `await` 调用。
2. **类型校验**：`query_type` 必须属于指定的五种操作类型之一。
3. **错误处理**：API 内部包含 `try-except` 块。操作失败时会记录错误日志并返回 `None` 或空列表，调用方应处理返回为空的情况。

## 变更影响分析
- 该模块作为插件系统的基础持久化层，其接口定义的变动将直接影响所有依赖数据库存储的插件。
- 内部逻辑将 Peewee 的结果集转换为字典列表（`dicts()`），这有助于解耦 ORM 对象，但也意味着返回的数据不再具有 ORM 模型的动态方法。

## 证据
- `src/plugin_system/apis/database_api.py` 源码中定义了 `async def db_query` 函数，支持 `create`, `update`, `delete` 等操作。
- `src/plugin_system/apis/database_api.py` 提供了示例用法：`records = await database_api.db_query(ActionRecords, query_type="get")`。
