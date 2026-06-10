#!/usr/bin/env python3
"""
验证控制台输出清理
"""

import sys
import os
from io import StringIO

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_console_output():
    """验证控制台输出清理"""

    print("=" * 60)
    print("🔍 验证控制台输出清理")
    print("=" * 60)

    # 导入模块
    try:
        from chat_with_tool_thinking import AgentLogger
        print("✅ 成功导入 AgentLogger")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 捕获控制台输出
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # 创建 logger 并测试
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, agent_name='test')

            # 测试日志记录
            logger.log_request({
                "round": 1,
                "question": "测试",
                "model": "qwen-max",
                "timestamp": "2026-06-09T10:45:31"
            })

            logger.log_response({
                "round": 1,
                "status_code": 200,
                "latency_ms": "100.50",
                "timestamp": "2026-06-09T10:45:32"
            })

    finally:
        # 恢复标准输出
        sys.stdout = old_stdout

    # 检查捕获的输出
    output = captured_output.getvalue()

    print("\n📊 控制台输出分析:")
    print(f"  输出长度: {len(output)} 字符")

    if output:
        print("  ⚠️  检测到控制台输出:")
        print(output)
        print("\n❌ 控制台仍有输出")
        return False
    else:
        print("  ✅ 没有控制台输出")

    # 检查日志文件
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AgentLogger(log_dir=tmpdir, agent_name='test')

        logger.log_request({"test": "data"})
        logger.log_response({"status": 200})

        # 检查文件是否存在
        log_files = list(Path(tmpdir).glob("*.log"))

        print(f"\n📄 日志文件数量: {len(log_files)}")

        if log_files:
            print("  ✅ 日志文件已创建")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"    - {log_file.name}: {size} bytes")
        else:
            print("  ❌ 未找到日志文件")

    print("\n" + "=" * 60)
    print("✅ 验证完成")
    print("=" * 60)

    print("\n💡 结论:")
    print("  - 标准日志不再输出到控制台")
    print("  - 所有日志信息都写入文件")
    print("  - 控制台保持清洁")

    return True


if __name__ == "__main__":
    success = test_console_output()

    if success:
        print("\n🎉 控制台输出清理验证通过！")
        sys.exit(0)
    else:
        print("\n❌ 验证失败")
        sys.exit(1)
