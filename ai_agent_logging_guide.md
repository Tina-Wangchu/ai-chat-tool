# AI Agent 日志记录完整指南

## 📋 概述

在AI Agent开发中，完善的日志记录是调试、监控和优化的关键。本文档详细介绍如何使用Python logging记录请求和响应的JSON数据，以及在AI Agent工作中需要记录的关键信息。

---

## 一、Python Logging 记录JSON数据

### 1.1 基础Logging配置

#### 完整配置示例

```python
import logging
import json
from datetime import datetime
import os

# ==================== 日志配置 ====================
class AgentLogger:
    """AI Agent专用日志记录器"""
    
    def __init__(self, log_dir="logs", agent_name="default_agent"):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志存储目录
            agent_name: Agent名称，用于文件命名
        """
        self.agent_name = agent_name
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志记录器
        self.logger = self._setup_logger()
        
        # JSON日志专用文件
        self.json_logger = self._setup_json_logger()
    
    def _setup_logger(self):
        """配置标准日志记录器"""
        logger = logging.getLogger(f"{self.agent_name}.logger")
        logger.setLevel(logging.DEBUG)
        
        # 清除已有处理器
        logger.handlers.clear()
        
        # 文件处理器 - 详细日志
        log_file = os.path.join(
            self.log_dir, 
            f"{self.agent_name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器 - 重要信息
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_json_logger(self):
        """配置JSON专用日志记录器"""
        json_logger = logging.getLogger(f"{self.agent_name}.json")
        json_logger.setLevel(logging.DEBUG)
        json_logger.handlers.clear()
        
        # JSON日志文件
        json_log_file = os.path.join(
            self.log_dir, 
            f"{self.agent_name}_json_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
        json_handler.setLevel(logging.DEBUG)
        
        # JSON格式化器
        json_formatter = logging.Formatter('%(message)s')
        json_handler.setFormatter(json_formatter)
        
        json_logger.addHandler(json_handler)
        
        return json_logger
    
    def log_request(self, request_data):
        """记录API请求"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "agent": self.agent_name,
            "data": request_data
        }
        
        # 标准日志
        self.logger.info(f"API请求: {json.dumps(request_data, ensure_ascii=False)}")
        
        # JSON日志
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_response(self, response_data):
        """记录API响应"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "agent": self.agent_name,
            "data": response_data
        }
        
        # 标准日志
        self.logger.info(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        
        # JSON日志
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_error(self, error_info):
        """记录错误信息"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "agent": self.agent_name,
            "data": error_info
        }
        
        # 标准日志
        self.logger.error(f"错误: {json.dumps(error_info, ensure_ascii=False)}")
        
        # JSON日志
        self.json_logger.error(json.dumps(log_entry, ensure_ascii=False))
    
    def log_tool_call(self, tool_name, arguments, result):
        """记录工具调用"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "tool_call",
            "agent": self.agent_name,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        }
        
        # 标准日志
        self.logger.info(f"工具调用 [{tool_name}]: {json.dumps(arguments, ensure_ascii=False)}")
        
        # JSON日志
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_thinking_process(self, thinking_content):
        """记录思考过程"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "thinking",
            "agent": self.agent_name,
            "content": thinking_content
        }
        
        # 标准日志
        self.logger.debug(f"思考过程: {thinking_content[:100]}...")
        
        # JSON日志
        self.json_logger.debug(json.dumps(log_entry, ensure_ascii=False))
```

---

### 1.2 在Dashscope API调用中使用

#### 完整示例代码

