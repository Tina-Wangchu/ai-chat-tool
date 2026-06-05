# 测试：是否可以只使用 MCP 配置，不手写 tools 定义
# 如果 MCP 自动加载工具定义成功，就不需要手写 tools

import dashscope
from dashscope import Generation
import os
import json

# 设置 API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

if not dashscope.api_key:
    print("❌ 未找到 DASHSCOPE_API_KEY")
    exit(1)

# ==================== 测试1：只传 MCP 配置，不传 tools ====================
print("\n【测试1】只使用 MCP 配置（不手写 tools 定义）")
print("-" * 70)

mcp_cfg = {
    "mcpServers": {
        "amap-maps": {
            "type": "streamableHttp",
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/amap-maps/mcp",
            "headers": {"Authorization": f"Bearer {dashscope.api_key}"}
        }
    }
}

try:
    print("📡 发送请求（仅使用 MCP 配置）...")
    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "苏州今天天气怎么样？"}],
        extra_body={"mcp": mcp_cfg},  # 只传 MCP 配置
        result_format="message"
    )

    choice = resp.output.choices[0]
    print(f"✅ 响应状态：{choice.finish_reason}")
    print(f"📝 响应内容：{choice.message.content}")

    # 检查是否有工具调用
    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
        print(f"\n🎉 成功！MCP 自动加载了工具定义")
        print(f"工具调用数量：{len(choice.message.tool_calls)}")

        tool_call = choice.message.tool_calls[0]
        print(f"工具名称：{tool_call['function']['name']}")
        print(f"工具参数：{json.loads(tool_call['function']['arguments'])}")

    else:
        print(f"\n❌ 没有工具调用")
        print(f"可能原因：")
        print(f"  1. MCP 配置不会自动加载工具定义")
        print(f"  2. 需要同时传递 tools 参数")

except Exception as e:
    print(f"❌ 错误：{str(e)}")

# ==================== 测试2：MCP + tools 一起传 ====================
print("\n" + "=" * 70)
print("\n【测试2】MCP 配置 + tools 定义同时传递")
print("-" * 70)

# 手写工具定义（和 weather_test.py 一样）
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

try:
    print("📡 发送请求（MCP + tools 都传）...")
    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "苏州今天天气怎么样？"}],
        extra_body={"mcp": mcp_cfg},
        tools=tools,  # 同时传递 tools
        result_format="message"
    )

    choice = resp.output.choices[0]
    print(f"✅ 响应状态：{choice.finish_reason}")

    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
        print(f"🎉 工具调用成功！")
        print(f"工具名称：{choice.message.tool_calls[0]['function']['name']}")
    else:
        print(f"📝 直接回复：{choice.message.content}")

except Exception as e:
    print(f"❌ 错误：{str(e)}")

print("\n" + "=" * 70)
print("💡 结论：")
print("  如果测试1成功 → 可以只使用 MCP，不需要手写 tools")
print("  如果测试1失败 → 必须同时传 MCP 和 tools")
print("=" * 70)
