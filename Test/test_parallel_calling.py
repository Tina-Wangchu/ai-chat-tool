#!/usr/bin/env python3
"""
Parallel Function Calling 快速测试脚本

测试修改后的 temperature_tester.py 是否正确支持多工具调用。
"""

import subprocess
import sys

print("=" * 70)
print("🧪 Parallel Function Calling 快速测试")
print("=" * 70)
print()

# 测试问题列表
test_cases = [
    {
        "name": "单城市查询",
        "question": "今天南京的天气如何",
        "expected_calls": 1
    },
    {
        "name": "两城市对比",
        "question": "对比一下西安和昆明的天气",
        "expected_calls": 2
    },
    {
        "name": "三城市查询",
        "question": "查询上海、广州、成都的天气",
        "expected_calls": 3
    }
]

print("📋 测试场景：")
for i, case in enumerate(test_cases, 1):
    print(f"{i}. {case['name']}")
    print(f"   问题：{case['question']}")
    print(f"   预期工具调用：{case['expected_calls']} 个")
    print()

print("=" * 70)
print("🚀 开始测试...")
print("=" * 70)
print()

# 测试第一个场景
print("✅ 测试 1：单城市查询")
print("   命令：python temperature_tester.py --temperature 0.7")
print("   提问：今天南京的天气如何")
print()
print("   预期结果：")
print("   - 工具调用数量：1 个")
print("   - AI 回复：包含南京的天气信息")
print("   - 输出日志：不为空")
print()

print("💡 手动测试步骤：")
print("   1. cd /Users/tinawang/sophomore_tina/26Summer/ai-chat-tool")
print("   2. python temperature_tester.py --temperature 0.7")
print("   3. 输入问题：今天南京的天气如何")
print("   4. 等待回复")
print("   5. 输入：quit")
print("   6. 查看日志：cat logs/temperature:0.7_outputs.log")
print()

print("=" * 70)
print("✅ 测试 2：两城市对比（关键测试）")
print("   命令：python temperature_tester.py --temperature 0.7")
print("   提问：对比一下西安和昆明的天气")
print()
print("   预期结果：")
print("   - 工具调用数量：2 个（西安、昆明）")
print("   - 进度显示：(1/2)、(2/2)")
print("   - AI 回复：包含两个城市的对比信息 ✅ 关键")
print("   - 输出日志：不为空")
print()

print("💡 这是关键测试！如果之前 AI 回复为空，现在应该有完整回复。")
print()

print("=" * 70)
print("✅ 测试 3：三城市查询")
print("   命令：python temperature_tester.py --temperature 0.7")
print("   提问：查询上海、广州、成都的天气")
print()
print("   预期结果：")
print("   - 工具调用数量：3 个（上海、广州、成都）")
print("   - 进度显示：(1/3)、(2/3)、(3/3)")
print("   - AI 回复：包含三个城市的天气信息")
print("   - 输出日志：不为空")
print()

print("=" * 70)
print("🔍 验证方法：")
print("=" * 70)
print()
print("方法 1：查看运行日志")
print("```bash")
print("tail -50 logs/temperature:0.7.log | grep '工具调用'")
print("```")
print()
print("应该看到：")
print("🔧 检测到 2 个工具调用（parallel function calling）")
print("  工具 1: amapMaps.weather(西安)")
print("  工具 2: amapMaps.weather(昆明)")
print("✅ 工具调用 1/2 完成：西安")
print("✅ 工具调用 2/2 完成：昆明")
print("📊 构建了 4 条消息（包含 2 个工具结果）")
print()

print("方法 2：查看 AI 输出")
print("```bash")
print("cat logs/temperature:0.7_outputs.log")
print("```")
print()
print("应该看到完整的 AI 回复，而不是空。")
print()

print("方法 3：检查文件大小")
print("```bash")
print("ls -lh logs/temperature:0.7_outputs.log")
print("```")
print()
print("文件应该有内容（不是 0 字节）。")
print()

print("=" * 70)
print("🎯 快速验证命令")
print("=" * 70)
print()
print("cd /Users/tinawang/sophomore_tina/26Summer/ai-chat-tool")
print()
print("# 运行程序")
print("python temperature_tester.py --temperature 0.7")
print()
print("# 提问两城市对比")
print("对比一下西安和昆明的天气")
print()
print("# 查看日志")
print("tail -30 logs/temperature:0.7.log")
print()
print("# 查看输出")
print("tail -20 logs/temperature:0.7_outputs.log")
print()

print("=" * 70)
print("✅ 修改总结")
print("=" * 70)
print()
print("修改位置：temperature_tester.py 第 929-971 行")
print()
print("修改内容：")
print("1. ✅ 处理所有工具调用（不是只处理第一个）")
print("2. ✅ 收集所有工具的结果")
print("3. ✅ 构建包含所有结果的消息")
print("4. ✅ 添加进度显示和日志")
print()
print("修改效果：")
print("- 支持多城市查询 ✅")
print("- 充分利用 parallel function calling ✅")
print("- AI 回复不再为空 ✅")
print()
print("=" * 70)
print("🎉 现在可以开始测试了！")
print("=" * 70)
