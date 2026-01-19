---
title: 插件清单 (Manifest) 规范
last_updated: 2026-01-19
---

## 概述
本规范定义了插件清单（Manifest）的元数据结构、合法性验证逻辑以及版本兼容性管理机制。该系统确保插件在 MaiBot 环境中能够通过核心工具类进行标准化校验。

## 目录/结构
核心实现位于 `src/plugin_system/utils` 目录下，包含以下关键文件与组件：
- **src/plugin_system/utils/manifest_utils.py**: 核心逻辑实现文件。
- **ManifestValidator**: 负责验证插件清单数据的类，包括字段完整性、版本号兼容性、作者格式及 URL 合法性。
- **VersionComparator**: 负责语义化版本解析、标准化（normalize_version）以及通过硬编码映射表（COMPATIBILITY_MAP）进行向前兼容判定。

## 适用范围
本规范适用于插件清单文件（通常为 _manifest.json）的定义与校验：
- **必需字段**: `REQUIRED_FIELDS` 必须包含 "manifest_version", "name", "version", "description", "author"。
- **支持的版本**: 目前 `SUPPORTED_MANIFEST_VERSIONS` 仅支持版本 [1]。
- **版本区间**: 支持通过 `is_version_in_range` 检查版本是否满足特定的区间要求。

## 变更影响分析
- **兼容性维护**: `COMPATIBILITY_MAP` 采用了硬编码的映射方式（如定义 0.8.x 系列的兼容关系），在主程序升级时需要手动维护，存在滞后风险。
- **容错处理**: `VersionComparator.parse_version` 在解析失败时会记录警告并静默降级到 0.0.0，这可能导致非预期的版本比较行为。
- **验证完整性**: 当前 `ManifestValidator` 对 URL 的验证仅限于协议头检查，且部分生成功能（ManifestGenerator）目前处于非激活状态。

## 证据
- `REQUIRED_FIELDS = ["manifest_version", "name", "version", "description", "author"]` 
- `class ManifestValidator` 
- `class VersionComparator` 
- `src/plugin_system/utils/manifest_utils.py`