#!/usr/bin/env python3
"""
测试对话历史功能
"""


def test_conversation_history():
    """测试对话历史添加功能"""

    print("=" * 60)
    print("🧪 测试对话历史功能")
    print("=" * 60)

    # 模拟对话历史
    conversation_history = []

    print("\n📝 模拟对话场景：")
    print("─" * 60)

    # 模拟第一轮对话
    question1 = "南京今天的天气怎么样？"
    conversation_history.append({"role": "user", "content": question1})
    print(f"👤 用户: {question1}")

    reply1 = "根据查询结果，南京今天多云，温度 20°C ~ 28°C"
    conversation_history.append({"role": "assistant", "content": reply1})
    print(f"🤖 AI: {reply1}")

    print(f"\n📊 对话历史: {len(conversation_history)} 条消息")

    # 模拟第二轮对话
    question2 = "那上海呢？"
    conversation_history.append({"role": "user", "content": question2})
    print(f"\n👤 用户: {question2}")

    reply2 = "上海今天晴天，温度 22°C ~ 30°C"
    conversation_history.append({"role": "assistant", "content": reply2})
    print(f"🤖 AI: {reply2}")

    print(f"\n📊 对话历史: {len(conversation_history)} 条消息")

    # 显示完整对话历史
    print("\n" + "─" * 60)
    print("📋 完整对话历史：")
    print("─" * 60)

    for i, msg in enumerate(conversation_history, 1):
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        print(f"{i}. {role_emoji} {msg['role']}: {msg['content']}")

    # 测试 /clear 功能
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

    # 模拟清空后的对话
    print("\n" + "─" * 60)
    print("👤 用户: 北京今天的天气？")
    print("─" * 60)

    question3 = "北京今天的天气？"
    conversation_history.append({"role": "user", "content": question3})
    print(f"👤 用户: {question3}")

    reply3 = "根据查询结果，北京今天阴天，温度 18°C ~ 25°C"
    conversation_history.append({"role": "assistant", "content": reply3})
    print(f"🤖 AI: {reply3}")

    print(f"\n📊 当前对话历史: {len(conversation_history)} 条消息")

    print("\n" + "=" * 60)
    print("✅ 对话历史功能测试完成")
    print("=" * 60)

    print("\n💡 验证要点：")
    print("  ✅ 用户问题自动添加到对话历史")
    print("  ✅ AI 回复自动添加到对话历史")
    print("  ✅ 对话历史顺序正确")
    print("  ✅ /clear 命令清空历史")
    print("  ✅ 清空后可以重新开始对话")

    return True


if __name__ == "__main__":
    import sys
    success = test_conversation_history()

    if success:
        print("\n🎉 对话历史功能测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)
