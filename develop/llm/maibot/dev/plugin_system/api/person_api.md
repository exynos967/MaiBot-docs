---
title: 个人信息 API
last_updated: 2026-01-19
---

## 概述

`person_api` 模块为插件系统提供统一的用户个人信息查询接口。通过该 API，插件可以根据平台 ID 或用户名获取系统内部唯一的 `person_id`（MD5 哈希值），并异步查询用户的特定属性（如昵称、印象等）。

## API 列表

### 1. get_person_id
- **类型**: 同步函数
- **功能**: 根据平台名称和原始用户 ID 获取系统唯一的 `person_id`。
- **参数**:
  - `platform` (str): 平台名称，例如 "qq", "telegram"。
  - `user_id` (int | str): 原始用户 ID。
- **返回**: `str` (唯一的 person_id，失败返回空字符串)。

### 2. get_person_value
- **类型**: 异步函数 (async)
- **功能**: 根据 `person_id` 获取指定的字段值。
- **参数**:
  - `person_id` (str): 用户的唯一标识 ID。
  - `field_name` (str): 字段名，如 "nickname", "impression"。
  - `default` (Any): 默认值，当字段不存在或获取失败时返回。
- **返回**: `Any` (字段值或默认值)。

### 3. get_person_id_by_name
- **类型**: 同步函数
- **功能**: 根据用户名查找对应的 `person_id`。
- **参数**:
  - `person_name` (str): 用户名。
- **返回**: `str` (person_id，未找到返回空字符串)。

## 调用约定

1. **导入路径**: `from src.plugin_system.apis import person_api`。
2. **异步处理**: `get_person_value` 是异步函数，调用时必须使用 `await` 关键字。
3. **异常处理**: API 内部已封装 try-except 块并记录错误日志，调用方通常只需处理返回的默认值或空字符串。

## 变更影响分析

- **依赖项**: 该 API 强依赖于 `src.person_info.person_info.Person` 类。如果 `Person` 类的构造函数签名或属性访问逻辑发生变化，此 API 需同步更新。
- **扩展性**: 增加新的用户信息字段无需修改 API 签名，只需在调用 `get_person_value` 时传入对应的 `field_name`。

## 证据

- **源码位置**: `src/plugin_system/apis/person_api.py`
- **核心定义**: 源码中定义了 `def get_person_id(platform: str, user_id: int | str) -> str:` 以及 `async def get_person_value(person_id: str, field_name: str, default: Any = None) -> Any:`，明确了同步与异步的区分。