#!/usr/bin/env python3
"""
工具调用验证脚本 - 简单直接的测试
"""

import subprocess
import sys

print("=" * 70)
print("🔍 工具调用验证测试")
print("=" * 70)

# 简单测试：查询南京天气
test_input = """1
南京今天的天气怎么样？
quit
"""

print("\n📋 测试场景：")
print("   角色：天气预报员")
print("   问题：南京今天的天气怎么样？")
print("   目标：验证AI是否使用真实天气数据")

print("\n⏳ 运行测试...\n")

try:
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool'
    )

    stdout, stderr = process.communicate(input=test_input, timeout=60)

    # 检查输出中的关键数据
    print("=" * 70)
    print("📊 测试结果分析")
    print("=" * 70)

    # 提取AI回复
    lines = stdout.split('\n')
    ai_response = ""
    for line in lines:
        if '🤖 AI:' in line:
            # 提取AI回复内容
            idx = line.index('🤖 AI:')
            ai_response = line[idx+5:].strip()
            break

    if ai_response:
        print(f"\n📝 AI回复片段（前200字符）：")
        print("-" * 70)
        print(ai_response[:200])
        print("-" * 70)

        # 检查真实数据指标
        real_data_indicators = [
            '21°C',
            '30°C',
            '阴',
            '东南风',
            '1-3级',
            '湿度'
        ]

        found_indicators = []
        for indicator in real_data_indicators:
            if indicator in ai_response:
                found_indicators.append(indicator)

        print(f"\n🔍 数据真实性检查：")
        print(f"   找到的真实数据点：{len(found_indicators)}/{len(real_data_indicators)}")

        if found_indicators:
            print(f"   ✅ 检测到的数据：{', '.join(found_indicators)}")
            print(f"\n🎉 结论：工具调用正常，AI使用了真实天气数据！")
        else:
            print(f"   ⚠️ 未检测到预期的真实数据点")
            print(f"   💡 AI可能使用了通用知识或模板回复")

            # 检查是否有占位符
            if 'X°C' in ai_response or 'Y°C' in ai_response:
                print(f"   ❌ 发现模板占位符（X°C、Y°C等）")
                print(f"   这表明AI没有收到工具返回的真实数据")

    else:
        print("\n⚠️ 未找到AI回复")

    # 显示工具调用日志
    print("\n" + "=" * 70)
    print("📄 最新的工具调用日志（最后5条）")
    print("=" * 70)

    try:
        with open('logs/weather_agent_tool_20260613.log', 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(line.strip())
    except:
        print("无法读取工具日志")

except subprocess.TimeoutExpired:
    print("\n⏰ 测试超时")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
