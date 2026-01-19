---
title: 表情包 API
last_updated: 2026-01-19
---

## 概述

`emoji_api` 模块是插件系统提供的标准表情包功能接口。该模块封装了底层 `emoji_manager` 的复杂逻辑，为插件开发者提供了一套简洁的异步 API，支持根据描述、情感标签获取表情包，以及进行表情包的注册与管理。

## API 列表

### 获取类 API

| 函数名 | 类型 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `get_by_description` | 异步 | `description: str` | `Optional[Tuple[str, str, str]]` | 根据描述文本匹配表情包，返回 (base64, 描述, 情感标签) |
| `get_random` | 异步 | `count: int = 1` | `List[Tuple[str, str, str]]` | 随机获取指定数量的有效表情包 |
| `get_by_emotion` | 异步 | `emotion: str` | `Optional[Tuple[str, str, str]]` | 根据情感标签（如 "happy"）随机获取一个匹配的表情包 |
| `get_all` | 异步 | 无 | `List[Tuple[str, str, str]]` | 获取系统中所有未删除的表情包数据 |

### 查询类 API

| 函数名 | 类型 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- |
| `get_count` | 同步 | `int` | 获取当前可用表情包的总数 |
| `get_info` | 同步 | `dict` | 获取系统信息，包含 `current_count`, `max_count`, `available_emojis` |
| `get_emotions` | 同步 | `List[str]` | 获取所有已去重并排序的情感标签列表 |
| `get_descriptions` | 同步 | `List[str]` | 获取所有可用表情包的描述列表 |

### 管理类 API

| 函数名 | 类型 | 参数 | 返回值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `register_emoji` | 异步 | `image_base64: str`, `filename: str = None` | `Dict[str, Any]` | 注册新表情包，支持自动生成唯一文件名 |
| `delete_emoji` | 异步 | `emoji_hash: str` | `Dict[str, Any]` | 根据哈希值删除指定表情包 |
| `delete_emoji_by_description` | 异步 | `description: str`, `exact_match: bool = False` | `Dict[str, Any]` | 根据描述文本批量或精确删除表情包 |

## 调用约定

1. **异步处理**：获取和管理类 API（如 `get_by_description`, `register_emoji`）均为 `async` 函数，调用时必须使用 `await` 关键字。
2. **输入校验**：
   - 描述和情感标签参数不能为空字符串，否则抛出 `ValueError`。
   - 参数类型必须严格符合签名要求（如 `count` 必须为 `int`），否则抛出 `TypeError`。
3. **返回格式**：
   - 成功获取表情包时，通常返回一个三元组 `(base64_string, description, emotion)`。
   - 管理类操作返回包含 `success` (bool) 和 `message` (str) 的字典。

## 变更影响分析

1. **存储限制**：`register_emoji` 会检查系统容量。如果达到 `max_count` 且未开启自动替换功能，注册将失败。
2. **文件系统交互**：注册操作会在 `EMOJI_DIR` 目录下创建物理文件，删除操作会触发底层管理器的删除逻辑。
3. **使用统计**：调用 `get_random` 或 `get_by_emotion` 成功获取表情包后，系统会自动调用 `emoji_manager.record_usage` 记录该表情包的使用次数。

## 证据

- **证据 1**：`src/plugin_system/apis/emoji_api.py` 中定义了获取接口：
  ```python
  async def get_by_description(description: str) -> Optional[Tuple[str, str, str]]:
      """根据描述选择表情包"""
  ```
- **证据 2**：`src/plugin_system/apis/emoji_api.py` 中定义了注册逻辑与容量检查：
  ```python
  async def register_emoji(image_base64: str, filename: Optional[str] = None) -> Dict[str, Any]:
      # ... 检查是否可以注册（未达到上限或启用替换）
      can_register = count_before < max_count or (count_before >= max_count and emoji_manager.emoji_num_max_reach_deletion)
  ```