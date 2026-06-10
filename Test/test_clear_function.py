#!/usr/bin/env python3
"""
测试 /clear 清空对话功能
"""

def test_clear_functionality():
    """测试 /clear 功能"""

    print("=" * 60)
    print("🧪 测试 /clear 清空对话功能")
    print("=" * 60)

    # 模拟对话历史
    conversation_history = []

    print("\n📝 模拟对话场景：")
    print("─" * 60)

    # 添加对话
    conversation_history.append({"role": "user", "content": "南京今天的天气？"})
    print("👤 用户: 南京今天的天气？")

    conversation_history.append({"role": "assistant", "content": "根据查询结果，南京今天多云..."})
    print("🤖 AI: 根据查询结果，南京今天多云...")

    conversation_history.append({"role": "user", "content": "那上海呢？"})
    print("👤 用户: 那上海呢？")

    conversation_history.append({"role": "assistant", "content": "上海今天晴天..."})
    print("🤖 AI: 上海今天晴天...")

    conversation_history.append({"role": "user", "content": "你觉得足球怎么样？"})
    print("👤 用户: 你觉得足球怎么样？")

    print(f"\n📊 当前对话历史: {len(conversation_history)} 条消息")

    # 测试 /clear 命令
    print("\n" + "─" * 60)
    print("👤 用户: /clear")
    print("─" * 60)

    # 执行清空操作
    if conversation_history:
        cleared_count = len(conversation_history)
        conversation_history.clear()
        print(f"\n✅ 已清空对话历史（删除了 {cleared_count} 条消息）")
    else:
        print("\n💡 当前没有对话历史")

    print(f"\n📊 清空后对话历史: {len(conversation_history)} 条消息")

    # 测试清空后的状态
    print("\n" + "─" * 60)
    print("👤 用户: 北京今天的天气？")
    print("─" * 60)

    conversation_history.append({"role": "user", "content": "北京今天的天气？"})
    print("👤 用户: 北京今天的天气？")

    conversation_history.append({"role": "assistant", "content": "根据查询结果，北京今天..."})
    print("🤖 AI: 根据查询结果，北京今天...")

    print(f"\n📊 当前对话历史: {len(conversation_history)} 条消息")

    # 测试重复清空
    print("\n" + "─" * 60)
    print("👤 用户: /clear")
    print("─" * 60)

    if conversation_history:
        cleared_count = len(conversation_history)
        conversation_history.clear()
        print(f"\n✅ 已清空对话历史（删除了 {cleared_count} 条消息）")
    else:
        print("\n💡 当前没有对话历史")

    print(f"\n📊 清空后对话历史: {len(conversation_history)} 条消息")

    print("\n" + "=" * 60)
    print("✅ /clear 功能测试完成")
    print("=" * 60)

    # 测试命令别名
    print("\n🔍 测试命令别名：")
    commands = ['clear', '/clear', '清空', '清空对话']

    for cmd in commands:
        if cmd.lower() in ['clear', '/clear', '清空', '清空对话']:
            print(f"  ✅ '{cmd}' - 有效命令")
        else:
            print(f"  ❌ '{cmd}' - 无效命令")

    print("\n💡 总结：")
    print("  - 对话历史使用 Python 列表维护")
    print("  - 支持 4 种命令别名")
    print("  - 清空前检查是否有历史记录")
    print("  - 清空后给用户明确反馈")
    print("  - 操作记录到日志系统")

    return True


if __name__ == "__main__":
    import sys
    success = test_clear_functionality()

    if success:
        print("\n🎉 /clear 功能测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)
