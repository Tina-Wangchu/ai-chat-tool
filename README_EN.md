# AI Chat Tool - Weather Query Assistant

An intelligent weather query system based on Alibaba Cloud Dashscope (通义千问) and Amap (高德地图) APIs, featuring MCP tool calling, streaming output, thinking mode, and multi-role conversations.

## Project Overview

This is a 2-month summer internship project focusing on learning LLM integration and AI Agent development. The project demonstrates how to:
- Integrate Alibaba Cloud Dashscope API (Qwen models)
- Implement MCP (Model Context Protocol) tool calling
- Build multi-turn conversation systems
- Implement streaming output and thinking mode
- Create comprehensive logging and testing frameworks

## Features

### 🎯 Core Features
- **Intelligent Weather Query**: Real-time weather information via Amap API
- **MCP Tool Calling**: Supports Alibaba Cloud MCP and local MCP servers
- **Streaming Output**: Real-time display of AI responses
- **Thinking Mode**: Deep reasoning mode support (thinking mode)
- **Multi-Role System**: Weather forecaster, programmer, mom, and more

### 🛠️ Technical Features
- Complete conversation history management
- Visual logging system (API calls, tool calls, thinking process)
- Parameter comparison testing framework
- Automated testing suite
- Temperature parameter experimentation tools

## Project Structure

```
ai-chat-tool/
├── main.py                           # Main program entry
├── config.yaml                       # Configuration file
├── config_load.py                    # Configuration loading module
├── weather/                          # Weather query module
│   ├── weather_ali_mcp.py           # Alibaba Cloud MCP implementation
│   ├── weather_amap_mcp.py          # Local MCP implementation
│   ├── weather_direct_api.py        # Direct API calls
│   ├── weather_manual_amap_mcp.py    # Manual JSON-RPC implementation
│   └── tool_call_compare.md         # Tool calling comparison docs
├── test/                             # Tests and documentation
│   ├── *.py                         # Various test scripts
│   ├── *.md                         # Technical documentation
│   └── function_test.md             # Function test report
├── CoT/                              # Chain of Thought experiments
│   ├── cot_experiment.py            # CoT experiment script
│   └── experiments/                  # Experiment result data
├── temperature_test/                 # Temperature parameter tests
│   ├── temperature_tester.py        # Temperature testing tool
│   └── *.md                         # Test reports and analysis
└── devleopment/                      # Development phase files
    └── *.py                         # Development example code
```

## Quick Start

### Requirements
- Python 3.13+
- Node.js 22+ (for MCP server)
- Alibaba Cloud Dashscope API Key
- Amap API Key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-chat-tool
```

2. **Set environment variables**
```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
export AMAP_API_KEY="your-amap-api-key"
```

Add the above to `~/.zshrc` or `~/.bashrc` for persistence.

3. **Install dependencies**
```bash
pip install dashscope pyyaml openai
npm install -g @amap/amap-maps-mcp-server
```

4. **Run the program**
```bash
python main.py
```

## Usage Guide

### Basic Commands

Available commands after startup:

| Command | Function |
|---------|----------|
| `/role` | Select conversation role |
| `/thinking` | Toggle thinking mode |
| `/clear` | Clear conversation history |
| `/clear N` | Keep last N conversation groups |
| `/clear -N` | Delete furthest N conversation groups |
| `/help` | Show help information |
| `/quit` | Exit program |

### Role System

Supports 3 predefined roles:
1. **Weather Forecaster** - Professional, accurate, focuses on data impact
2. **Programmer** - Logical, technical thinking
3. **Mom** - Gentle, caring, health-conscious

### Thinking Mode

Enter `/thinking` to access thinking mode menu:
- `1` - Enable thinking mode (deep reasoning, for complex questions)
- `2` - Disable thinking mode (fast response, for simple questions)
- `3` - View current configuration
- `4` - Return to main conversation

## Configuration

### config.yaml

Main configuration items:

```yaml
api:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-max"  # or qwen3.7-max, qwen-plus

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

### Environment Variables

