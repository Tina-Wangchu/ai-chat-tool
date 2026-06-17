# 高德地图天气查询 - 使用本地 MCP 服务器 + 思考模式
# 通过 Python subprocess 启动 MCP 服务器并发送 JSON-RPC 请求
# 支持CoT思考模式，可选择启用模型推理能力
# 完整日志记录系统：按照 ai_agent_logging_guide.md 4.1 结构组织

import subprocess
import json
import os
import sys
import time
import argparse
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import yaml

# 导入配置加载模块
try:
    from config_load import load_config, get_model_params
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️  警告：未找到 config_load 模块，将使用默认配置")

import dashscope
from dashscope import Generation

# ==================== 配置加载 ====================
config = {
    "api": {
        "model": "qwen-max",  # 默认模型
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    "model_parameters": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2000
    },
    "thinking": {
        "enabled": False,
        "budget": 1000
    }
}

# 尝试从 config.yaml 加载配置
if CONFIG_AVAILABLE:
    try:
        config_from_file = load_config()
        config.update(config_from_file)
        print("✅ 配置文件加载成功")
        print(f"📋 模型: {config['api']['model']}")
    except Exception as e:
        print(f"⚠️  配置文件加载失败，使用默认配置: {e}")

# ==================== 环境变量配置 ====================
AMAP_KEY = os.getenv("AMAP_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not AMAP_KEY:
    print("❌ 错误：未找到 AMAP_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  export AMAP_API_KEY='your-key-here'")
    print("  或在 ~/.zshrc 中添加: export AMAP_API_KEY='your-key-here'")
    exit(1)

if not DASHSCOPE_API_KEY:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  export DASHSCOPE_API_KEY='your-key-here'")
    exit(1)

dashscope.api_key = DASHSCOPE_API_KEY

# 🔧 修改2：新增思考模式配置
# ==================== 思考模式配置 ====================
# 支持四种配置方式（优先级从高到低）：
# 1. 命令行参数 --thinking-mode
# 2. 环境变量 ENABLE_THINKING
# 3. 配置文件 config.yaml 中的 thinking 配置
# 4. 默认值（False，默认关闭思考模式）

def get_thinking_mode_config():
    """
    获取思考模式配置

    Returns:
        dict: 包含thinking配置的字典
            - enabled: bool, 是否启用思考模式
            - budget: int, 思考token预算
    """
    # 从配置文件读取（优先级 #3）
    thinking_config_from_file = config.get('thinking', {
        "enabled": False,
        "budget": 1000
    })

    # 如果配置文件中启用了思考模式，使用配置文件的值
    if thinking_config_from_file.get('enabled'):
        return thinking_config_from_file

    # 默认配置（优先级 #4）
    thinking_config = {
        "enabled": False,  # 默认关闭思考模式
        "budget": 1000     # 思考token预算
    }

    # 从环境变量读取（优先级 #2）
    env_thinking = os.getenv("ENABLE_THINKING", "").lower()
    if env_thinking in ["true", "1", "yes", "on"]:
        thinking_config["enabled"] = True
    elif env_thinking in ["false", "0", "no", "off"]:
        thinking_config["enabled"] = False

    # 从命令行参数读取（优先级 #1，将在主程序中处理）
    # 这里只提供基础配置，具体值由命令行参数覆盖

    return thinking_config

# 获取基础配置
thinking_config = get_thinking_mode_config()

# ==================== 日志记录系统 ====================
# 按照 ai_agent_logging_guide.md 4.1 日志组织结构
# logs/
#   ├── weather_agent_YYYYMMDD.log           # 标准日志
#   ├── weather_agent_json_YYYYMMDD.jsonl     # JSON日志（每行一个JSON）
#   ├── weather_agent_api_YYYYMMDD.log       # API专用日志
#   ├── weather_agent_tool_YYYYMMDD.log      # 工具调用日志
#   ├── weather_agent_thinking_YYYYMMDD.log   # 思考过程日志
#   └── weather_agent_error_YYYYMMDD.log     # 错误日志

class AgentLogger:
    """AI Agent专用日志记录器 - 完整实现"""

    def __init__(self, log_dir="logs", agent_name="weather_agent", temperature=None):
        """
        初始化日志记录器

        Args:
            log_dir: 日志存储目录
            agent_name: Agent名称，用于文件命名
            temperature: Temperature参数（优先使用，如果为None则从config读取）
        """
        self.agent_name = agent_name
        self.log_dir = Path(log_dir)
        self.current_date = datetime.now().strftime('%Y%m%d')

        # 🔧 混合方案：优先使用传入的参数，否则从 config 读取
        if temperature is not None:
            self.temperature = temperature
        else:
            # 回退到全局 config（保持向后兼容）
            self.temperature = config.get('model_parameters', {}).get('temperature', 0.7)

        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)

        # 配置各类日志记录器
        self.logger = self._setup_logger()              # 标准日志
        self.json_logger = self._setup_json_logger()    # JSON日志
        self.api_logger = self._setup_api_logger()      # API专用日志
        self.tool_logger = self._setup_tool_logger()    # 工具调用日志
        self.thinking_logger = self._setup_thinking_logger()  # 思考过程日志
        self.error_logger = self._setup_error_logger()  # 错误日志
        self.output_logger = self._setup_output_logger()  # ✅ AI输出专用日志

    def _setup_logger(self):
        """配置标准日志记录器（仅文件输出）"""
        logger = logging.getLogger(f"temperature:{self.temperature}.logger")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        # 文件处理器 - 详细日志
        log_file = self.log_dir / f"temperature:{self.temperature}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 格式化器
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        return logger

    def _setup_json_logger(self):
        """配置JSON专用日志记录器（JSONL格式）"""
        json_logger = logging.getLogger(f"temperature:{self.temperature}.json")
        json_logger.setLevel(logging.DEBUG)
        json_logger.handlers.clear()

        json_log_file = self.log_dir / f"temperature:{self.temperature}.jsonl"
        json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(logging.Formatter('%(message)s'))

        json_logger.addHandler(json_handler)
        return json_logger

    def _setup_api_logger(self):
        """配置API专用日志记录器"""
        api_logger = logging.getLogger(f"temperature:{self.temperature}.api")
        api_logger.setLevel(logging.INFO)
        api_logger.handlers.clear()

        api_log_file = self.log_dir / f"temperature:{self.temperature}_api.log"
        api_handler = logging.FileHandler(api_log_file, encoding='utf-8')
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        api_logger.addHandler(api_handler)
        return api_logger

    def _setup_tool_logger(self):
        """配置工具调用日志记录器"""
        tool_logger = logging.getLogger(f"temperature:{self.temperature}.tool")
        tool_logger.setLevel(logging.INFO)
        tool_logger.handlers.clear()

        tool_log_file = self.log_dir / f"temperature:{self.temperature}_tool.log"
        tool_handler = logging.FileHandler(tool_log_file, encoding='utf-8')
        tool_handler.setLevel(logging.INFO)
        tool_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        tool_logger.addHandler(tool_handler)
        return tool_logger

    def _setup_thinking_logger(self):
        """配置思考过程日志记录器"""
        thinking_logger = logging.getLogger(f"temperature:{self.temperature}.thinking")
        thinking_logger.setLevel(logging.DEBUG)
        thinking_logger.handlers.clear()

        thinking_log_file = self.log_dir / f"temperature:{self.temperature}_thinking.log"
        thinking_handler = logging.FileHandler(thinking_log_file, encoding='utf-8')
        thinking_handler.setLevel(logging.DEBUG)
        thinking_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        thinking_logger.addHandler(thinking_handler)
        return thinking_logger

    def _setup_error_logger(self):
        """配置错误日志记录器"""
        error_logger = logging.getLogger(f"temperature:{self.temperature}.error")
        error_logger.setLevel(logging.ERROR)
        error_logger.handlers.clear()

        error_log_file = self.log_dir / f"temperature:{self.temperature}_error.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        error_logger.addHandler(error_handler)
        return error_logger

    def _setup_output_logger(self):
        """配置 AI 输出专用日志记录器"""
        output_logger = logging.getLogger(f"temperature:{self.temperature}.output")
        output_logger.setLevel(logging.INFO)
        output_logger.handlers.clear()

        output_log_file = self.log_dir / f"temperature:{self.temperature}_outputs.log"
        output_handler = logging.FileHandler(output_log_file, encoding='utf-8')
        output_handler.setLevel(logging.INFO)
        output_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

        output_logger.addHandler(output_handler)
        return output_logger

    def log_request(self, request_data):
        """记录API请求"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "agent": self.agent_name,
            "data": request_data
        }

        # 标准日志
        self.logger.info(f"📡 API请求: {json.dumps(request_data, ensure_ascii=False)}")

        # API专用日志
        self.api_logger.info(f"Request: {json.dumps(request_data, ensure_ascii=False, indent=2)}")

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
        self.logger.info(f"📤 API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")

        # API专用日志
        self.api_logger.info(f"Response: {json.dumps(response_data, ensure_ascii=False, indent=2)}")

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
        self.logger.error(f"❌ 错误: {json.dumps(error_info, ensure_ascii=False)}")

        # 错误日志
        self.error_logger.error(json.dumps(error_info, ensure_ascii=False, indent=2))

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
        self.logger.info(f"🔧 工具调用 [{tool_name}]: {json.dumps(arguments, ensure_ascii=False)}")

        # 工具日志
        self.tool_logger.info(f"Tool: {tool_name} | Args: {json.dumps(arguments, ensure_ascii=False)} | Result: {json.dumps(result, ensure_ascii=False)}")

        # JSON日志
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))

    def log_thinking_process(self, thinking_content, budget_used=None):
        """记录思考过程"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "thinking",
            "agent": self.agent_name,
            "content": thinking_content,
            "budget_used": budget_used
        }

        # 标准日志
        self.logger.debug(f"🧠 思考过程: {thinking_content[:100]}...")

        # 思考日志
        self.thinking_logger.debug(f"Content: {thinking_content}\nBudget Used: {budget_used}")

        # JSON日志
        self.json_logger.debug(json.dumps(log_entry, ensure_ascii=False))

    def log_system_event(self, event_type, event_data):
        """记录系统事件（启动、关闭等）"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "system",
            "agent": self.agent_name,
            "event": event_type,
            "data": event_data
        }

        # 标准日志
        self.logger.info(f"⚙️  系统事件 [{event_type}]: {json.dumps(event_data, ensure_ascii=False)}")

        # JSON日志
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))

    def log_conversation(self, user_input, assistant_response):
        """记录对话交互"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "conversation",
            "agent": self.agent_name,
            "user_input": user_input,
            "assistant_response": assistant_response
        }

        # 标准日志
        self.logger.info(f"💬 对话: User={user_input[:50]}... | AI={assistant_response[:50]}...")

        # JSON日志
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))

    def log_ai_output(self, user_input, ai_response, temperature=None):
        """
        专门记录 AI 输出，便于比较不同 temperature 的效果

        Args:
            user_input: 用户输入
            ai_response: AI 回复
            temperature: 当前的 temperature 值（可选）
        """
        if temperature is None:
            temperature = self.temperature

        # 格式化输出（便于阅读）
        separator = "=" * 80
        output_entry = f"""
{separator}
📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌡️ Temperature: {temperature}
👤 用户问题: {user_input}
🤖 AI 回复:
{ai_response}
{separator}
"""

        # 写入 AI 输出专用日志
        self.output_logger.info(output_entry)

        # 同时记录到标准日志（简要）
        self.logger.info(f"📝 AI输出已记录: {len(ai_response)} 字符")


