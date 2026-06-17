#!/usr/bin/env python3
"""
测试纯推理场景下的thinking mode日志记录

这个脚本测试不使用工具调用的复杂问题，
验证reasoning_content是否能被正确记录。
"""

import subprocess
import sys
import os
from pathlib import Path

# 切换到ai-chat-tool目录
os.chdir('/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool')

print("=" * 60)
print("🧪 纯推理场景测试 - Thinking Mode日志记录")
print("=" * 60)

# 测试输入：启用thinking mode，问纯推理问题（不需要工具调用）
test_input = """3
/thinking
1
请用逻辑推理解决这个问题：有三个盒子，其中一个是红色苹果，一个是橘子，一个是空盒子。如果红色苹果不在第一个盒子里，也不在第三个盒子里，那它在哪里？请详细说明你的推理过程。
quit
"""

print("\n📋 测试场景：")
print("- 角色：妈妈")
print("- 启用thinking mode")
print("- 问题：纯逻辑推理（不需要工具调用）")
print("\n⏳ 开始测试...\n")

try:
    # 运行程序
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 发送输入
    stdout, stderr = process.communicate(input=test_input, timeout=120)

    print("\n" + "=" * 60)
    print("✅ 程序执行完成")
    print("=" * 60)

    # 显示输出
    if stdout:
        print("\n📤 程序输出（最后4000字符）：")
        print("-" * 60)
        print(stdout[-4000:] if len(stdout) > 4000 else stdout)
        print("-" * 60)

    # 检查thinking日志
    print("\n" + "=" * 60)
    print("🧠 Thinking日志检查")
    print("=" * 60)

    log_dir = Path("logs")
    thinking_logs = sorted(log_dir.glob("weather_agent_thinking_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)

    if thinking_logs:
        latest_thinking = thinking_logs[0]
        print(f"\n📄 最新Thinking日志: {latest_thinking.name}")
        print(f"   大小: {latest_thinking.stat().st_size} bytes")

        with open(latest_thinking, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')

            print(f"   总行数: {len(lines)}")
            print(f"   总字符数: {len(content)}")

            # 统计包含实际推理内容的行（不只是"思考模式已启用"）
            reasoning_lines = [l for l in lines if 'Content:' in l and '思考模式已启用' not in l and len(l) > 100]

            print(f"   实际推理内容行数: {len(reasoning_lines)}")

            if reasoning_lines:
                print(f"\n✅ 发现实际推理内容！")
                print(f"\n前5条推理记录:")
                for line in reasoning_lines[:5]:
                    print(f"   {line[:150]}")
            else:
                print(f"\n⚠️ 未发现明显的推理内容（只有配置信息）")
                print(f"\n完整日志内容:")
                for line in lines[-10:]:
                    print(f"   {line}")

except subprocess.TimeoutExpired:
    print("\n⏰ 程序运行超时（120秒）")
    process.kill()
except Exception as e:
    print(f"\n❌ 测试出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("💡 说明：")
print("=" * 60)
print("""
1. 如果看到实际推理内容，说明reasoning_content记录功能正常
2. 如果只有配置信息，可能是因为：
   - qwen-max模型在当前场景下不返回reasoning_content
   - 需要使用专门的thinking模式模型（如qwen3-thinking系列）
   - 或者需要不同的提示词来触发推理过程

3. 推理内容应该通过message.reasoning_content字段返回
   并记录到weather_agent_thinking_*.log文件中
""")
print("=" * 60)
