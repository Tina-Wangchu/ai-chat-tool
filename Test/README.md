# Test 文件夹

## 📋 概述

本文件夹包含所有测试脚本，用于验证 AI Chat Tool 的各种功能。

---

## 📁 测试文件列表

### 核心功能测试

| 文件 | 功能描述 | 状态 |
|:-----|:---------|:-----|
| `test_logging_system.py` | 基础日志系统测试 | ✅ |
| `test_fix.py` | logging 系统测试 | ✅ |
| `test_timestamp_latency.py` | 时间戳和耗时记录测试 | ✅ |
| `test_console_output.py` | 控制台输出清理测试 | ✅ |
| `test_conversation_history.py` | 对话历史功能测试 | ✅ |
| `test_clear_function.py` | /clear 命令测试 | ✅ |

### 天气工具测试

| 文件 | 功能描述 | 状态 |
|:-----|:---------|:-----|
| `test_simple_tool_dashscope.py` | Dashscope 工具调用测试 | ✅ |
| `test_with_amap_key.py` | Amap API Key 验证测试 | ✅ |

---

## 🚀 运行测试

### 运行所有测试
```bash
cd Test
python test_*.py
```

### 单独运行测试
```bash
cd Test
python test_logging_system.py
python test_clear_function.py
```

---

## 📝 测试说明

### test_logging_system.py
**功能：** 验证 AgentLogger 基础功能
- 创建日志目录
- 记录各种类型的日志
- 生成 7 个日志文件

### test_clear_function.py
**功能：** 验证 /clear 清空对话功能
- 添加对话到历史
- 清空对话历史
- 验证清空后可以重新开始

### test_console_output.py
**功能：** 验证控制台输出清理
- 确保日志不输出到控制台
- 所有日志只写入文件

### test_conversation_history.py
**功能：** 验证对话历史添加功能
- 自动添加用户问题
- 自动添加 AI 回复
- 验证历史记录顺序

### test_timestamp_latency.py
**功能：** 验证时间戳和耗时记录
- 检查日志中的时间戳格式
- 检查响应日志中的耗时

### test_fix.py
**功能：** logging 系统修复验证

### test_simple_tool_dashscope.py
**功能：** 测试 Dashscope 工具调用

### test_with_amap_key.py
**功能：** 验证 Amap API Key 配置

---

## 🔧 测试维护

### 添加新测试

1. 创建测试文件：`test_xxx.py`
2. 添加到本 README
3. 运行验证

### 测试命名规范

- ✅ 使用 `test_` 前缀
- ✅ 功能描述清晰
- ✅ 包含测试说明
- ✅ 返回 0（成功）或 1（失败）

---

## 📊 测试状态

所有测试均已验证通过：
- ✅ 代码导入正常
- ✅ 功能实现正确
- ✅ 日志文件生成正确
- ✅ 配置加载成功

---

## 📅 相关文档

- [ai_agent_logging_guide.md](../ai_agent_logging_guide.md) - 日志系统完整指南
- [agent_logger_explanation.md](../agent_logger_explanation.md) - AgentLogger 原理说明
- [parameters_guide.md](../parameters_guide.md) - 参数配置说明

---

## ✅ 移动记录

**移动时间：** 2026-06-09 13:32

**移动的文件：**
- 7 个根目录的 test_*.py 文件
- 2 个 weather/ 目录的 test_*.py 文件
- 总计 9 个测试文件

**移动前：** 测试文件分散在根目录和 weather/ 目录

**移动后：** 所有测试文件集中在 Test/ 目录
