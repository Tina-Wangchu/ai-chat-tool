# AI Agent 专用日志记录仪（AgentLogger）功能与原理

## 📋 概述

`AgentLogger` 是一个专门为 AI Agent 设计的日志记录类，它像一台精密的"记录仪"，能够自动捕捉、分类和存储 AI Agent 运行过程中的所有关键信息。

---

## 🎯 核心功能

### 1. 多维度日志分类

AgentLogger 将 AI Agent 的运行信息分为 **7 个类别**：

| 日志类型 | 专门用途 | 存储位置 |
|:---------|:---------|:---------|
| **API 请求** | 记录发给 LLM 的所有请求 | `.log` + `.jsonl` + `api.log` |
| **API 响应** | 记录 LLM 的所有响应 | `.log` + `.jsonl` + `api.log` |
| **工具调用** | 记录外部工具的调用过程 | `.log` + `.jsonl` + `tool.log` |
| **思考过程** | 记录 CoT 推理过程 | `.log` + `.jsonl` + `thinking.log` |
| **错误信息** | 记录所有异常和错误 | `.log` + `.jsonl` + `error.log` |
| **对话交互** | 记录用户和 AI 的对话 | `.log` + `.jsonl` |
| **系统事件** | 记录 Agent 启动/关闭等事件 | `.log` + `.jsonl` |

---

### 2. 双格式输出

AgentLogger 同时生成两种格式的日志：

#### **格式 1：标准日志（.log）** - 人类可读
```
2026-06-09 10:45:31 - weather_agent.logger - INFO - 📡 API请求: {"question": "南京天气", "model": "qwen-max"}
```
**用途：** 快速查看、调试、人工阅读

#### **格式 2：JSON 日志（.jsonl）** - 机器可读
```json
{"timestamp":"2026-06-09T10:45:31.448418","type":"request","agent":"weather_agent","data":{...}}
```
**用途：** 自动化分析、数据挖掘、日志聚合

---

### 3. 七个专门日志记录器

AgentLogger 内部维护 **7 个独立的日志记录器**：

```python
self.logger         # 标准日志（所有信息）
self.json_logger     # JSON 日志（机器处理）
self.api_logger       # API 专用日志
self.tool_logger      # 工具调用日志
self.thinking_logger  # 思考过程日志
self.error_logger     # 错误日志
# （移除了性能指标日志）
```

---

## 🔧 工作原理

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent 应用                             │
│                                                              │
│  用户问题 → API 调用 → 工具调用 → AI 回复 → 用户反馈      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   AgentLogger (日志记录仪)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 接收日志调用                                       │   │
│  │  • log_request(request_data)                       │   │
│  │  • log_response(response_data)                     │   │
│  │  • log_tool_call(tool, args, result)                 │   │
│  │  │                                               │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ 分类到对应的日志记录器                      │   │   │
│  │  │  • API 请求 → api_logger + json_logger       │   │   │
│  │  │  • 工具调用 → tool_logger + json_logger       │   │   │
│  │  │  • 错误信息 → error_logger + json_logger     │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                    │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ 格式化输出                                     │   │   │
│  │  │  • 标准日志 → .log 文件（人类可读）         │   │   │
│  │  │  • JSON 日志 → .jsonl 文件（机器可读）     │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      日志文件系统                             │
│                                                              │
│  logs/                                                      │
│  ├── weather_agent_20260609.log        ← 标准日志             │
│  ├── weather_agent_json_20260609.jsonl  ← JSON 日志            │
│  ├── weather_agent_api_20260609.log      ← API 专用            │
│  ├── weather_agent_tool_20260609.log     ← 工具调用            │
│  ├── weather_agent_thinking_20260609.log ← 思考过程            │
│  └── weather_agent_error_20260609.log    ← 错误日志            │
└─────────────────────────────────────────────────────────────┘
```

---

### 核心方法

#### 1. `log_request(data)` - 记录 API 请求

**功能：** 记录发送给 LLM 的所有请求

**输入数据：**
```python
{
    "round": 1,
    "question": "南京今天的天气怎么样？",
    "model": "qwen-max",
    "thinking_mode": true,
    "timestamp": "2026-06-09T10:45:31"
}
```

**输出位置：**
- 标准日志：`weather_agent_YYYYMMDD.log`
- JSON 日志：`weather_agent_json_YYYYMMDD.jsonl`
- API 日志：`weather_agent_api_YYYYMMDD.log`

---

#### 2. `log_response(data)` - 记录 API 响应

**功能：** 记录 LLM 的所有响应

**输入数据：**
```python
{
    "round": 1,
    "status_code": 200,
    "finish_reason": "tool_calls",
    "latency_ms": "1234.50",
    "timestamp": "2026-06-09T10:45:32"
}
```

**记录内容：**
- HTTP 状态码
- 响应耗时
- 结束原因（stop/tool_calls）
- Token 使用情况

---

#### 3. `log_tool_call(tool, args, result)` - 记录工具调用

**功能：** 记录 MCP 工具的完整调用过程

**示例：**
```python
logger.log_tool_call(
    tool_name="get_weather",
    arguments={"city": "南京"},
    result={"status": "success", "data": {...}}
)
```

**记录内容：**
- 工具名称
- 调用参数
- 执行结果
- 执行时间

---

#### 4. `log_thinking_process(content, budget)` - 记录思考过程

**功能：** 记录 AI 的深度推理过程（CoT）

**用途：**
- 分析 AI 的推理链
- 评估思考质量
- 调优 thinking budget

---

#### 5. `log_error(error_info)` - 记录错误信息

**功能：** 记录所有异常和错误

**记录内容：**
- 错误类型
- 错误消息
- 错误上下文
- 堆栈跟踪

---

#### 6. `log_conversation(user_input, assistant_response)` - 记录对话

**功能：** 记录用户和 AI 的完整对话

**用途：**
- 对话历史分析
- 用户行为研究
- 质量评估

---

#### 7. `log_system_event(event, data)` - 记录系统事件

**功能：** 记录 Agent 生命周期事件

**事件类型：**
- `agent_startup` - Agent 启动
- `agent_shutdown` - Agent 关闭
- `mcp_server_started` - MCP 服务器启动
- `thinking_mode_changed` - 思考模式切换
- `conversation_cleared` - 对话清空

---

## 🎛️ 初始化与配置

### 创建 AgentLogger 实例

```python
from chat_with_tool_thinking import AgentLogger

