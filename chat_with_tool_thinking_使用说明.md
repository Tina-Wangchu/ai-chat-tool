# chat_with_tool_thinking.py 使用说明

## 📋 概述

`chat_with_tool_thinking.py` 是一个功能完整的天气查询 AI Agent，支持：

- 🌤️ 通过高德地图 MCP 服务器查询天气
- 🧠 思考模式（Chain of Thought）深度推理
- 📊 完整的 Python logging 日志记录系统
- 💬 多轮对话交互

---

## 🗂️ 日志文件组织结构

按照 `ai_agent_logging_guide.md` 4.1 标准，日志文件组织如下：

```
logs/
├── weather_agent_20260608.log           # 标准日志（所有级别）
├── weather_agent_json_20260608.jsonl     # JSON日志（每行一个JSON对象）
├── weather_agent_api_20260608.log       # API专用日志（请求/响应）
├── weather_agent_tool_20260608.log      # 工具调用日志
├── weather_agent_thinking_20260608.log   # 思考过程日志
└── weather_agent_error_20260608.log     # 错误日志
```

---

## 🚀 快速开始

### 1. 环境变量设置

```bash
export AMAP_API_KEY="your-amap-key"
export DASHSCOPE_API_KEY="your-dashscope-key"
```

### 2. 基本运行

```bash
cd ai-chat-tool
python chat_with_tool_thinking.py
```

### 3. 命令行参数

```bash
# 启用思考模式
python chat_with_tool_thinking.py --thinking-mode on

# 关闭思考模式
python chat_with_tool_thinking.py --thinking-mode off

# 自定义思考预算和日志目录
python chat_with_tool_thinking.py --thinking-mode on --thinking-budget 1500 --log-dir my_logs
```

---

## 🎮 交互命令

### 天气查询
```
🧠 请输入问题: 南京今天的天气怎么样？
```

### 思考模式控制
```
🧠 请输入问题: /thinking
```
会显示菜单：
```
1. ✅ 启用思考模式（深度推理，适合复杂问题）
2. ❌ 关闭思考模式（快速回答，适合简单问题）
3. 📊 查看当前配置
4. 🔙 返回主对话
```


### 帮助信息
```
🧠 请输入问题: /help
```

### 退出
```
🧠 请输入问题: quit
```

---

## 📊 日志内容示例

### 标准日志格式（.log 文件）

```
2026-06-08 20:45:31 - weather_agent.logger - INFO - 🚀 启动 MCP 服务器...
2026-06-08 20:45:31 - weather_agent.logger - INFO - 💬 用户问题: 南京今天的天气怎么样？
2026-06-08 20:45:32 - weather_agent.logger - INFO - 📡 API请求: {...}
2026-06-08 20:45:33 - weather_agent.logger - INFO - 📤 API响应: {...}
2026-06-08 20:45:34 - weather_agent.tool - INFO - Tool: get_weather | Args: {"city": "南京"} | Result: {...}
2026-06-08 20:45:35 - weather_agent.logger - INFO - 💬 对话: User=南京今天的天气... | AI=根据查询结果...
```

### JSON 日志格式（.jsonl 文件）

```json
{"timestamp":"2026-06-08T20:45:31.448418","type":"request","agent":"weather_agent","data":{"round":1,"question":"南京今天的天气怎么样？","model":"qwen-max","thinking_mode":true,"timestamp":"2026-06-08T20:45:31.448418"}}
{"timestamp":"2026-06-08T20:45:32.123456","type":"response","agent":"weather_agent","data":{"round":1,"status_code":200,"finish_reason":"tool_calls","latency_ms":"1234.50","timestamp":"2026-06-08T20:45:32.123456"}}
{"timestamp":"2026-06-08T20:45:33.789012","type":"tool_call","agent":"weather_agent","tool_name":"get_weather","arguments":{"city":"南京"},"result":{"status":"success","data":{...}}}
{"timestamp":"2026-06-08T20:45:34.345678","type":"conversation","agent":"weather_agent","user_input":"南京今天的天气怎么样？","assistant_response":"根据查询结果，南京今天..."}}
```

**关键字段说明：**
- `timestamp`: ISO 8601 格式的时间戳
- `latency_ms`: API 响应耗时（毫秒）
- `round`: 对话轮次（1 或 2）

---

## 🔍 日志分析

### 读取 JSONL 日志

```python
import json
from pathlib import Path

# 读取 JSONL 日志
jsonl_file = Path("logs/weather_agent_json_20260608.jsonl")

with open(jsonl_file, 'r', encoding='utf-8') as f:
    for line in f:
        log_entry = json.loads(line)
        print(log_entry)
```