```python
import dashscope
from dashscope import Generation
import json

class WeatherAgentWithLogging:
    """带日志记录的天气查询Agent"""
    
    def __init__(self, api_key, log_dir="logs"):
        # 初始化日志记录器
        self.logger = AgentLogger(log_dir=log_dir, agent_name="weather_agent")
        
        # 设置API密钥
        dashscope.api_key = api_key
        
        self.logger.logger.info("🚀 WeatherAgent初始化完成")
    
    def query_weather(self, question):
        """
        查询天气（带完整日志记录）
        
        Args:
            question: 用户问题
        """
        try:
            # ===== 第一轮：发送问题 =====
            self.logger.logger.info("📡 开始第一轮API调用")
            
            # 构建请求
            request_data = {
                "model": "qwen-max",
                "messages": [{"role": "user", "content": question}],
                "extra_body": {"mcp": mcp_cfg}
            }
            
            # 记录请求
            self.logger.log_request({
                "round": 1,
                "question": question,
                "model": request_data["model"],
                "tools": tools
            })
            
            # 发送请求
            start_time = time.time()
            resp = Generation.call(**request_data)
            end_time = time.time()
            
            # 记录响应
            self.logger.log_response({
                "round": 1,
                "status_code": resp.status_code,
                "request_id": resp.request_id,
                "latency": f"{(end_time - start_time)*1000:.2f}ms",
                "output": resp.output.model_dump() if hasattr(resp.output, 'model_dump') else str(resp.output),
                "usage": resp.usage.model_dump() if hasattr(resp.usage, 'model_dump') else str(resp.usage)
            })
            
            # 检查是否有工具调用
            choice = resp.output.choices[0]
            
            if choice.finish_reason == "tool_calls" and hasattr(choice.message, 'tool_calls'):
                tool_call = choice.message.tool_calls[0]
                tool_name = tool_call['function']['name']
                tool_args = json.loads(tool_call['function']['arguments'])
                
                # 记录工具调用
                self.logger.log_tool_call(
                    tool_name=tool_name,
                    arguments=tool_args,
                    result="pending"
                )
                
                # 执行工具
                city = tool_args.get("city", "未知")
                self.logger.logger.info(f"🔧 正在查询 {city} 的天气...")
                
                weather_data = get_weather_data(city, client)
                
                # 记录工具结果
                self.logger.logger.info(f"📊 获取到天气数据: {weather_data}")
                
                # ===== 第二轮：发送工具结果 =====
                self.logger.logger.info("📡 开始第二轮API调用")
                
                messages_2 = [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                    {"role": "tool", "tool_call_id": tool_call["id"], "content": json.dumps(weather_data, ensure_ascii=False)}
                ]
                
                # 记录第二轮请求
                self.logger.log_request({
                    "round": 2,
                    "messages_count": len(messages_2),
                    "tool_result_provided": True
                })
                
                # 发送第二轮请求
                resp2 = Generation.call(
                    model="qwen-max",
                    messages=messages_2
                )
                
                # 记录第二轮响应
                final_reply = resp2.output.choices[0].message.content
                self.logger.log_response({
                    "round": 2,
                    "final_answer": final_reply,
                    "usage": resp2.usage.model_dump() if hasattr(resp2.usage, 'model_dump') else str(resp2.usage)
                })
                
                self.logger.logger.info(f"✅ 查询完成")
                return final_reply
            
            else:
                # 无工具调用，直接回复
                self.logger.logger.warning("⚠️ 未触发工具调用")
                direct_reply = choice.message.content
                self.logger.log_response({
                    "round": 1,
                    "direct_reply": direct_reply,
                    "note": "no_tool_call"
                })
                return direct_reply
        
        except Exception as e:
            # 记录错误
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            self.logger.log_error(error_info)
            self.logger.logger.error(f"❌ 查询失败: {str(e)}")
            raise
```

---

### 1.3 带思考模式的日志记录

