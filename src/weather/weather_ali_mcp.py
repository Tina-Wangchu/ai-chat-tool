# 高德地图天气查询 - 使用 dashscope 库和 MCP 工具 使用阿里云MCP 然后调用高德API
# 基于测试验证的正确实现方式

import dashscope
from dashscope import Generation
import os
import json
import requests

print("=" * 60)
print("🌤️ 高德地图天气查询")
print("=" * 60)

# ==================== 配置 ====================
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

if not dashscope.api_key:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  export DASHSCOPE_API_KEY='your-key-here'")
    exit(1)


# 检查高德地图 API Key
AMAP_KEY = os.getenv("AMAP_API_KEY")

if not AMAP_KEY:
    print("❌ 错误：未找到 AMAP_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  export AMAP_API_KEY='your-key-here'")
    print("  或在 ~/.zshrc 中添加: export AMAP_API_KEY='your-key-here'")
    exit(1)

USE_REAL_DATA = True

# ==================== MCP 配置 ====================
# 阿里云官方 MCP 配置格式
mcp_cfg = {
    "mcpServers": {
        "amap-maps": {
            "type": "streamableHttp",
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/amap-maps/mcp",
            "headers": {"Authorization": f"Bearer {dashscope.api_key}"}
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

# ==================== 天气数据获取函数 ====================
def get_weather_data(city: str) -> dict:

    # 如果配置了高德 API Key，尝试获取真实数据
    if USE_REAL_DATA and AMAP_KEY:
        try:
            print(f"  🌐 调用高德 REST API 查询 {city} 实时天气...")
            url = "https://restapi.amap.com/v3/weather/weatherInfo"
            params = {
                "key": AMAP_KEY,
                "city": city,
                "extensions": "base"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            print(f"  📊 原始响应结构: {list(data.keys())}")
            print(f"  🔍 完整数据: {data}")

            if data.get("status") == "1" and data.get("lives"):
                live = data["lives"][0]
                print(f"  🌡️  天气: {live.get('weather')}, 温度: {live.get('temperature')}°C")
                print(f"  💧 湿度: {live.get('humidity')}%, 风向: {live.get('winddirection')}风 {live.get('windpower')}级")

                return {
                    "city": city,
                    "province": live.get('province', ''),
                    "temperature": f"{live.get('temperature')}°C",
                    "humidity": f"{live.get('humidity')}%",
                    "weather": live.get('weather'),
                    "wind": f"{live.get('winddirection')}风 {live.get('windpower')}级",
                    "reporttime": live.get('reporttime', ''),
                    "source": "高德地图实时数据"
                }
            else:
                print(f"  ⚠️  API 返回错误: {data.get('info', '未知错误')}")
        except Exception as e:
            print(f"  ⚠️  真实数据获取失败: {str(e)}")
            import traceback
            traceback.print_exc()

    # 使用模拟数据
    import random
    weather_conditions = ["晴", "多云", "阴", "小雨", "大雨", "雪"]

    return {
        "city": city,
        "temperature": f"{random.randint(15, 30)}°C",
        "condition": random.choice(weather_conditions),
        "humidity": f"{random.randint(40, 80)}%",
        "wind": f"{random.choice(['东风','南风','西风','北风'])} {random.randint(1, 5)}级",
        "source": "模拟数据（未配置 AMAP_API_KEY 或查询失败）"
    }

# ==================== 对话函数 ====================
def ask_weather_with_mcp(question: str, show_details: bool = True):
    """
    使用 MCP 工具查询天气

    Args:
        question: 用户问题
        show_details: 是否显示详细信息
    """

    if show_details:
        print("\n📡 正在调用 AI...")

    try:
        # 第一轮：发送问题，包含 MCP 配置和 tools 定义
        resp = Generation.call(
            model="qwen-max",
            messages=[{"role": "user", "content": question}],
            extra_body={"mcp": mcp_cfg},  # 传递 MCP 配置
            tools=tools,                   # 传递工具定义
            result_format="message"
        )

        choice = resp.output.choices[0]


        # 检查是否有工具调用
        if choice.finish_reason == "tool_calls" and hasattr(choice.message, 'tool_calls'):

            tool_call = choice.message.tool_calls[0]
            tool_name = tool_call['function']['name']  # dashscope 格式：字典访问
            tool_args_str = tool_call['function']['arguments']


            # 获取城市
            city = json.loads(tool_args_str).get("city", "未知")

            # 执行工具（获取天气数据）
            if show_details:
                print(f"\n🔧 正在查询 {city} 的天气...")

            # 获取天气数据
            weather_data = get_weather_data(city)

            # 构建包含工具结果的对话消息
            messages_2 = [
                {"role": "user", "content": question},
                {"role": "assistant", "content": None, "tool_calls": [tool_call]},  # dashscope 格式
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

    print("\n🌤️ 高德地图天气查询系统已启动！")

    try:
        while True:
            print("\n" + "─" * 60)
            question = input("👤 请输入问题（或输入 quit 退出）: ").strip()

            if not question:
                print("⚠️  请输入问题")
                continue

            if question.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！")
                break

            ask_weather_with_mcp(question, show_details=True)

    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        print("👋 再见！")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
