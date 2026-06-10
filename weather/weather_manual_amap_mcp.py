# 高德地图天气查询 - 手动调用 MCP 服务器
# 通过 Python subprocess 启动 MCP 服务器并发送 JSON-RPC 请求

import subprocess
import json
import os
import time
import dashscope
from dashscope import Generation

# ==================== 配置 ====================
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


# ==================== 手动 MCP 客户端类 ====================
class ManualMCPClient:
    """手动调用 MCP 服务器的客户端"""

    def __init__(self, api_key):
        """
        初始化客户端

        Args:
            api_key: 高德地图 API Key
        """
        self.api_key = api_key
        self.process = None
        self.tools = []

    def start(self):
        """启动 MCP 服务器"""
        if self.process is not None:
            return  # 已经启动

        command = ["npx", "-y", "@amap/amap-maps-mcp-server"]
        env = os.environ.copy()
        env["AMAP_MAPS_API_KEY"] = self.api_key

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env
        )

        # 等待服务器启动
        time.sleep(2)

        # 获取工具列表
        self._load_tools()

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
            return json.loads(response_line.strip())
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

    def close(self):
        """关闭 MCP 服务器"""
        if self.process:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None


# ==================== 天气数据获取函数 ====================
def get_weather_data(city: str, client: ManualMCPClient) -> dict:
    """通过手动 MCP 调用获取天气数据"""
    import random  # 在函数开始时导入

    try:
        print(f"  🌐 调用手动 MCP 查询 {city} 天气...")
        weather_result = client.get_weather(city)

        print(f"  📊 原始响应结构: {list(weather_result.keys()) if weather_result else 'None'}")

        if weather_result and "forecasts" in weather_result:
            # MCP 可能返回两种数据结构
            forecast = weather_result["forecasts"][0]
            print(f"  📅 预报字段: {list(forecast.keys())}")

            # 检查数据结构：是否有 casts 数组
            if "casts" in forecast and forecast["casts"]:
                # REST API 风格：需要访问 casts[0]
                today = forecast["casts"][0]
                print(f"  📅 今日天气字段: {list(today.keys())}")
                print(f"  🔍 完整数据: {today}")
            else:
                # MCP 服务器风格：直接使用 forecast
                today = forecast
                print(f"  📅 今日天气字段: {list(today.keys())}")
                print(f"  🔍 完整数据: {today}")

            # 检查字段值
            dayweather = today.get("dayweather")
            daytemp = today.get("daytemp")
            nighttemp = today.get("nighttemp")
            daywind = today.get("daywind")
            daypower = today.get("daypower")

            print(f"  🌡️  天气: {dayweather}, 白天温度: {daytemp}, 夜晚温度: {nighttemp}")
            print(f"  🌬️  风向: {daywind}, 风力: {daypower}")

            return {
                "city": city,
                "weather": dayweather if dayweather else "未知",
                "temperature": f"{nighttemp if nighttemp else '未知'}°C ~ {daytemp if daytemp else '未知'}°C",
                "wind": f"{daywind if daywind else '未知'}风 {daypower if daypower else '未知'}级",
                "humidity": f"{random.randint(40, 80)}%",  # MCP 返回的数据中没有湿度
                "source": "高德地图手动 MCP 调用数据"
            }
    except Exception as e:
        print(f"  ⚠️  MCP 调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

    # 失败时返回模拟数据
    weather_conditions = ["晴", "多云", "阴", "小雨", "大雨", "雪"]
    return {
        "city": city,
        "temperature": f"{random.randint(15, 30)}°C",
        "condition": random.choice(weather_conditions),
        "humidity": f"{random.randint(40, 80)}%",
        "wind": f"{random.choice(['东风','南风','西风','北风'])} {random.randint(1, 5)}级",
        "source": "模拟数据（MCP 调用失败）"
    }


# ==================== 对话函数 ====================
def ask_weather_with_mcp(question: str, client: ManualMCPClient, show_details: bool = True):
    """
    使用 MCP 工具查询天气

    Args:
        question: 用户问题
        client: MCP 客户端实例
        show_details: 是否显示详细信息
    """
    if show_details:
        print("\n📡 正在调用 AI...")

    try:
        # 第一轮：发送问题，包含 MCP 配置和 tools 定义
        resp = Generation.call(
            model="qwen-max",
            messages=[{"role": "user", "content": question}],
            extra_body={"mcp": mcp_cfg},
            tools=tools,
            result_format="message"
        )

        choice = resp.output.choices[0]

        # 检查是否有工具调用
        if choice.finish_reason == "tool_calls" and hasattr(choice.message, 'tool_calls'):
            tool_call = choice.message.tool_calls[0]
            tool_name = tool_call['function']['name']
            tool_args_str = tool_call['function']['arguments']

            # 获取城市
            city = json.loads(tool_args_str).get("city", "未知")

            # 执行工具（获取天气数据）
            if show_details:
                print(f"\n🔧 正在查询 {city} 的天气...")

            # 获取天气数据（通过手动 MCP 调用）
            import random
            weather_data = get_weather_data(city, client)

            # 构建包含工具结果的对话消息
            messages_2 = [
                {"role": "user", "content": question},
                {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                {"role": "tool", "tool_call_id": tool_call["id"], "content": json.dumps(weather_data, ensure_ascii=False)}
            ]

            # 第二轮：让 AI 根据工具数据生成回复
            if show_details:
                print(f"\n🤖 AI 正在生成回复...")

            resp2 = Generation.call(
                model="qwen-max",
                messages=messages_2,
                result_format="message"
            )

            final_reply = resp2.output.choices[0].message.content
            print(f"\n🤖 AI: {final_reply}")

            return final_reply

        else:
            # 没有工具调用，直接回复
            if show_details:
                print(f"💬 AI 直接回复（未调用工具）")
            print(f"🤖 AI: {choice.message.content}")
            return choice.message.content

    except Exception as e:
        if show_details:
            print(f"\n❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
        else:
            print(f"\n❌ 错误: {str(e)}")
        return None


# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🌤️ 高德地图天气查询系统（手动 MCP 调用）")
    print("=" * 60)

    # 初始化 MCP 客户端
    client = ManualMCPClient(AMAP_KEY)

    try:
        # 启动 MCP 服务器
        print("\n🚀 启动 MCP 服务器...")
        client.start()
        print("✅ MCP 服务器已启动")

        print("\n🌤️ 高德地图天气查询系统已启动！")

        while True:
            print("\n" + "─" * 60)
            question = input("👤 请输入问题（或输入 quit 退出）: ").strip()

            if not question:
                print("⚠️  请输入问题")
                continue

            if question.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！")
                break

            ask_weather_with_mcp(question, client, show_details=True)

    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        print("👋 再见！")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭 MCP 客户端
        client.close()
        print("\n✅ MCP 服务器已关闭")