```python
def query_with_thinking_logging(self, question, thinking_enabled=False):
    """带思考模式的查询（含日志）"""
    
    # 构建extra_body
    extra_body = {
        "mcp": mcp_cfg
    }
    
    if thinking_enabled:
        extra_body["thinking"] = {
            "enabled": True,
            "budget": 1000
        }
        self.logger.logger.info("🧠 思考模式已启用")
    
    # 记录请求配置
    self.logger.log_request({
        "question": question,
        "thinking_mode": thinking_enabled,
        "thinking_budget": 1000 if thinking_enabled else 0
    })
    
    # API调用...
    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": question}],
        extra_body=extra_body
    )
    
    # 如果有思考过程，记录它
    if hasattr(resp, 'result') and 'thinking' in resp.result:
        thinking_content = resp.result['thinking']
        final_answer = resp.result['content']
        
        # 记录思考过程
        self.logger.log_thinking_process({
            "thinking": thinking_content,
            "answer": final_answer
        })
        
        # 记录完整响应
        self.logger.log_response({
            "thinking_length": len(thinking_content),
            "answer_length": len(final_answer),
            "full_response": {
                "thinking": thinking_content,
                "content": final_answer
            }
        })
```

---

## 二、AI Agent需要记录的关键信息

### 2.1 必须记录的信息（Must-Have）

#### 📡 API请求信息

```json
{
  "timestamp": "2026-06-08T10:30:45",
  "type": "request",
  "request_id": "req_123456",
  "model": "qwen-max",
  "messages": [
    {"role": "user", "content": "南京今天天气怎么样？"}
  ],
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 0.9
  },
  "extra_body": {
    "thinking": {
      "enabled": true,
      "budget": 1000
    },
    "mcp": {
      "mcpServers": {...}
    }
  }
}
```

**关键字段：**
- `request_id`: 请求唯一标识符
- `timestamp`: 请求时间戳
- `model`: 使用的模型名称
- `messages`: 完整对话历史
- `parameters`: 模型参数
- `extra_body`: 扩展配置（thinking、MCP等）

---

#### 📤 API响应信息

```json
{
  "timestamp": "2026-06-08T10:30:46",
  "type": "response",
  "request_id": "req_123456",
  "status_code": 200,
  "latency_ms": 1234.56,
  "output": {
    "choices": [
      {
        "finish_reason": "tool_calls",
        "message": {
          "role": "assistant",
          "content": null,
          "tool_calls": [...]
        }
      }
    ]
  },
  "usage": {
    "input_tokens": 150,
    "output_tokens": 80,
    "total_tokens": 230
  },
  "request_id": "dashscope-request-123"
}
```

**关键指标：**
- `status_code`: HTTP状态码
- `latency_ms`: 响应延迟（毫秒）
- `finish_reason`: 结束原因（stop/tool_calls等）
- `usage`: Token使用情况
- `request_id`: 服务端请求ID（用于问题追踪）

---

### 2.2 工具调用信息（Tool Calling）

#### 🔧 工具调用记录

```json
{
  "timestamp": "2026-06-08T10:30:47",
  "type": "tool_call",
  "tool_name": "amapMaps.weather",
  "arguments": {
    "city": "南京"
  },
  "execution_time_ms": 234.5,
  "result": {
    "status": "success",
    "data": {
      "city": "南京",
      "weather": "多云",
      "temperature": "20°C ~ 28°C"
    }
  },
  "error": null
}
```

**记录内容：**
- 工具名称
- 调用参数
- 执行时间
- 执行结果
- 错误信息（如有）

---

### 2.3 思考过程记录（Thinking Mode）

#### 🧠 思考过程日志

```json
{
  "timestamp": "2026-06-08T10:30:45",
  "type": "thinking",
  "question": "分析未来一周南京的天气趋势",
  "thinking_process": "让我一步步分析这个天气趋势问题...\n1. 首先需要获取未来7天的天气预报...\n2. 分析温度变化趋势...\n3. 考虑降水概率...",
  "thinking_tokens_used": 856,
  "final_answer": "根据分析，未来一周南京天气呈现逐步升温趋势...",
  "budget": 1000
}
```

**分析指标：**
- 思考过程长度
- Token使用情况
- 推理步骤数量
- 思考质量（手动评估）

---

### 2.4 错误和异常信息

#### ❌ 错误日志

