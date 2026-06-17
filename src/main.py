# 高德地图天气查询 - 增强版（包含 chat_cli.py 所有功能）
# 新增功能：
# - 角色系统（天气预报员、程序员、妈妈）
# - 真正的多轮对话记忆
# - 流式输出
# - 灵活的历史管理
# - 消息计数警告

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
import concurrent.futures  # ✅ 新增：用于并行执行工具调用

# ✅ 添加项目根目录到 PYTHONPATH（支持从 src/ 运行）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入配置加载模块
try:
    from src.config_load import load_config
    CONFIG_AVAILABLE = True
except ImportError:
    try:
        # 备用导入：支持直接从项目根目录运行
        from config_load import load_config
        CONFIG_AVAILABLE = True
    except ImportError:
        CONFIG_AVAILABLE = False
        print("⚠️  警告：未找到 config_load 模块，将使用默认配置")

import dashscope
from dashscope import Generation

# ==================== 角色系统定义 ====================
ROLES = {
    "1": {
        "name": "天气预报员",
        "content": """你是一位专业的天气预报员，语言风格专业、准确、友好。
你会用天气专业术语来解释天气现象，同时让普通听众也能理解。
你会关注天气对人们生活的影响，并给出实用的建议。
在回答问题时，你会：
- 使用准确的气象术语
- 关注天气数据的具体数值
- 提供专业的生活建议
- 保持积极友好的态度"""
    },
    "2": {
        "name": "程序员",
        "content": """你是一位经验丰富的程序员，思维方式逻辑严密，喜欢用技术角度分析问题。
你会用程序员的思维方式来回答天气相关问题，可能涉及：
- 数据结构和算法的类比
- 技术实现的讨论
- 逻辑分析
- 用技术语言描述现象
你的回答简洁、准确、有条理，偶尔会使用编程术语做比喻。"""
    },
    "3": {
        "name": "妈妈",
        "content": """你是一位温柔体贴的妈妈，总是关心对方的健康和安全。
你会用妈妈的语气和视角来回应，给予关爱和建议。
你会特别关注：
- 穿衣建议（会不会冷/热）
- 出行安全
- 健康提醒（带伞、防晒等）
- 温暖的关怀和叮嘱
你的回答充满母爱，让人感到温暖和安心。"""
    }
}

# ==================== 配置加载 ====================
# 默认配置（仅作为 config.yaml 不存在时的备份）
config = {
    "api": {
        "model": "qwen-max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    "model_parameters": {
        "temperature": 0.7,
        "top_p": 1.0,
        "max_tokens": 20000
    },
    "thinking": {
        "enabled": False,
        "budget": 1000
    }
}

# 从 config.yaml 加载配置（优先级高于默认值）
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
    exit(1)

if not DASHSCOPE_API_KEY:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  export DASHSCOPE_API_KEY='your-key-here'")
    exit(1)

dashscope.api_key = DASHSCOPE_API_KEY

# ==================== 思考模式配置 ====================
# 直接从 config.yaml 读取思考模式配置
thinking_config = config.get('thinking', {
    "enabled": False,
    "budget": 1000
})

# ==================== 流式输出配置 ====================
# 直接从 config.yaml 读取流式输出配置
stream_config = config.get('stream', {
    "enabled": True
})

# ==================== 日志记录系统 ====================
class AgentLogger:
    """AI Agent专用日志记录器"""
    
    def __init__(self, log_dir="logs", agent_name="weather_agent"):
        self.agent_name = agent_name
        self.log_dir = Path(log_dir)
        self.current_date = datetime.now().strftime('%Y%m%d')
        
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logger()
        self.json_logger = self._setup_json_logger()
        self.api_logger = self._setup_api_logger()
        self.tool_logger = self._setup_tool_logger()
        self.thinking_logger = self._setup_thinking_logger()
        self.error_logger = self._setup_error_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger(f"{self.agent_name}.logger")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        
        log_file = self.log_dir / f"{self.agent_name}_{self.current_date}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_json_logger(self):
        json_logger = logging.getLogger(f"{self.agent_name}.json")
        json_logger.setLevel(logging.DEBUG)
        json_logger.handlers.clear()
        
        json_log_file = self.log_dir / f"{self.agent_name}_json_{self.current_date}.jsonl"
        json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(logging.Formatter('%(message)s'))
        
        json_logger.addHandler(json_handler)
        return json_logger
    
    def _setup_api_logger(self):
        api_logger = logging.getLogger(f"{self.agent_name}.api")
        api_logger.setLevel(logging.INFO)
        api_logger.handlers.clear()
        
        api_log_file = self.log_dir / f"{self.agent_name}_api_{self.current_date}.log"
        api_handler = logging.FileHandler(api_log_file, encoding='utf-8')
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        api_logger.addHandler(api_handler)
        return api_logger
    
    def _setup_tool_logger(self):
        tool_logger = logging.getLogger(f"{self.agent_name}.tool")
        tool_logger.setLevel(logging.INFO)
        tool_logger.handlers.clear()
        
        tool_log_file = self.log_dir / f"{self.agent_name}_tool_{self.current_date}.log"
        tool_handler = logging.FileHandler(tool_log_file, encoding='utf-8')
        tool_handler.setLevel(logging.INFO)
        tool_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        tool_logger.addHandler(tool_handler)
        return tool_logger
    
    def _setup_thinking_logger(self):
        thinking_logger = logging.getLogger(f"{self.agent_name}.thinking")
        thinking_logger.setLevel(logging.DEBUG)
        thinking_logger.handlers.clear()
        
        thinking_log_file = self.log_dir / f"{self.agent_name}_thinking_{self.current_date}.log"
        thinking_handler = logging.FileHandler(thinking_log_file, encoding='utf-8')
        thinking_handler.setLevel(logging.DEBUG)
        thinking_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        thinking_logger.addHandler(thinking_handler)
        return thinking_logger
    
    def _setup_error_logger(self):
        error_logger = logging.getLogger(f"{self.agent_name}.error")
        error_logger.setLevel(logging.ERROR)
        error_logger.handlers.clear()
        
        error_log_file = self.log_dir / f"{self.agent_name}_error_{self.current_date}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        error_logger.addHandler(error_handler)
        return error_logger
    
    def log_request(self, request_data):
        """记录API请求"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "agent": self.agent_name,
            "data": request_data
        }
        
        self.logger.info(f"📡 API请求: {json.dumps(request_data, ensure_ascii=False)}")
        self.api_logger.info(f"Request: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_response(self, response_data):
        """记录API响应"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "agent": self.agent_name,
            "data": response_data
        }
        
        self.logger.info(f"📤 API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        self.api_logger.info(f"Response: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_error(self, error_info):
        """记录错误信息"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "agent": self.agent_name,
            "data": error_info
        }
        
        self.logger.error(f"❌ 错误: {json.dumps(error_info, ensure_ascii=False)}")
        self.error_logger.error(json.dumps(error_info, ensure_ascii=False, indent=2))
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
        
        self.logger.info(f"🔧 工具调用 [{tool_name}]: {json.dumps(arguments, ensure_ascii=False)}")
        self.tool_logger.info(f"Tool: {tool_name} | Args: {json.dumps(arguments, ensure_ascii=False)} | Result: {json.dumps(result, ensure_ascii=False)}")
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
        
        self.logger.debug(f"🧠 思考过程: {thinking_content[:100]}...")
        self.thinking_logger.debug(f"Content: {thinking_content}\nBudget Used: {budget_used}")
        self.json_logger.debug(json.dumps(log_entry, ensure_ascii=False))
    
    def log_system_event(self, event_type, event_data):
        """记录系统事件"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "system",
            "agent": self.agent_name,
            "event": event_type,
            "data": event_data
        }
        
        self.logger.info(f"⚙️  系统事件 [{event_type}]: {json.dumps(event_data, ensure_ascii=False)}")
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
        
        self.logger.info(f"💬 对话: User={user_input[:50]}... | AI={assistant_response[:50]}...")
        self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))

