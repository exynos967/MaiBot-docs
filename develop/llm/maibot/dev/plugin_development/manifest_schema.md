---
title: Plugin Manifest Specification
last_updated: 2026-01-19
---

## 概述
本文档定义了 MaiBot 插件系统的元数据标准和清单文件（Manifest）的校验机制。基于 `src/plugin_system/utils/manifest_utils.py` 中的逻辑，确保所有插件在加载前均符合预设的结构化要求。

## 目录/结构
插件系统清单相关的核心逻辑位于 `src/plugin_system/utils/` 目录下：
- **ManifestValidator**: 负责执行 `validate_manifest` 检查，确保包含所有必需字段。
- **VersionComparator**: 提供语义化版本控制，支持 `compare_versions` 和 `is_version_in_range`。
- **必需字段清单 (REQUIRED_FIELDS)**: 
  - `manifest_version`: 清单版本标识。
  - `name`: 插件名称。
  - `version`: 插件语义化版本。
  - `description`: 功能描述。
  - `author`: 开发作者信息。

## 适用范围
该规范适用于 Mai-with-u/MaiBot 框架下的所有插件模块。系统强制要求插件清单必须包含 `REQUIRED_FIELDS` 中定义的字段，并当前仅支持清单版本 1。

## 变更影响分析
- **版本兼容性**: 通过 `COMPATIBILITY_MAP` 维护插件版本与主程序 `MMC_VERSION`（定义于 `src.config.config`）的对应关系，更新主程序版本可能需要同步维护该硬编码映射。
- **验证反馈**: 当清单验证失败时，可以通过 `get_validation_report` 获取详细的错误描述。

## 证据
- `REQUIRED_FIELDS = ["manifest_version", "name", "version", "description", "author"]`
- `src/plugin_system/utils/manifest_utils.py`