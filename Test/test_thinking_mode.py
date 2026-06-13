#!/usr/bin/env python3
"""
Thinking Mode 日志功能测试脚本

测试目标：
1. 验证 thinking mode 参数格式是否正确
2. 验证思考推理流程是否正确记录到日志
3. 对比启用和禁用 thinking mode 的差异

测试问题：
- 简单问题：南京今天的天气怎么样？（不需要复杂推理）
- 复杂问题：根据今天南京和上海的天气，哪个城市更适合户外运动？需要对比分析。（适合测试thinking mode）
"""

import subprocess
import time
import sys
from pathlib import Path

def test_thinking_mode():
    """测试thinking mode日志功能"""

    print("=" * 60)
    print("🧪 Thinking Mode 日志功能测试")
    print("=" * 60)

    # 准备测试输入
    # 1. 选择角色（妈妈角色 - 编号3）
    # 2. 启用 thinking mode（输入 /thinking 然后选择 1）
    # 3. 问复杂问题：根据今天南京和上海的天气，哪个城市更适合户外运动？
    # 4. 退出

    test_inputs = [
        "3\n",  # 选择角色：妈妈
        "/thinking\n",  # 进入thinking模式菜单
        "1\n",  # 启用thinking mode
        "根据今天南京和上海的天气对比分析，哪个城市更适合户外运动？请给出详细理由。\n",  # 复杂问题
        "quit\n"  # 退出
    ]

    print("\n📋 测试计划：")
    print("1. ✅ 选择角色：妈妈")
    print("2. ✅ 启用 thinking mode")
    print("3. ✅ 提问：根据今天南京和上海的天气对比分析，哪个城市更适合户外运动？")
    print("4. ✅ 观察日志输出")
    print("\n⏳ 开始测试...\n")

    # 运行main.py
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )

        # 发送输入
        for input_text in test_inputs:
            time.sleep(2)  # 等待程序处理
            process.stdin.write(input_text)
            process.stdin.flush()

        # 等待完成
        time.sleep(10)
        process.stdin.close()
        process.terminate()

        stdout, stderr = process.communicate(timeout=30)

        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)

        # 显示输出
        print("\n📤 程序输出：")
        print("-" * 60)
        print(stdout[-5000:] if len(stdout) > 5000 else stdout)  # 显示最后5000字符
        print("-" * 60)

        if stderr:
            print("\n⚠️ 错误输出：")
            print("-" * 60)
            print(stderr)
            print("-" * 60)

        # 检查日志文件
        check_log_files()

    except subprocess.TimeoutExpired:
        print("\n⏰ 测试超时")
        process.kill()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")

def check_log_files():
    """检查日志文件是否生成并显示内容"""

    print("\n" + "=" * 60)
    print("📊 日志文件检查")
    print("=" * 60)

    log_dir = Path("logs")
    if not log_dir.exists():
        print("❌ 日志目录不存在")
        return

    # 查找最新的日志文件
    log_files = {
        "主日志": list(log_dir.glob("weather_agent_*.log")),
        "思考日志": list(log_dir.glob("weather_agent_thinking_*.log")),
        "API日志": list(log_dir.glob("weather_agent_api_*.log")),
        "JSON日志": list(log_dir.glob("weather_agent_json_*.jsonl"))
    }

    for log_type, files in log_files.items():
        if files:
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            print(f"\n✅ {log_type}: {latest_file.name}")
            print(f"   大小: {latest_file.stat().st_size} bytes")
            print(f"   修改时间: {time.ctime(latest_file.stat().st_mtime)}")

            # 显示最后几行内容
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   总行数: {len(lines)}")
                        print(f"   最后内容:")
                        for line in lines[-10:]:
                            print(f"      {line.rstrip()}")
            except Exception as e:
                print(f"   ⚠️ 读取文件出错: {e}")
        else:
            print(f"\n❌ {log_type}: 未找到")

    # 特别检查thinking日志
    print("\n" + "-" * 60)
    print("🧠 思考日志详细检查")
    print("-" * 60)

    thinking_logs = list(log_dir.glob("weather_agent_thinking_*.log"))
    if thinking_logs:
        latest_thinking = max(thinking_logs, key=lambda p: p.stat().st_mtime)
        print(f"\n📄 文件: {latest_thinking.name}")

        try:
            with open(latest_thinking, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')

                print(f"📊 统计信息:")
                print(f"   - 总行数: {len(lines)}")
                print(f"   - 总字符数: {len(content)}")

                # 检查是否有思考内容
                reasoning_entries = [l for l in lines if 'reasoning' in l.lower() or 'thinking' in l.lower() or '思考' in l]
                print(f"   - 思考相关行数: {len(reasoning_entries)}")

                if reasoning_entries:
                    print(f"\n✅ 发现思考内容记录！")
                    print(f"\n前5条思考记录:")
                    for line in reasoning_entries[:5]:
                        print(f"   {line}")
                else:
                    print(f"\n⚠️ 未发现明显的思考内容标记")

                print(f"\n完整内容预览（最后20行）:")
                for line in lines[-20:]:
                    print(f"   {line}")

        except Exception as e:
            print(f"❌ 读取thinking日志出错: {e}")
    else:
        print("❌ 未找到thinking日志文件")

    print("\n" + "=" * 60)
    print("💡 提示：请检查上述日志文件，确认thinking mode的推理过程是否被正确记录")
    print("=" * 60)

if __name__ == "__main__":
    test_thinking_mode()