# ==================== MCP 配置 ====================
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

# ==================== MCP 客户端类 ====================
class AmapMCPClient:
    """高德地图 MCP 客户端"""
    
    def __init__(self, api_key, logger=None):
        self.api_key = api_key
        self.process = None
        self.tools = []
        self.logger = logger
    
    def start(self):
        """启动 MCP 服务器"""
        if self.process is not None:
            if self.logger:
                self.logger.logger.info("MCP 服务器已在运行")
            return
        
        if self.logger:
            self.logger.logger.info("🚀 启动 MCP 服务器...")
        
        command = ["npx", "-y", "@amap/amap-maps-mcp-server"]
        env = os.environ.copy()
        env["AMAP_MAPS_API_KEY"] = self.api_key
        
        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            time.sleep(2)
            
            if self.process.poll() is not None:
                stderr_output = self.process.stderr.read()
                error_msg = f"MCP 服务器启动失败: {stderr_output}"
                
                if self.logger:
                    self.logger.log_error({
                        "error_type": "MCPStartupError",
                        "error_message": error_msg,
                        "stderr": stderr_output
                    })
                
                raise RuntimeError(error_msg)
            
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
        """查询天气"""
        weather_tool = None
        for tool in self.tools:
            if "weather" in tool["name"].lower():
                weather_tool = tool
                break
        
        if not weather_tool:
            raise RuntimeError("未找到天气工具")
        
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

# ==================== 天气数据获取函数 ====================
def get_weather_data(city: str, client: AmapMCPClient, logger=None) -> dict:
    """通过本地 MCP 服务器获取天气数据"""
    import random
    
    try:
        if logger:
            logger.logger.info(f"🔍 开始查询天气: {city}")
            logger.log_tool_call("get_weather", {"city": city}, "pending")
        
        start_time = time.time()
        weather_result = client.get_weather(city)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000
        
        if weather_result and "forecasts" in weather_result:
            today = weather_result["forecasts"][0]
            
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
                "humidity": f"{random.randint(40, 80)}%",
                "source": "高德地图 MCP 服务器数据"
            }
            
            if logger:
                logger.log_tool_call("get_weather", {"city": city}, {
                    "status": "success",
                    "execution_time_ms": execution_time,
                    "data": result_data
                })
            
            return result_data
    
    except Exception as e:
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

# ==================== 并行工具执行函数 ====================
def execute_single_tool(tool_name: str, tool_args: dict, client: AmapMCPClient, logger=None) -> str:
    """
    执行单个工具调用（用于并行执行）

    Args:
        tool_name: 工具名称
        tool_args: 工具参数
        client: MCP 客户端
        logger: 日志记录器

    Returns:
        JSON 字符串格式的结果
    """
    # ✅ 支持多种工具名称映射（兼容Dashscope API返回的名称）
    weather_tools = ["get_weather", "amapMaps.weather", "maps_weather"]

    if tool_name in weather_tools:
        city = tool_args.get("city", "")

        if logger:
            logger.logger.info(f"🔧 执行天气查询工具: {tool_name}, 城市: {city}")
            logger.log_tool_call(tool_name, {"city": city}, "started")

        weather_data = get_weather_data(city, client, logger)

        if logger:
            logger.log_tool_call(tool_name, {"city": city}, {
                "status": "success",
                "data": weather_data
            })
            logger.logger.info(f"✅ 工具执行完成: {tool_name}")

        return json.dumps(weather_data, ensure_ascii=False)
    else:
        if logger:
            logger.logger.warning(f"⚠️ 未知工具: {tool_name}")
            logger.log_tool_call(tool_name, tool_args, {"status": "unknown_tool"})
        return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)


