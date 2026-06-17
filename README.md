# AI Chat Tool - 天气查询助手

一个基于阿里云百炼（Dashscope）和高德地图 API 的智能天气查询系统，支持 MCP 工具调用、流式输出、思考模式和多角色对话。
英文版README见README_EN.md (For English README, see README_EN.md)

## 项目概述

本项目是一个学习 LLM 集成和 AI Agent 开发的实习项目，展示了如何：
- 集成阿里云 Dashscope API (通义千问模型)
- 实现 MCP (Model Context Protocol) 工具调用
- 构建多轮对话系统
- 实现流式输出和思考模式
- 完整的日志记录和测试系统

## 功能特性

### 🎯 核心功能
- **智能天气查询**：基于高德地图 API 的实时天气信息
- **MCP 工具调用**：支持阿里云 MCP 和本地 MCP 服务器
- **流式输出**：实时显示 AI 响应过程
- **思考模式**：支持深度推理模式（thinking mode）
- **多角色系统**：天气预报员、程序员、妈妈等不同角色

### 🛠️ 技术特性
- 完整的对话历史管理
- 可视化日志系统（API 调用、工具调用、思考过程）
- 参数对比测试框架
- 自动化测试套件
- 温度参数实验工具

## 项目结构

```
ai-chat-tool/
├── src/                              # 源代码目录
│   ├── main.py                       # 主程序入口
│   ├── config_load.py                # 配置加载模块
│   ├── weather/                      # 天气查询模块
│   │   ├── weather_ali_mcp.py       # 阿里云 MCP 实现
│   │   ├── weather_amap_mcp.py      # 本地 MCP 实现
│   │   ├── weather_direct_api.py    # 直接 API 调用
│   │   └── weather_manual_amap_mcp.py  # 手动 JSON-RPC 实现
│   └── experiments/                  # 实验性代码
│       ├── cot_experiment.py        # CoT 实验
│       └── temperature_tester.py   # 温度测试工具
├── config.yaml                       # 配置文件
├── logs/                             # 日志目录
│   ├── production/                   # 生产环境日志
│   ├── temperature_tests/            # 温度测试日志
│   ├── testing/                      # 测试日志
│   ├── archived/                     # 历史归档日志
│   └── README.md                     # 日志说明文档
├── test/                             # 测试目录
│   ├── core/                         # 核心功能测试
│   ├── thinking_mode/                # 思考模式测试
│   ├── tool_calling/                 # 工具调用测试
│   ├── logging/                      # 日志系统测试
│   ├── debug/                        # 调试测试
│   ├── docs/                         # 测试文档
│   └── function_test.md              # 功能测试报告
├── CoT/                              # Chain of Thought 实验
│   └── experiments/                  # 实验数据
├── temperature/                       # 温度参数测试
│   └── *.md                          # 测试报告
├── paper/                            # 研究论文
├── develope_progress/                # 开发历史
├── four_questions/                   # 实验配置
├── README.md                         # 项目说明
└── README_EN.md                      # 英文版说明
```

## 快速开始

### 环境要求
- Python 3.13+
- Node.js 22+ (用于 MCP 服务器)
- 阿里云百炼 API Key
- 高德地图 API Key

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ai-chat-tool
```

2. **设置环境变量**
```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
export AMAP_API_KEY="your-amap-api-key"
```

建议将以上内容添加到 `~/.zshrc` 或 `~/.bashrc`

3. **安装依赖**
```bash
pip install dashscope pyyaml openai
npm install -g @amap/amap-maps-mcp-server
```

4. **运行程序**
```bash
# 方式 1：直接运行（从项目根目录）
python src/main.py

# 方式 2：使用模块运行
python -m src.main

# 方式 3：创建启动脚本
echo 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent)); from src.main import main; main()' > run.py
python run.py
```

## 使用指南

### 基本命令

启动后可使用以下命令：

| 命令 | 功能 |
|------|------|
| `/role` | 选择对话角色 |
| `/thinking` | 切换思考模式 |
| `/clear` | 清空对话历史 |
| `/clear N` | 保留最近 N 组对话 |
| `/clear -N` | 删除最远的 N 组对话 |
| `/help` | 显示帮助信息 |
| `/quit` | 退出程序 |

### 角色系统

支持 3 个预定义角色：
1. **天气预报员** - 专业准确，关注数据影响
2. **程序员** - 逻辑严密，技术思维
3. **妈妈** - 温柔体贴，关心健康

### 思考模式

输入 `/thinking` 进入思考模式菜单：
- `1` - 启用思考模式（深度推理，适合复杂问题）
- `2` - 关闭思考模式（快速回答，适合简单问题）
- `3` - 查看当前配置
- `4` - 返回主对话

## 配置说明

### config.yaml

主要配置项：

```yaml
api:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-max"  # 或 qwen3.7-max, qwen-plus

