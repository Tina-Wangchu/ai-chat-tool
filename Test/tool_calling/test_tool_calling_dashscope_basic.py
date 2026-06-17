# 简单工具调用测试 - 使用 dashscope 库
# 不使用 MCP，只用标准 tools 参数测试模型是否能识别工具

import dashscope
from dashscope import Generation
import os

# 设置 API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

print("=" * 60)
print("🧪 简单工具调用测试")
print("=" * 60)

# ==================== 测试1：直接对话（无工具）====================
print("\n【测试1】直接对话（不使用工具）")
print("-" * 60)

try:
    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "你好"}],
        result_format="message"
    )
    print(f"✅ 回复: {resp.output.choices[0].message.content}")
except Exception as e:
    print(f"❌ 错误: {str(e)}")

# ==================== 测试2：使用标准 tools 参数====================
print("\n【测试2】使用标准 tools 参数（计算器工具）")
print("-" * 60)

tools = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "执行数学计算，返回计算结果",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "要执行的操作，如 'add', 'subtract', 'multiply', 'divide'",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {
                    "type": "number",
                    "description": "第一个数字"
                },
                "b": {
                    "type": "number",
                    "description": "第二个数字"
                }
            },
            "required": ["operation", "a", "b"]
        }
    }
}]

# 模拟工具执行函数
def execute_calculator(operation: str, a: float, b: float) -> str:
    """执行计算"""
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b if b != 0 else "除数不能为零"
        else:
            result = "未知操作"
        return f"计算结果：{a} {operation.replace('add', '+').replace('subtract', '-')} {b} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

try:
    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "10 + 5 等于多少？"}],
        tools=tools,
        result_format="message"
    )

    choice = resp.output.choices[0]
    print(f"完成原因: {choice.finish_reason}")
    print(f"回复内容: {choice.message.content}")

    # 检查是否有工具调用
    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
        print(f"\n🎉 工具调用成功！")
        print(f"工具调用数量: {len(choice.message.tool_calls)}")

        tool_call = choice.message.tool_calls[0]
        print(f"工具名称: {tool_call['function']['name']}")  # 修复：使用字典访问

        # 解析参数
        import json
        args = json.loads(tool_call['function']['arguments'])  # 修复：使用字典访问
        print(f"工具参数: {args}")

        # 执行工具
        result = execute_calculator(
            args.get("operation"),
            args.get("a"),
            args.get("b")
        )

        print(f"\n🔧 工具执行结果: {result}")

        # 构建第二轮对话，将工具结果传回给模型
        messages_2 = [
            {"role": "user", "content": "10 + 5 等于多少？"},
            {"role": "assistant", "content": None, "tool_calls": [tool_call]},  # 修复：直接使用字典
            {"role": "tool", "tool_call_id": tool_call["id"], "content": result}  # 修复：使用字典访问
        ]

        resp2 = Generation.call(
            model="qwen-max",
            messages=messages_2,
            result_format="message"
        )

        print(f"\n🤖 最终回复: {resp2.output.choices[0].message.content}")

    else:
        print(f"\n❌ 模型没有调用工具，而是直接回答")
        print(f"原因可能是：")
        print(f"  - 工具定义格式问题")
        print(f"  - 模型不支持工具调用")
        print(f"  - 配置传递方式错误")

except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()

# ==================== 测试3：天气工具（简化版）====================
print("\n" + "=" * 60)
print("\n【测试3】天气查询工具（简化版）")
print("-" * 60)

weather_tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的实时天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如：北京、上海"
                }
            },
            "required": ["city"]
        }
    }
}]

try:
    resp = Generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "苏州今天天气怎么样？"}],
        tools=weather_tools,
        result_format="message"
    )

    choice = resp.output.choices[0]
    print(f"完成原因: {choice.finish_reason}")

    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
        print(f"✅ 天气工具调用成功！")

        tool_call = choice.message.tool_calls[0]
        print(f"工具: {tool_call['function']['name']}")  # 修复：使用字典访问
        print(f"参数: {json.loads(tool_call['function']['arguments'])}")  # 修复：使用字典访问

        # 模拟天气数据
        mock_weather = {
            "city": "苏州",
            "temperature": "25°C",
            "condition": "多云转晴",
            "humidity": "65%"
        }

        # 构建包含工具结果的对话
        messages_with_result = [
            {"role": "user", "content": "苏州今天天气怎么样？"},
            {"role": "assistant", "content": None, "tool_calls": [tool_call]},  # 修复：直接使用字典
            {"role": "tool", "tool_call_id": tool_call["id"], "content": json.dumps(mock_weather, ensure_ascii=False)}  # 修复：使用字典访问 id
        ]

        resp2 = Generation.call(
            model="qwen-max",
            messages=messages_with_result,
            result_format="message"
        )

        print(f"\n🤖 最终回复: {resp2.output.choices[0].message.content}")

    else:
        print(f"❌ 模型没有调用天气工具")
        print(f"直接回复: {choice.message.content}")

        print(f"\n💡 如果模型直接回复说无法查询天气，说明：")
        print(f"  1. 工具定义格式可能不对")
        print(f"  2. 模型可能不支持天气查询功能")
        print(f"  3. 需要检查 dashscope 库的工具调用文档")

except Exception as e:
    print(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🧪 测试完成")
print("=" * 60)
print("\n💡 总结：")
print("  - 如果测试2成功：说明模型支持工具调用，问题在 MCP 配置")
print("  - 如果测试2失败：说明基础工具调用就有问题，需要检查基础配置")
print("  - 如果测试3成功：说明天气工具定义正确，问题在 MCP 配置传递")
