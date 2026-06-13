# Tool Calling
import json
import requests  # 添加 requests 库
from config_load import get_client, load_config

config = load_config()
client = get_client()

# 从配置读取默认系统提示词
default_system_prompt = config.get('roles', {}).get('available', [{}])[2].get('system_prompt',
    "你是一个友好的AI助手，擅长回答问题并提供帮助。")

# ── 1. 定义工具 ──────────────────────────────────────────
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
    }
]

# ── 2. 真实工具执行函数（使用 wttr.in API）────────────────────────
def execute_tool(name: str, args: dict) -> str:
    """
    执行工具调用
    使用 wttr.in
    文档: https://wttr.in/:help
    """
    if name == "get_weather":
        city = args.get("city", "")
        unit = args.get("unit", "celsius")

        try:
            # format=j1 返回 JSON 格式 
            # 一个f-string 用来构建完整的API地址 把city替换为用户查询的城市
            url = f"https://wttr.in/{city}?format=j1"

            # 发送请求
            # 使用request库向API服务器发送GET请求
            # response 是一个对象，包含：
            #response.status_code   # 状态码（200 = 成功，404 = 未找到）
            #response.text          # 原始文本
            #response.json()        # 解析后的 JSON 数据
            #response.headers       # 响应头信息
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 解析 JSON 响应 把json转换为python string
            weather_data = response.json()

            # 提取当前天气信息
            current = weather_data.get("current_condition", [{}])[0]

            temp_c = int(current.get("temp_C", "N/A"))
            temp_f = int(current.get("temp_F", "N/A"))

            # 根据单位选择温度
            temp = temp_f if unit == "fahrenheit" else temp_c
            unit_symbol = "°F" if unit == "fahrenheit" else "°C"

            # 获取天气描述
            condition = current.get("weatherDesc", [{}])[0].get("value", "未知")

            # 获取其他信息
            humidity = current.get("humidity", "N/A")
            wind_speed = current.get("windspeedKmph", "N/A")

            # 构建返回结果
            result = {
                "city": city,
                "temperature": f"{temp}{unit_symbol}",
                "condition": condition,
                "humidity": f"{humidity}%",
                "wind_speed": f"{wind_speed} km/h",
                "query_unit": unit
            }

            return json.dumps(result, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            return json.dumps({
                "error": f"天气查询失败: {str(e)}",
                "city": city
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": f"处理天气数据时出错: {str(e)}",
                "city": city
            }, ensure_ascii=False)

    return json.dumps({"error": f"unknown tool: {name}"}, ensure_ascii=False)

# ── 3. Agentic Loop ─────────────────────────────────────
messages = [
    {"role": "system", "content": default_system_prompt},
    {"role": "user", "content": "北京和上海今天天气怎么样？"}
]

while True:

    response = client.chat.completions.create(
        model=config['api']['model'],  # 从配置读取模型
        tools=tools,
        tool_choice="auto",
        messages=messages
    )

    choice = response.choices[0]
    messages.append({"role": "assistant", "content": choice.message.content,
                     "tool_calls": choice.message.tool_calls})

    # ── 循环终止条件 ───────────────────────────────────────
    if choice.finish_reason != "tool_calls":
        print("最终回答：", choice.message.content)
        break

    # ── 4. 执行工具并回传结果 ─────────────────────────────
    for tool_call in choice.message.tool_calls:
        result = execute_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,       # 必须与请求中的 id 对应
            "content": result
        })