```json
{
  "timestamp": "2026-06-08T10:35:12",
  "type": "error",
  "error_type": "APIError",
  "error_code": "rate_limit_exceeded",
  "error_message": "API rate limit exceeded",
  "request_context": {
    "model": "qwen-max",
    "retry_count": 3,
    "last_request_id": "req_789"
  },
  "traceback": "Traceback (most recent call last):\n  ...",
  "impact": "user_facing",
  "recovery_action": "will_retry_after_60s"
}
```

**关键要素：**
- 错误类型和代码
- 请求上下文
- 完整堆栈跟踪
- 影响评估
- 恢复动作

---

### 2.5 性能指标

#### 📊 性能监控

```json
{
  "timestamp": "2026-06-08T10:40:00",
  "type": "metrics",
  "api_metrics": {
    "total_requests": 1523,
    "successful_requests": 1498,
    "failed_requests": 25,
    "avg_latency_ms": 1234.5,
    "p95_latency_ms": 2345.6,
    "p99_latency_ms": 4567.8
  },
  "token_metrics": {
    "total_input_tokens": 234567,
    "total_output_tokens": 123456,
    "total_tokens": 357923,
    "avg_tokens_per_request": 234.9
  },
  "tool_metrics": {
    "total_tool_calls": 856,
    "successful_tool_calls": 842,
    "failed_tool_calls": 14,
    "avg_tool_execution_time_ms": 456.7
  },
  "thinking_metrics": {
    "thinking_enabled_requests": 234,
    "avg_thinking_tokens": 892.3,
    "thinking_accuracy_improvement": "+15.3%"
  }
}
```

---

### 2.6 用户交互信息

#### 💬 对话日志

```json
{
  "timestamp": "2026-06-08T10:45:30",
  "type": "conversation",
  "conversation_id": "conv_abc123",
  "user_id": "user_xyz789",
  "session_id": "session_def456",
  "messages": [
    {
      "role": "user",
      "content": "南京今天天气怎么样？",
      "timestamp": "2026-06-08T10:45:30"
    },
    {
      "role": "assistant",
      "content": "南京今天多云，温度20-28°C...",
      "timestamp": "2026-06-08T10:45:32",
      "tool_calls_used": true
    },
    {
      "role": "user",
      "content": "那明天呢？",
      "timestamp": "2026-06-08T10:45:35"
    }
  ],
  "conversation_state": "active",
  "total_turns": 2
}
```

---

### 2.7 系统和配置信息

#### ⚙️ 系统日志

```json
{
  "timestamp": "2026-06-08T09:00:00",
  "type": "system",
  "event": "agent_startup",
  "agent_name": "weather_agent",
  "version": "2.1.0",
  "configuration": {
    "model": "qwen-max",
    "thinking_mode": "auto",
    "thinking_budget": 1000,
    "mcp_servers": ["amap-maps"],
    "log_level": "DEBUG"
  },
  "environment": {
    "python_version": "3.9.7",
    "dashscope_version": "1.14.0",
    "os": "macOS",
    "api_key_configured": true
  }
}
```

---

## 三、日志级别和分类

### 3.1 日志级别使用指南

| 级别 | 用途 | 示例场景 |
|:----|:----|:---------|
| **DEBUG** | 详细调试信息 | 完整请求/响应JSON、内部状态变化 |
| **INFO** | 一般信息 | API调用开始/结束、工具调用成功 |
| **WARNING** | 警告信息 | 重试发生、降级服务、非关键错误 |
| **ERROR** | 错误信息 | API调用失败、工具执行失败 |
| **CRITICAL** | 严重错误 | 服务不可用、配置错误、安全漏洞 |

---

### 3.2 日志分类策略

#### 按功能分类

