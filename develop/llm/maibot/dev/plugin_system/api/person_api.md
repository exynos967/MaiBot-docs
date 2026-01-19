---
title: 个人信息 API
last_updated: 2026-01-19
---

## 概述
个人信息 API 模块（`person_api.py`）为插件系统提供统一的用户信息查询接口。它封装了对底层 `Person` 类的操作，允许插件通过平台标识、用户原始 ID 或用户名获取系统唯一的 `person_id`，并支持异步查询用户的具体属性字段（如昵称、好感度等）。

## API 列表

### 1. get_person_id
- **描述**: 根据平台名称和原始用户 ID 获取系统唯一的 `person_id`。
- **签名**: `get_person_id(platform: str, user_id: int | str) -> str`
- **参数**: 
    - `platform`: 平台名称（如 "qq", "telegram"）。
    - `user_id`: 用户在该平台的原始 ID。
- **返回值**: 唯一的 person_id（MD5 哈希值），若发生异常则返回空字符串。

### 2. get_person_value (Async)
- **描述**: 根据 `person_id` 异步获取指定的属性字段值。
- **签名**: `async def get_person_value(person_id: str, field_name: str, default: Any = None) -> Any`
- **参数**: 
    - `person_id`: 用户的唯一标识 ID。
    - `field_name`: 要获取的字段名（如 "nickname", "impression"）。
    - `default`: 当字段不存在或获取失败时返回的默认值。
- **返回值**: 字段值或提供的默认值。

### 3. get_person_id_by_name
- **描述**: 根据用户名获取对应的 `person_id`。
- **签名**: `get_person_id_by_name(person_name: str) -> str`
- **返回值**: person_id，如果未找到或发生错误则返回空字符串。

## 调用约定
1. **模块导入**: 推荐使用 `from src.plugin_system.apis import person_api`。
2. **异步调用**: `get_person_value` 是异步函数，调用时必须使用 `await` 关键字。
3. **错误处理**: API 内部已集成异常捕获与日志记录（使用 `person_api` 标签），调用方通常只需检查返回值是否为默认值或空字符串。

## 变更影响分析
- **底层依赖**: 该 API 模块直接依赖 `src.person_info.person_info.Person` 类。如果 `Person` 类的构造函数签名或内部属性存储逻辑发生变化，此 API 模块需要同步调整。
- **字段扩展**: `get_person_value` 使用 `getattr` 动态获取属性，因此只要 `Person` 类增加了新属性，该 API 即可直接支持查询，无需修改代码。

## 证据
- **证据 1**: `src/plugin_system/apis/person_api.py` 中定义了 `get_person_id` 函数，其逻辑为 `Person(platform=platform, user_id=str(user_id)).person_id`。
- **证据 2**: `src/plugin_system/apis/person_api.py` 中定义了 `async def get_person_value`，通过 `getattr(person, field_name)` 实现对用户属性的动态访问。