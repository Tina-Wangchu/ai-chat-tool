# 测试：使用你的高德 API Key，验证 MCP 是否会自动调用高德 API
import dashscope
from dashscope import Generation
import os
import json

print("=" * 70)
print("🧪 测试：使用高德 API Key，验证 MCP 自动调用")
print("=" * 70)

# 配置 API Keys
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 🔑 使用用户提供的高德 API Key
AMAP_KEY = "ina_amap_maps_key1"  # 你的高德地图 API Key

print(f"\n📋 配置状态：")
print(f"  - DashScope API Key: {'✅ 已配置' if dashscope.api_key else '❌ 未配置'}")
print(f"  - 高德地图 API Key: ✅ {AMAP_KEY[:8]}...{AMAP_KEY[-4:]}")

# MCP 配置 + tools 定义
mcp_cfg = {
    "mcpServers": {
        "amap-maps": {
            "type": "streamableHttp",
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/amap-maps/mcp",
            "headers": {"Authorization": f"Bearer {dashscope.api_key}"}
        }
    }
}

tools = [{
    "type": "function",
    "function": {
        "name": "amapMaps.weather",
        "description": "查询天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
}]

print("\n" + "=" * 70)
print("【测试】发送天气查询（使用高德 API Key）")
print("-" * 70)

try:
    print("📡 第一轮：发送查询请求...")

    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "苏州今天天气怎么样？"}],
        extra_body={"mcp": mcp_cfg},
        tools=tools,
        result_format="message"
    )

    choice = resp.output.choices[0]
    print(f"响应状态：{choice.finish_reason}")

    if choice.finish_reason == "tool_calls" and hasattr(choice.message, 'tool_calls'):
        tool_call = choice.message.tool_calls[0]
        tool_name = tool_call['function']['name']
        tool_args = json.loads(tool_call['function']['arguments'])

        print(f"✅ 工具调用：{tool_name}")
        print(f"✅ 参数：{tool_args}")

        # 🔴 关键检查：看看响应中是否已经包含了天气数据
        print(f"\n🔍 检查：MCP 是否已经自动调用了高德 API？")

        output_dict = resp.output.__dict__

        if output_dict:
            print(f"响应数据：")
            print(json.dumps(output_dict, ensure_ascii=False, indent=2, default=str))

            # 检查是否有天气数据字段
            if any(key in str(output_dict) for key in ['temperature', 'weather', '湿度', '温度']):
                print(f"\n✅ 成功！MCP 自动获取了天气数据")
            else:
                print(f"\n❌ 响应中不包含天气数据")
        else:
            print(f"❌ 响应为空，MCP 没有自动调用高德 API")

        print(f"\n💡 结论：")
        print(f"  如果看到真实的天气数据 → MCP 会自动调用高德 API")
        print(f"  如果响应为空或无天气数据 → 需要自己手动调用高德 API")

    else:
        print(f"❌ 没有工具调用")
        print(f"直接回复：{choice.message.content}")

except Exception as e:
    print(f"❌ 错误：{str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