```python
# 1. API日志 (api.log)
logger_api = logging.getLogger('agent.api')
logger_api.info("API请求: ...")

# 2. 工具日志 (tool.log)
logger_tool = logging.getLogger('agent.tool')
logger_tool.info("工具调用: amapMaps.weather")

# 3. 思考日志 (thinking.log)
logger_thinking = logging.getLogger('agent.thinking')
logger_thinking.debug("思考过程: ...")

# 4. 错误日志 (error.log)
logger_error = logging.getLogger('agent.error')
logger_error.error("API调用失败: ...")

# 5. 性能日志 (metrics.log)
logger_metrics = logging.getLogger('agent.metrics')
logger_metrics.info("性能指标: ...")
```

#### 按时间分类

```python
# 按日期轮转
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    'agent.log',
    when='midnight',  # 每天午夜
    interval=1,
    backupCount=30     # 保留30天
)
```

---

## 四、日志存储和管理

### 4.1 日志文件组织结构

```
logs/
├── weather_agent_20260608.log           # 标准日志
├── weather_agent_json_20260608.jsonl     # JSON日志（每行一个JSON）
├── weather_agent_api_20260608.log       # API专用日志
├── weather_agent_tool_20260608.log      # 工具调用日志
├── weather_agent_thinking_20260608.log   # 思考过程日志
├── weather_agent_error_20260608.log     # 错误日志
├── weather_agent_metrics_20260608.log    # 性能指标日志
└── archived/                             # 归档目录
    ├── 202605/
    │   ├── weather_agent_20260531.log.gz
    │   └── ...
    └── 202604/
        └── ...
```

---

### 4.2 日志轮转配置

```python
from logging.handlers import RotatingFileHandler

# 按文件大小轮转
handler = RotatingFileHandler(
    'agent.log',
    maxBytes=100*1024*1024,  # 100MB
    backupCount=5,           # 保留5个备份
    encoding='utf-8'
)

# 按时间轮转
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    'agent.log',
    when='H',      # 每小时
    interval=1,
    backupCount=24*7,  # 保留7天
    encoding='utf-8'
)
```

---

### 4.3 JSON日志格式（JSONL）

**优点：**
- 每行一个独立JSON对象
- 易于解析和分析
- 支持流式处理
- 适合大数据量

**示例：**
```jsonl
{"timestamp":"2026-06-08T10:30:45","type":"request","data":{...}}
{"timestamp":"2026-06-08T10:30:46","type":"response","data":{...}}
{"timestamp":"2026-06-08T10:30:47","type":"tool_call","data":{...}}
```

**读取方法：**
```python
import json

# 读取JSONL日志
with open('agent_json_20260608.jsonl', 'r') as f:
    for line in f:
        log_entry = json.loads(line)
        print(log_entry)
```

---

## 五、日志分析工具

### 5.1 简单分析脚本

```python
import json
from collections import Counter
from datetime import datetime

def analyze_logs(log_file):
    """分析JSON日志文件"""
    
    # 统计数据
    stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "tool_calls": Counter(),
        "errors": Counter(),
        "avg_latency": 0,
        "total_tokens": 0
    }
    
    latencies = []
    
    with open(log_file, 'r') as f:
        for line in f:
            log_entry = json.loads(line)
            
            if log_entry["type"] == "request":
                stats["total_requests"] += 1
            
            elif log_entry["type"] == "response":
                if log_entry["data"]["status_code"] == 200:
                    stats["successful_requests"] += 1
                else:
                    stats["failed_requests"] += 1
                
                if "latency_ms" in log_entry["data"]:
                    latencies.append(float(log_entry["data"]["latency_ms"]))
                
                if "usage" in log_entry["data"]:
                    stats["total_tokens"] += log_entry["data"]["usage"]["total_tokens"]
            
            elif log_entry["type"] == "tool_call":
                stats["tool_calls"][log_entry["tool_name"]] += 1
            
            elif log_entry["type"] == "error":
                stats["errors"][log_entry["error_type"]] += 1
    
    # 计算平均延迟
    if latencies:
        stats["avg_latency"] = sum(latencies) / len(latencies)
    
    return stats

# 使用示例
stats = analyze_logs("logs/weather_agent_json_20260608.jsonl")
print(json.dumps(stats, indent=2, ensure_ascii=False))
```

