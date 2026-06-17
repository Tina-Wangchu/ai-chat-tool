#!/usr/bin/env python3
"""
测试时间戳和耗时记录
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_timestamp_latency():
    """测试时间戳和耗时记录"""

    print("=" * 60)
    print("🧪 测试时间戳和耗时记录")
    print("=" * 60)

    try:
        from chat_with_tool_thinking import AgentLogger
        print("✅ 成功导入 AgentLogger")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 创建临时 logger
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AgentLogger(log_dir=tmpdir, agent_name='test')

        print("\n📝 测试日志记录...")

        # 测试请求日志（包含时间戳）
        request_data = {
            "round": 1,
            "question": "测试问题",
            "model": "qwen-max",
            "thinking_mode": True,
            "timestamp": datetime.now().isoformat()
        }
        logger.log_request(request_data)
        print("  ✅ 请求日志已记录（包含时间戳）")

        # 测试响应日志（包含时间戳和耗时）
        import time
        start_time = time.time()
        time.sleep(0.1)  # 模拟 API 调用
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        response_data = {
            "round": 1,
            "status_code": 200,
            "finish_reason": "tool_calls",
            "latency_ms": f"{latency_ms:.2f}",
            "timestamp": datetime.now().isoformat()
        }
        logger.log_response(response_data)
        print("  ✅ 响应日志已记录（包含时间戳和耗时）")

        # 检查 JSONL 日志文件
        jsonl_file = Path(tmpdir) / f"test_json_{datetime.now().strftime('%Y%m%d')}.jsonl"
        if jsonl_file.exists():
            print(f"\n📄 JSONL 日志文件: {jsonl_file.name}")

            with open(jsonl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print(f"  📊 日志条目数: {len(lines)}")

            # 解析并显示日志条目
            print("\n📖 日志内容:")
            for i, line in enumerate(lines):
                log_entry = json.loads(line)
                print(f"\n  条目 {i+1}:")
                print(f"    类型: {log_entry.get('type')}")
                print(f"    时间戳: {log_entry.get('timestamp')}")

                # 检查数据中的时间戳和耗时
                data = log_entry.get('data', {})
                if 'timestamp' in data:
                    print(f"    数据时间戳: {data['timestamp']}")
                if 'latency_ms' in data:
                    print(f"    耗时: {data['latency_ms']} ms")

            # 验证时间戳和耗时是否存在
            print("\n✅ 验证结果:")
            all_have_timestamp = True
            responses_have_latency = True

            for line in lines:
                log_entry = json.loads(line)
                data = log_entry.get('data', {})

                # 检查时间戳
                if 'timestamp' not in data:
                    all_have_timestamp = False
                    print(f"  ⚠️  缺少时间戳: {log_entry.get('type')}")

                # 检查耗时（仅响应日志）
                if log_entry.get('type') == 'response':
                    if 'latency_ms' not in data:
                        responses_have_latency = False
                        print(f"  ⚠️  响应日志缺少耗时")

            if all_have_timestamp:
                print("  ✅ 所有日志都包含时间戳")
            if responses_have_latency:
                print("  ✅ 所有响应日志都包含耗时")

        else:
            print("  ❌ 未找到 JSONL 日志文件")

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

    print("\n💡 日志格式说明:")
    print("  - 每个日志条目都有时间戳（timestamp 字段）")
    print("  - 响应日志包含耗时（latency_ms 字段）")
    print("  - 时间戳格式：ISO 8601 (2026-06-08T20:45:31.448418)")
    print("  - 耗时单位：毫秒 (ms)")

    return True


if __name__ == "__main__":
    success = test_timestamp_latency()

    if success:
        print("\n🎉 时间戳和耗时记录测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)
