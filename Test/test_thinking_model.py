#!/usr/bin/env python3
"""
测试thinking专用模型是否能返回reasoning_content

测试模型：
- qwen-max-longthinking
- qwq-thinking
"""

import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ 错误：需要安装 openai 库")
    sys.exit(1)

# ==================== 配置部分 ====================
API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not API_KEY:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    sys.exit(1)

# 要测试的thinking专用模型
THINKING_MODELS = [
    "qwen-max-longthinking",
    "qwq-thinking"
]

def test_model(model_name):
    """测试单个模型"""

    print("\n" + "=" * 70)
    print(f"🧠 测试模型：{model_name}")
    print("=" * 70)

    # 简单但需要推理的问题
    question = """请用逻辑推理解决这个问题，并展示你的推理过程：

有5个盒子排成一排，只有一个盒子里有金币。盒子编号从1到5。

已知线索：
1. 金币不在第1个盒子里
2. 金币不在第5个盒子里
3. 金币所在的盒子编号是偶数
4. 如果金币在第2个盒子，那么第3个盒子是空的（实际上第3个盒子确实是空的）
5. 金币不在第4个盒子里

请根据这些线索，推理出金币在哪个盒子里？要求详细说明每一步推理过程。"""

    print(f"\n📋 测试问题：推理金币位置")
    print("-" * 70)

    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        print(f"\n📡 发送请求到 {model_name}...")
        print(f"   思考模式：✅ 已启用")
        print(f"   输出模式：非流式")
        print("-" * 70)

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": question}],
            extra_body={
                "enable_thinking": True,
                "thinking_budget": 1000
            },
            stream=False
        )

        message = response.choices[0].message

        print(f"\n🔍 响应字段检查：")
        has_content = hasattr(message, 'content') and message.content
        has_reasoning = hasattr(message, 'reasoning_content') and message.reasoning_content

        print(f"   - content: {'✅' if has_content else '❌'}")
        print(f"   - reasoning_content: {'✅' if has_reasoning else '❌'}")

        result = {
            "model": model_name,
            "has_content": has_content,
            "has_reasoning": has_reasoning,
            "reasoning_length": len(message.reasoning_content) if has_reasoning else 0,
            "answer_length": len(message.content) if has_content else 0
        }

        if has_reasoning:
            print(f"\n🎉 成功！{model_name} 返回了推理内容！")
            print(f"\n🧠 推理内容长度：{len(message.reasoning_content)} 字符")
            print(f"\n📝 推理内容预览（前400字符）：")
            print("-" * 70)
            print(message.reasoning_content[:400])
            print("-" * 70)

            # 保存到日志
            log_file = Path("logs/thinking_models_test.log")
            log_file.parent.mkdir(exist_ok=True)
            with open(log_file, 'a', encoding='utf-8') as f:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"\n{'='*70}\n")
                f.write(f"[{timestamp}] 模型：{model_name}\n")
                f.write(f"{'='*70}\n")
                f.write(f"\n✅ 找到reasoning_content！\n")
                f.write(f"\n🧠 推理内容：\n{message.reasoning_content}\n")
                f.write(f"\n🎯 最终回答：\n{message.content}\n")
                f.write(f"\n{'='*70}\n\n")

            print(f"\n✅ 完整日志已保存到：logs/thinking_models_test.log")
        else:
            print(f"\n⚠️ {model_name} 未返回reasoning_content")
            print(f"   模型可能不支持或需要不同的参数配置")

        if has_content:
            print(f"\n🎯 最终回答预览（前200字符）：")
            print("-" * 70)
            print(message.content[:200])
            print("-" * 70)

        return result

    except Exception as e:
        print(f"\n❌ 测试 {model_name} 失败：{e}")
        return {
            "model": model_name,
            "error": str(e)
        }

def main():
    """测试所有thinking专用模型"""

    print("=" * 70)
    print("🧠 Thinking专用模型测试")
    print("=" * 70)
    print("\n目标：验证哪些模型返回reasoning_content")

    results = []

    for model in THINKING_MODELS:
        result = test_model(model)
        results.append(result)

    # 汇总结果
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)

    print(f"\n{'模型名称':<30} {'reasoning_content':<20} {'状态'}")
    print("-" * 70)

    for result in results:
        if "error" in result:
            print(f"{result['model']:<30} {'❌ 错误':<20} {result['error']}")
        else:
            status = "✅ 支持" if result['has_reasoning'] else "❌ 不支持"
            reasoning_len = f"{result['reasoning_length']} 字符" if result['has_reasoning'] else "N/A"
            print(f"{result['model']:<30} {reasoning_len:<20} {status}")

    print("\n" + "=" * 70)
    print("💡 结论和建议")
    print("=" * 70)

    supported_models = [r['model'] for r in results if r.get('has_reasoning')]

    if supported_models:
        print(f"\n✅ 发现支持reasoning_content的模型：")
        for model in supported_models:
            print(f"   - {model}")

        print(f"\n💡 建议：")
        print(f"   1. 在config.yaml中使用上述模型之一")
        print(f"   2. 在main.py中正确记录reasoning_content到日志")
        print(f"   3. 使用复杂问题触发深度推理")
    else:
        print(f"\n⚠️ 所有测试模型均未返回reasoning_content")
        print(f"\n可能原因：")
        print(f"   1. 模型名称不正确（请查看阿里云文档确认最新模型名）")
        print(f"   2. API版本问题（可能需要不同的endpoint）")
        print(f"   3. 权限问题（部分模型需要单独申请）")
        print(f"\n💡 建议：")
        print(f"   1. 访问阿里云模型列表：https://help.aliyun.com/zh/model-studio")
        print(f"   2. 确认模型名称和可用性")
        print(f"   3. 检查API Key是否有权限访问这些模型")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    from datetime import datetime
    print(f"\n⏰ 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    main()

    print(f"\n⏰ 完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