---

### 5.2 实时监控脚本

```python
import time
import json
from datetime import datetime

def monitor_logs(log_file, interval=5):
    """实时监控日志文件"""
    
    print(f"🔍 开始监控日志文件: {log_file}")
    print(f"📊 刷新间隔: {interval}秒")
    print("=" * 60)
    
    last_size = 0
    
    while True:
        try:
            current_size = os.path.getsize(log_file)
            
            if current_size > last_size:
                # 读取新增内容
                with open(log_file, 'r') as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                
                for line in new_lines:
                    log_entry = json.loads(line)
                    
                    # 实时显示关键事件
                    if log_entry["type"] == "error":
                        print(f"❌ [{log_entry['timestamp']}] {log_entry['error_type']}")
                    elif log_entry["type"] == "response":
                        latency = log_entry["data"].get("latency_ms", 0)
                        if latency > 3000:
                            print(f"⚠️  高延迟: {latency}ms")
                    elif log_entry["type"] == "request":
                        print(f"📡 [{log_entry['timestamp']}] 新请求")
                
                last_size = current_size
            
            time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n👋 停止监控")
            break
        except Exception as e:
            print(f"❌ 监控错误: {e}")
            time.sleep(interval)

# 使用
monitor_logs("logs/weather_agent_json_20260608.jsonl", interval=2)
```

---

## 六、生产环境最佳实践

### 6.1 日志配置清单

✅ **必须配置：**
- [x] 文件路径和命名规则
- [x] 日志级别（开发：DEBUG，生产：INFO）
- [x] 日志轮转策略
- [x] 编码格式（UTF-8）
- [x] 时间戳格式（ISO 8601）

✅ **推荐配置：**
- [x] 日志分类（API/Tool/Error等）
- [x] JSON格式化
- [x] 敏感信息过滤
- [x] 异步日志记录
- [x] 日志压缩归档

---

### 6.2 敏感信息处理

```python
def sanitize_for_logging(data):
    """清理敏感信息"""
    
    sensitive_fields = ['api_key', 'password', 'token', 'secret']
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                # 隐藏敏感字段
                sanitized[key] = "***HIDDEN***"
            else:
                sanitized[key] = sanitize_for_logging(value)
        return sanitized
    
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    
    else:
        return data

# 使用
request_data = {
    "model": "qwen-max",
    "api_key": "sk-1234567890abcdef",
    "messages": [...]
}

sanitized_data = sanitize_for_logging(request_data)
logger.log_request(sanitized_data)
```

---

### 6.3 性能优化

```python
import logging
from logging.handlers import QueueHandler, QueueListener
import queue

# 异步日志记录
log_queue = queue.Queue(maxsize=1000)
queue_handler = QueueHandler(log_queue)

# 文件处理器
file_handler = logging.FileHandler('agent.log')

# 启动监听器
listener = QueueListener(log_queue, file_handler)
listener.start()

# 记录器使用队列处理器
logger = logging.getLogger('agent')
logger.addHandler(queue_handler)
logger.setLevel(logging.INFO)

# 程序结束时关闭
# listener.stop()
```

---

## 七、完整示例：天气查询Agent的完整日志实现

### 7.1 完整代码结构

