# Day 4: 多轮对话实现
# 功能：循环输入、维护对话历史、支持退出和清空

import os
from openai import OpenAI


api_key = os.getenv("DASHSCOPE_API_KEY")

if not api_key:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  export DASHSCOPE_API_KEY='your-key-here'")
    exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 系统提示词
messages = [
    {
        "role": "system",
        "content": "你是一个友好的AI助手，擅长回答问题并提供帮助。"
    }
]

# 获得用户输入函数
def get_user_input():
    user_input = input("\n💬 你: ").strip()

    # 处理特殊命令
    if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
        return '/quit'
    elif user_input.lower() == '/clear':
        return '/clear'
    elif user_input.lower() in ['/help', 'help']:
        return '/help'
    elif not user_input:  # 空输入
        return None

    # 处理 clear 命令的参数（如 clear 10 或 clear -5）
    if user_input.lower().startswith('clear '):
        return user_input  # 返回完整命令供后续处理

    return user_input

def print_help():
    """打印帮助信息"""
    print("\n" + "=" * 60)
    print("📖 命令帮助")
    print("=" * 60)
    print("  /help         - 显示此帮助信息")
    print("  /clear        - 清空所有对话历史")
    print("  /clear N      - 保留最近 N 组对话（1组=用户+AI）")
    print("  /clear -N     - 删除最远的 N 组对话")
    print("  /quit         - 退出程序")
    print("=" * 60)

# 清空历史
"""
    处理 clear 命令：
    - /clear       清空所有对话历史
    - /clear N     保留最近 N 组对话（1组 = 用户消息 + AI回复）
    - /clear -N    删除最远的 N 组对话
"""

def clear_history(command='/clear'):
    global messages

    # 解析命令参数

    parts = command.split()
    if len(parts) == 1:
        # /clear 无参数：清空所有对话
        messages = [
            {
                "role": "system",
                "content": "你是一个友好的AI助手，擅长回答问题并提供帮助。"
            }
        ]
        print("✅ 对话历史已清空，可以重新开始对话了")
        return

    # 有参数的情况
    try:
        param = parts[1]

        # 处理负数（删除最远的 N 组对话）
        if param.startswith('-'):
            n = int(param)
            groups_to_remove = abs(n)

            # 计算当前对话组数（不包括 system 消息）
            current_groups = (len(messages) - 1) // 2

            if groups_to_remove >= current_groups:
                # 如果要删除的数量大于等于现有组数，则清空所有
                messages = [messages[0]]
                print(f"✅ 已删除所有 {current_groups} 组对话")
            else:
                # 删除最远的 N 组对话
                # 每组对话 = 2条消息（用户 + assistant）
                messages_to_remove = groups_to_remove * 2
                messages = [messages[0]] + messages[messages_to_remove:]
                print(f"✅ 已删除最远的 {groups_to_remove} 组对话")

        # 处理正数（保留最近 N 组对话）
        else:
            n = int(param)
            groups_to_keep = abs(n)

            # 保留 system 消息 + 最近 N 组对话
            # 每组对话 = 2条消息
            messages_to_keep = groups_to_keep * 2 + 1  # +1 是 system 消息

            if messages_to_keep >= len(messages):
                print(f"⚠️  当前只有 {(len(messages) - 1) // 2} 组对话，无需删除")
            else:
                messages = [messages[0]] + messages[-(groups_to_keep * 2):]
                print(f"✅ 已保留最近 {groups_to_keep} 组对话")

    except ValueError:
        print("❌ 参数错误！用法：")
        print("  /clear       - 清空所有对话历史")
        print("  /clear N     - 保留最近 N 组对话")
        print("  /clear -N    - 删除最远的 N 组对话")
    except Exception as e:
        print(f"❌ 执行出错: {str(e)}")

def check_message_count():
    """当对话消息超过50时，给出提示"""
    if len(messages) > 50:
        current_groups = (len(messages) - 1) // 2
        print(f"\n🔔 对话较多（当前 {current_groups} 组），建议清理以保持流畅！")

def chat_with_ai(user_message):
    """调用 AI 模型获取回复"""
    # 将用户消息添加到历史
    messages.append({
        "role": "user",
        "content": user_message
    })

    try:
        # 调用模型
        completion = client.chat.completions.create(
            model="qwen3.6-plus",
            messages=messages
        )

        # 获取 AI 回复
        ai_response = completion.choices[0].message.content

        # 将 AI 回复添加到历史
        messages.append({
            "role": "assistant",
            "content": ai_response
        })

        return ai_response

    except Exception as e:
        return f"❌ 调用出错: {str(e)}"

# 主程序

print("\n" + "=" * 60)
print("🤖 AI 聊天助手（多轮对话版）")
print("=" * 60)
print("提示：输入 /help 查看命令帮助")
print("=" * 60)

# 主循环
while True:
    # 获取用户输入
    user_input = get_user_input()

    # 处理特殊命令
    if user_input == '/quit':
        print("\n👋 再见！感谢使用！")
        break

    elif user_input.startswith('/clear'):
        clear_history(user_input)
        continue

    elif user_input == '/help':
        print_help()
        continue

    elif user_input is None:
        print("⚠️  请输入内容，或输入 /quit 退出")
        continue

    # 调用 AI 并显示回复
    ai_response = chat_with_ai(user_input)
    print(f"\n🤖 AI: {ai_response}")

    # 显示当前对话轮数
    print(f"📊 当前对话历史: {len(messages) - 1} 条消息（不含 system）")

    # 检查消息数量，超过50时给出提示
    check_message_count()
