#!/usr/bin/env python3
"""
测试 AI 响应为空的问题

这个脚本用于测试和调试 AI 回复为空的情况。
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("🧪 测试 AI 响应为空的问题")
print("=" * 70)
print()

print("📋 测试问题：")
print("  1. 简单问题：今天南京的天气如何")
print("  2. 复杂问题：对比一下西安和昆明的天气")
print()

print("🔍 调试信息：")
print("  - 检查 API 响应的 content 字段")
print("  - 检查思考模式下的响应结构")
print("  - 验证 content 为空时的处理")
print()

print("=" * 70)
print("💡 建议：")
print("=" * 70)
print()
print("如果 AI 回复仍然为空，可能的原因：")
print()
print("1. **思考模式问题**")
print("   - 启用思考模式时，API 响应的 content 可能在不同位置")
print("   - 需要检查 thinking 字段或其他特殊字段")
print()
print("2. **多城市查询问题**")
print("   - 问题要求对比两个城市，但 AI 只调用了一次工具")
print("   - 需要支持多轮工具调用")
print()
print("3. **API 配置问题**")
print("   - 模型不支持思考模式")
print("   - 需要检查模型配置和 API 版本")
print()
print("4. **响应解析问题**")
print("   - content 字段结构变化")
print("   - 需要添加更详细的调试日志")
print()
print("=" * 70)
print("🚀 运行测试：")
print("=" * 70)
print()
print("cd /Users/tinawang/sophomore_tina/26Summer/ai-chat-tool")
print("python temperature_tester.py --temperature 0.7 --thinking-mode off")
print()
print("或者先关闭思考模式测试：")
print("python temperature_tester.py --temperature 0.7 --thinking-mode off")
print()
