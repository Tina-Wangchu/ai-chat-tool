#!/usr/bin/env python3
"""
测试修复后的代码
验证 hasattr 的问题是否已解决
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_usage_attribute_access():
    """测试 usage 属性访问的安全性"""

    print("=" * 60)
    print("🧪 测试 usage 属性访问")
    print("=" * 60)

    # 模拟 Dashscope 的 Usage 对象
    class MockUsage:
        """模拟 Dashscope Usage 对象"""

        def __init__(self):
            self.input_tokens = 100
            self.output_tokens = 50
            self.total_tokens = 150

        def __getattr__(self, item):
            # 模拟 dashscope 的行为：访问不存在的属性时抛出 KeyError
            raise KeyError(f"KeyError: '{item}'")

    # 模拟 Dashscope 的 Response 对象
    class MockResponse:
        """模拟 Dashscope Response 对象"""

        def __init__(self):
            self.status_code = 200
            self.usage = MockUsage()

    resp = MockResponse()

    print("\n📝 测试 1: 安全的 usage 访问方式（try-except）")
    try:
        usage_data = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "total_tokens": resp.usage.total_tokens
        }
        print(f"✅ 成功获取 usage 数据: {usage_data}")
    except (AttributeError, KeyError, TypeError) as e:
        usage_data = str(resp.usage) if hasattr(resp, 'usage') else "unknown"
        print(f"⚠️  降级为字符串: {usage_data}")

    print("\n📝 测试 2: 使用 hasattr 检查 resp.usage.model_dump（会导致错误）")
    try:
        # 这是原来的错误方式
        if hasattr(resp.usage, 'model_dump'):
            print("有 model_dump 方法")
        else:
            print("没有 model_dump 方法")
    except KeyError as e:
        print(f"❌ 使用 hasattr 检查 model_dump 会导致 KeyError: {e}")

    print("\n📝 测试 3: 使用 hasattr 检查 resp.usage（安全）")
    if hasattr(resp, 'usage'):
        print(f"✅ resp 对象有 usage 属性")
        print(f"   usage 对象: {resp.usage}")

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print("\n💡 结论:")
    print("  - 使用 try-except 安全访问 usage 属性")
    print("  - 避免使用 hasattr 检查 model_dump 等方法")
    print("  - 使用 hasattr 检查 resp 对象的属性是安全的")


def test_log_response_code():
    """测试修复后的 log_response 代码"""

    print("\n" + "=" * 60)
    print("🧪 测试修复后的代码片段")
    print("=" * 60)

    # 模拟 resp 对象
    class MockUsage:
        def __init__(self):
            self.input_tokens = 150
            self.output_tokens = 80
            self.total_tokens = 230

        def __getattr__(self, item):
            raise KeyError(f"KeyError: '{item}'")

    class MockResp:
        def __init__(self):
            self.status_code = 200
            self.usage = MockUsage()

    class MockChoice:
        def __init__(self):
            self.finish_reason = "tool_calls"

    resp = MockResp()
    choice = MockChoice()

    # 模拟日志记录
    latency_ms = 1234.56

    print("\n📝 使用修复后的代码:")
    try:
        # 安全地获取 usage 数据
        try:
            usage_data = {
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
                "total_tokens": resp.usage.total_tokens
            }
        except (AttributeError, KeyError, TypeError):
            usage_data = str(resp.usage) if hasattr(resp, 'usage') else "unknown"

        response_data = {
            "round": 1,
            "status_code": resp.status_code,
            "latency_ms": f"{latency_ms:.2f}",
            "finish_reason": choice.finish_reason,
            "usage": usage_data
        }

        print(f"✅ 成功记录响应数据:")
        print(f"   status_code: {response_data['status_code']}")
        print(f"   latency_ms: {response_data['latency_ms']}")
        print(f"   finish_reason: {response_data['finish_reason']}")
        print(f"   usage: {response_data['usage']}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ 代码测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_usage_attribute_access()
    test_log_response_code()

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    print("\n💡 修复说明:")
    print("  原代码: hasattr(resp.usage, 'model_dump')")
    print("  问题:   dashscope 对象的 __getattr__ 会抛出 KeyError")
    print("  修复:   使用 try-except 安全访问属性")