# 创建日志记录仪
logger = AgentLogger(
    log_dir="logs",          # 日志存储目录
    agent_name="weather_agent"  # Agent 名称
)
```

### 自动创建的日志文件

```
logs/
├── weather_agent_20260609.log           # 标准日志
├── weather_agent_json_20260609.jsonl     # JSON 日志
├── weather_agent_api_20260609.log       # API 专用日志
├── weather_agent_tool_20260609.log      # 工具调用日志
├── weather_agent_thinking_20260609.log   # 思考过程日志
└── weather_agent_error_20260609.log     # 错误日志
```

---

## 📊 日志格式详解

### 标准日志格式

**优点：** 人类可读，便于调试

```
2026-06-09 10:45:31 - weather_agent.logger - INFO - 💬 用户问题: 南京天气
2026-06-09 10:45:32 - weather_agent.logger - INFO - 📡 API请求: {"model": "qwen-max", ...}
2026-06-09 10:45:33 - weather_agent.api - INFO - Request: {...}
2026-06-09 10:45:34 - weather_agent.tool - INFO - Tool: get_weather | Args: {...}
```

---

### JSONL 日志格式

**优点：** 机器可读，便于分析

```json
{"timestamp":"2026-06-09T10:45:31.448418","type":"request","agent":"weather_agent","data":{...}}
{"timestamp":"2026-06-09T10:45:32.123456","type":"response","agent":"weather_agent","data":{...}}
{"timestamp":"2026-06-09T10:45:33.789012","type":"tool_call","agent":"weather_agent","data":{...}}
```

**每行一个独立的 JSON 对象**，便于流式处理。

---

## 🔍 使用示例

### 在 AI Agent 中集成

```python
from chat_with_tool_thinking import AgentLogger

# 初始化日志记录仪
logger = AgentLogger(log_dir="logs", agent_name="weather_agent")

# 记录用户问题
logger.logger.info(f"💬 用户问题: {question}")

# 记录 API 请求
logger.log_request({
    "round": 1,
    "question": question,
    "model": "qwen-max",
    "timestamp": datetime.now().isoformat()
})

# 记录工具调用
logger.log_tool_call(
    tool_name="get_weather",
    arguments={"city": "南京"},
    result={"status": "success", "data": {...}}
)

# 记录 API 响应
logger.log_response({
    "status_code": 200,
    "latency_ms": "1234.50",
    "timestamp": datetime.now().isoformat()
})

