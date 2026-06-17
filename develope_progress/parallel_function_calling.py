# 并行工具调用示例
# 演示如何同时调用多个工具（如同时查询多个城市的天气）

import json
import requests
import concurrent.futures  # Python 内置标准库 用于并行执行
from config_load import get_client, load_config

# ==================== 1. 配置加载 ====================
config = load_config()
client = get_client()

# 从配置读取默认系统提示词
default_system_prompt = config.get('roles', {}).get('available', [{}])[2].get('system_prompt',
    "你是一个友好的AI助手，擅长回答问题并提供帮助。")

# ==================== 2. 定义工具 ====================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气，包括温度和天气状况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取指定城市的当前时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"}
                },
                "required": ["city"]
            }
        }
    }
]

# ==================== 3. 工具执行函数 ====================
def execute_tool(name: str, args: dict) -> str:
    """执行工具调用"""
    if name == "get_weather":
        city = args.get("city", "")
        unit = args.get("unit", "celsius")

        try:
            # 调用 wttr.in 天气 API
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            weather_data = response.json()
            current = weather_data.get("current_condition", [{}])[0]

            temp_c = int(current.get("temp_C", "N/A"))
            temp_f = int(current.get("temp_F", "N/A"))
            temp = temp_f if unit == "fahrenheit" else temp_c
            unit_symbol = "°F" if unit == "fahrenheit" else "°C"

            condition = current.get("weatherDesc", [{}])[0].get("value", "未知")
            humidity = current.get("humidity", "N/A")

            result = {
                "city": city,
                "temperature": f"{temp}{unit_symbol}",
                "condition": condition,
                "humidity": f"{humidity}%",
                "tool": "weather"
            }

            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"天气查询失败: {str(e)}", "city": city}, ensure_ascii=False)

    elif name == "get_time":
        # 模拟时间查询（实际项目可以使用时区 API）
        city = args.get("city", "")
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "city": city,
            "time": current_time,
            "tool": "time"
        }

        return json.dumps(result, ensure_ascii=False)

    return json.dumps({"error": f"unknown tool: {name}"}, ensure_ascii=False)


# ==================== 4. 并行执行工具调用 ====================
def execute_tools_parallel(tool_calls, messages):
    """
    并行执行多个工具调用

    Args:
        tool_calls: 工具调用列表
        messages: 消息列表（用于添加工具返回结果）
    """
    print(f"\n🔄 需要调用 {len(tool_calls)} 个工具，开始并行执行...")

    # 使用线程池并行执行
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交所有任务到线程池
        futures = {
            tc.id: executor.submit(
                execute_tool,
                tc.function.name,
                json.loads(tc.function.arguments)
            )
            for tc in tool_calls
        }

        # 等待所有任务完成并获取结果
        for tc in tool_calls:
            try:
                result = futures[tc.id].result(timeout=15)  # 等待结果，最多15秒
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
                print(f"✅ 工具 {tc.function.name} ({tc.id}) 执行完成")
            except concurrent.futures.TimeoutError:
                print(f"⏰ 工具 {tc.function.name} ({tc.id}) 超时")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"error": "执行超时"}, ensure_ascii=False)
                })
            except Exception as e:
                print(f"❌ 工具 {tc.function.name} ({tc.id}) 执行失败: {str(e)}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                })


# ==================== 5. 主循环 ====================
def run_conversation(user_message: str):
    """运行对话"""

    # 初始化消息
    messages = [
        {"role": "system", "content": default_system_prompt},
        {"role": "user", "content": user_message}
    ]

    print(f"\n👤 用户: {user_message}")

    while True:
        try:
            # 调用模型
            response = client.chat.completions.create(
                model=config['api']['model'],
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            choice = response.choices[0]

            # 添加助手回复到消息历史
            messages.append({
                "role": "assistant",
                "content": choice.message.content,
                "tool_calls": choice.message.tool_calls
            })

            # 如果没有工具调用，说明对话结束
            if choice.finish_reason != "tool_calls":
                print(f"\n🤖 AI: {choice.message.content}")
                break

            # 有工具调用，并行执行
            print(f"\n🔧 AI 决定调用 {len(choice.message.tool_calls)} 个工具")
            execute_tools_parallel(choice.message.tool_calls, messages)

        except Exception as e:
            print(f"\n❌ 错误: {str(e)}")
            break


# ==================== 6. 测试示例 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 并行工具调用示例")
    print("=" * 60)

    # 示例1：查询多个城市的天气（并行执行）
    print("\n【示例1】查询多个城市的天气")
    run_conversation("北京、上海、广州、深圳今天的天气怎么样？")

    # 示例2：同时查询天气和时间（并行执行）
    print("\n" + "=" * 60)
    print("\n【示例2】同时查询天气和时间")
    run_conversation("告诉我北京现在的天气和东京的时间")

    # 示例3：单个调用（对比性能）
    print("\n" + "=" * 60)
    print("\n【示例3】单个城市查询")
    run_conversation("杭州今天天气怎么样？")

    print("\n" + "=" * 60)
    print("✅ 所有示例完成！")
    print("=" * 60)