```python
# weather_agent_with_logging.py

import logging
import json
import os
import time
import dashscope
from dashscope import Generation
from datetime import datetime
from typing import Dict, Any, Optional

class CompleteWeatherAgent:
    """完整的天气查询Agent（带完整日志记录）"""
    
    def __init__(self, api_key: str, log_dir: str = "logs"):
        """
        初始化Agent
        
        Args:
            api_key: Dashscope API密钥
            log_dir: 日志目录
        """
        self.api_key = api_key
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 初始化各种日志记录器
        self.setup_loggers()
        
        # 配置API
        dashscope.api_key = api_key
        
        # 记录启动信息
        self.log_startup()
    
    def setup_loggers(self):
        """设置所有日志记录器"""
        
        # 1. 主日志记录器
        self.logger = logging.getLogger('weather_agent')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # 文件处理器
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'weather_agent_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 2. JSON日志记录器（用于分析）
        self.json_logger = logging.getLogger('weather_agent.json')
        self.json_logger.setLevel(logging.DEBUG)
        self.json_logger.handlers.clear()
        
        json_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'weather_agent_json_{datetime.now().strftime("%Y%m%d")}.jsonl'),
            encoding='utf-8'
        )
        json_handler.setFormatter(logging.Formatter('%(message)s'))
        self.json_logger.addHandler(json_handler)
        
        # 3. 错误日志记录器
        self.error_logger = logging.getLogger('weather_agent.error')
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.handlers.clear()
        
        error_handler = logging.FileHandler(
            os.path.join(self.log_dir, f'weather_agent_error_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
    
    def log_startup(self):
        """记录启动信息"""
        startup_info = {
            "timestamp": datetime.now().isoformat(),
            "event": "startup",
            "agent": "weather_agent",
            "version": "1.0.0",
            "api_key_configured": bool(self.api_key),
            "log_directory": self.log_dir
        }
        
        self.logger.info("🚀 WeatherAgent启动")
        self.json_logger.info(json.dumps(startup_info, ensure_ascii=False))
    
    def log_request(self, request_data: Dict[str, Any]):
        """记录API请求"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "data": request_data
        }
        
        self.logger.info(f"📡 API请求: {request_data.get('model', 'unknown')} - {request_data.get('question', '')[:50]}...")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_response(self, response_data: Dict[str, Any]):
        """记录API响应"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "data": response_data
        }
        
        self.logger.info(f"📤 API响应: {response_data.get('status_code', 'unknown')} - {response_data.get('latency_ms', 0):.2f}ms")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_tool_call(self, tool_name: str, arguments: Dict, result: Any):
        """记录工具调用"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "tool_call",
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        }
        
        self.logger.info(f"🔧 工具调用: {tool_name}")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_error(self, error_info: Dict[str, Any]):
        """记录错误"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "data": error_info
        }
        
        self.logger.error(f"❌ 错误: {error_info.get('error_type', 'Unknown')} - {error_info.get('error_message', '')}")
        self.error_logger.error(json.dumps(log_entry, ensure_ascii=False))
        self.json_logger.error(json.dumps(log_entry, ensure_ascii=False))
    
    def query_weather(self, question: str, thinking_enabled: bool = False) -> Optional[str]:
        """
        查询天气（带完整日志）
        
        Args:
            question: 用户问题
            thinking_enabled: 是否启用思考模式
            
        Returns:
            AI回复
        """
        request_id = f"req_{int(time.time() * 1000)}"
        
        try:
            # 记录请求开始
            self.logger.info(f"🔍 开始处理查询 [{request_id}]: {question}")
            
            # 构建请求配置
            extra_body = {
                "mcp": mcp_cfg
            }
            
            if thinking_enabled:
                extra_body["thinking"] = {
                    "enabled": True,
                    "budget": 1000
                }
                self.logger.info("🧠 思考模式已启用")
            
            # 记录请求
            self.log_request({
                "request_id": request_id,
                "question": question,
                "model": "qwen-max",
                "thinking_mode": thinking_enabled,
                "extra_body": extra_body
            })
            
            # 发起API调用
            start_time = time.time()
            resp = Generation.call(
                model="qwen-max",
                messages=[{"role": "user", "content": question}],
                extra_body=extra_body,
                tools=tools,
                result_format="message"
            )
            end_time = time.time()
            
            # 记录响应
            latency_ms = (end_time - start_time) * 1000
            self.log_response({
                "request_id": request_id,
                "status_code": resp.status_code,
                "request_id_dashscope": resp.request_id,
                "latency_ms": latency_ms,
                "usage": {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                    "total_tokens": resp.usage.total_tokens
                }
            })
            
            # 处理响应...
            choice = resp.output.choices[0]
            
            if choice.finish_reason == "tool_calls":
                # 工具调用场景
                tool_call = choice.message.tool_calls[0]
                tool_name = tool_call['function']['name']
                tool_args = json.loads(tool_call['function']['arguments'])
                
                # 记录工具调用
                self.log_tool_call(tool_name, tool_args, "pending")
                
                # 执行工具
                city = tool_args.get("city")
                weather_data = get_weather_data(city, client)
                
                # 记录工具结果
                self.log_tool_call(tool_name, tool_args, weather_data)
                
                # 第二轮API调用...
                messages_2 = [...]
                resp2 = Generation.call(model="qwen-max", messages=messages_2)
                final_reply = resp2.output.choices[0].message.content
                
                # 记录最终响应
                self.log_response({
                    "request_id": request_id,
                    "round": 2,
                    "final_answer": final_reply,
                    "complete": True
                })
                
                self.logger.info(f"✅ 查询完成 [{request_id}]")
                return final_reply
            
            else:
                # 直接回复场景
                direct_reply = choice.message.content
                self.log_response({
                    "request_id": request_id,
                    "direct_reply": direct_reply,
                    "no_tool_call": True
                })
                return direct_reply
        
        except Exception as e:
            # 记录错误
            error_info = {
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            self.log_error(error_info)
            return None


# 使用示例
if __name__ == "__main__":
    agent = CompleteWeatherAgent(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        log_dir="logs"
    )
    
    # 查询天气
    answer = agent.query_weather("南京今天天气怎么样？")
    print(f"答案: {answer}")
    
    # 使用思考模式
    answer = agent.query_weather(
        "分析未来一周南京的天气趋势，给出出行建议",
        thinking_enabled=True
    )
    print(f"答案: {answer}")
```