# 记录完整对话
logger.log_conversation(question, ai_response)
```

---

## 🎨 设计特点

### 1. 专注性

专为 AI Agent 设计，记录 Agent 特定的信息：
- ✅ API 请求/响应
- ✅ 工具调用
- ✅ 思考过程
- ✅ 对话交互

而不是通用的日志系统。

### 2. 结构化

每条日志都包含完整的上下文：
```json
{
  "timestamp": "...",
  "type": "request",
  "agent": "weather_agent",
  "data": {...}
}
```

便于后续分析和追踪。

### 3. 多层级

- **按功能分类**：API、Tool、Thinking、Error 等
- **按格式分类**：.log（人类）+ .jsonl（机器）
- **按用途分类**：调试、分析、监控

### 4. 时间戳

所有日志都包含 ISO 8601 格式的时间戳：
```
2026-06-09T10:45:31.448418  # 精确到毫秒
```

便于时序分析和性能追踪。

---

## 💡 为什么需要 AgentLogger？

### 1. 通用日志系统不足

Python 的 `logging` 模块是通用的，没有针对 AI Agent 的特殊需求：
- ❌ 不支持 JSONL 格式
- ❌ 不记录对话历史
- ❌ 不区分 API/Tool/Thinking 等类型

### 2. AgentLogger 的优势

| 功能 | 通用 logging | AgentLogger |
|:-----|:-------------|:------------|
| JSONL 输出 | ❌ 需要手动实现 | ✅ 自动支持 |
| 分类存储 | ❌ 需要手动配置 | ✅ 自动分类到 7 个文件 |
| 上下文信息 | ❌ 只有消息文本 | ✅ 包含完整元数据 |
| 时间戳 | ✅ 有 | ✅ 精确到毫秒 |
| 对话历史 | ❌ 不支持 | ✅ 专门记录 |

---

## 🚀 扩展性

### 添加新的日志类型

```python
# 在 AgentLogger 类中添加新方法

def log_custom_event(self, event_type, event_data):
    """记录自定义事件"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "custom",
        "agent": self.agent_name,
        "event_type": event_type,
        "data": event_data
    }
    
    self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    self.logger.info(f"🔖 自定义事件 [{event_type}]: {json.dumps(event_data, ensure_ascii=False)}")
```

### 集成到其他 Agent

```python
from chat_with_tool_thinking import AgentLogger

class MyAgent:
    def __init__(self):
        # 初始化日志记录仪
        self.logger = AgentLogger(log_dir="logs", agent_name="my_agent")
    
    def process(self, question):
        # 记录请求
        self.logger.log_request({"question": question})
        
        # 调用 LLM
        response = self.call_llm(question)
        
        # 记录响应
        self.logger.log_response({"response": response})
```

---

## 📈 性能考虑

### 文件 I/O 优化

- **异步写入：** 日志写入不阻塞主流程
- **批量写入：** 多条日志批量写入文件
- **缓冲区管理：** 自动管理内存缓冲区

### 日志轮转

建议在生产环境中添加日志轮转：

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# 按文件大小轮转
handler = RotatingFileHandler(
    'agent.log',
    maxBytes=100*1024*1024,  # 100MB
    backupCount=5,
    encoding='utf-8'
)

# 按时间轮转
handler = TimedRotatingFileHandler(
    'agent.log',
    when='midnight',
    backupCount=30
)
```

---

## 🔒 安全注意事项

### 1. 敏感信息过滤

**不要记录：**
- ❌ API 密钥（即使部分也不行）
- ❌ 用户隐私信息（地址、电话等）
- ❌ 内部机密信息

### 2. 数据脱敏

如需记录敏感数据，先脱敏：

```python
# ❌ 错误：直接记录
logger.log_request({"api_key": "sk-1234567890"})

# ✅ 正确：脱敏后记录
logger.log_request({"api_key": "sk-1234****"})
```

---

## 📚 相关文档

- [ai_agent_logging_guide.md](ai_agent_logging_guide.md) - 完整日志记录指南
- [chat_with_tool_thinking.py](chat_with_tool_thinking.py) - AgentLogger 实现
- [Python logging 模块](https://docs.python.org/3/library/logging.html) - Python 官方文档

---

## ✅ 总结

AgentLogger 是一个专为 AI Agent 设计的"日志记录仪"：

**核心功能：**
- 📊 7 种日志分类
- 📝 双格式输出（.log + .jsonl）
- 🕒 6 个专用日志文件
- ⏱️ 完整时间戳记录

**设计特点：**
- 🎯 专注 AI Agent 场景
- 🏗️ 结构化日志格式
- 🔧 易于扩展和集成
- 🔒 安全性考虑

**使用价值：**
- 📈 便于调试和问题追踪
- 📊 支持自动化分析
- 📝 完整的运行记录
- 🎓 便于学习和研究

AgentLogger 就像 AI Agent 的"黑匣子记录仪"，完整记录 Agent 运行的每一个关键环节！
