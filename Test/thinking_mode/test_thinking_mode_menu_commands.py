#!/usr/bin/env python3
"""
测试思考模式菜单命令处理
"""

def handle_thinking_command(cmd: str, current_thinking_state: bool) -> bool:
    """处理思考模式相关命令"""
    cmd_lower = cmd.lower().strip()

    if cmd_lower in ["启用思考", "开启思考", "1", "on", "enable"]:
        print("\n✅ 思考模式已启用")
        print("🧠 模型将进行深度推理，回答质量更高但响应稍慢")
        return True

    elif cmd_lower in ["关闭思考", "禁用思考", "2", "0", "off", "disable"]:
        print("\n❌ 思考模式已关闭")
        print("⚡ 模型将快速回答，适合简单问题")
        return False

    elif cmd_lower in ["查看", "状态", "3", "status"]:
        print(f"\n📊 当前思考模式状态：{'✅ 已启用' if current_thinking_state else '❌ 未启用'}")
        if current_thinking_state:
            print("💡 思考token预算：1000")
            print("🎯 适用于：复杂推理、多步计算、逻辑分析")
        else:
            print("⚡ 快速回答模式")
            print("🎯 适用于：简单问答、快速查询")
        return current_thinking_state

    elif cmd_lower in ["返回", "back", "4", "exit"]:
        print("\n🔙 返回主对话")
        return current_thinking_state  # 保持当前状态，直接返回

    else:
        print(f"\n⚠️  未知命令：{cmd}")
        print("请输入：启用/关闭思考，或输入'help'查看帮助")
        return current_thinking_state


def test_commands():
    """测试所有命令"""
    print("=" * 60)
    print("🧠 思考模式菜单命令测试")
    print("=" * 60)

    test_cases = [
        # (命令, 当前状态, 期望结果, 描述)
        ("1", False, True, "输入'1'启用思考"),
        ("2", True, False, "输入'2'关闭思考"),
        ("启用思考", False, True, "中文'启用思考'"),
        ("关闭思考", True, False, "中文'关闭思考'"),
        ("3", False, False, "查看状态（当前关闭）"),
        ("3", True, True, "查看状态（当前开启）"),
        ("4", False, False, "返回主对话（保持当前状态）"),
        ("返回", True, True, "中文'返回'"),
        ("unknown", False, False, "未知命令（保持当前状态）"),
    ]

    all_passed = True

    for cmd, current_state, expected_result, description in test_cases:
        print(f"\n📋 测试：{description}")
        print(f"   输入: '{cmd}' | 当前状态: {'开启' if current_state else '关闭'}")

        result = handle_thinking_command(cmd, current_state)

        if result == expected_result:
            print(f"   ✅ 通过 - 结果: {'开启' if result else '关闭'}")
        else:
            print(f"   ❌ 失败 - 期望: {'开启' if expected_result else '关闭'}，实际: {'开启' if result else '关闭'}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("❌ 有测试失败")
    print("=" * 60)


if __name__ == "__main__":
    test_commands()
