---
title: "Legacy and Modern API Conversion"
last_updated: 2026-01-19
---

## 概述
Maim Message 作为一个专业的消息处理库，采用了双层架构设计。为了兼容现有的遗留消息模型并支持基于双事件循环架构优化的现代 "API-Server" 版本，系统引入了标准化的消息转换机制。该机制允许在 Legacy API 组件与现代 API 结构之间进行双向转换，确保了系统的向后兼容性与灵活性。

## 目录/结构
核心转换逻辑主要分布在以下模块中：
- `src/maim_message/message_base.py`: 定义了遗留消息的基础结构，如 `BaseMessageInfo` 和 `Seg`。
- `src/maim_message/api_message_base.py`: 定义了现代 API 版本的核心数据结构 `APIMessageBase`。
- `src/maim_message/converter.py`: 包含静态工具类 `MessageConverter`，实现具体的转换逻辑。

## 适用范围
该转换逻辑适用于以下场景：
1. **接收消息**: 将底层驱动接收到的原始遗留消息模型转换为 `APIMessageBase` 以供现代 API 层处理。
2. **发送消息**: 将应用层构建的 `APIMessageBase` 对象转换回符合遗留协议的格式以实现兼容发送。

## 变更影响分析
- **架构统一性**: 通过 `MessageConverter` 提供的标准化转换，系统实现了 `MessageBase` 与 `APIMessageBase` 之间的无缝桥接，降低了多版本共存的复杂度。
- **性能优化**: 现代 `APIMessageBase` 结构专为双事件循环架构设计，转换过程中的效率直接影响到整体消息路由的吞吐量。
- **导出限制**: 注意到 API-Server 版本的相关组件（如转换器）未在根模块 `__init__.py` 中导出，开发者需从子模块中显式导入 `MessageConverter`。

## 证据
- "提供 MessageBase 和 APIMessageBase 之间的标准化双向转换。"
- "API-Server Version消息类，基于双事件循环架构优化"
- "Explains the logic for bridging legacy message models with the new API-Server version."
