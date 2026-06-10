#!/usr/bin/env python3
"""
Temperature 对比实验快速验证脚本

验证修改后的 temperature_experiment.txt 和 temperature_tester.py 是否正确。
"""

import sys
import os

print("=" * 70)
print("🧪 Temperature 对比实验验证")
print("=" * 70)
print()

# 添加项目路径
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

print("📋 实验配置验证：")
print()

# 1. 验证实验文件
print("1. 检查 temperature_experiment.txt")
experiment_file = os.path.join(project_dir, "temperature_experiment.txt")

try:
    with open(experiment_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"✅ 文件存在：{experiment_file}")
    print()
    print("文件内容：")
    print("-" * 70)
    print(content)
    print("-" * 70)
    print()

    # 解析配置
    lines = content.strip().split('\n')
    temps = []
    questions = []
    repeats = 1

    for line in lines:
        line = line.strip()
        if line.startswith("Temperature to be tested:"):
            temp_str = line.split(":", 1)[1].strip()
            temps = [float(t.strip()) for t in temp_str.split()]
        elif line.startswith("Repeats per question:"):
            repeats = int(line.split(":", 1)[1].strip())
        elif line.startswith("Question"):
            question = line.split(":", 1)[1].strip()
            questions.append(question)

    print("解析结果：")
    print(f"  - 温度值（{len(temps)}个）：{temps}")
    print(f"  - 问题数量（{len(questions)}个）")
    print(f"  - 重复次数：{repeats}")
    print(f"  - 总测试次数：{len(temps) * len(questions) * repeats}")
    print()

    if len(temps) == 3 and len(questions) == 2 and repeats == 3:
        print("✅ 配置正确！")
    else:
        print("⚠️  配置不符合预期")
        print(f"   预期：3个温度，2个问题，重复3次")
        print(f"   实际：{len(temps)}个温度，{len(questions)}个问题，重复{repeats}次")

except FileNotFoundError:
    print(f"❌ 文件不存在：{experiment_file}")
    print()
    print("请确认文件路径正确")

print()
print("=" * 70)
print("🚀 运行实验")
print("=" * 70)
print()
print("cd /Users/tinawang/sophomore_tina/26Summer/ai-chat-tool")
print("python temperature_tester.py --batch-test --clear-logs")
print()
print("预期结果：")
print("  - 总共 18 次测试（3个温度 × 2个问题 × 3次重复）")
print("  - 每个温度生成 6 条 AI 输出")
print("  - 可以对比不同 temperature 的回复差异")
print()
print("=" * 70)
print("📊 查看结果")
print("=" * 70)
print()
print("查看 AI 输出：")
print("  cat logs/temperature:0.0_outputs.log")
print("  cat logs/temperature:0.5_outputs.log")
print("  cat logs/temperature:1.0_outputs.log")
print()
print("对比同一问题的多次运行：")
print("  grep '运行 1/3' logs/temperature:0.0_outputs.log")
print("  grep '运行 2/3' logs/temperature:0.0_outputs.log")
print("  grep '运行 3/3' logs/temperature:0.0_outputs.log")
print()
print("对比不同 temperature：")
print("  echo '=== Temp 0.0 ===' && grep -A 5 'Question1' logs/temperature:0.0_outputs.log | head -10")
print("  echo '=== Temp 1.0 ===' && grep -A 5 'Question1' logs/temperature:1.0_outputs.log | head -10")
print()
print("=" * 70)
