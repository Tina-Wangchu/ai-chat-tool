#!/usr/bin/env python3
"""简单的thinking mode测试"""
import subprocess
import sys
import time
from pathlib import Path

# 准备测试输入
test_input = """3
/thinking
1
根据今天南京和上海的天气对比分析，哪个城市更适合户外运动？请给出详细理由。
quit
"""

print("=" * 60)
print("🧪 Thinking Mode 日志功能测试")
print("=" * 60)
print("\n测试输入：")
print("1. 选择角色：妈妈")
print("2. 启用 thinking mode")
print("3. 提问：南京和上海天气对比分析")
print("\n⏳ 开始测试...\n")

try:
    # 切换到main.py所在目录
    import os
    os.chdir('/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool')

    # 运行程序
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 发送输入
    stdout, stderr = process.communicate(input=test_input, timeout=60)

    print("\n" + "=" * 60)
    print("✅ 程序执行完成")
    print("=" * 60)

    # 显示输出（最后部分）
    if stdout:
        print("\n📤 程序输出（最后3000字符）：")
        print("-" * 60)
        print(stdout[-3000:] if len(stdout) > 3000 else stdout)
        print("-" * 60)

    if stderr:
        print("\n⚠️ 错误输出：")
        print("-" * 60)
        print(stderr[-1000:] if len(stderr) > 1000 else stderr)
        print("-" * 60)

except subprocess.TimeoutExpired:
    print("\n⏰ 程序运行超时（60秒）")
    process.kill()
except Exception as e:
    print(f"\n❌ 测试出错: {e}")
    import traceback
    traceback.print_exc()

# 检查日志文件
print("\n" + "=" * 60)
print("📊 日志文件检查")
print("=" * 60)

log_dir = Path("logs")
if log_dir.exists():
    # 列出所有日志文件
    log_files = sorted(log_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)

    if log_files:
        print(f"\n找到 {len(log_files)} 个日志文件：\n")
        for log_file in log_files[:10]:  # 只显示最新的10个
            size = log_file.stat().st_size
            mtime = time.ctime(log_file.stat().st_mtime)
            print(f"  📄 {log_file.name}")
            print(f"     大小: {size} bytes | 修改时间: {mtime}")

            # 如果是thinking日志，显示内容摘要
            if "thinking" in log_file.name:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.strip().split('\n')
                        print(f"     📊 行数: {len(lines)} | 字符数: {len(content)}")
                        if lines:
                            print(f"     📝 最后几行:")
                            for line in lines[-3:]:
                                print(f"        {line[:100]}")
                except:
                    pass
    else:
        print("❌ 日志目录为空")
else:
    print("❌ 日志目录不存在")

print("\n" + "=" * 60)
print("💡 请查看日志目录中的 thinking 日志文件")
print("   路径: /Users/tinawang/sophomore_tina/26Summer/ai-chat-tool/logs/")
print("=" * 60)
