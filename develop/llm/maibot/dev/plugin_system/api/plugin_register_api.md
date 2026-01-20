---
last_updated: 2026-01-19
---

# 插件注册 API (Plugin Register API)

## 概述
`register_plugin` 是 MaiBot 插件系统的标准入口，通过装饰器模式将外部开发的插件类注册到系统的插件管理器（`plugin_manager`）中。它负责执行基本的类型校验、名称合法性检查以及插件源码路径的物理定位。

## API 列表

### `register_plugin(cls)`
- **类型**: 函数装饰器
- **主要职责**: 
  - 验证被装饰的类是否为 `BasePlugin` 的子类。
  - 校验插件名称 `plugin_name` 是否包含非法字符（如 `.`）。
  - 自动溯源插件的物理路径并将其记录到管理器中。
  - 将插件类存储于 `plugin_manager.plugin_classes` 映射表中。

## 调用约定
1. **继承要求**: 被注册的类必须显式继承自 `src.plugin_system.base.base_plugin.BasePlugin`。
2. **属性定义**: 类必须定义 `plugin_name` 字符串属性。
3. **命名规范**: `plugin_name` 不允许包含点号 (`.`)，建议使用下划线（`_`）进行命名。
4. **注册时机**: 该 API 仅负责注册类引用（Class Reference），不执行即时实例化。实例化由 `plugin_manager` 在后续生命周期中负责。

## 变更影响分析
- **路径依赖**: 注册逻辑通过查找 `pyproject.toml` 来定位项目根目录。如果项目结构中缺少此文件，注册过程将失败。
- **管理器耦合**: 该装饰器直接操作 `src.plugin_system.core.plugin_manager` 中的 `plugin_classes` 和 `plugin_paths` 字典。对这些数据结构的修改需要同步更新此注册 API。
- **异常处理**: 若插件名包含点号，会抛出 `ValueError`。若不符合继承关系，则通过 Logger 输出错误信息但不中断程序，仅返回原类对象。

## 证据
- 源码定义位置: `src/plugin_system/apis/plugin_register_api.py`
- 类型校验逻辑: `if not issubclass(cls, BasePlugin):` 用于确保插件基类合规性。
- 命名限制证据: `if "." in plugin_name: raise ValueError(...)` 证实了对点号的字符限制。
