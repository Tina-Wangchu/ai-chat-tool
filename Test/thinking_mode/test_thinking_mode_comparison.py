#!/usr/bin/env python3
"""
对比测试：thinking mode开启 vs 关闭时的工具调用效果

目标：验证thinking mode是否影响AI使用工具返回的数据
"""

import subprocess
import sys
import os
from pathlib import Path

# 切换到ai-chat-tool目录
os.chdir('/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool')

def test_with_thinking_mode(thinking_enabled):
    """测试thinking mode开启/关闭时的效果"""

    mode = "启用" if thinking_enabled else "关闭"
    print("\n" + "=" * 70)
    print(f"🧪 测试：Thinking Mode {mode}")
    print("=" * 70)

    # 准备测试输入
    if thinking_enabled:
        # 启用thinking mode
        test_input = """3
1
南京今天的天气怎么样？请详细说明温度、天气状况和风力。
quit
"""
    else:
        # 不启用thinking mode（默认就是关闭）
        test_input = """3
南京今天的天气怎么样？请详细说明温度、天气状况和风力。
quit
"""

    print(f"\n📋 测试输入：")
    print("   角色：妈妈")
    print(f"   Thinking Mode：{'启用' if thinking_enabled else '关闭'}")
    print("   问题：南京今天的天气怎么样？")
    print("\n⏳ 开始测试...\n")

    try:
        # 运行程序
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool'
        )

        # 发送输入
        stdout, stderr = process.communicate(input=test_input, timeout=120)

        print("\n" + "=" * 70)
        print("✅ 程序执行完成")
        print("=" * 70)

        # 提取AI回复
        lines = stdout.split('\n')
        ai_response_started = False
        ai_response_lines = []

        for line in lines:
            if '🤖 AI:' in line or ai_response_started:
                ai_response_started = True
                ai_response_lines.append(line)

        if ai_response_lines:
            ai_response = '\n'.join(ai_response_lines).replace('🤖 AI: ', '').strip()
            print(f"\n📝 AI回复：")
            print("-" * 70)
            print(ai_response[:500])
            print("-" * 70)

            # 检查是否包含真实数据
            has_real_data = False
            indicators = ['21°C', '30°C', '阴', '东南风', '1-3级']

            for indicator in indicators:
                if indicator in ai_response:
                    has_real_data = True
                    break

            print(f"\n🔍 数据分析：")
            print(f"   包含真实天气数据：{'✅ 是' if has_real_data else '❌ 否'}")

            if has_real_data:
                print(f"   检测到的数据点：")
                for indicator in indicators:
                    if indicator in ai_response:
                        print(f"      - {indicator}")
            else:
                print(f"   ⚠️ AI似乎使用了模板或通用知识")

            return {
                'thinking_enabled': thinking_enabled,
                'has_real_data': has_real_data,
                'response': ai_response
            }
        else:
            print("\n⚠️ 未找到AI回复")
            return None

    except subprocess.TimeoutExpired:
        print("\n⏰ 程序运行超时（120秒）")
        process.kill()
        return None
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主测试函数"""

    print("=" * 70)
    print("🔬 Thinking Mode对工具调用的影响测试")
    print("=" * 70)
    print("\n目标：验证thinking mode是否会影响AI使用工具返回的数据")

    results = []

    # 测试1：关闭thinking mode
    result1 = test_with_thinking_mode(thinking_enabled=False)
    if result1:
        results.append(result1)

    # 测试2：启用thinking mode
    result2 = test_with_thinking_mode(thinking_enabled=True)
    if result2:
        results.append(result2)

    # 对比结果
    print("\n" + "=" * 70)
    print("📊 测试结果对比")
    print("=" * 70)

    if len(results) == 2:
        print(f"\n{'模式':<20} {'使用真实数据':<20}")
        print("-" * 70)

        for r in results:
            mode = "Thinking Mode启用" if r['thinking_enabled'] else "Thinking Mode关闭"
            data_status = "✅ 是" if r['has_real_data'] else "❌ 否"
            print(f"{mode:<20} {data_status:<20}")

        print("\n" + "=" * 70)
        print("💡 结论")
        print("=" * 70)

        if results[0]['has_real_data'] and results[1]['has_real_data']:
            print("\n✅ 两种模式都正确使用工具返回的数据")
            print("   Thinking Mode不影响工具调用功能")
        elif results[0]['has_real_data'] and not results[1]['has_real_data']:
            print("\n⚠️ 发现问题：")
            print("   - Thinking Mode关闭时：✅ 使用真实数据")
            print("   - Thinking Mode启用时：❌ 使用模板/通用知识")
            print("\n   这表明Thinking Mode可能干扰了工具结果的传递")
        elif not results[0]['has_real_data'] and not results[1]['has_real_data']:
            print("\n❌ 两种模式都没有使用真实数据")
            print("   工具调用系统可能存在问题")
        else:
            print("\n🤔 意外的结果模式")

    else:
        print("\n⚠️ 测试未完成，缺少对比数据")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
