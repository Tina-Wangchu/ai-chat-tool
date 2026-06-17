# 流式输出 + 工具调用完整示例
# 演示如何处理流式工具调用并收集完整信息

from config_load import get_client, load_config

# ==================== 配置加载 ====================
config = load_config()
client = get_client()

# ==================== 定义工具 ====================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"],
            },
        },
    },
]

# ==================== 创建流式请求 ====================
print("📡 创建流式请求...\n")

stream = client.chat.completions.create(
    model=config['api']['model'],
    messages=[{"role": "user", "content": "杭州天气?"}],
    tools=tools,
    stream=True,  # 启用流式输出
    extra_body={
        "enable_passage_insertion": False,
        "incremental_output": True
    }
)

# ==================== 第一遍遍历：查看每个块 ====================
print("【第一遍遍历】查看每个流式块的内容：\n")

for chunk in stream:
    # 检查 choices 是否存在且非空
    if chunk.choices and len(chunk.choices) > 0:
        delta = chunk.choices[0].delta
        print(f"块内容: {delta.tool_calls}")
    else:
        print("块内容: (空块，无 choices)")

# ==================== 重新创建请求（因为流只能遍历一次）====================
print("\n📡 重新创建流式请求...\n")

stream = client.chat.completions.create(
    model=config['api']['model'],
    messages=[{"role": "user", "content": "杭州天气?"}],
    tools=tools,
    stream=True,
    extra_body={
        "enable_passage_insertion": False,
        "incremental_output": True
    }
)

# ==================== 第二遍遍历：收集完整工具调用 ====================
print("\n【第二遍遍历】收集完整的工具调用信息：\n")

tool_calls = {}
for response_chunk in stream:
    # 检查 choices 是否存在且非空
    if response_chunk.choices and len(response_chunk.choices) > 0:
        delta_tool_calls = response_chunk.choices[0].delta.tool_calls
        if delta_tool_calls:
            for tool_call_chunk in delta_tool_calls:
                call_index = tool_call_chunk.index

                # 初始化工具调用
                if call_index not in tool_calls:
                    tool_calls[call_index] = tool_call_chunk
                else:
                    # 累积参数（因为是流式传输）
                    tool_calls[call_index].function.arguments += tool_call_chunk.function.arguments

# ==================== 打印最终结果 ====================
print("\n✅ 收集完成的工具调用：\n")

if tool_calls:
    # 直接访问工具调用对象
    tool_call = tool_calls[0]
    print(f"完整 JSON: {tool_call.model_dump_json()}")

    print("\n📋 解析后的工具调用信息：\n")
    print(f"工具 ID: {tool_call.id}")
    print(f"工具名称: {tool_call.function.name}")
    print(f"工具参数: {tool_call.function.arguments}")
else:
    print("没有收集到工具调用")