### 统计分析

```python
from collections import Counter

# 统计日志类型
type_counts = Counter()

with open(jsonl_file, 'r', encoding='utf-8') as f:
    for line in f:
        log_entry = json.loads(line)
        type_counts[log_entry['type']] += 1

print(f"请求次数: {type_counts['request']}")
print(f"响应次数: {type_counts['response']}")
print(f"工具调用: {type_counts['tool_call']}")
print(f"错误次数: {type_counts['error']}")
```

---

## 📝 代码结构

### AgentLogger 类

核心日志记录类，包含以下方法：

| 方法 | 用途 |
|:-----|:-----|
| `log_request(request_data)` | 记录 API 请求 |
| `log_response(response_data)` | 记录 API 响应 |
| `log_error(error_info)` | 记录错误信息 |
| `log_tool_call(tool_name, arguments, result)` | 记录工具调用 |
| `log_thinking_process(thinking_content, budget_used)` | 记录思考过程 |
| `log_system_event(event_type, event_data)` | 记录系统事件 |
| `log_conversation(user_input, assistant_response)` | 记录对话交互 |

### 关键修改点

1. **AmapMCPClient 类**：添加 `logger` 参数，在启动和工具调用时记录日志
2. **get_weather_data 函数**：添加 `logger` 参数，记录天气查询过程
3. **ask_weather_with_mcp 函数**：添加 `logger` 参数，记录完整的对话流程
4. **主程序**：初始化 AgentLogger，传递给所有函数，记录系统启动/关闭

---

## 🛠️ 日志级别

| 级别 | 用途 | 示例场景 |
|:-----|:-----|:---------|
| **DEBUG** | 详细调试信息 | 完整请求/响应JSON、内部状态变化 |
| **INFO** | 一般信息 | API调用开始/结束、工具调用成功 |
| **WARNING** | 警告信息 | 重试发生、降级服务、非关键错误 |
| **ERROR** | 错误信息 | API调用失败、工具执行失败 |
| **CRITICAL** | 严重错误 | 服务不可用、配置错误、安全漏洞 |

---

## 💡 最佳实践

### 1. 日志文件管理

```bash
# 查看日志目录
ls -lh logs/

# 查看最新日志
tail -f logs/weather_agent_20260608.log

# 查看 JSONL 日志
tail -f logs/weather_agent_json_20260608.jsonl

# 查看错误日志
tail -f logs/weather_agent_error_20260608.log
```

### 2. 日志分析

```bash
# 统计请求数
grep "API请求" logs/weather_agent_20260608.log | wc -l

# 查找错误
grep "ERROR" logs/weather_agent_20260608.log

# 分析 JSONL 日志
jq -s '.' logs/weather_agent_json_20260608.jsonl
```

### 3. 日志轮转

日志文件按日期自动创建新文件，格式为 `*_YYYYMMDD.*`。

建议定期清理旧日志：

```bash
# 删除 30 天前的日志
find logs/ -name "*.log" -mtime +30 -delete
find logs/ -name "*.jsonl" -mtime +30 -delete
```

---

## 🔧 配置说明

### 思考模式配置

| 配置项 | 说明 | 默认值 |
|:-------|:-----|:-------|
| `enabled` | 是否启用思考模式 | `False` |
| `budget` | 思考 token 预算 | `1000` |

配置优先级：命令行参数 > 环境变量 > 默认值

### 日志配置

| 配置项 | 说明 | 默认值 |
|:-------|:-----|:-------|
| `log_dir` | 日志存储目录 | `logs` |
| `agent_name` | Agent 名称 | `weather_agent` |

---

## 📚 相关文档

- [ai_agent_logging_guide.md](ai_agent_logging_guide.md) - AI Agent 日志记录完整指南
- [thinking_mode_principle_and_implementation.md](../thinking_mode_principle_and_implementation.md) - 思考模式原理和实现

---

## ✅ 验证清单

运行程序后，检查以下内容：

- [ ] `logs/` 目录已创建
- [ ] 包含 6 个日志文件（.log 和 .jsonl）
- [ ] 标准日志包含时间戳、级别、消息
- [ ] JSONL 日志每行是一个完整的 JSON 对象
- [ ] 日志记录正常工作，无性能统计相关代码

---

## 🎯 下一步

1. **运行程序**：`python chat_with_tool_thinking.py`
2. **测试查询**：输入天气相关问题
3. **查看日志**：检查 `logs/` 目录
4. **分析数据**：使用提供的分析脚本

---

## 📞 支持

如有问题，请参考：
- 实习生工作指南
- CLAUDE.md
- 相关技术文档

**Happy Logging! 🎉**