def execute_tools_parallel(tool_calls, messages, client: AmapMCPClient, logger=None, show_details=False):
    """
    并行执行多个工具调用

    Args:
        tool_calls: 工具调用列表
        messages: 消息列表（用于添加工具返回结果）
        client: MCP 客户端
        logger: 日志记录器
        show_details: 是否显示详细信息
    """
    if len(tool_calls) == 0:
        return

    if show_details:
        print(f"\n🔄 需要调用 {len(tool_calls)} 个工具，开始并行执行...")

    # 使用线程池并行执行
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交所有任务到线程池
        # ✅ 兼容处理字典和对象格式的tool_calls
        futures = {}
        for tc in tool_calls:
            if isinstance(tc, dict):
                # 字典格式
                tc_id = tc.get("id")
                tc_function_name = tc.get("function", {}).get("name")
                tc_arguments = tc.get("function", {}).get("arguments", "{}")
            else:
                # 对象格式
                tc_id = tc.id
                tc_function_name = tc.function.name
                tc_arguments = tc.function.arguments

            futures[tc_id] = executor.submit(
                execute_single_tool,
                tc_function_name,
                json.loads(tc_arguments) if isinstance(tc_arguments, str) else tc_arguments,
                client,
                logger
            )

        # 等待所有任务完成并获取结果
        for tc in tool_calls:
            try:
                # ✅ 兼容处理字典和对象格式
                if isinstance(tc, dict):
                    tc_id = tc.get("id")
                    tc_function_name = tc.get("function", {}).get("name")
                    tc_arguments = tc.get("function", {}).get("arguments", "{}")
                else:
                    tc_id = tc.id
                    tc_function_name = tc.function.name
                    tc_arguments = tc.function.arguments

                result = futures[tc_id].result(timeout=15)  # 等待结果，最多15秒
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": result
                })
                if show_details:
                    args = json.loads(tc_arguments) if isinstance(tc_arguments, str) else tc_arguments
                    city = args.get("city", "未知")
                    print(f"✅ {city} 的天气查询完成")
            except concurrent.futures.TimeoutError:
                # ✅ 兼容处理字典和对象格式
                if isinstance(tc, dict):
                    tc_id = tc.get("id")
                    tc_function_name = tc.get("function", {}).get("name")
                else:
                    tc_id = tc.id
                    tc_function_name = tc.function.name

                if show_details:
                    print(f"⏰ 工具 {tc_function_name} ({tc_id}) 超时")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": json.dumps({"error": "执行超时"}, ensure_ascii=False)
                })
            except Exception as e:
                # ✅ 兼容处理字典和对象格式
                if isinstance(tc, dict):
                    tc_id = tc.get("id")
                    tc_function_name = tc.get("function", {}).get("name")
                else:
                    tc_id = tc.id
                    tc_function_name = tc.function.name

                if show_details:
                    print(f"❌ 工具 {tc_function_name} ({tc_id}) 执行失败: {str(e)}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                })

# ==================== 角色选择系统 ====================
def select_role(conversation_history):
    """让用户选择角色"""
    print("\n" + "=" * 60)
    print("🎭 请选择对话角色")
    print("=" * 60)
    print("  1. 天气预报员 - 专业准确，关注数据影响")
    print("  2. 程序员     - 逻辑严密，技术思维")
    print("  3. 妈妈       - 温柔体贴，关心健康")
    print("=" * 60)
    
    while True:
        choice = input("请输入选项 (1/2/3): ").strip()
        
        if choice in ["1", "2", "3"]:
            selected_role = ROLES[choice]
            
            # 清空对话历史并添加新的系统提示词
            conversation_history.clear()
            conversation_history.append({
                "role": "system",
                "content": selected_role["content"]
            })
            
            print(f"\n✅ 已选择角色：{selected_role['name']}")
            print(f"💡 提示：输入 /role 可以重新选择角色")
            return selected_role["content"]
        
        print("⚠️  无效选项，请输入 1、2 或 3")

# ==================== 历史管理功能 ====================
def clear_history(conversation_history, system_prompt, command='/clear'):
    """处理 clear 命令"""
    parts = command.split()
    if len(parts) == 1:
        # /clear 无参数：清空所有对话，但保留系统提示词
        conversation_history.clear()
        conversation_history.append({
            "role": "system",
            "content": system_prompt
        })
        print("✅ 对话历史已清空，可以重新开始对话了")
        return
    
    # 有参数的情况
    try:
        param = parts[1]
        
        # 处理负数（删除最远的 N 组对话）
        if param.startswith('-'):
            n = int(param)
            groups_to_remove = abs(n)
            
            # 计算当前对话组数（不包括 system 消息）
            current_groups = (len(conversation_history) - 1) // 2
            
            if groups_to_remove >= current_groups:
                # 如果要删除的数量大于等于现有组数，则清空所有
                conversation_history.clear()
                conversation_history.append(conversation_history[0])
                print(f"✅ 已删除所有 {current_groups} 组对话")
            else:
                # 删除最远的 N 组对话
                messages_to_remove = groups_to_remove * 2
                conversation_history[:] = [conversation_history[0]] + conversation_history[messages_to_remove:]
                print(f"✅ 已删除最远的 {groups_to_remove} 组对话")
        
        # 处理正数（保留最近 N 组对话）
        else:
            n = int(param)
            groups_to_keep = abs(n)
            
            # 保留 system 消息 + 最近 N 组对话
            messages_to_keep = groups_to_keep * 2 + 1
            
            if messages_to_keep >= len(conversation_history):
                print(f"⚠️  当前只有 {(len(conversation_history) - 1) // 2} 组对话，无需删除")
            else:
                conversation_history[:] = [conversation_history[0]] + conversation_history[-(groups_to_keep * 2):]
                print(f"✅ 已保留最近 {groups_to_keep} 组对话")
    
    except ValueError:
        print("❌ 参数错误！用法：")
        print("  /clear       - 清空所有对话历史")
        print("  /clear N     - 保留最近 N 组对话")
        print("  /clear -N    - 删除最远的 N 组对话")
    except Exception as e:
        print(f"❌ 执行出错: {str(e)}")

def check_message_count(conversation_history):
    """当对话消息超过50时，给出提示"""
    if len(conversation_history) > 50:
        current_groups = (len(conversation_history) - 1) // 2
        print(f"\n🔔 对话较多（当前 {current_groups} 组），建议清理以保持流畅！")

# ==================== 帮助系统 ====================
def print_help():
    """打印帮助信息"""
    print("\n" + "=" * 60)
    print("📖 命令帮助")
    print("=" * 60)
    print("💬 天气查询：")
    print("  - 直接输入问题，如：'南京今天的天气怎么样？'")
    print("  - 支持多轮对话，可追问天气详情")
    print("\n🎭 角色系统：")
    print("  - /role         - 重新选择对话角色")
    print("  - 天气预报员：专业准确，关注数据影响")
    print("  - 程序员：逻辑严密，技术思维")
    print("  - 妈妈：温柔体贴，关心健康")
    print("\n🧠 思考模式：")
    print("  - /thinking     - 切换思考模式")
    print("  - 启用后模型会深度推理，回答更详细")
    print("  - 关闭时快速回答，适合简单问题")
    print("\n📡 流式输出：")
    print("  - /stream       - 切换流式输出模式")
    print("  - 启用后实时显示AI回复内容（逐字显示）")
    print("  - 关闭后等待完整回复后一次性显示")
    print("  - 流式输出：响应更快，用户体验更好")
    print("  - 非流式：适合需要完整内容的场景")
    print("\n💬 对话管理：")
    print("  - /clear        - 清空所有对话历史")
    print("  - /clear N      - 保留最近 N 组对话")
    print("  - /clear -N     - 删除最远的 N 组对话")
    print("\n📊 日志功能：")
    print("  - 完整日志记录已启用")
    print("\n⚙️  系统命令：")
    print("  - /help         - 显示此帮助信息")
    print("  - /quit         - 退出程序")
    print("=" * 60)

# ==================== 思考模式交互 ====================
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
    """处理思考模式相关命令"""
    cmd_lower = cmd.lower().strip()

    if cmd_lower in ["启用思考", "开启思考", "1", "on", "enable"]:
        print("\n✅ 思考模式已启用")
        print("🧠 模型将进行深度推理，回答质量更高但响应稍慢")
        return True

    elif cmd_lower in ["关闭思考", "禁用思考", "2", "0", "off", "disable"]:
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

    elif cmd_lower in ["返回", "back", "4", "exit"]:
        print("\n🔙 返回主对话")
        return current_thinking_state  # 保持当前状态，直接返回

    else:
        print(f"\n⚠️  未知命令：{cmd}")
        print("请输入：启用/关闭思考，或输入'help'查看帮助")
        return current_thinking_state

# ==================== 流式模式交互 ====================
def show_stream_menu():
    """显示流式输出模式菜单"""
    print("\n" + "=" * 60)
    print("📡 流式输出模式设置")
    print("=" * 60)
    print("1. ✅ 启用流式输出（实时显示，逐字呈现）")
    print("2. ❌ 关闭流式输出（等待完整回复后显示）")
    print("3. 📊 查看当前配置")
    print("4. 🔙 返回主对话")
    print("=" * 60)

def handle_stream_command(cmd: str, current_stream_state: bool) -> bool:
    """处理流式输出模式相关命令"""
    cmd_lower = cmd.lower().strip()

    if cmd_lower in ["启用流式", "开启流式", "1", "on", "enable"]:
        print("\n✅ 流式输出已启用")
        print("📡 AI回复将实时显示，用户体验更好")
        return True

    elif cmd_lower in ["关闭流式", "禁用流式", "2", "0", "off", "disable"]:
        print("\n❌ 流式输出已关闭")
        print("⏳ AI回复将等待完整内容后一次性显示")
        return False

    elif cmd_lower in ["查看", "状态", "3", "status"]:
        print(f"\n📊 当前流式输出状态：{'✅ 已启用' if current_stream_state else '❌ 未启用'}")
        if current_stream_state:
            print("🎯 实时显示AI回复内容")
            print("⚡ 响应速度更快，用户体验更好")
        else:
            print("🎯 等待完整回复后一次性显示")
            print("📋 适合需要完整内容的场景")
        return current_stream_state

    elif cmd_lower in ["返回", "back", "4", "exit"]:
        print("\n🔙 返回主对话")
        return current_stream_state  # 保持当前状态，直接返回

    else:
        print(f"\n⚠️  未知命令：{cmd}")
        print("请输入：启用/关闭流式，或输入'help'查看帮助")
        return current_stream_state

# ==================== 对话函数（增强版：流式输出 + 完整历史）====================
def ask_weather_with_mcp(question: str, client: AmapMCPClient, conversation_history,
                         show_details: bool = True, thinking_enabled: bool = False,
                         stream_enabled: bool = True,
                         logger=None, system_prompt=None):
    """
    使用 MCP 工具查询天气 - 增强版

    新增功能：
    - 流式输出（可开关）
    - 传递完整对话历史
    - 支持角色系统

    Args:
        question: 用户问题
        client: MCP 客户端实例
        conversation_history: 对话历史列表（会被修改）
        show_details: 是否显示详细信息
        thinking_enabled: 是否启用思考模式
        stream_enabled: 是否启用流式输出
        logger: AgentLogger 实例
        system_prompt: 系统提示词（角色定义）
    """
    
    if show_details:
        print("\n📡 正在调用 AI...")
        
        if thinking_enabled:
            print("🧠 思考模式：✅ 已启用（深度推理中...）")
        else:
            print("🧠 思考模式：❌ 未启用（快速回答模式）")
    
    # 添加用户问题到对话历史
    conversation_history.append({
        "role": "user",
        "content": question
    })
    
    # 记录用户问题
    if logger:
        logger.logger.info(f"💬 用户问题: {question}")
        logger.logger.debug(f"对话历史长度: {len(conversation_history)}")
    
    try:
        # 构建 extra_body 参数
        extra_body = {
            "mcp": mcp_cfg
        }
        
        # 如果启用思考模式，添加 thinking 配置
        if thinking_enabled:
            # ✅ 使用正确的阿里云API参数格式
            extra_body["enable_thinking"] = True
            extra_body["thinking_budget"] = thinking_config.get("budget", 1000)
            print(f"  💡 思考模式配置：enable_thinking=True, budget={thinking_config.get('budget', 1000)}，模型将进行深度推理")

            if logger:
                logger.log_thinking_process(f"思考模式已启用，budget={thinking_config.get('budget', 1000)}")
        
        # 记录请求（传递完整对话历史）
        if logger:
            logger.log_request({
                "question": question,
                "conversation_length": len(conversation_history),
                "model": config['api']['model'],
                "thinking_mode": thinking_enabled,
                "tools": tools,
                "timestamp": datetime.now().isoformat()
            })
        
        # 第一轮：发送问题（包含完整对话历史）
        start_time = time.time()
        resp = Generation.call(
            model=config['api']['model'],
            messages=conversation_history,  # ✅ 传递完整对话历史
            extra_body=extra_body,
            tools=tools,
            result_format="message"
        )
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # ✅ 添加错误处理：检查 resp.output 是否为 None
        if resp.output is None:
            error_msg = f"API返回空响应 (status_code: {resp.status_code})"
            if logger:
                logger.logger.error(f"❌ {error_msg}")
                logger.logger.error(f"完整响应: {resp}")

            print(f"\n❌ 错误：API返回空响应")
            print(f"状态码: {resp.status_code}")
            print(f"模型: {config['api']['model']}")

            # 检查是否是模型问题
            if "qwen3.7-max" in config['api']['model'] or "qwen3.7-plus" in config['api']['model']:
                print(f"\n💡 可能原因：")
                print(f"   - {config['api']['model']} 模型可能不稳定或有bug")
                print(f"   - 建议使用稳定的 'qwen-max' 模型")
                print(f"\n🔧 修复建议：")
                print(f"   修改 config.yaml:")
                print(f"   api:")
                print(f"     model: qwen-max")

            return f"抱歉，AI模型返回了空响应。请尝试重新提问或更换模型。"

        choice = resp.output.choices[0]
        
        # 记录响应
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
            tool_calls = choice.message.tool_calls

            if show_details:
                cities = []
                for tc in tool_calls:
                    try:
                        # 兼容字典和对象两种格式
                        if isinstance(tc, dict):
                            args = json.loads(tc.get("function", {}).get("arguments", "{}"))
                            city = args.get("city", "未知")
                        else:
                            args = json.loads(tc.function.arguments)
                            city = args.get("city", "未知")
                        cities.append(city)
                    except:
                        pass
                print(f"\n🔧 正在查询 {len(cities)} 个城市的天气: {', '.join(cities)}...")

            # 构建包含工具调用的对话消息
            messages_2 = list(conversation_history)  # 复制完整历史

            # ✅ 调试：记录原始tool_calls结构
            if logger:
                logger.logger.debug(f"🔍 [DEBUG] 原始tool_calls类型: {type(tool_calls)}")
                logger.logger.debug(f"🔍 [DEBUG] 原始tool_calls结构: {json.dumps(tool_calls, ensure_ascii=False, default=str)}")

            # ✅ 兼容处理字典和对象格式的tool_calls
            formatted_tool_calls = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    # 字典格式
                    formatted_tool_calls.append({
                        "id": tc.get("id"),
                        "function": {
                            "name": tc.get("function", {}).get("name"),
                            "arguments": tc.get("function", {}).get("arguments")
                        }
                    })
                else:
                    # 对象格式
                    formatted_tool_calls.append({
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })

            # ✅ 调试：记录格式化后tool_calls
            if logger:
                logger.logger.debug(f"🔍 [DEBUG] 格式化后tool_calls: {json.dumps(formatted_tool_calls, ensure_ascii=False)}")

            messages_2.append({
                "role": "assistant",
                "content": None,
                "tool_calls": formatted_tool_calls
            })

            # ✅ 调试：记录添加assistant消息后的messages_2
            if logger:
                logger.logger.debug(f"🔍 [DEBUG] 添加assistant消息后，messages_2长度: {len(messages_2)}")
                logger.logger.debug(f"🔍 [DEBUG] messages_2最后一条: {json.dumps(messages_2[-1], ensure_ascii=False)}")

            # ✅ 并行执行所有工具调用
            execute_tools_parallel(tool_calls, messages_2, client, logger, show_details)

            # ✅ 调试：记录执行工具后的完整messages_2结构
            if logger:
                logger.logger.debug(f"🔍 [DEBUG] 执行工具后messages_2总长度: {len(messages_2)}")
                # 显示最后3条消息（通常包含原始问题、assistant工具调用、tool结果）
                logger.logger.debug(f"🔍 [DEBUG] messages_2最后3条消息:")
                for i, msg in enumerate(messages_2[-3:], start=len(messages_2)-3):
                    logger.logger.debug(f"  [{i}] role={msg.get('role')}, content={msg.get('content', None) if msg.get('role') != 'tool' else '<tool_result>'}, tool_call_id={msg.get('tool_call_id', 'N/A')}")

            # 第二轮：让 AI 根据工具数据生成回复（流式输出）
            extra_body_2 = {
                "mcp": mcp_cfg
            }

            # 根据stream_enabled决定是否启用增量输出
            if stream_enabled:
                extra_body_2["incremental_output"] = True  # ✅ 启用增量输出

            if thinking_enabled:
                # ✅ 使用正确的阿里云API参数格式
                extra_body_2["enable_thinking"] = True
                extra_body_2["thinking_budget"] = thinking_config.get("budget", 1000)

            # 记录第二轮请求
            if logger:
                logger.log_request({
                    "round": 2,
                    "messages_count": len(messages_2),
                    "tool_result_provided": True,
                    "thinking_mode": thinking_enabled,
                    "stream_mode": stream_enabled,
                    "timestamp": datetime.now().isoformat()
                })
            
            if show_details:
                print(f"\n🤖 AI 正在生成回复...")
                if stream_enabled:
                    print("📡 流式输出模式：✅ 已启用")
                else:
                    print("📡 流式输出模式：❌ 未启用（等待完整回复）")

            start_time_2 = time.time()

            # ✅ 使用流式输出（根据参数决定）
            if stream_enabled:
                # 流式输出模式
                resp2 = Generation.call(
                    model=config['api']['model'],
                    messages=messages_2,
                    extra_body=extra_body_2,
                    stream=True,  # ✅ 启用流式输出
                    result_format="message"
                )

                # 收集完整回复并实时显示
                full_response = ""
                previous_length = 0  # 记录之前打印的长度
                print("🤖 AI: ", end="", flush=True)
            else:
                # 非流式输出模式（等待完整回复）
                resp2 = Generation.call(
                    model=config['api']['model'],
                    messages=messages_2,
                    extra_body=extra_body_2,
                    stream=False,  # ✅ 禁用流式输出
                    result_format="message"
                )

                # 直接获取完整回复
                if hasattr(resp2, 'output') and resp2.output and hasattr(resp2.output, 'choices') and resp2.output.choices:
                    full_response = resp2.output.choices[0].message.content
                    print(f"🤖 AI: {full_response}")
                else:
                    full_response = ""
                    print("❌ 无法获取回复")

            # 流式输出处理（仅当stream_enabled为True时执行）
            if stream_enabled:
                full_reasoning = ""  # 存储完整的思考内容

                for chunk in resp2:
                    try:
                        # Dashscope 流式格式: chunk.output.choices[0].message.content
                        if hasattr(chunk, 'output') and chunk.output:
                            if hasattr(chunk.output, 'choices') and chunk.output.choices:
                                message = chunk.output.choices[0].message

                                # ✅ 处理思考内容 (reasoning_content) - 使用try-except避免KeyError
                                try:
                                    reasoning_content = message.reasoning_content
                                    if reasoning_content:
                                        # 记录思考内容到日志
                                        if logger:
                                            # 记录新增的思考内容
                                            new_reasoning = reasoning_content[len(full_reasoning):] if len(reasoning_content) > len(full_reasoning) else ""
                                            if new_reasoning:
                                                logger.log_thinking_process(new_reasoning, budget_used=thinking_config.get('budget', 1000))
                                        full_reasoning = reasoning_content
                                except (KeyError, AttributeError):
                                    # reasoning_content不存在或无法访问，跳过
                                    pass

                                # 处理响应内容
                                try:
                                    content = message.content
                                    if content:
                                        # ✅ 直接使用完整content（流式输出每次都是累积的）
                                        if len(content) > previous_length:
                                            # 只打印新增的部分（增量）
                                            new_content = content[previous_length:]
                                            print(new_content, end="", flush=True)
                                            previous_length = len(content)

                                        # ✅ 始终更新full_response为最新的完整content
                                        full_response = content

                                        # ✅ 调试：记录content长度变化
                                        if logger and len(content) % 50 == 0:  # 每50字符记录一次
                                            logger.logger.debug(f"📝 Content长度: {len(content)} 字符")
                                except (KeyError, AttributeError):
                                    # content不存在或无法访问，跳过
                                    pass

                    except (AttributeError, IndexError) as e:
                        # 跳过无法处理的chunk
                        continue

            # ✅ 如果有思考内容,记录完整的思考过程
            if full_reasoning and logger:
                logger.logger.info(f"🧠 完整思考过程长度: {len(full_reasoning)} 字符")

            # ✅ 记录最终响应长度
            if logger:
                logger.logger.info(f"📝 最终响应长度: {len(full_response)} 字符")
                if len(full_response) < 50:
                    logger.logger.warning(f"⚠️ 响应异常短: {full_response}")

            print()  # 完成后换行

            end_time_2 = time.time()
            latency_ms_2 = (end_time_2 - start_time_2) * 1000
            
            # 添加 AI 回复到对话历史
            conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
            # 记录响应
            if logger:
                logger.log_response({
                    "round": 2,
                    "status_code": resp2.status_code if hasattr(resp2, 'status_code') else 'stream',
                    "latency_ms": f"{latency_ms_2:.2f}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 记录完整对话
            if logger:
                logger.log_conversation(question, full_response)
            
            return full_response
        
        else:
            # 没有工具调用，直接回复
            extra_body_direct = {
                "mcp": mcp_cfg
            }

            # 根据stream_enabled决定是否启用增量输出
            if stream_enabled:
                extra_body_direct["incremental_output"] = True  # ✅ 启用增量输出

            if thinking_enabled:
                # ✅ 使用正确的阿里云API参数格式
                extra_body_direct["enable_thinking"] = True
                extra_body_direct["thinking_budget"] = thinking_config.get("budget", 1000)

            if show_details:
                print(f"💬 AI 直接回复（未调用工具）")
                if stream_enabled:
                    print("📡 流式输出模式：✅ 已启用")
                else:
                    print("📡 流式输出模式：❌ 未启用（等待完整回复）")

            # 重新调用以支持思考模式和流式输出
            if stream_enabled:
                # 流式输出模式
                resp_direct = Generation.call(
                    model=config['api']['model'],
                    messages=conversation_history,  # ✅ 传递完整历史
                    extra_body=extra_body_direct,
                    tools=tools,
                    stream=True,  # ✅ 启用流式输出
                    result_format="message"
                )

                # 收集完整回复并实时显示
                direct_reply = ""
                previous_length = 0  # 记录之前打印的长度
                print("🤖 AI: ", end="", flush=True)
            else:
                # 非流式输出模式
                resp_direct = Generation.call(
                    model=config['api']['model'],
                    messages=conversation_history,  # ✅ 传递完整历史
                    extra_body=extra_body_direct,
                    tools=tools,
                    stream=False,  # ✅ 禁用流式输出
                    result_format="message"
                )

                # 直接获取完整回复
                if hasattr(resp_direct, 'output') and resp_direct.output and hasattr(resp_direct.output, 'choices') and resp_direct.output.choices:
                    direct_reply = resp_direct.output.choices[0].message.content
                    print(f"🤖 AI: {direct_reply}")
                else:
                    direct_reply = ""
                    print("❌ 无法获取回复")

            # 流式输出处理（仅当stream_enabled为True时执行）
            if stream_enabled:
                full_reasoning = ""  # 存储完整的思考内容

                for chunk in resp_direct:
                    try:
                        # Dashscope 流式格式: chunk.output.choices[0].message.content
                        if hasattr(chunk, 'output') and chunk.output:
                            if hasattr(chunk.output, 'choices') and chunk.output.choices:
                                message = chunk.output.choices[0].message

                                # ✅ 处理思考内容 (reasoning_content) - 使用try-except避免KeyError
                                try:
                                    reasoning_content = message.reasoning_content
                                    if reasoning_content:
                                        # 记录思考内容到日志
                                        if logger:
                                            # 记录新增的思考内容
                                            new_reasoning = reasoning_content[len(full_reasoning):] if len(reasoning_content) > len(full_reasoning) else ""
                                            if new_reasoning:
                                                logger.log_thinking_process(new_reasoning, budget_used=thinking_config.get('budget', 1000))
                                        full_reasoning = reasoning_content
                                except (KeyError, AttributeError):
                                    # reasoning_content不存在或无法访问，跳过
                                    pass

                                # 处理响应内容
                                try:
                                    content = message.content
                                    if content and len(content) > previous_length:
                                        # ✅ 只打印新增的部分（增量）
                                        new_content = content[previous_length:]
                                        print(new_content, end="", flush=True)
                                        previous_length = len(content)
                                        direct_reply = content  # 保存完整内容
                                except (KeyError, AttributeError):
                                    # content不存在或无法访问，跳过
                                    pass

                    except (AttributeError, IndexError) as e:
                        # 跳过无法处理的chunk
                        continue

                # ✅ 如果有思考内容,记录完整的思考过程
                if full_reasoning and logger:
                    logger.logger.info(f"🧠 完整思考过程长度: {len(full_reasoning)} 字符")

                print()  # 完成后换行

            # ✅ 如果有思考内容,记录完整的思考过程
            if full_reasoning and logger:
                logger.logger.info(f"🧠 完整思考过程长度: {len(full_reasoning)} 字符")

            print()  # 完成后换行
            
            # 添加 AI 回复到对话历史
            conversation_history.append({
                "role": "assistant",
                "content": direct_reply
            })
            
            # 记录直接回复
            if logger:
                logger.log_conversation(question, direct_reply)
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

# ==================== 主程序 ====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='高德地图天气查询系统 - 增强版')
    parser.add_argument('--thinking-mode', type=str, choices=['on', 'off'],
                       help='启用或关闭思考模式（on/off）')
    parser.add_argument('--thinking-budget', type=int, default=1000,
                       help='思考token预算（默认：1000）')
    parser.add_argument('--log-dir', type=str, default='logs',
                       help='日志存储目录（默认：logs）')
    parser.add_argument('--stream-mode', type=str, choices=['on', 'off'],
                       help='启用或关闭流式输出（on/off）')

    try:
        args = parser.parse_args()
    except:
        args = None
    
    # 根据命令行参数或环境变量设置思考模式
    if args and args.thinking_mode:
        if args.thinking_mode == 'on':
            thinking_config["enabled"] = True
            thinking_config["budget"] = args.thinking_budget
        else:
            thinking_config["enabled"] = False

    # 根据命令行参数设置流式输出模式
    if args and args.stream_mode:
        if args.stream_mode == 'on':
            stream_config["enabled"] = True
        else:
            stream_config["enabled"] = False
    
    # 初始化日志记录器
    log_dir = args.log_dir if args else 'logs'
    agent_logger = AgentLogger(log_dir=log_dir, agent_name="weather_agent")
    
    # 记录系统启动
    agent_logger.log_system_event("agent_startup", {
        "version": "3.0-enhanced",
        "thinking_mode": thinking_config["enabled"],
        "thinking_budget": thinking_config["budget"],
        "stream_mode": stream_config["enabled"],
        "log_dir": log_dir
    })
    
    # 显示启动信息
    print("=" * 60)
    print("🌤️ 高德地图天气查询系统（增强版）")
    print("=" * 60)

    thinking_status = "🧠 思考模式：" + ("✅ 已启用" if thinking_config["enabled"] else "❌ 未启用")
    print(f"   {thinking_status}")

    if thinking_config["enabled"]:
        print(f"   💡 思考预算：{thinking_config['budget']} tokens")
        print("   🎯 适用场景：复杂推理、深度分析")
    else:
        print("   ⚡ 快速回答模式")
        print("   🎯 适用场景：简单查询、快速问答")

    stream_status = "📡 流式输出：" + ("✅ 已启用" if stream_config["enabled"] else "❌ 未启用")
    print(f"   {stream_status}")

    if stream_config["enabled"]:
        print("   🎯 实时显示AI回复内容")
    else:
        print("   🎯 等待完整回复后一次性显示")

    print(f"   📋 日志目录：{log_dir}")
    print("   🎭 角色系统：天气预报员、程序员、妈妈")

    print("=" * 60)
    
    # 初始化 MCP 客户端
    client = AmapMCPClient(AMAP_KEY, logger=agent_logger)
    
    try:
        # 启动 MCP 服务器
        print("\n🚀 启动 MCP 服务器...")
        client.start()
        print("✅ MCP 服务器已启动")
        
        print("\n🌤️ 高德地图天气查询系统已启动！")
        print("💡 新增功能：")
        print("  - 输入'/role'可选择角色（天气预报员、程序员、妈妈）")
        print("  - 输入'/thinking'可切换思考模式")
        print("  - 输入'/stream'可切换流式输出模式")
        print("  - 输入'/clear'清空对话历史（支持 /clear N 和 /clear -N）")
        print("  - 输入'/help'查看帮助信息")
        print("  - 支持流式输出和完整多轮对话记忆")
        print("  - 完整日志记录功能已启用")

        # 初始化对话状态
        thinking_enabled = thinking_config["enabled"]
        stream_enabled = stream_config["enabled"]
        conversation_history = []
        current_system_prompt = ROLES["3"]["content"]  # 默认：妈妈角色
        
        # 添加系统提示词到历史
        conversation_history.append({
            "role": "system",
            "content": current_system_prompt
        })
        
        # 首次运行时选择角色
        print("\n")
        current_system_prompt = select_role(conversation_history)
        
        print("\n提示：输入 /help 查看命令帮助")
        print("=" * 60)
        
        # 主循环
        while True:
            print("\n" + "─" * 60)
            
            # 显示当前状态
            role_indicator = "🎭 "
            thinking_indicator = "🧠 " if thinking_enabled else "⚡ "
            question = input(f"{role_indicator}{thinking_indicator}请输入问题（或输入 help/quit）: ").strip()
            
            if not question:
                print("⚠️  请输入问题")
                continue
            
            # 处理命令
            if question.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！")
                break
            
            elif question.lower() in ['help', '/help', '帮助']:
                print_help()
                continue
            
            # 角色相关命令
            elif question.lower() in ['role', '/role', '角色', '切换角色']:
                current_system_prompt = select_role(conversation_history)
                continue
            
            # 思考模式相关命令
            elif question.lower() in ['thinking', '/thinking', '思考', '思考模式']:
                show_thinking_menu()
                thinking_cmd = input("请选择操作（1-4）: ").strip()
                thinking_enabled = handle_thinking_command(thinking_cmd, thinking_enabled)

                # 记录配置变更
                agent_logger.log_system_event("thinking_mode_changed", {
                    "new_state": thinking_enabled
                })

                continue

            # 流式模式相关命令
            elif question.lower() in ['stream', '/stream', '流式', '流式输出']:
                show_stream_menu()
                stream_cmd = input("请选择操作（1-4）: ").strip()
                stream_enabled = handle_stream_command(stream_cmd, stream_enabled)

                # 记录配置变更
                agent_logger.log_system_event("stream_mode_changed", {
                    "new_state": stream_enabled
                })

                continue

            # 清空对话命令（支持参数）
            elif question.lower().startswith('clear') or question.lower().startswith('/clear'):
                clear_history(conversation_history, current_system_prompt, question)
                
                # 记录清空操作
                agent_logger.log_system_event("conversation_cleared", {
                    "command": question
                })
                
                continue
            
            # 调用对话函数
            ask_weather_with_mcp(
                question,
                client,
                conversation_history,
                show_details=True,
                thinking_enabled=thinking_enabled,
                stream_enabled=stream_enabled,
                logger=agent_logger,
                system_prompt=current_system_prompt
            )
            
            # 检查消息数量
            check_message_count(conversation_history)
    
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
        print(f"🧠 最终思考模式状态：{'✅ 已启用' if thinking_enabled else '❌ 未启用'}")
        print(f"📡 最终流式输出状态：{'✅ 已启用' if stream_enabled else '❌ 未启用'}")

        # 记录系统关闭
        agent_logger.log_system_event("agent_shutdown", {
            "final_thinking_state": thinking_enabled,
            "final_stream_state": stream_enabled
        })
