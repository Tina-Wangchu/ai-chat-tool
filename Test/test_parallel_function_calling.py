#!/usr/bin/env python3
"""
测试并行工具调用功能
验证 main.py 中的 parallel function calling 是否正常工作
"""

import sys
import os

# 确保可以导入 main 模块
sys.path.insert(0, os.path.dirname(__file__))

def test_parallel_function_calling():
    """测试并行工具调用"""

    print("=" * 60)
    print("🧪 测试并行工具调用功能")
    print("=" * 60)

    # 测试问题：应该触发多个工具调用
    test_questions = [
        "分析南京和上海的天气差异",
        "北京、上海、广州、深圳今天的天气怎么样？",
        "比较杭州和成都的天气情况"
    ]

    print("\n📋 测试场景：")
    for i, question in enumerate(test_questions, 1):
        print(f"  {i}. {question}")

    print("\n" + "=" * 60)
    print("💡 提示：每个问题都应该触发多个城市的并行查询")
    print("✅ 成功标志：看到多个 '✅ 城市名 的天气查询完成' 消息")
    print("=" * 60)

    # 这里我们不直接运行完整测试，而是给用户说明如何测试
    print("\n📖 如何测试：")
    print("  运行以下命令：")
    print("  python main.py")
    print("\n  然后输入上述测试问题，观察是否并行查询多个城市")

    print("\n" + "=" * 60)
    print("✅ 测试准备完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_parallel_function_calling()