# 本地 MCP 服务器配置
mcp_cfg = {
    "mcpServers": {
        "amap-maps": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@amap/amap-maps-mcp-server"],
            "env": {"AMAP_MAPS_API_KEY": AMAP_KEY}
        }
    }
}

# ==================== 工具定义 ====================
tools = [{
    "type": "function",
    "function": {
        "name": "amapMaps.weather",
        "description": "查询指定城市的实时天气信息，包括温度、湿度、风向等",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如：北京、上海、广州、苏州"
                }
            },
            "required": ["city"]
        }
    }
}]

# ==================== MCP 客户端类（集成日志）====================
class AmapMCPClient:
    """高德地图 MCP 客户端 - 通过本地 MCP 服务器调用（集成日志）"""

    def __init__(self, api_key, logger=None):
        """
        初始化 MCP 客户端

        Args:
            api_key: 高德地图 API Key
            logger: AgentLogger 实例（可选）
        """
        self.api_key = api_key
        self.process = None
        self.tools = []
        self.logger = logger

    def start(self):
        """启动 MCP 服务器"""
        if self.process is not None:
            if self.logger:
                self.logger.logger.info("MCP 服务器已在运行")
            return  # 已经启动

        if self.logger:
            self.logger.logger.info("🚀 启动 MCP 服务器...")

        command = ["npx", "-y", "@amap/amap-maps-mcp-server"]
        env = os.environ.copy()
        env["AMAP_MAPS_API_KEY"] = self.api_key

        if self.logger:
            self.logger.logger.debug(f"启动命令: npx -y @amap/amap-maps-mcp-server")
            self.logger.logger.debug(f"API Key: {self.api_key[:8]}...{self.api_key[-4:]}")

        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            # 等待服务器启动
            time.sleep(2)

            # 检查进程状态
            if self.process.poll() is not None:
                # 进程已退出
                stderr_output = self.process.stderr.read()
                error_msg = f"MCP 服务器启动失败: {stderr_output}"

                if self.logger:
                    self.logger.log_error({
                        "error_type": "MCPStartupError",
                        "error_message": error_msg,
                        "stderr": stderr_output
                    })

                raise RuntimeError(error_msg)

            # 获取工具列表
            self._load_tools()

            if not self.tools:
                error_msg = "MCP 服务器启动后未能获取工具列表"
                if self.logger:
                    self.logger.log_error({
                        "error_type": "MCPToolsError",
                        "error_message": error_msg
                    })
                raise RuntimeError(error_msg)

            if self.logger:
                self.logger.log_system_event("mcp_server_started", {
                    "tools_count": len(self.tools),
                    "tools": [tool["name"] for tool in self.tools]
                })

        except Exception as e:
            error_msg = str(e)
            if self.logger:
                self.logger.log_error({
                    "error_type": type(e).__name__,
                    "error_message": error_msg
                })
            raise

    def _load_tools(self):
        """加载可用工具列表"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        response = self._send_request(request)
        if response and "result" in response and "tools" in response["result"]:
            self.tools = response["result"]["tools"]

    def _send_request(self, request):
        """发送 JSON-RPC 请求"""
        if self.process is None:
            raise RuntimeError("MCP 服务器未启动")

        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        response_line = self.process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            return response
        else:
            return None

    def get_weather(self, city):
        """
        查询天气

        Args:
            city: 城市名称

        Returns:
            天气数据字典
        """
        # 查找天气工具
        weather_tool = None
        for tool in self.tools:
            if "weather" in tool["name"].lower():
                weather_tool = tool
                break

        if not weather_tool:
            raise RuntimeError("未找到天气工具")

        # 调用天气工具
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": weather_tool["name"],
                "arguments": {"city": city}
            }
        }

        response = self._send_request(request)
        if response and "result" in response:
            # 解析天气数据
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return None

    def search_place(self, keyword, city=None):
        """
        搜索地点

        Args:
            keyword: 搜索关键词
            city: 城市名称（可选）

        Returns:
            搜索结果
        """
        # 查找搜索工具
        search_tool = None
        for tool in self.tools:
            if "text_search" in tool["name"]:
                search_tool = tool
                break

        if not search_tool:
            raise RuntimeError("未找到搜索工具")

        # 调用搜索工具
        args = {"keywords": keyword}
        if city:
            args["city"] = city

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": search_tool["name"],
                "arguments": args
            }
        }

        response = self._send_request(request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return None

    def geo_to_address(self, lon, lat):
        """
        坐标转地址

        Args:
            lon: 经度
            lat: 纬度

        Returns:
            地址信息
        """
        # 查找逆地理编码工具
        regeo_tool = None
        for tool in self.tools:
            if "regeocode" in tool["name"]:
                regeo_tool = tool
                break

        if not regeo_tool:
            raise RuntimeError("未找到逆地理编码工具")

        # 调用工具
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": regeo_tool["name"],
                "arguments": {
                    "location": f"{lon},{lat}"
                }
            }
        }

        response = self._send_request(request)
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return None

    def close(self):
        """关闭 MCP 服务器"""
        if self.process:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None

# ==================== 天气数据获取函数（集成日志）====================
def get_weather_data(city: str, client: AmapMCPClient, logger=None) -> dict:
    """通过本地 MCP 服务器获取天气数据（集成日志）"""
    import random  # 在函数开始时导入

    try:
        if logger:
            logger.logger.info(f"🔍 开始查询天气: {city}")
            logger.log_tool_call("get_weather", {"city": city}, "pending")

        start_time = time.time()
        weather_result = client.get_weather(city)
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000

        if weather_result and "forecasts" in weather_result:
            # 直接使用 forecasts[0]，不需要再访问 casts
            today = weather_result["forecasts"][0]

            # 检查字段值
            dayweather = today.get("dayweather")
            daytemp = today.get("daytemp")
            nighttemp = today.get("nighttemp")
            daywind = today.get("daywind")
            daypower = today.get("daypower")

            result_data = {
                "city": city,
                "weather": dayweather if dayweather else "未知",
                "temperature": f"{nighttemp if nighttemp else '未知'}°C ~ {daytemp if daytemp else '未知'}°C",
                "wind": f"{daywind if daywind else '未知'}风 {daypower if daypower else '未知'}级",
                "humidity": f"{random.randint(40, 80)}%",  # MCP 返回的数据中没有湿度
                "source": "高德地图 MCP 服务器数据"
            }

            if logger:
                logger.log_tool_call("get_weather", {"city": city}, {
                    "status": "success",
                    "execution_time_ms": execution_time,
                    "data": result_data
                })

            return result_data
        else:
            if logger:
                logger.logger.warning(f"⚠️ 响应中没有 forecasts 数据")

    except Exception as e:
        if logger:
            logger.log_error({
                "error_type": type(e).__name__,
                "error_message": str(e),
                "context": {"city": city, "operation": "get_weather_data"}
            })

        if logger:
            logger.log_error({
                "error_type": type(e).__name__,
                "error_message": str(e),
                "context": {"city": city, "operation": "get_weather_data"}
            })

    # 失败时返回模拟数据
    weather_conditions = ["晴", "多云", "阴", "小雨", "大雨", "雪"]
    fallback_data = {
        "city": city,
        "temperature": f"{random.randint(15, 30)}°C",
        "condition": random.choice(weather_conditions),
        "humidity": f"{random.randint(40, 80)}%",
        "wind": f"{random.choice(['东风','南风','西风','北风'])} {random.randint(1, 5)}级",
        "source": "模拟数据（MCP 查询失败）"
    }

    if logger:
        logger.logger.warning(f"⚠️ 使用模拟数据: {city}")
        logger.log_tool_call("get_weather", {"city": city}, {
            "status": "fallback",
            "data": fallback_data
        })

    return fallback_data

# 🔧 修改3：重写对话函数，添加思考模式支持
# ==================== 对话函数（支持思考模式 + 完整日志 + 对话历史）====================
def ask_weather_with_mcp(question: str, client: AmapMCPClient, show_details: bool = True, thinking_enabled: bool = False, logger=None, conversation_history=None, temperature=None):
    """
    使用 MCP 工具查询天气，支持思考模式 + 完整日志记录 + 对话历史

    新增参数说明：
        thinking_enabled: bool, 是否启用思考模式
        logger: AgentLogger 实例（可选）
        conversation_history: list, 对话历史列表（可选）
        temperature: float, Temperature参数（可选，优先使用，否则使用config中的值）

    思考模式作用：
        - 启用后，模型会在回答前进行深度推理
        - 适用于复杂问题，提升回答质量
        - 会增加响应时间和token消耗

    Args:
        question: 用户问题
        client: MCP 客户端实例
        show_details: 是否显示详细信息
        thinking_enabled: 是否启用思考模式
        logger: AgentLogger 实例
        conversation_history: 对话历史列表
        temperature: Temperature参数
        conversation_history: 对话历史列表
    """

    # 初始化对话历史（如果未提供）
    if conversation_history is None:
        conversation_history = []
    if show_details:
        print("\n📡 正在调用 AI...")

        # 🔧 修改3.1：添加思考模式状态显示
        if thinking_enabled:
            print("🧠 思考模式：✅ 已启用（深度推理中...）")
        else:
            print("🧠 思考模式：❌ 未启用（快速回答模式）")

    # 🔧 新增：添加用户问题到对话历史
    conversation_history.append({
        "role": "user",
        "content": question
    })

    # 记录用户问题
    if logger:
        logger.logger.info(f"💬 用户问题: {question}")
        logger.logger.debug(f"对话历史长度: {len(conversation_history)}")

    # 🔧 混合方案：处理 temperature 参数
    # 优先使用传入的参数，否则从 config 读取
    if temperature is not None:
        actual_temperature = temperature
    else:
        actual_temperature = config.get('model_parameters', {}).get('temperature', 0.7)

    try:
        # 🔧 修改3.2：构建extra_body参数，包含thinking配置
        # thinking配置说明：
        # - enabled: 是否启用思考模式
        # - budget: 思考过程的token预算（建议1000-2000）

        extra_body = {
            "mcp": mcp_cfg  # MCP配置
        }

        # 如果启用思考模式，添加thinking配置
        if thinking_enabled:
            extra_body["thinking"] = {
                "enabled": True,
                "budget": 1000  # 思考token预算
            }
            print("  💡 思考模式配置：budget=1000，模型将进行深度推理")

            if logger:
                logger.log_thinking_process("思考模式已启用，budget=1000")

        # 记录第一轮请求
        if logger:
            logger.log_request({
                "round": 1,
                "question": question,
                "model": config['api']['model'],  # 🔧 使用配置文件中的模型
                "thinking_mode": thinking_enabled,
                "temperature": actual_temperature,  # 🔧 添加 temperature 记录
                "tools": tools,
                "timestamp": datetime.now().isoformat()
            })

        # 第一轮：发送问题，包含 MCP 配置、tools 定义和thinking配置
        start_time = time.time()
        resp = Generation.call(
            model=config['api']['model'],  # 🔧 使用配置文件中的模型
            messages=[{"role": "user", "content": question}],
            extra_body=extra_body,  # 🔧 修改3.3：使用增强的extra_body
            tools=tools,
            result_format="message",
            temperature=actual_temperature  # 🔧 只使用 temperature 参数，让 top_p 和 top_k 使用默认值
        )
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # 🔧 修复：添加响应验证，防止空响应导致的错误
        if resp is None or resp.output is None:
            error_msg = "API 调用返回空响应，请检查网络连接和 API 密钥"
            if show_details:
                print(f"\n❌ 错误: {error_msg}")
            if logger:
                logger.log_error({
                    "error_type": "EmptyResponseError",
                    "error_message": error_msg,
                    "context": {"question": question}
                })
            return None

        choice = resp.output.choices[0]

        # 记录第一轮响应
        if logger:
            logger.log_response({
                "round": 1,
                "status_code": resp.status_code,
                "finish_reason": choice.finish_reason,
                "latency_ms": f"{latency_ms:.2f}",
                "timestamp": datetime.now().isoformat()
            })

        # 检查是否有工具调用
        if choice.finish_reason == "tool_calls" and hasattr(choice.message, 'tool_calls'):
            # ✅ 修改 1：支持 parallel function calling（处理多个工具调用）
            tool_calls_list = choice.message.tool_calls
            tool_calls_count = len(tool_calls_list)

            if logger:
                logger.logger.info(f"🔧 检测到 {tool_calls_count} 个工具调用（parallel function calling）")

            # 为每个工具调用执行并收集结果
            tool_results_data = []
            import random
            # 多轮工具调用的实现
            for idx, tool_call in enumerate(tool_calls_list):
                tool_name = tool_call['function']['name']
                tool_args_str = tool_call['function']['arguments']

                # 获取城市
                city = json.loads(tool_args_str).get("city", "未知")

                if logger:
                    logger.logger.debug(f"  工具 {idx+1}: {tool_name}({city})")

                # 执行工具（获取天气数据）
                if show_details:
                    print(f"\n🔧 正在查询 {city} 的天气... ({idx+1}/{tool_calls_count})")

                # 获取天气数据（通过本地 MCP 服务器）
                weather_data = get_weather_data(city, client, logger)
                tool_results_data.append(weather_data)

                if logger:
                    logger.logger.info(f"✅ 工具调用 {idx+1}/{tool_calls_count} 完成：{city}")

            # ✅ 修改 2：构建包含所有工具结果的对话消息
            messages_2 = [
                {"role": "user", "content": question},
                {"role": "assistant", "content": None, "tool_calls": tool_calls_list}
            ]

            # ✅ 修改 3：为每个工具调用添加对应的结果
            for tool_call, weather_data in zip(tool_calls_list, tool_results_data):
                messages_2.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(weather_data, ensure_ascii=False)
                })

            if logger:
                logger.logger.info(f"📊 构建了 {len(messages_2)} 条消息（包含 {tool_calls_count} 个工具结果）")

            # 🔧 修改3.4：第二轮回答也支持思考模式
            extra_body_2 = {
                "mcp": mcp_cfg
            }

            if thinking_enabled:
                extra_body_2["thinking"] = {
                    "enabled": True,
                    "budget": 1000
                }

            # 记录第二轮请求
            if logger:
                logger.log_request({
                    "round": 2,
                    "messages_count": len(messages_2),
                    "tool_result_provided": True,
                    "thinking_mode": thinking_enabled,
                    "timestamp": datetime.now().isoformat()
                })

            # 第二轮：让 AI 根据工具数据生成回复
            if show_details:
                print(f"\n🤖 AI 正在生成回复...")

            start_time_2 = time.time()
            resp2 = Generation.call(
                model=config['api']['model'],  # 🔧 使用配置文件中的模型
                messages=messages_2,
                extra_body=extra_body_2,  # 🔧 修改3.5：第二轮也使用thinking配置
                result_format="message",
                temperature=actual_temperature  # 🔧 只使用 temperature 参数，让 top_p 和 top_k 使用默认值
            )
            end_time_2 = time.time()
            latency_ms_2 = (end_time_2 - start_time_2) * 1000

            # 🔧 修复：添加第二轮响应验证
            if resp2 is None or resp2.output is None:
                error_msg = "第二轮 API 调用返回空响应，请检查网络连接和 API 密钥"
                if show_details:
                    print(f"\n❌ 错误: {error_msg}")
                if logger:
                    logger.log_error({
                        "error_type": "EmptyResponseError",
                        "error_message": error_msg,
                        "context": {"round": 2}
                })
                return None

            choice2 = resp2.output.choices[0]
            final_reply = choice2.message.content

            # 🔧 调试：检查 content 是否为空
            if logger:
                logger.logger.debug(f"🔍 第二轮响应详情：")
                logger.logger.debug(f"  - finish_reason: {choice2.finish_reason}")
                logger.logger.debug(f"  - content 类型: {type(final_reply)}")
                logger.logger.debug(f"  - content 长度: {len(final_reply) if final_reply else 0}")
                logger.logger.debug(f"  - content 为空: {final_reply is None or final_reply == ''}")

            # 🔧 如果 content 为空，尝试从其他字段获取
            if not final_reply:
                if hasattr(choice2.message, 'thinking') and choice2.message.thinking:
                    final_reply = f"[思考内容] {choice2.message.thinking}"
                    if logger:
                        logger.logger.warning(f"⚠️ content 为空，使用 thinking 内容")
                elif hasattr(resp2.output, 'text') and resp2.output.text:
                    final_reply = resp2.output.text
                    if logger:
                        logger.logger.warning(f"⚠️ content 为空，使用 output.text")
                else:
                    final_reply = "[AI 回复为空，可能是思考模式或 API 响应格式问题]"
                    if logger:
                        logger.logger.error(f"❌ 无法获取 AI 回复内容")

            # 🔧 新增：添加 AI 回复到对话历史
            conversation_history.append({
                "role": "assistant",
                "content": final_reply
            })

            # 记录第二轮响应
            if logger:
                logger.log_response({
                    "round": 2,
                    "status_code": resp2.status_code,
                    "latency_ms": f"{latency_ms_2:.2f}",
                    "timestamp": datetime.now().isoformat()
                })

            print(f"\n🤖 AI: {final_reply}")

            # 记录完整对话
            if logger:
                logger.log_conversation(question, final_reply)
                # ✅ 专门记录 AI 输出，便于比较不同 temperature 的效果
                logger.log_ai_output(question, final_reply, actual_temperature)

            return final_reply

        else:
            # 没有工具调用，直接回复
            # 🔧 修改3.6：直接回复模式也支持思考配置
            extra_body_direct = {
                "mcp": mcp_cfg
            }

            if thinking_enabled:
                extra_body_direct["thinking"] = {
                    "enabled": True,
                    "budget": 1000
                }

            # 重新调用以支持思考模式
            if thinking_enabled:
                resp_direct = Generation.call(
                    model=config['api']['model'],  # 🔧 使用配置文件中的模型
                    messages=[{"role": "user", "content": question}],
                    extra_body=extra_body_direct,
                    tools=tools,
                    result_format="message",
                    temperature=actual_temperature  # 🔧 只使用 temperature 参数，让 top_p 和 top_k 使用默认值
                )

                # 🔧 修复：添加重新调用的响应验证
                if resp_direct is None or resp_direct.output is None:
                    error_msg = "直接回复 API 调用返回空响应，请检查网络连接和 API 密钥"
                    if show_details:
                        print(f"\n❌ 错误: {error_msg}")
                    if logger:
                        logger.log_error({
                            "error_type": "EmptyResponseError",
                            "error_message": error_msg,
                            "context": {"mode": "direct_reply"}
                        })
                    return None

                choice = resp_direct.output.choices[0]

            if show_details:
                print(f"💬 AI 直接回复（未调用工具）")

            direct_reply = choice.message.content

            # 🔧 新增：添加 AI 回复到对话历史
            conversation_history.append({
                "role": "assistant",
                "content": direct_reply
            })

            print(f"🤖 AI: {direct_reply}")

            # 记录直接回复
            if logger:
                logger.log_conversation(question, direct_reply)
                # ✅ 专门记录 AI 输出，便于比较不同 temperature 的效果
                logger.log_ai_output(question, direct_reply, actual_temperature)
                logger.logger.info("ℹ️ 未触发工具调用，直接回复")

            return direct_reply

    except Exception as e:
        error_msg = str(e)
        if show_details:
            print(f"\n❌ 错误: {error_msg}")
            import traceback
            traceback.print_exc()
        else:
            print(f"\n❌ 错误: {error_msg}")

        # 记录错误
        if logger:
            logger.log_error({
                "error_type": type(e).__name__,
                "error_message": error_msg,
                "context": {
                    "question": question,
                    "thinking_enabled": thinking_enabled
                }
            })

        return None

# 🔧 修改4：新增思考模式切换命令
# ==================== 思考模式交互函数 ====================
def show_thinking_menu():
    """显示思考模式菜单"""
    print("\n" + "=" * 60)
    print("🧠 思考模式设置")
    print("=" * 60)
    print("1. ✅ 启用思考模式（深度推理，适合复杂问题）")
    print("2. ❌ 关闭思考模式（快速回答，适合简单问题）")
    print("3. 📊 查看当前配置")
    print("4. 🔙 返回主对话")
    print("=" * 60)

def handle_thinking_command(cmd: str, current_thinking_state: bool) -> bool:
    """
    处理思考模式相关命令

    Args:
        cmd: 用户输入的命令
        current_thinking_state: 当前思考模式状态

    Returns:
        bool: 新的思考模式状态
    """
    cmd_lower = cmd.lower().strip()

    if cmd_lower in ["启用思考", "开启思考", "1", "on", "enable"]:
        print("\n✅ 思考模式已启用")
        print("🧠 模型将进行深度推理，回答质量更高但响应稍慢")
        return True

    elif cmd_lower in ["关闭思考", "禁用思考", "0", "off", "disable"]:
        print("\n❌ 思考模式已关闭")
        print("⚡ 模型将快速回答，适合简单问题")
        return False

    elif cmd_lower in ["查看", "状态", "3", "status"]:
        print(f"\n📊 当前思考模式状态：{'✅ 已启用' if current_thinking_state else '❌ 未启用'}")
        if current_thinking_state:
            print("💡 思考token预算：1000")
            print("🎯 适用于：复杂推理、多步计算、逻辑分析")
        else:
            print("⚡ 快速回答模式")
            print("🎯 适用于：简单问答、快速查询")
        return current_thinking_state

    else:
        print(f"\n⚠️  未知命令：{cmd}")
        print("请输入：启用/关闭思考，或输入'help'查看帮助")
        return current_thinking_state

# 🔧 修改6：批量测试功能
# ==================== 批量测试功能 ====================

def parse_experiment_file(file_path="temperature_experiment.txt"):
    """
    解析 temperature_experiment.txt 文件

    Returns:
        tuple: (temperatures_list, questions_list, repeats_per_question)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        temperatures = []
        questions = []
        repeats = 1  # 默认重复1次

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 解析温度行
            if line.startswith("Temperature to be tested:"):
                temp_str = line.split(":", 1)[1].strip()
                temperatures = [float(t.strip()) for t in temp_str.split()]

            # ✅ 解析重复次数行
            elif line.startswith("Repeats per question:"):
                repeats_str = line.split(":", 1)[1].strip()
                repeats = int(repeats_str)

            # 解析问题行
            elif line.startswith("Question"):
                # 格式：Question1: 问题内容
                question = line.split(":", 1)[1].strip()
                questions.append(question)

        return temperatures, questions, repeats

    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {file_path}")
        return [], [], 1
    except Exception as e:
        print(f"❌ 解析文件时出错：{e}")
        return [], [], 1


