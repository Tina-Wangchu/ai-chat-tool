"""
CoT对照实验脚本
对比开启CoT和关闭CoT两种模式下的推理能力差异
"""

import json
import os
import time
from dashscope import Generation
from datetime import datetime

# ==================== 配置 ====================
# 设置API Key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    print("请先设置环境变量：export DASHSCOPE_API_KEY='your-key-here'")
    exit(1)

# 设置API Key（使用Generation模块）
Generation.api_key = DASHSCOPE_API_KEY

# 实验配置
MODEL = "qwen-max"  # 使用更强的推理模型
TEMPERATURE = 0.7   # 保持创造性
MAX_TOKENS = 2000

# ==================== 测试题库 ====================

# 数学计算题库
MATH_QUESTIONS = [
    {
        "question": "小明有15个弹珠，给了小红3个，又买了8个，然后掉了2个。请问小明现在有多少个弹珠？",
        "correct_answer": 18,
        "category": "数学计算"
    },
    {
        "question": "一个电影院有40个座位，每排8个座位。如果前三排坐满，还剩下多少个空座位？",
        "correct_answer": 16,
        "category": "数学计算"
    },
    {
        "question": "张三去买水果，苹果5元/斤，买了3斤；香蕉3元/斤，买了2斤。他付了30元，应该找回多少钱？",
        "correct_answer": 9,
        "category": "数学计算"
    },
    {
        "question": "一个数乘以3，然后加上7，再除以2，最后减去4，结果是5。这个数是多少？",
        "correct_answer": 2,
        "category": "数学计算"
    },
    {
        "question": "一个工厂原来每天生产100件产品，现在提高了效率，每天生产原来的1.5倍。如果工作5天，能生产多少件产品？",
        "correct_answer": 750,
        "category": "数学计算"
    }
]

# 逻辑推理题库
LOGIC_QUESTIONS = [
    {
        "question": "有三个盒子，一个装红球，一个装蓝球，一个装红蓝混合。三个盒子标签全贴错了。如果从标签为'红球'的盒子中取出一个球是红色，问这个盒子实际装什么？其他两个盒子各装什么？",
        "correct_answer": "混合球；标'蓝球'的盒子装红球；标'混合'的盒子装蓝球",
        "category": "逻辑推理"
    },
    {
        "question": "A比B大，B比C大，C比D大，D比E大。请问谁第二大？",
        "correct_answer": "B",
        "category": "逻辑推理"
    },
    {
        "question": "如果所有猫都是动物，所有动物都需要食物，那么所有猫是否都需要食物？为什么？",
        "correct_answer": "是",
        "category": "逻辑推理"
    },
    {
        "question": "在一个家庭中，父亲说'我是唯一的男性'，母亲说'我有两个女儿'，大女儿说'我有一个妹妹'。这个家庭有几个人？分别是谁？",
        "correct_answer": "4个人：父亲、母亲、大女儿、小女儿",
        "category": "逻辑推理"
    },
    {
        "question": "如果今天是星期三，那么100天后是星期几？",
        "correct_answer": "星期五",
        "category": "逻辑推理"
    }
]

# 常识推理题库
COMMON_SENSE_QUESTIONS = [
    {
        "question": "如果把一杯热水放在冰箱里，它会变热还是变冷？为什么？",
        "correct_answer": "变冷",
        "category": "常识推理"
    },
    {
        "question": "一个人站在镜子前，他举起右手，镜子里的人举起哪只手？",
        "correct_answer": "左手",
        "category": "常识推理"
    },
    {
        "question": "为什么下雨天打雷闪电时，我们先看到闪电后听到雷声？",
        "correct_answer": "因为光速比声速快",
        "category": "常识推理"
    },
    {
        "question": "如果把植物放在完全黑暗的地方，它会怎样？为什么？",
        "correct_answer": "会死亡或生长不良",
        "category": "常识推理"
    },
    {
        "question": "为什么夏天穿白色衣服比黑色衣服凉快？",
        "correct_answer": "白色反射阳光，黑色吸收阳光",
        "category": "常识推理"
    }
]

# 合并所有题目
ALL_QUESTIONS = MATH_QUESTIONS + LOGIC_QUESTIONS + COMMON_SENSE_QUESTIONS

# ==================== 实验函数 ====================

def test_without_cot(question):
    """不使用CoT的测试"""
    try:
        response = Generation.call(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            result_format="message"
        )

        if response.status_code == 200:
            result = response.output.choices[0].message.content
            return {
                "success": True,
                "answer": result,
                "tokens_used": response.usage.total_tokens
            }
        else:
            return {
                "success": False,
                "error": str(response),
                "answer": None,
                "tokens_used": 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "answer": None,
            "tokens_used": 0
        }

