#!/usr/bin/env python3
"""
验证性能日志是否已完全删除
"""

import sys
import os


def verify_performance_removal():
    """验证性能相关代码是否已删除"""

    print("=" * 60)
    print("🔍 验证性能日志删除")
    print("=" * 60)

    # 导入模块
    try:
        from chat_with_tool_thinking import AgentLogger
        print("✅ 成功导入 AgentLogger")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 创建临时 logger 实例
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AgentLogger(log_dir=tmpdir, agent_name='test')

        # 检查是否没有 stats 属性
        if hasattr(logger, 'stats'):
            print("❌ 错误：仍然有 stats 属性")
            return False
        else:
            print("✅ 成功：stats 属性已删除")

        # 检查是否没有 get_stats 方法
        if hasattr(logger, 'get_stats'):
            print("❌ 错误：仍然有 get_stats 方法")
            return False
        else:
            print("✅ 成功：get_stats 方法已删除")

        # 检查是否没有 print_stats 方法
        if hasattr(logger, 'print_stats'):
            print("❌ 错误：仍然有 print_stats 方法")
            return False
        else:
            print("✅ 成功：print_stats 方法已删除")

        # 检查核心日志记录器
        loggers = ['logger', 'json_logger', 'api_logger', 'tool_logger', 'thinking_logger', 'error_logger']
        for attr in loggers:
            if hasattr(logger, attr):
                print(f"✅ {attr} 存在")
            else:
                print(f"❌ {attr} 缺失")
                return False

        # 检查核心方法
        methods = [
            'log_request', 'log_response', 'log_error',
            'log_tool_call', 'log_thinking_process',
            'log_system_event', 'log_conversation'
        ]
        for method in methods:
            if hasattr(logger, method):
                print(f"✅ {method}() 存在")
            else:
                print(f"❌ {method}() 缺失")
                return False

        print(f"\n📁 日志目录: {tmpdir}")
        print(f"📂 文件列表: {os.listdir(tmpdir)}")

    # 检查源代码中没有性能相关的关键词
    print("\n" + "=" * 60)
    print("🔍 检查源代码")
    print("=" * 60)

    source_file = 'chat_with_tool_thinking.py'
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()

    # 检查不应出现的关键词
    forbidden_keywords = [
        'self.stats',
        'get_stats',
        'print_stats',
        'latency_ms',
        'usage_data',
        '/stats',
        '性能统计'
    ]

    found_issues = False
    for keyword in forbidden_keywords:
        if keyword in source:
            print(f"⚠️  发现不应存在的关键词: {keyword}")
            found_issues = True

    if not found_issues:
        print("✅ 没有发现性能相关的关键词")

    print("\n" + "=" * 60)
    print("✅ 验证完成")
    print("=" * 60)

    return not found_issues


if __name__ == "__main__":
    success = verify_performance_removal()

    if success:
        print("\n🎉 所有性能日志已成功删除！")
        sys.exit(0)
    else:
        print("\n❌ 仍有问题需要修复")
        sys.exit(1)
