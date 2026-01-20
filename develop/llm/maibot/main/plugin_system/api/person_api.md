---
last_updated: 2026-01-19
---

## 概述
个人信息 API 模块（person_api.py）为插件系统提供核心用户属性查询功能。它支持将不同平台的原始用户 ID 映射为系统唯一的 person_id，并通过该标识符异步检索用户的昵称、好感度等个性化字段。

## API 列表

### 1. get_person_id
- **函数签名**: `def get_person_id(platform: str, user_id: int | str) -> str`
- **描述**: 根据平台名称（如 qq）和用户原始 ID 返回唯一的 person_id（MD5 哈希值）。
- **返回值**: 成功返回 32 位哈希字符串，失败返回空字符串。

### 2. get_person_value
- **函数签名**: `async def get_person_value(person_id: str, field_name: str, default: Any = None) -> Any`
- **描述**: 异步获取指定用户的特定字段值（如 nickname, impression）。
- **返回值**: 返回字段的具体值；若字段不存在或发生异常，返回 default 参数指定的值。

### 3. get_person_id_by_name
- **函数签名**: `def get_person_id_by_name(person_name: str) -> str`
- **描述**: 通过用户名反向查找对应的 person_id。

## 调用约定
1. **导入路径**: 开发者需从 `src.plugin_system.apis import person_api` 导入模块。
2. **异步约束**: `get_person_value` 是协程函数，必须使用 `await` 关键字进行调用。
3. **错误处理**: 该 API 内部集成了异常捕获与日志记录（logger），调用方在一般情况下无需额外 wrap try-except，可依赖其提供的默认返回值。

## 变更影响分析
- **核心依赖**: 本模块直接依赖 `src.person_info.person_info.Person` 类。如果 `Person` 类的初始化逻辑或数据库映射发生变化，本模块所有函数将受到直接影响。
- **动态属性**: `get_person_value` 内部使用 `getattr(person, field_name)` 获取数据，这意味着其可用字段完全取决于 `Person` 类定义的实例属性。若 `Person` 类移除了某个属性，依赖该属性的插件将只能获取到默认值。

## 证据
- 源码位置: `src/plugin_system/apis/person_api.py`
- 核心逻辑 1: `def get_person_id(platform: str, user_id: int | str) -> str:`
- 核心逻辑 2: `async def get_person_value(person_id: str, field_name: str, default: Any = None) -> Any:`