model_parameters:
  temperature: 0.7
  top_p: 1.0
  max_tokens: 20000

stream:
  enabled: true
  incremental_output: true

thinking:
  enabled: false
  budget: 1000
```

### 环境变量

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API 密钥 | [阿里云百炼控制台](https://bailian.console.aliyun.com/) |
| `AMAP_API_KEY` | 高德地图 API 密钥 | [高德开放平台](https://lbs.amap.com/) |

## 日志系统

### 日志位置

所有日志文件存储在 `logs/` 目录中。

### 日志组织

- **logs/production/** - 当前生产环境日志
- **logs/temperature_tests/** - 温度参数测试日志
- **logs/testing/** - 功能测试专用日志
- **logs/archived/** - 历史归档日志

### 日志类型

本系统实现 7 种专用日志：

1. **主日志** (`weather_agent_YYYYMMDD.log`)
   - 所有运行信息、调试消息

2. **JSON 日志** (`weather_agent_json_YYYYMMDD.jsonl`)
   - 机器可读的结构化日志（JSONL 格式）

3. **API 日志** (`*_api_*.log`)
   - HTTP 请求/响应、延迟、状态码

4. **工具日志** (`*_tool_*.log`)
   - MCP 工具调用、参数、执行结果

5. **思考日志** (`*_thinking_*.log`)
   - AI 推理过程、思考预算使用

6. **错误日志** (`*_error_*.log`)
   - 异常和错误追踪

7. **输出日志** (`*_outputs.log`)
   - 完整对话记录（用于温度参数对比）

### 查看最新日志

```bash
# 查看今天的日志
tail -f logs/production/weather_agent_$(date +%Y%m%d).log

# 查看今天的 JSON 日志
cat logs/production/weather_agent_json_$(date +%Y%m%d).jsonl

# 查看错误日志
tail -f logs/production/weather_agent_error_$(date +%Y%m%d).log
```

### 日志分析

详细日志说明请参阅：[日志目录 README](logs/README.md)

## 测试

### 运行功能测试
```bash
python test/function_test_automation.py
```

### 运行天气查询测试
```bash
python test/tool_calling/test_tool_calling_mcp_amap_integration.py
```

### 温度参数测试
```bash
python src/experiments/temperature_tester.py
```

查看测试报告：
- [功能测试报告](test/function_test.md)
- [工具调用对比](src/weather/tool_call_compare.md)
- [温度测试分析](temperature/temperature_analysis.md)

## 文档

### 技术文档
- [MCP 协议详解](test/docs/agent_logger_explanation.md)
- [流式输出算法](test/docs/stream_algorithm.md)
- [日志系统指南](test/docs/ai_agent_logging_guide.md)
- [配置文件说明](test/docs/config_guide.md)

### 开发文档
- [CoT 实验报告](CoT/CoT_test_report.md)
- [思考模式实现](CoT/think_mode/THINKING_MODE_IMPLEMENTATION.md)
- [API 输出日志指南](test/docs/AI_OUTPUT_LOG_GUIDE.md)

## 常见问题

### Q: 如何更换模型？
修改 `config.yaml` 中的 `api.model` 字段：
- `qwen-max` - 稳定版本（推荐）
- `qwen3.7-max` - 最新模型（可能有流式输出问题）
- `qwen-plus` - 轻量版本

### Q: MCP 服务器启动失败？
1. 检查 Node.js 版本：`node --version` (需要 22+)
2. 手动测试：`npx -y @amap/amap-maps-mcp-server`
3. 检查 `AMAP_API_KEY` 环境变量

### Q: 日志文件在哪里？
日志存储在 `logs/` 目录中，按照类型组织：
- `logs/production/` - 当前生产环境日志（最新日志）
- `logs/archived/` - 历史归档日志
- `logs/temperature_tests/` - 温度参数测试日志

详细说明请参阅：[日志目录 README](logs/README.md)

## 开发历程

本项目是 2 个月夏季实习项目的一部分：

**课程 1（第1个月）**：AI Chat Tool 开发
- LLM API 集成
- MCP 工具调用
- 配置管理系统
- 日志和参数调优

**课程 2（第2个月）**：Paper Retrieval Agent 开发
- Hermes Agent 部署
- Agent Skill 开发
- 微信集成
- PDF 报告生成

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/Tina-Wangchu/ai-chat-tool.git
- 作者：Tina Wang
- 完成时间：2025年6月

## 致谢

- 阿里云百炼平台提供 LLM API
- 高德地图提供天气数据 API
- MCP 协议规范参考 [Model Context Protocol](https://modelcontextprotocol.io/)

---


