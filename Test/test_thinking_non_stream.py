#!/usr/bin/env python3
"""
测试非流式模式下的thinking mode

目标：验证reasoning_content是否在非流式模式下返回
"""

import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ 错误：需要安装 openai 库")
    print("请运行：pip install openai")
    sys.exit(1)

# ==================== 配置部分 ====================
API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not API_KEY:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    sys.exit(1)

def test_thinking_non_stream():
    """测试非流式thinking mode"""

    print("=" * 70)
    print("🧠 非流式Thinking Mode测试")
    print("=" * 70)

    # 复杂推理问题
    question = """请详细推理解决以下问题，并展示你的思考过程：

某公司有3个部门：A部门、B部门和C部门。已知：
1. A部门的人数比B部门多20%
2. B部门的人数比C部门少10人
3. 三个部门的总人数是120人

请计算每个部门各有多少人？要求：
- 详细说明每一步的推理过程
- 展示方程的建立过程
- 验证你的答案是否正确

这是一个需要逐步推理的复杂问题，请认真思考。"""

    print("\n📋 测试问题：")
    print(question[:200] + "...")
    print("-" * 70)

    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        print("\n📡 发送请求...")
        print("   模型：qwen-max")
        print("   思考模式：✅ 已启用")
        print("   输出模式：非流式 (stream=False)")
        print("-" * 70)

        # 非流式请求
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[{"role": "user", "content": question}],
            extra_body={
                "enable_thinking": True,
                "thinking_budget": 1000
            },
            stream=False  # ✅ 非流式模式
        )

        print("\n" + "=" * 70)
        print("📊 响应分析")
        print("=" * 70)

        # 检查响应结构
        message = response.choices[0].message

        print(f"\n🔍 响应字段检查：")
        print(f"   - content: {'✅ 存在' if hasattr(message, 'content') and message.content else '❌ 不存在或为空'}")
        print(f"   - reasoning_content: {'✅ 存在' if hasattr(message, 'reasoning_content') and message.reasoning_content else '❌ 不存在或为空'}")
        print(f"   - role: {message.role if hasattr(message, 'role') else 'N/A'}")

        # 检查reasoning_content
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            print(f"\n🧠 推理内容长度：{len(message.reasoning_content)} 字符")
            print(f"\n📝 推理内容预览（前500字符）：")
            print("-" * 70)
            print(message.reasoning_content[:500])
            print("-" * 70)

            # 保存完整推理内容
            log_file = Path("logs/thinking_non_stream_test.log")
            log_file.parent.mkdir(exist_ok=True)
            with open(log_file, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"\n{'='*60}\n")
                f.write(f"[{timestamp}] 非流式Thinking Mode测试\n")
                f.write(f"{'='*60}\n")
                f.write(f"\n🧠 推理内容：\n{message.reasoning_content}\n")
                f.write(f"\n🎯 最终回答：\n{message.content}\n")
                f.write(f"\n{'='*60}\n\n")

            print(f"\n✅ 完整推理内容已保存到：{log_file}")
        else:
            print(f"\n⚠️ 未发现reasoning_content字段")
            print(f"   可能原因：")
            print(f"   1. qwen-max模型在此场景下不返回推理内容")
            print(f"   2. 需要使用thinking专用模型（qwen-max-longthinking）")
            print(f"   3. 问题复杂度不足以触发深度推理")

        # 显示最终回答
        if hasattr(message, 'content') and message.content:
            print(f"\n🎯 最终回答长度：{len(message.content)} 字符")
            print(f"\n📝 最终回答预览（前300字符）：")
            print("-" * 70)
            print(message.content[:300])
            print("-" * 70)

        # 检查usage信息
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            print(f"\n📊 Token使用情况：")
            print(f"   - prompt_tokens: {usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else 'N/A'}")
            print(f"   - completion_tokens: {usage.completion_tokens if hasattr(usage, 'completion_tokens') else 'N/A'}")
            print(f"   - total_tokens: {usage.total_tokens if hasattr(usage, 'total_tokens') else 'N/A'}")

            # 检查thinking相关的token使用
            if hasattr(usage, 'thinking_tokens'):
                print(f"   - thinking_tokens: {usage.thinking_tokens}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⏰ 开始时间：", end=" ")
    from datetime import datetime
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    success = test_thinking_non_stream()

    print("\n" + "=" * 70)
    if success:
        print("🎉 测试完成")
        print("=" * 70)
        print("\n💡 检查要点：")
        print("1. 是否看到 reasoning_content 字段")
        print("2. 如果有，说明非流式模式支持推理内容记录")
        print("3. 如果没有，需要尝试thinking专用模型")
    else:
        print("⚠️ 测试失败")
    print("=" * 70)

    print("\n⏰ 结束时间：", end=" ")
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
