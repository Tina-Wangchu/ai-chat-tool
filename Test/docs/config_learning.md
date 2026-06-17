# 大模型 API 调用配置指南

本文档详细介绍调用大语言模型（LLM）API 时可用的配置参数及其语法。

---

## 目录

- [1. 配置文件格式对比](#1-配置文件格式对比)
- [2. API 基础配置](#2-api-基础配置)
- [3. 模型参数配置](#3-模型参数配置)
- [4. 流式输出配置](#4-流式输出配置)
- [5. 思考模式配置](#5-思考模式配置)
- [6. 消息格式配置](#6-消息格式配置)
- [7. 完整配置示例](#7-完整配置示例)
- [8. 代码实现](#8-代码实现)

---

## 1. 配置文件格式对比

### 1.1 JSON 格式

JSON（JavaScript Object Notation）是一种轻量级的数据交换格式。

**特点：**
- 语法严格，必须使用双引号
- 不支持注释
- 支持嵌套对象和数组
- 广泛用于 API 请求/响应

**示例配置（JSON）：**

```json
{
  "api": {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "${DASHSCOPE_API_KEY}",
    "model": "qwen3.6-plus"
  },
  "model_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000
  },
  "stream": {
    "enabled": true,
    "extra_body": {
      "enable_passage_insertion": false,
      "incremental_output": true
    }
  },
  "thinking": {
    "enabled": false,
    "budget": 0
  },
  "roles": {
    "default": "AI助手",
    "available": [
      {
        "id": "1",
        "name": "小学生",
        "system_prompt": "你是一个小学生，性格活泼可爱。"
      },
      {
        "id": "2",
        "name": "妈妈",
        "system_prompt": "你是一位温柔的妈妈。"
      },
      {
        "id": "3",
        "name": "AI助手",
        "system_prompt": "你是一个友好的AI助手。"
      }
    ]
  }
}
```

### 1.2 YAML 格式

YAML（YAML Ain't Markup Language）是一种人类友好的数据序列化标准。

**特点：**
- 语法简洁，使用缩进表示层级
- 支持注释（使用 `#`）
- 支持多行字符串（使用 `|`）
- 更易读易写

**示例配置（YAML）：**

```yaml
api:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_key: "${DASHSCOPE_API_KEY}"
  model: "qwen3.6-plus"

model_parameters:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 2000

stream:
  enabled: true
  extra_body:
    enable_passage_insertion: false
    incremental_output: true

thinking:
  enabled: false
  budget: 0

roles:
  default: "AI助手"
  available:
    - id: "1"
      name: "小学生"
      system_prompt: |
        你是一个小学生，性格活泼可爱。
        你会用孩子的视角看待问题。

    - id: "2"
      name: "妈妈"
      system_prompt: |
        你是一位温柔的妈妈，说话亲切温暖。

    - id: "3"
      name: "AI助手"
      system_prompt: |
        你是一个友好的AI助手，专业且有礼貌。
```

### 1.3 JSON vs YAML 对比

| 特性 | JSON | YAML |
|------|------|------|
| 语法严格性 | 严格（必须双引号） | 宽松（可省略引号） |
| 注释支持 | ❌ 不支持 | ✅ 支持 |
| 多行字符串 | 需要使用 `\n` | 使用 `\|` 或 `>` |
| 可读性 | 中等 | 高 |
| 写入难度 | 中等 | 低 |
| 解析速度 | 快 | 中等 |
| API 使用 | ✅ 广泛使用 | ⚠️ 较少使用 |

### 1.4 语法对比示例

**字符串定义：**

```json
// JSON
{
  "name": "AI助手",
  "description": "这是一个很长的描述\n可以包含换行符"
}
```

```yaml
# YAML
name: AI助手
description: |
  这是一个很长的描述
  可以包含换行
  更易读
```

**数组定义：**

```json
// JSON
{
  "roles": ["user", "assistant", "system"]
}
```

```yaml
# YAML
roles:
  - user
  - assistant
  - system
```

**嵌套对象：**

```json
// JSON
{
  "api": {
    "base_url": "https://api.example.com",
    "timeout": 30
  }
}
```

```yaml
# YAML
api:
  base_url: https://api.example.com
  timeout: 30
```

### 1.5 读取配置文件（Python）

**读取 JSON：**

```python
import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print(config['api']['model'])
```

**读取 YAML：**

```python
import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

print(config['api']['model'])
```

---

## 2. API 基础配置

### 1.1 `base_url` - API 基础地址

指定 API 服务的端点 URL。

```python
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

**常见地域配置：**

| 地域 | base_url |
|------|----------|
| 华北2（北京） | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 美国（弗吉尼亚） | `https://dashscope-us.aliyuncs.com/compatible-mode/v1` |
| 新加坡 | `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` |
| 德国（法兰克福） | `https://{WorkspaceId}.eu-central-1.maas.aliyuncs.com/compatible-mode/v1` |

### 1.2 `api_key` - API 密钥

用于身份认证的密钥。

```python
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxx"

# 推荐方式：从环境变量读取
import os
api_key = os.getenv("DASHSCOPE_API_KEY")
```

### 1.3 `model` - 模型名称

指定要使用的模型。

```python
model = "qwen3.6-plus"
```

**常用模型：**

| 模型名称 | 说明 |
|----------|------|
| `qwen3.6-plus` | 通义千问 3.6 Plus |
| `qwen-turbo` | 通义千问 Turbo |
| `qwen-max` | 通义千问 Max |

---

## 3. 模型参数配置

### 3.1 `temperature` - 温度参数

控制模型输出的随机性。**范围：0.0 ~ 2.0**

```python
temperature = 0.7
```

| 值 | 效果 | 适用场景 |
|----|------|----------|
| 0.0 | 完全确定性，相同输入总是相同输出 | 代码生成、精确答案 |
| 0.3 - 0.5 | 较保守，减少随机性 | 事实性问答、技术文档 |
| 0.7 - 0.9 | 平衡创造性和确定性（推荐） | 通用对话、写作辅助 |
| 1.0 - 1.5 | 较高随机性 | 创意写作、头脑风暴 |
| 1.5 - 2.0 | 高度随机，输出不可预测 | 实验性场景 |

### 3.2 `top_p` - 核采样（Top-P Sampling）

另一种控制随机性的方式，与 `temperature` 二选一使用。**范围：0.0 ~ 1.0**

```python
top_p = 0.9
```

- 值越小，输出越集中
- 值越大，输出越多样化
- 通常设置为 0.9

### 3.3 `max_tokens` - 最大输出长度

限制模型单次回复的最大 Token 数量。

```python
max_tokens = 2000
```

**注意事项：**
- 1 Token ≈ 0.75 个中文字符 ≈ 0.5 个英文单词
- 设置过短可能截断回复
- 设置过长会增加延迟和费用

### 3.4 `presence_penalty` - 存在惩罚

**范围：-2.0 ~ 2.0**

```python
presence_penalty = 0.0
```

- 正值：减少重复话题
- 负值：鼓励重复话题

### 3.5 `frequency_penalty` - 频率惩罚

**范围：-2.0 ~ 2.0**

```python
frequency_penalty = 0.0
```

- 正值：减少重复用词
- 负值：增加重复用词

---

## 4. 流式输出配置

### 4.1 `stream` - 流式输出开关

```python
stream = True  # 启用流式输出
```

| 值 | 效果 |
|----|------|
| `True` | 逐字符实时输出 |
| `False` | 等待完整回复后一次性输出 |

### 4.2 流式输出处理代码

```python
completion = client.chat.completions.create(
    model="qwen3.6-plus",
    messages=messages,
    stream=True  # 启用流式输出
)

for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
```

### 4.3 `extra_body` - 额外流式参数

用于优化流式输出体验。

```python
extra_body={
    "enable_passage_insertion": False,  # 禁用段落插入以减少缓冲
    "incremental_output": True           # 启用增量输出
}
```

---

## 5. 思考模式配置

### 5.1 思考模式概述

思考模式（Thinking Mode）让模型在回答前进行深度推理，适用于复杂任务。

### 5.2 `thinking` 参数

```python
extra_body={
    "thinking": {
        "enabled": True,    # 启用思考模式
        "budget": 1000      # 思考 Token 预算
    }
}
```

| 参数 | 说明 |
|------|------|
| `enabled` | 是否启用思考模式 |
| `budget` | 思考过程的 Token 数量限制 |

**注意事项：**
- 启用思考模式会增加响应时间
- 思考过程会消耗额外的 Token
- 适用于数学推理、逻辑分析等复杂任务

---

## 6. 消息格式配置

### 6.1 消息结构

```python
messages = [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户消息"},
    {"role": "assistant", "content": "助手回复"}
]
```

### 6.2 角色类型（role）

| 角色 | 说明 | 使用场景 |
|------|------|----------|
| `system` | 系统提示词 | 定义 AI 的行为和角色 |
| `user` | 用户消息 | 用户的输入 |
| `assistant` | 助手回复 | AI 的历史回复 |
| `tool` | 工具消息 | 工具调用结果（函数调用时使用） |

### 6.3 系统提示词示例

```python
system_prompt = """
你是一个友好的AI助手，具备以下特点：
- 回答专业、准确
- 语气有礼貌
- 遇到不确定的问题会主动说明
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "你好"}
]
```

---

## 7. 完整代码示例

### 7.1 基础调用（非流式）

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

completion = client.chat.completions.create(
    model="qwen3.6-plus",
    messages=[
        {"role": "system", "content": "你是一个友好的助手"},
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ],
    temperature=0.7,
    top_p=0.9,
    max_tokens=2000
)

print(completion.choices[0].message.content)
```

### 7.2 流式输出

```python
completion = client.chat.completions.create(
    model="qwen3.6-plus",
    messages=[
        {"role": "system", "content": "你是一个友好的助手"},
        {"role": "user", "content": "讲一个有趣的故事"}
    ],
    stream=True,
    extra_body={
        "enable_passage_insertion": False,
        "incremental_output": True
    }
)

for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
```

### 7.3 多轮对话

```python
messages = [
    {"role": "system", "content": "你是一个友好的助手"}
]

while True:
    user_input = input("\n用户: ")
    if user_input.lower() in ['quit', 'exit']:
        break

    messages.append({"role": "user", "content": user_input})

    completion = client.chat.completions.create(
        model="qwen3.6-plus",
        messages=messages,
        temperature=0.7
    )

    response = completion.choices[0].message.content
    print(f"助手: {response}")

    messages.append({"role": "assistant", "content": response})
```

### 7.4 读取配置文件（JSON & YAML）

**读取 JSON 配置：**

```python
import json
import os
from openai import OpenAI

# 读取 JSON 配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=config['api']['base_url']
)

# 调用模型
completion = client.chat.completions.create(
    model=config['api']['model'],
    messages=[
        {"role": "system", "content": config['roles']['available'][2]['system_prompt']},
        {"role": "user", "content": "你好"}
    ],
    temperature=config['model_parameters']['temperature'],
    max_tokens=config['model_parameters']['max_tokens'],
    stream=config['stream']['enabled']
)
```

**读取 YAML 配置：**

```python
import yaml
import os
from openai import OpenAI

# 读取 YAML 配置文件
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 创建客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=config['api']['base_url']
)

# 调用模型
completion = client.chat.completions.create(
    model=config['api']['model'],
    messages=[
        {"role": "system", "content": config['roles']['available'][2]['system_prompt']},
        {"role": "user", "content": "你好"}
    ],
    temperature=config['model_parameters']['temperature'],
    max_tokens=config['model_parameters']['max_tokens'],
    stream=config['stream']['enabled']
)
```

---

## 8. 完整配置示例（JSON & YAML）

### 8.1 完整 JSON 配置示例

```json
{
  "api": {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "${DASHSCOPE_API_KEY}",
    "model": "qwen3.6-plus"
  },
  "model_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0
  },
  "stream": {
    "enabled": true,
    "extra_body": {
      "enable_passage_insertion": false,
      "incremental_output": true
    }
  },
  "thinking": {
    "enabled": false,
    "budget": 0
  },
  "roles": {
    "default": "AI助手",
    "available": [
      {
        "id": "1",
        "name": "小学生",
        "description": "活泼可爱，充满童真",
        "system_prompt": "你是一个小学生，性格活泼可爱，说话简单直接。你会用孩子的视角看待问题，回答问题时会带上一些童真和好奇心。"
      },
      {
        "id": "2",
        "name": "妈妈",
        "description": "温柔亲切，充满关爱",
        "system_prompt": "你是一位温柔的妈妈，说话亲切温暖，总是关心对方。你会用妈妈的语气和视角来回应，给予关爱和建议。"
      },
      {
        "id": "3",
        "name": "AI助手",
        "description": "专业准确，有礼貌",
        "system_prompt": "你是一个友好的AI助手，擅长回答问题并提供帮助。你的回答专业、准确、有礼貌。"
      }
    ]
  },
  "conversation": {
    "message_count_warning_threshold": 50,
    "auto_select_role_on_start": true,
    "history_save_path": "./conversation_history/"
  },
  "security": {
    "enable_content_filter": true,
    "filter_level": "medium"
  },
  "debug": {
    "verbose": false,
    "log_requests": false,
    "log_path": "./logs/"
  }
}
```

**保存为 `config.json`**

### 8.2 完整 YAML 配置示例

```yaml
api:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_key: "${DASHSCOPE_API_KEY}"
  model: "qwen3.6-plus"

model_parameters:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 2000
  presence_penalty: 0.0
  frequency_penalty: 0.0

stream:
  enabled: true
  extra_body:
    enable_passage_insertion: false
    incremental_output: true

thinking:
  enabled: false
  budget: 0

roles:
  default: "AI助手"
  available:
    - id: "1"
      name: "小学生"
      description: "活泼可爱，充满童真"
      system_prompt: |
        你是一个小学生，性格活泼可爱，说话简单直接。
        你会用孩子的视角看待问题，回答问题时会带上一些童真和好奇心。

    - id: "2"
      name: "妈妈"
      description: "温柔亲切，充满关爱"
      system_prompt: |
        你是一位温柔的妈妈，说话亲切温暖，总是关心对方。
        你会用妈妈的语气和视角来回应，给予关爱和建议。

    - id: "3"
      name: "AI助手"
      description: "专业准确，有礼貌"
      system_prompt: |
        你是一个友好的AI助手，擅长回答问题并提供帮助。
        你的回答专业、准确、有礼貌。

conversation:
  message_count_warning_threshold: 50
  auto_select_role_on_start: true
  history_save_path: "./conversation_history/"

security:
  enable_content_filter: true
  filter_level: "medium"

debug:
  verbose: false
  log_requests: false
  log_path: "./logs/"
```

**保存为 `config.yaml`**

### 8.3 简化配置示例

**JSON 简化版：**

```json
{
  "api": {
    "model": "qwen3.6-plus"
  },
  "model_parameters": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "stream": {
    "enabled": true
  }
}
```

**YAML 简化版：**

```yaml
api:
  model: "qwen3.6-plus"

model_parameters:
  temperature: 0.7
  max_tokens: 2000

stream:
  enabled: true
```

### 8.4 消息配置示例

**单轮对话（JSON 格式）：**

```json
{
  "messages": [
    {"role": "system", "content": "你是一个友好的助手"},
    {"role": "user", "content": "你好"}
  ]
}
```

**单轮对话（YAML 格式）：**

```yaml
messages:
  - role: system
    content: "你是一个友好的助手"
  - role: user
    content: "你好"
```

**多轮对话（JSON 格式）：**

```json
{
  "messages": [
    {"role": "system", "content": "你是一个友好的助手"},
    {"role": "user", "content": "我叫小明"},
    {"role": "assistant", "content": "你好小明，很高兴认识你！"},
    {"role": "user", "content": "你还记得我的名字吗？"}
  ]
}
```

**多轮对话（YAML 格式）：**

```yaml
messages:
  - role: system
    content: "你是一个友好的助手"
  - role: user
    content: "我叫小明"
  - role: assistant
    content: "你好小明，很高兴认识你！"
  - role: user
    content: "你还记得我的名字吗？"
```

---

## 参数速查表

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | str | - | - | 模型名称 |
| `temperature` | float | 0.0 ~ 2.0 | - | 输出随机性 |
| `top_p` | float | 0.0 ~ 1.0 | - | 核采样 |
| `max_tokens` | int | 1 ~ 模型上限 | - | 最大输出长度 |
| `stream` | bool | true/false | false | 流式输出 |
| `presence_penalty` | float | -2.0 ~ 2.0 | 0 | 存在惩罚 |
| `frequency_penalty` | float | -2.0 ~ 2.0 | 0 | 频率惩罚 |

---

## 常见问题

### Q1: Temperature 和 Top-P 如何选择？

**推荐：** 二者选其一使用，通常使用 `temperature` 即可。

- 如果需要精确答案：`temperature=0.3`
- 如果需要创造性：`temperature=0.9`
- 如果需要平衡：`temperature=0.7`

### Q2: Max Tokens 设置多少合适？

根据场景调整：

| 场景 | 推荐值 |
|------|--------|
| 简短回答 | 100-500 |
| 一般对话 | 1000-2000 |
| 长篇写作 | 2000-4000 |

### Q3: 何时启用流式输出？

**推荐启用：**
- 交互式对话场景
- 长文本生成
- 需要实时反馈的用户体验

**不推荐启用：**
- 批量处理
- 后台任务
- 需要完整响应后再处理的场景

---

## 参考资源

- [阿里云百练文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [通义千问模型介绍](https:// tongyi.aliyun.com/qianwen/)