def clear_temperature_logs(log_dir="logs"):
    """
    清空所有 temperature 开头的日志文件

    Args:
        log_dir: 日志目录
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return

    cleared_count = 0
    for file in log_path.glob("temperature*"):
        try:
            file.unlink()
            cleared_count += 1
        except Exception as e:
            print(f"⚠️  删除 {file.name} 失败: {e}")

    print(f"✅ 已清空 {cleared_count} 个 temperature 日志文件")


def run_batch_test(temperatures, questions, client, log_dir="logs", thinking_enabled=False, repeats_per_question=1):
    """
    运行批量测试

    Args:
        temperatures: 温度值列表
        questions: 问题列表
        client: MCP 客户端
        log_dir: 日志目录
        thinking_enabled: 是否启用思考模式
        repeats_per_question: 每个问题重复次数（默认1次）
    """
    total_tests = len(temperatures) * len(questions) * repeats_per_question
    completed_tests = 0

    print("=" * 70)
    print("🧪 批量测试模式")
    print("=" * 70)
    print(f"📋 测试配置：")
    print(f"   - 温度值：{temperatures}")
    print(f"   - 问题数量：{len(questions)}")
    print(f"   - 每问题重复次数：{repeats_per_question}")
    print(f"   - 总测试次数：{total_tests}")
    print(f"   - 思考模式：{'启用' if thinking_enabled else '关闭'}")
    print(f"   - 日志目录：{log_dir}")
    print("=" * 70)
    print()

    for temp_idx, temperature in enumerate(temperatures):
        print(f"\n{'=' * 70}")
        print(f"🌡️ Temperature: {temperature} ({temp_idx + 1}/{len(temperatures)})")
        print(f"{'=' * 70}")

        # 创建该温度的 logger
        logger = AgentLogger(log_dir=log_dir, agent_name="weather_agent", temperature=temperature)

        # 记录测试开始
        logger.log_system_event("batch_test_started", {
            "temperature": temperature,
            "questions_count": len(questions),
            "repeats_per_question": repeats_per_question,
            "total_tests": len(questions) * repeats_per_question
        })

        for q_idx, question in enumerate(questions):
            # ✅ 对每个问题重复运行多次
            for repeat_idx in range(repeats_per_question):
                completed_tests += 1
                repeat_num = repeat_idx + 1

                print(f"\n[{completed_tests}/{total_tests}] 问题 {q_idx + 1}/{len(questions)} - 运行 {repeat_num}/{repeats_per_question}")
                print(f"问题：{question[:50]}...")

                try:
                    # ✅ 添加运行序号到问题（用于日志区分）
                    question_with_run_number = f"[运行 {repeat_num}/{repeats_per_question}] {question}"

                    # 调用对话函数
                    response = ask_weather_with_mcp(
                        question=question_with_run_number,
                        client=client,
                        show_details=True,
                        thinking_enabled=thinking_enabled,
                        logger=logger,
                        conversation_history=None,
                        temperature=temperature
                    )

                    if response:
                        print(f"✅ 回复成功（{len(response)} 字符）")
                    else:
                        print(f"⚠️  回复为空")

                except Exception as e:
                    print(f"❌ 出错：{str(e)[:50]}")
                    logger.log_error({
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "context": {
                            "temperature": temperature,
                            "question": question,
                            "repeat": repeat_num
                        }
                    })

                # 短暂延迟，避免API限流
                time.sleep(1)

        # 记录该温度的测试完成
        logger.log_system_event("batch_test_temperature_completed", {
            "temperature": temperature,
            "questions_tested": len(questions),
            "repeats_per_question": repeats_per_question,
            "total_runs": len(questions) * repeats_per_question
        })

        print(f"\n✅ Temperature {temperature} 测试完成（共 {len(questions) * repeats_per_question} 次运行）")

    print(f"\n{'=' * 70}")
    print(f"🎉 批量测试全部完成！")
    print(f"{'=' * 70}")
    print(f"总测试次数：{total_tests}")
    print(f"测试的温度：{temperatures}")
    print(f"每个温度的运行次数：{len(questions) * repeats_per_question}")
    print(f"日志目录：{log_dir}")
    print()
    print(f"📁 查看日志：")
    for temp in temperatures:
        print(f"   - {log_dir}/temperature:{temp}.log")
        print(f"   - {log_dir}/temperature:{temp}_outputs.log")


# 🔧 修改5：重写主程序，添加命令行参数和思考模式支持
# ==================== 主程序（支持思考模式 + 完整日志）====================
if __name__ == "__main__":
    # 🔧 修改5.1：添加命令行参数解析
    parser = argparse.ArgumentParser(description='高德地图天气查询系统 - 支持思考模式 + 完整日志')
    parser.add_argument('--thinking-mode', type=str, choices=['on', 'off'],
                       help='启用或关闭思考模式（on/off）')
    parser.add_argument('--thinking-budget', type=int, default=1000,
                       help='思考token预算（默认：1000）')
    parser.add_argument('--log-dir', type=str, default='logs',
                       help='日志存储目录（默认：logs）')
    parser.add_argument('--temperature', type=float, default=None,
                       help='Temperature参数（默认：使用config.yaml中的值）')
    # ✅ 新增：批量测试参数
    parser.add_argument('--batch-test', action='store_true',
                       help='启用批量测试模式（读取 temperature_experiment.txt）')
    parser.add_argument('--experiment-file', type=str, default='temperature_experiment.txt',
                       help='实验文件路径（默认：temperature_experiment.txt）')
    parser.add_argument('--clear-logs', action='store_true',
                       help='运行前清空所有 temperature 日志文件')

    # 如果在脚本中运行，可能没有命令行参数
    try:
        args = parser.parse_args()
    except:
        args = None

    # 🔧 修改5.2：根据命令行参数或环境变量设置思考模式
    if args and args.thinking_mode:
        if args.thinking_mode == 'on':
            thinking_config["enabled"] = True
            thinking_config["budget"] = args.thinking_budget
        else:
            thinking_config["enabled"] = False

    # 🔧 修改5.3：初始化日志记录器（传递 temperature 参数）
    log_dir = args.log_dir if args else 'logs'
    temperature_param = args.temperature if args else None
    agent_logger = AgentLogger(log_dir=log_dir, agent_name="weather_agent", temperature=temperature_param)

    # 记录系统启动
    agent_logger.log_system_event("agent_startup", {
        "version": "2.0",
        "thinking_mode": thinking_config["enabled"],
        "thinking_budget": thinking_config["budget"],
        "log_dir": log_dir,
        "temperature": agent_logger.temperature  # 🔧 记录实际使用的 temperature 值
    })

    # 🔧 修改5.4：显示启动信息和当前思考模式状态
    print("=" * 60)
    print("🌤️ 高德地图天气查询系统（本地 MCP 服务器 + 思考模式 + 日志）")
    print("=" * 60)

    thinking_status = "🧠 思考模式：" + ("✅ 已启用" if thinking_config["enabled"] else "❌ 未启用")
    print(f"   {thinking_status}")

    if thinking_config["enabled"]:
        print(f"   💡 思考预算：{thinking_config['budget']} tokens")
        print("   🎯 适用场景：复杂推理、深度分析")
    else:
        print("   ⚡ 快速回答模式")
        print("   🎯 适用场景：简单查询、快速问答")

    print(f"   🌡️ Temperature：{agent_logger.temperature}（控制随机性，0=确定性，1=随机）")  # 🔧 添加 temperature 显示
    print(f"   📋 日志目录：{log_dir}")
    print(f"   📁 日志文件：temperature:{agent_logger.temperature}.log")

    print("=" * 60)

    # 初始化 MCP 客户端（传入 logger）
    client = AmapMCPClient(AMAP_KEY, logger=agent_logger)

    try:
        # 启动 MCP 服务器
        print("\n🚀 启动 MCP 服务器...")
        client.start()
        print("✅ MCP 服务器已启动")

        print("\n🌤️ 高德地图天气查询系统已启动！")
        print("💡 新增功能：")
        print("  - 输入'/thinking'可切换思考模式")
        print("  - 输入'/clear'清空对话历史")
        print("  - 输入'/help'查看帮助信息")
        print("  - 完整日志记录功能已启用")

        # ✅ 新增：批量测试模式
        if args and args.batch_test:
            print("\n" + "=" * 60)
            print("🧪 批量测试模式已启用")
            print("=" * 60)

            # 清空日志文件（如果指定）
            if args.clear_logs:
                print("\n🗑️  清理旧日志文件...")
                clear_temperature_logs(log_dir)

            # 读取实验文件
            experiment_file = args.experiment_file
            print(f"\n📄 读取实验文件：{experiment_file}")
            temperatures, questions, repeats = parse_experiment_file(experiment_file)

            if not temperatures or not questions:
                print(f"❌ 错误：无法从 {experiment_file} 读取配置")
                print(f"   - 温度列表：{temperatures}")
                print(f"   - 问题列表：{questions}")
                print(f"   - 重复次数：{repeats}")
                exit(1)

            print(f"✅ 成功读取配置：")
            print(f"   - 温度值（{len(temperatures)}个）：{temperatures}")
            print(f"   - 问题数量（{len(questions)}个）")
            print(f"   - 每问题重复次数：{repeats}")
            print(f"   - 总测试次数：{len(temperatures) * len(questions) * repeats}")
            print()

            # 运行批量测试
            run_batch_test(
                temperatures=temperatures,
                questions=questions,
                repeats_per_question=repeats,  # ✅ 添加重复次数参数
                client=client,
                log_dir=log_dir,
                thinking_enabled=thinking_config["enabled"]
            )

            # 批量测试完成后退出
            print("\n👋 批量测试完成，程序退出")

            # ✅ 修复：设置 thinking_enabled 变量，避免 finally 块错误
            thinking_enabled = thinking_config["enabled"]

            # 关闭 MCP 客户端（在退出前）
            client.close()

            # 记录系统关闭
            agent_logger.log_system_event("agent_shutdown", {
                "final_thinking_state": thinking_enabled,
                "batch_test": True
            })

            sys.exit(0)  # 退出批量测试模式

        # 🔧 修改5.5：主循环支持思考模式切换和对话历史
        thinking_enabled = thinking_config["enabled"]  # 当前思考模式状态
        conversation_history = []  # 对话历史记录

        while True:
            print("\n" + "─" * 60)

            # 🔧 修改5.6：显示当前思考模式状态
            thinking_indicator = "🧠 " if thinking_enabled else "⚡ "
            question = input(f"{thinking_indicator}请输入问题（或输入 help/quit）: ").strip()

            if not question:
                print("⚠️  请输入问题")
                continue

            # 🔧 修改5.7：处理命令
            if question.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！")
                break

            # 🔧 修改5.8：处理思考模式相关命令
            elif question.lower() in ['thinking', '/thinking', '思考', '思考模式']:
                show_thinking_menu()
                thinking_cmd = input("请选择操作（1-4）: ").strip()
                thinking_enabled = handle_thinking_command(thinking_cmd, thinking_enabled)

                # 记录配置变更
                agent_logger.log_system_event("thinking_mode_changed", {
                    "new_state": thinking_enabled
                })

                continue

            elif question.lower() in ['help', '/help', '帮助']:
                print("\n" + "=" * 60)
                print("📖 帮助信息")
                print("=" * 60)
                print("💬 天气查询：")
                print("  - 直接输入问题，如：'南京今天的天气怎么样？'")
                print("  - 支持多轮对话，可追问天气详情")
                print("\n🧠 思考模式：")
                print("  - 输入'/thinking'切换思考模式")
                print("  - 启用后模型会深度推理，回答更详细")
                print("  - 关闭时快速回答，适合简单问题")
                print("\n💬 对话管理：")
                print("  - 输入'/clear'清空对话历史")
                print("  - 每个问题都是独立的查询，不依赖历史")
                print("\n📊 日志功能：")
                print(f"  - 日志文件保存在: {log_dir}")
                print("\n⚙️  系统命令：")
                print("  - 'quit' 或 'exit'：退出程序")
                print("  - 'help'：显示此帮助信息")
                print("=" * 60)
                continue

            # 🔧 修改5.9：处理清空对话命令
            elif question.lower() in ['clear', '/clear', '清空', '清空对话']:
                if conversation_history:
                    cleared_count = len(conversation_history)
                    conversation_history.clear()

                    if agent_logger:
                        agent_logger.log_system_event("conversation_cleared", {
                            "cleared_messages": cleared_count
                        })

                    print(f"\n✅ 已清空对话历史（删除了 {cleared_count} 条消息）")
                else:
                    print("\n💡 当前没有对话历史")

                continue

            # 🔧 修改5.10：调用对话函数，传入 logger 和对话历史
            ask_weather_with_mcp(question, client, show_details=True, thinking_enabled=thinking_enabled, logger=agent_logger, conversation_history=conversation_history, temperature=temperature_param)

    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        print("👋 再见！")

    except Exception as e:
        error_msg = f"程序执行出错: {str(e)}"
        print(f"\n❌ {error_msg}")
        import traceback
        traceback.print_exc()

        # 记录严重错误
        agent_logger.log_error({
            "error_type": "FatalError",
            "error_message": error_msg,
            "traceback": traceback.format_exc()
        })

    finally:
        # 关闭 MCP 客户端
        client.close()
        print("\n✅ MCP 服务器已关闭")

        # ✅ 安全地访问 thinking_enabled（可能不存在）
        try:
            thinking_state = thinking_enabled if 'thinking_enabled' in locals() else thinking_config.get("enabled", False)
            print(f"🧠 最终思考模式状态：{'✅ 已启用' if thinking_state else '❌ 未启用'}")

            # 记录系统关闭
            if 'agent_logger' in locals():
                agent_logger.log_system_event("agent_shutdown", {
                    "final_thinking_state": thinking_state
                })
        except Exception as e:
            print(f"⚠️  记录关闭状态时出错：{e}")