---

## 八、总结和检查清单

### 8.1 日志记录检查清单

#### ✅ 基础配置
- [x] 设置日志目录和文件命名规则
- [x] 配置日志级别（开发DEBUG，生产INFO）
- [x] 设置UTF-8编码
- [x] 配置日志轮转
- [x] 设置时间戳格式

#### ✅ 关键信息记录
- [x] API请求（model、messages、parameters）
- [x] API响应（status_code、latency、usage）
- [x] 工具调用（tool_name、arguments、result）
- [x] 错误信息（error_type、message、traceback）
- [x] 思考过程（thinking content、tokens）

#### ✅ 性能监控
- [x] 延迟记录（每次API调用）
- [x] Token使用统计
- [x] 错误率统计
- [x] 工具调用成功率

#### ✅ 安全和隐私
- [x] 过滤敏感信息（API密钥、密码）
- [x] 日志文件权限控制
- [x] 定期清理和归档

---

### 8.2 快速启动模板

```python
# 快速启动日志记录
from weather_agent_with_logging import CompleteWeatherAgent

# 1. 创建Agent
agent = CompleteWeatherAgent(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    log_dir="logs"
)

# 2. 查询（自动记录日志）
answer = agent.query_weather("南京今天天气怎么样？")

# 3. 查看日志
# 标准日志: logs/weather_agent_20260608.log
# JSON日志: logs/weather_agent_json_20260608.jsonl
# 错误日志: logs/weather_agent_error_20260608.log
```

---

## 📚 延伸阅读

### 相关工具和库
1. **Python logging模块** - 官方文档
2. **structlog** - 结构化日志库
3. **ELK Stack** - 日志分析平台
4. **Grafana Loki** - 轻量级日志聚合

### 最佳实践
1. **日志分层** - 按重要性和功能分类
2. **异步记录** - 提高性能
3. **JSON格式** - 便于分析
4. **定期清理** - 避免磁盘占满

---

**文档创建时间：** 2026-06-08  
**文档版本：** v1.0  
**适用场景：** AI Agent开发、调试、监控、分析

*本文档提供了AI Agent日志记录的完整实现方案，从基础配置到生产环境最佳实践。*
