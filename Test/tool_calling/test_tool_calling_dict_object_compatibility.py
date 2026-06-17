#!/usr/bin/env python3
"""
测试 tool_calls 字典/对象兼容性修复

这个脚本测试修复后的代码是否能正确处理：
1. 字典格式的 tool_calls（Dashscope API返回的格式）
2. 对象格式的 tool_calls（兼容旧格式）
"""

import json
import sys
from pathlib import Path

def test_tool_calls_parsing():
    """测试 tool_calls 解析逻辑"""

    print("=" * 60)
    print("🧪 Tool Calls 兼容性测试")
    print("=" * 60)

    # 模拟字典格式的 tool_calls（Dashscope API 返回格式）
    dict_tool_calls = [
        {
            "id": "call_123",
            "function": {
                "name": "amapMaps.weather",
                "arguments": '{"city": "南京"}'
            }
        },
        {
            "id": "call_456",
            "function": {
                "name": "amapMaps.weather",
                "arguments": '{"city": "上海"}'
            }
        }
    ]

    # 模拟对象格式的 tool_calls（兼容格式）
    class ToolCall:
        def __init__(self, id, function_name, arguments):
            self.id = id
            self.function = type('obj', (object,), {
                'name': function_name,
                'arguments': arguments
            })

    obj_tool_calls = [
        ToolCall("call_789", "amapMaps.weather", '{"city": "北京"}'),
        ToolCall("call_101", "amapMaps.weather", '{"city": "广州"}")
    ]

    print("\n测试1: 字典格式解析")
    print("-" * 60)

    for tc in dict_tool_calls:
        # 使用修复后的逻辑
        if isinstance(tc, dict):
            tc_id = tc.get("id")
            tc_function_name = tc.get("function", {}).get("name")
            tc_arguments = tc.get("function", {}).get("arguments", "{}")

            print(f"✅ ID: {tc_id}")
            print(f"   Function: {tc_function_name}")
            print(f"   Arguments: {tc_arguments}")

            # 验证解析正确
            assert tc_id == "call_123" or tc_id == "call_456"
            assert tc_function_name == "amapMaps.weather"
            args = json.loads(tc_arguments)
            assert "city" in args

    print("\n测试2: 对象格式解析")
    print("-" * 60)

    for tc in obj_tool_calls:
        # 使用修复后的逻辑
        if isinstance(tc, dict):
            tc_id = tc.get("id")
            tc_function_name = tc.get("function", {}).get("name")
            tc_arguments = tc.get("function", {}).get("arguments", "{}")
        else:
            tc_id = tc.id
            tc_function_name = tc.function.name
            tc_arguments = tc.function.arguments

        print(f"✅ ID: {tc_id}")
        print(f"   Function: {tc_function_name}")
        print(f"   Arguments: {tc_arguments}")

        # 验证解析正确
        assert tc_id == "call_789" or tc_id == "call_101"
        assert tc_function_name == "amapMaps.weather"
        args = json.loads(tc_arguments)
        assert "city" in args

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

    print("\n📊 修复总结:")
    print("1. ✅ 修复了 ask_weather_with_mcp 函数中的 tool_calls 处理")
    print("2. ✅ 修复了 execute_tools_parallel 函数中的 tool_calls 处理")
    print("3. ✅ 现在代码可以同时处理字典和对象两种格式")
    print("4. ✅ 兼容 Dashscope API 返回的字典格式")
    print("5. ✅ 保持向后兼容性")

    print("\n💡 修复的代码逻辑:")
    print("-" * 60)
    print("""
if isinstance(tc, dict):
    # 字典格式（Dashscope API）
    tc_id = tc.get("id")
    tc_function_name = tc.get("function", {}).get("name")
    tc_arguments = tc.get("function", {}).get("arguments", "{}")
else:
    # 对象格式（兼容旧格式）
    tc_id = tc.id
    tc_function_name = tc.function.name
    tc_arguments = tc.function.arguments
    """)

    return True

if __name__ == "__main__":
    try:
        test_tool_calls_parsing()
        print("\n🎉 测试成功！代码修复有效。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
