#!/usr/bin/env python3
"""
Temperature 日志测试脚本

测试不同 temperature 值的日志是否正确保存在对应的文件中。
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 测试的 temperature 值
TEMPERATURES = [0.1, 0.5, 0.9]

# 测试问题
TEST_QUESTION = "今天南京的天气如何"

# 日志目录
LOG_DIR = "logs"

print("=" * 70)
print("🧪 Temperature 日志测试")
print("=" * 70)
print(f"测试的 temperature 值：{TEMPERATURES}")
print(f"测试问题：{TEST_QUESTION}")
print(f"日志目录：{LOG_DIR}")
print("=" * 70)
print()

# 清理旧的日志文件
print("📋 步骤 1：清理旧日志文件...")
log_path = Path(LOG_DIR)
if log_path.exists():
    for file in log_path.glob("temperature:*.log"):
        file.unlink()
        print(f"  删除：{file.name}")
print()

# 测试每个 temperature 值
for temp in TEMPERATURES:
    print(f"🧪 步骤 2.{TEMPERATURES.index(temp) + 1}：测试 temperature = {temp}")
    print(f"  命令：python 'main copy.py' --temperature {temp}")
    print(f"  问题：{TEST_QUESTION}")
    print(f"  日志文件：temperature:{temp}.log")
    print()

    # 构建命令
    cmd = [
        sys.executable,
        "main copy.py",
        "--temperature", str(temp),
        "--thinking-mode", "off"
    ]

    print(f"  运行中...")

    # 创建子进程
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 发送问题
    try:
        stdout, stderr = process.communicate(
            input=f"{TEST_QUESTION}\nquit\n",
            timeout=30
        )

        if process.returncode == 0:
            print(f"  ✅ 程序运行成功")
        else:
            print(f"  ⚠️  程序退出码：{process.returncode}")

    except subprocess.TimeoutExpired:
        process.kill()
        print(f"  ⚠️  程序超时，已终止")
    except Exception as e:
        print(f"  ❌ 错误：{e}")

    print()
    time.sleep(1)  # 等待日志写入

# 检查生成的日志文件
print("📋 步骤 3：检查生成的日志文件...")
print()

log_path = Path(LOG_DIR)
found_files = []

for temp in TEMPERATURES:
    expected_file = log_path / f"temperature:{temp}.log"
    if expected_file.exists():
        size = expected_file.stat().st_size
        line_count = 0
        with open(expected_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)

        found_files.append(expected_file)
        print(f"  ✅ 找到：{expected_file.name}")
        print(f"     大小：{size} bytes，行数：{line_count}")
    else:
        print(f"  ❌ 未找到：{expected_file.name}")

print()

# 显示所有日志文件
print("📋 步骤 4：显示所有 temperature 日志文件...")
print()

if log_path.exists():
    temp_files = sorted(log_path.glob("temperature:*.log"))
    if temp_files:
        for file in temp_files:
            size = file.stat().st_size
            print(f"  📄 {file.name} ({size} bytes)")
    else:
        print("  ⚠️  没有找到 temperature 日志文件")

print()

# 总结
print("=" * 70)
print("📊 测试总结")
print("=" * 70)

if len(found_files) == len(TEMPERATURES):
    print(f"✅ 测试通过！所有 {len(TEMPERATURES)} 个 temperature 值的日志文件都已生成")
    print()
    print("生成的日志文件：")
    for file in found_files:
        print(f"  - {file.name}")
else:
    print(f"⚠️  测试部分通过：{len(found_files)}/{len(TEMPERATURES)} 个日志文件已生成")
    print()
    print("未找到的文件：")
    for temp in TEMPERATURES:
        expected_file = log_path / f"temperature:{temp}.log"
        if not expected_file.exists():
            print(f"  - {expected_file.name}")

print()
print("💡 查看日志文件内容：")
print(f"   cat {LOG_DIR}/temperature:0.1.log")
print()