def test_with_cot(question):
    """使用CoT的测试"""
    cot_question = f"{question}\n\n请一步步思考，详细说明你的推理过程。"

    try:
        response = Generation.call(
            model=MODEL,
            messages=[{"role": "user", "content": cot_question}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            result_format="message"
        )

        if response.status_code == 200:
            result = response.output.choices[0].message.content
            return {
                "success": True,
                "answer": result,
                "tokens_used": response.usage.total_tokens
            }
        else:
            return {
                "success": False,
                "error": str(response),
                "answer": None,
                "tokens_used": 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "answer": None,
            "tokens_used": 0
        }

def extract_final_answer(response_text):
    """从回答中提取最终答案"""
    # 简单的答案提取逻辑
    response_text = response_text.strip()

    # 查找常见的答案标识
    answer_markers = ["答案是", "因此答案是", "所以答案是", "answer is", "最终答案是"]

    for marker in answer_markers:
        if marker in response_text:
            parts = response_text.split(marker)
            if len(parts) > 1:
                return parts[1].strip().split()[0]  # 返回答案的第一个词/数字

    # 如果没有找到明确答案，尝试提取数字
    import re
    numbers = re.findall(r'\d+', response_text)
    if numbers:
        return numbers[-1]  # 返回最后一个数字（通常是最终答案）

    return response_text[:50]  # 返回前50个字符作为摘要

def run_experiment():
    """运行完整实验"""
    print("=" * 80)
    print("🧪 CoT对照实验开始")
    print("=" * 80)

    results = []

    for i, question_data in enumerate(ALL_QUESTIONS, 1):
        question = question_data["question"]
        correct_answer = question_data["correct_answer"]
        category = question_data["category"]

        print(f"\n{'─' * 80}")
        print(f"题目 {i}/15 ({category})")
        print(f"{'─' * 80}")
        print(f"问题：{question}")
        print(f"正确答案：{correct_answer}")

        # 测试不使用CoT
        print(f"\n🔵 测试1：不使用CoT")
        without_cot = test_without_cot(question)
        if without_cot["success"]:
            print(f"回答：{without_cot['answer']}")
            print(f"Token使用：{without_cot['tokens_used']}")
        else:
            print(f"❌ 错误：{without_cot['error']}")

        time.sleep(1)  # 避免请求过快

        # 测试使用CoT
        print(f"\n🟢 测试2：使用CoT")
        with_cot = test_with_cot(question)
        if with_cot["success"]:
            print(f"回答：{with_cot['answer']}")
            print(f"Token使用：{with_cot['tokens_used']}")
        else:
            print(f"❌ 错误：{with_cot['error']}")

        # 记录结果
        result_record = {
            "question_id": i,
            "category": category,
            "question": question,
            "correct_answer": str(correct_answer),
            "without_cot": {
                "answer": without_cot["answer"] if without_cot["success"] else without_cot["error"],
                "tokens": without_cot["tokens_used"],
                "success": without_cot["success"]
            },
            "with_cot": {
                "answer": with_cot["answer"] if with_cot["success"] else with_cot["error"],
                "tokens": with_cot["tokens_used"],
                "success": with_cot["success"]
            }
        }
        results.append(result_record)

        time.sleep(2)  # 避免API限流

    return results

def analyze_results(results):
    """分析实验结果"""
    print("\n" + "=" * 80)
    print("📊 实验结果分析")
    print("=" * 80)

    # 统计成功率
    without_cot_success = sum(1 for r in results if r["without_cot"]["success"])
    with_cot_success = sum(1 for r in results if r["with_cot"]["success"])

    print(f"\n📈 基本统计")
    print(f"总题目数：{len(results)}")
    print(f"无CoT成功率：{without_cot_success}/{len(results)} ({without_cot_success/len(results)*100:.1f}%)")
    print(f"有CoT成功率：{with_cot_success}/{len(results)} ({with_cot_success/len(results)*100:.1f}%)")

    # 按类别统计
    categories = ["数学计算", "逻辑推理", "常识推理"]

    print(f"\n📊 分类统计")
    for category in categories:
        category_results = [r for r in results if r["category"] == category]
        without_correct = sum(1 for r in category_results if r["without_cot"]["success"])
        with_correct = sum(1 for r in category_results if r["with_cot"]["success"])

        print(f"\n{category}：")
        print(f"  无CoT：{without_correct}/{len(category_results)} ({without_correct/len(category_results)*100:.1f}%)")
        print(f"  有CoT：{with_correct}/{len(category_results)} ({with_correct/len(category_results)*100:.1f}%)")

    # Token使用统计
    without_tokens = sum(r["without_cot"]["tokens"] for r in results if r["without_cot"]["success"])
    with_tokens = sum(r["with_cot"]["tokens"] for r in results if r["with_cot"]["success"])

    print(f"\n💰 Token使用统计")
    print(f"无CoT总Token：{without_tokens}")
    print(f"有CoT总Token：{with_tokens}")
    print(f"增加比例：{(with_tokens-with_tokens)/without_tokens*100:.1f}%")

    return {
        "total_questions": len(results),
        "without_cot_success_rate": without_cot_success/len(results)*100,
        "with_cot_success_rate": with_cot_success/len(results)*100,
        "token_increase": (with_tokens-with_tokens)/without_tokens*100
    }

def save_results(results, analysis):
    """保存实验结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 保存到 experiments 子文件夹
    filename = f"experiments/cot_experiment_results_{timestamp}.json"

    full_results = {
        "experiment_info": {
            "model": MODEL,
            "temperature": TEMPERATURE,
            "timestamp": timestamp,
            "total_questions": len(results)
        },
        "analysis": analysis,
        "detailed_results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存到：{filename}")

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🧪 CoT对照实验")
    print("=" * 80)
    print(f"模型：{MODEL}")
    print(f"温度：{TEMPERATURE}")
    print(f"题目数量：{len(ALL_QUESTIONS)}")
    print("=" * 80)

    # 运行实验
    results = run_experiment()

    # 分析结果
    analysis = analyze_results(results)

    # 保存结果
    save_results(results, analysis)

    print("\n✅ 实验完成！")