| Variable | Description | How to Get |
|----------|-------------|------------|
| `DASHSCOPE_API_KEY` | Alibaba Cloud Dashscope API Key | [Dashscope Console](https://bailian.console.aliyun.com/) |
| `AMAP_API_KEY` | Amap API Key | [Amap Open Platform](https://lbs.amap.com/) |

## Testing

### Run Function Tests
```bash
python test/function_test_automation.py
```

### Run Weather Query Tests
```bash
python test/test_with_amap_key.py
```

### Temperature Parameter Tests
```bash
python temperature_test/temperature_tester.py
```

View test reports:
- [Function Test Report](test/function_test.md)
- [Tool Calling Comparison](weather/tool_call_compare.md)
- [Temperature Test Analysis](temperature_test/temperature_analysis.md)

## Documentation

### Technical Documents
- [MCP Protocol Explained](test/agent_logger_explanation.md)
- [Streaming Output Algorithm](test/stream_algorithm.md)
- [Logging System Guide](test/ai_agent_logging_guide.md)
- [Configuration Guide](test/config_guide.md)

### Development Documents
- [CoT Experiment Report](CoT/CoT_test_report.md)
- [Thinking Mode Implementation](CoT/think_mode/THINKING_MODE_IMPLEMENTATION.md)
- [API Output Log Guide](test/AI_OUTPUT_LOG_GUIDE.md)

## FAQ

### Q: How to change the model?
Modify the `api.model` field in `config.yaml`:
- `qwen-max` - Stable version (recommended)
- `qwen3.7-max` - Latest model (may have streaming issues)
- `qwen-plus` - Lightweight version

### Q: MCP server fails to start?
1. Check Node.js version: `node --version` (requires 22+)
2. Test manually: `npx -y @amap/amap-maps-mcp-server`
3. Check `AMAP_API_KEY` environment variable

### Q: Where are the log files?
Logs are stored in the `logs/` directory, including:
- `weather_agent_*.log` - Main logs
- `weather_agent_api_*.log` - API call logs
- `weather_agent_tool_*.log` - Tool call logs
- `weather_agent_thinking_*.log` - Thinking process logs

## Development History

This project is part of a 2-month summer internship program:

**Course 1 (Month 1)**: AI Chat Tool Development
- LLM API integration
- MCP tool calling
- Configuration management system
- Logging and parameter tuning

**Course 2 (Month 2)**: Paper Retrieval Agent Development
- Hermes Agent deployment
- Agent Skill development
- WeChat integration
- PDF report generation

## Architecture Overview

### Weather Query System (`ai-chat-tool/weather/`)

Four implementations demonstrating different MCP calling patterns:

| File | Architecture | Key Pattern |
|------|--------------|--------------|
| `weather_ali_mcp.py` | Python → Dashscope MCP (cloud) → Amap REST API | Cloud-hosted MCP, simplest integration |
| `weather_amap_mcp.py` | Python → Local MCP server (npx subprocess) → Amap REST API | Local MCP server with JSON-RPC over stdio |
| `weather_direct_api.py` | Python → Direct HTTP to Amap REST API | No MCP, pure HTTP requests |
| `weather_manual_amap_mcp.py` | Python → Manual JSON-RPC to local MCP server | Hand-crafted JSON-RPC protocol implementation |

All implementations support:
- Dashscope AI for intent recognition (extracting city name from user query)
- Multi-turn conversation with `while True` loop
- Both `DASHSCOPE_API_KEY` and `AMAP_API_KEY` environment variables
- Debugging output with emoji markers (🔍, 🌐, 📊, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Contact

- Project Repository: [GitHub Repository]
- Author: Tina Wang
- Completion Date: June 2025

## Acknowledgments

- Alibaba Cloud Dashscope Platform for LLM API
- Amap for weather data API
- MCP Protocol specification reference [Model Context Protocol](https://modelcontextprotocol.io/)

---

⚠️ **Note**: Do not hardcode API keys in code. Always use environment variables. Ensure no sensitive information is included before committing to GitHub.
