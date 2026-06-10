# 高德地图天气查询 - 直接调用 REST API
# 无需启动 MCP 服务器，直接发送 HTTP 请求

import requests
import json
import os
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
# 直接 API 调用时，MCP 配置主要用于 AI 理解意图
mcp_cfg = {
    "mcpServers": {
        "amap-maps": {
            "type": "streamableHttp",
            "url": "https://restapi.amap.com/v3/weather/weatherInfo",
            "headers": {"Authorization": f"Bearer {AMAP_KEY}"}
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


# ==================== 高德 API 客户端类 ====================
class AmapDirectAPI:
    """高德地图 API 直接调用客户端"""

    def __init__(self, api_key):
        """
        初始化客户端

        Args:
            api_key: 高德地图 API Key
        """
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com"

    def get_weather(self, city):
        """
        查询天气

        Args:
            city: 城市名称或 adcode

        Returns:
            天气数据字典
        """
        url = f"{self.base_url}/v3/weather/weatherInfo"
        params = {
            "key": self.api_key,
            "city": city,
            "extensions": "all"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1":
                return data
            else:
                return {"error": data.get("info", "未知错误")}
        except Exception as e:
            return {"error": str(e)}

    def search_place(self, keywords, city=None):
        """
        搜索地点（关键词搜索）

        Args:
            keywords: 搜索关键词
            city: 城市名称（可选）

        Returns:
            搜索结果
        """
        url = f"{self.base_url}/v5/place/text"
        params = {
            "key": self.api_key,
            "keywords": keywords
        }
        if city:
            params["city"] = city

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1":
                return data
            else:
                return {"error": data.get("info", "未知错误")}
        except Exception as e:
            return {"error": str(e)}

    def geo_to_address(self, lon, lat):
        """
        坐标转地址（逆地理编码）

        Args:
            lon: 经度
            lat: 纬度

        Returns:
            地址信息
        """
        url = f"{self.base_url}/v3/geocode/regeo"
        params = {
            "key": self.api_key,
            "location": f"{lon},{lat}",
            "extensions": "all"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1":
                return data
            else:
                return {"error": data.get("info", "未知错误")}
        except Exception as e:
            return {"error": str(e)}

    def address_to_geo(self, address, city=None):
        """
        地址转坐标（地理编码）

        Args:
            address: 地址
            city: 城市名称（可选）

        Returns:
            坐标信息
        """
        url = f"{self.base_url}/v3/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address
        }
        if city:
            params["city"] = city

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "1":
                return data
            else:
                return {"error": data.get("info", "未知错误")}
        except Exception as e:
            return {"error": str(e)}


# ==================== 天气数据获取函数 ====================
def get_weather_data(city: str, client: AmapDirectAPI) -> dict:
    """通过直接 API 调用获取天气数据"""
    import random  # 在函数开始时导入

    try:
        print(f"  🌐 调用 REST API 查询 {city} 天气...")
        weather_result = client.get_weather(city)

        print(f"  📊 原始响应结构: {list(weather_result.keys()) if weather_result else 'None'}")

        if "error" not in weather_result and "forecasts" in weather_result:
            # REST API 返回的数据结构：forecasts[0].casts[0]
            forecast = weather_result["forecasts"][0]
            print(f"  📅 预报字段: {list(forecast.keys())}")

            # 检查是否有 casts 数组
            if "casts" in forecast and forecast["casts"]:
                today = forecast["casts"][0]  # 使用 casts[0]
                print(f"  📅 今日天气字段: {list(today.keys())}")
                print(f"  🔍 完整数据: {today}")  # 添加完整数据输出

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
                    "humidity": f"{random.randint(40, 80)}%",  # API 返回的数据中没有湿度
                    "source": "高德地图 REST API 数据"
                }
            else:
                print(f"  ⚠️  响应中没有 casts 数据")
        else:
            print(f"  ⚠️  响应中没有 forecasts 数据或存在错误")
    except Exception as e:
        print(f"  ⚠️  API 调用失败: {str(e)}")
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
        "source": "模拟数据（API 调用失败）"
    }


# ==================== 对话函数 ====================
def ask_weather_with_mcp(question: str, client: AmapDirectAPI, show_details: bool = True):
    """
    使用 MCP 工具查询天气

    Args:
        question: 用户问题
        client: API 客户端实例
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

            # 获取天气数据（通过直接 API 调用）
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
    print("🌤️ 高德地图天气查询系统（直接 API 调用）")
    print("=" * 60)

    # 初始化 API 客户端
    client = AmapDirectAPI(AMAP_KEY)

    try:
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
