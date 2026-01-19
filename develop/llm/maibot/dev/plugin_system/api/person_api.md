--- 
last_updated: 2026-01-19 
--- 

## 概述

个人信息API模块位于 `src/plugin_system/apis/person_api.py`，主要为插件提供用户标识（person_id）的检索以及用户属性（如昵称、印象等）的异步查询功能。该模块作为 `src.person_info.person_info.Person` 类的封装，确保插件能以标准化的方式访问底层用户数据。

## API 列表

### 1. get_person_id
- **签名**: `get_person_id(platform: str, user_id: int | str) -> str`
- **功能**: 根据平台名称（如 "qq", "telegram"）和平台原始用户 ID 获取系统唯一的 `person_id`（MD5值）。
- **返回**: 成功返回 person_id 字符串，失败返回空字符串。

### 2. get_person_value (异步)
- **签名**: `async def get_person_value(person_id: str, field_name: str, default: Any = None) -> Any`
- **功能**: 获取指定用户的字段值。常见字段包括 `nickname`, `impression` 等。
- **返回**: 对应字段值，若字段不存在或获取失败则返回 `default`。

### 3. get_person_id_by_name
- **签名**: `get_person_id_by_name(person_name: str) -> str`
- **功能**: 通过用户名检索对应的 `person_id`。
- **返回**: person_id 字符串或空字符串。

## 调用约定

- **导入路径**: 开发者应从 `src.plugin_system.apis` 导入 `person_api`。
- **异步处理**: `get_person_value` 必须使用 `await` 关键字调用，因为它涉及可能的异步数据库操作。
- **异常安全**: 模块内部已封装 `try-except` 逻辑，发生错误时会通过 `logger` 记录错误信息，不会直接抛出异常中断插件运行。

## 变更影响分析

- **核心依赖**: 该 API 高度依赖 `src.person_info.person_info.Person` 类。若该类签名变更，API 模块需同步更新。
- **可扩展性**: 字段获取使用 `getattr(person, field_name)`，这意味着只要 `Person` 类支持的属性，该 API 均可透出。

## 证据

- 源码位置 `src/plugin_system/apis/person_api.py` 中定义了 `get_person_id(platform: str, user_id: int | str) -> str` 用于生成 MD5 哈希 ID。
- 源码位置 `src/plugin_system/apis/person_api.py` 中定义了 `async def get_person_value` 并在内部使用 `getattr(person, field_name)` 动态获取属性。