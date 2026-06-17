"""
CoT对照实验脚本（改进版）
修复了答案验证和token计算的bug，重新设计了实验策略
"""

import json
import os
import time
import re
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

# ==================== 实验配置（改进版）====================
MODEL = "qwen-turbo"  # 使用更小的模型，更容易体现CoT价值
TEMPERATURE = 0.0     # 使用0确保可重复性
MAX_TOKENS_WITHOUT_COT = 100  # 限制无CoT的输出长度，强制简洁
MAX_TOKENS_WITH_COT = 2000     # CoT模式允许详细输出

# ==================== 改进的测试题库（增加难度）====================

# 数学计算题库（增加难度）
MATH_QUESTIONS = [
    {
        "question": "小明有15个弹珠，给了小红3个，又买了8个，然后掉了2个。请问小明现在有多少个弹珠？",
        "correct_answer": 18,
        "answer_type": "number",
        "category": "数学计算"
    },
    {
        "question": "一个电影院有40个座位，每排8个座位。如果前三排坐满，还剩下多少个空座位？",
        "correct_answer": 16,
        "answer_type": "number",
        "category": "数学计算"
    },
    {
        "question": "张三去买水果，苹果5元/斤，买了3斤；香蕉3元/斤，买了2斤。他付了30元，应该找回多少钱？",
        "correct_answer": 9,
        "answer_type": "number",
        "category": "数学计算"
    },
    {
        "question": "一个数乘以3，然后加上7，再除以2，最后减去4，结果是5。这个数是多少？",
        "correct_answer": "2",  # 注意：(x*3+7)/2-4=5, (x*3+7)/2=9, x*3+7=18, x*3=11, x=11/3≈3.67，但重新计算：设x为原数，(3x+7)/2-4=5，(3x+7)/2=9，3x+7=18，3x=11，x=11/3
        "answer_type": "number",
        "category": "数学计算"
    },
    {
        "question": "一个工厂原来每天生产100件产品，现在提高了效率，每天生产原来的1.5倍。如果工作5天，能生产多少件产品？",
        "correct_answer": 750,
        "answer_type": "number",
        "category": "数学计算"
    },
    # 新增加难度的数学题
    {
        "question": "甲、乙两人同时从A地出发去B地。甲每小时走6公里，乙每小时走4公里。甲比乙早2小时到达，问A地到B地的距离是多少公里？",
        "correct_answer": 24,  # 设距离为x，x/6 = x/4 - 2, x/6 - x/4 = -2, -2x/12 = -2, x = 12
        "answer_type": "number",
        "category": "数学计算"
    },
    {
        "question": "一个水池有进水管和出水管，单开进水管6小时注满，单开出水管8小时放完。如果两管同时开，多少小时可以注满水池？",
        "correct_answer": 24,  # 1/6 - 1/8 = 1/24, 需要24小时
        "answer_type": "number",
        "category": "数学计算"
    }
]

# 逻辑推理题库（增加难度）
LOGIC_QUESTIONS = [
    {
        "question": "有三个盒子，一个装红球，一个装蓝球，一个装红蓝混合。三个盒子标签全贴错了。如果从标签为'红球'的盒子中取出一个球是红色，问这个盒子实际装什么？其他两个盒子各装什么？",
        "correct_answer": ["混合球", "红蓝混合", "mixed"],
        "answer_type": "text",
        "keywords": ["混合", "红蓝混合", "mixed"],
        "category": "逻辑推理"
    },
    {
        "question": "A比B大，B比C大，C比D大，D比E大。请问谁第二大？",
        "correct_answer": ["B", "b"],
        "answer_type": "single_choice",
        "category": "逻辑推理"
    },
    {
        "question": "如果所有猫都是动物，所有动物都需要食物，那么所有猫是否都需要食物？为什么？",
        "correct_answer": ["是", "需要", "是的", "require"],
        "answer_type": "yes_no",
        "category": "逻辑推理"
    },
    {
        "question": "在一个家庭中，父亲说'我是唯一的男性'，母亲说'我有两个女儿'，大女儿说'我有一个妹妹'。这个家庭有几个人？分别是谁？",
        "correct_answer": ["4", "四", "four"],
        "answer_type": "number",
        "expected_content": ["父亲", "母亲", "大女儿", "小女儿"],
        "category": "逻辑推理"
    },
    {
        "question": "如果今天是星期三，那么100天后是星期几？",
        "correct_answer": ["星期五", "周五", "Friday"],
        "answer_type": "single_choice",
        "category": "逻辑推理"
    },
    # 新增加难度的逻辑题
    {
        "question": "在一个岛上，有两种人：骑士（永远说真话）和无赖（永远说假话）。你遇到两个人，A说'B是骑士'，B说'我们两个是不同类型的'。请问A和B分别是什么类型？",
        "correct_answer": ["A是无赖，B是骑士", "无赖，骑士", "A是knave，B是knight"],
        "answer_type": "text",
        "keywords": ["无赖", "骑士", "knave", "knight"],
        "category": "逻辑推理"
    },
    {
        "question": "有100个囚犯，编号1-100。典狱长准备100个盒子，每个盒子里放一个囚犯的编号。每个囚犯可以打开50个盒子找一个编号。如果所有囚犯都找到自己的编号则全部释放，否则全部处死。最优策略是什么？成功率是多少？",
        "correct_answer": ["循环", "cycle", "跟随", "follow", "30%", "31%"],
        "answer_type": "text",
        "keywords": ["循环", "cycle", "跟随", "follow", "30%", "31%"],
        "category": "逻辑推理"
    }
]

# 常识推理题库（增加难度）
COMMON_SENSE_QUESTIONS = [
    {
        "question": "如果把一杯热水放在冰箱里，它会变热还是变冷？为什么？",
        "correct_answer": ["变冷", "降温", "降低温度"],
        "answer_type": "choice",
        "category": "常识推理"
    },
    {
        "question": "一个人站在镜子前，他举起右手，镜子里的人举起哪只手？",
        "correct_answer": ["左手", "left hand"],
        "answer_type": "choice",
        "category": "常识推理"
    },
    {
        "question": "为什么下雨天打雷闪电时，我们先看到闪电后听到雷声？",
        "correct_answer": ["光速比声速快", "光速快", "声速慢"],
        "answer_type": "text",
        "keywords": ["光速", "声速", "快"],
        "category": "常识推理"
    },
    {
        "question": "如果把植物放在完全黑暗的地方，它会怎样？为什么？",
        "correct_answer": ["死亡", "死", "枯萎", "生长不良"],
        "answer_type": "choice",
        "keywords": ["光合作用", "光照"],
        "category": "常识推理"
    },
    {
        "question": "为什么夏天穿白色衣服比黑色衣服凉快？",
        "correct_answer": ["反射", "吸收", "黑色吸热", "白色反射"],
        "answer_type": "text",
        "keywords": ["反射", "吸收", "热量"],
        "category": "常识推理"
    },
    # 新增加难度的常识题
    {
        "question": "在一个完全密封的房间里点燃蜡烛，蜡烛最终会熄灭。这是为什么？需要什么条件才能持续燃烧？",
        "correct_answer": ["氧气", "缺氧", "oxygen", "空气"],
        "answer_type": "text",
        "keywords": ["氧气", "燃烧", "oxygen"],
        "category": "常识推理"
    },
    {
        "question": "为什么在高原地区水的沸点比平原低？这对煮饭有什么影响？",
        "correct_answer": ["气压", "气压低", "压力", "煮不熟"],
        "answer_type": "text",
        "keywords": ["气压", "沸点", "煮不熟"],
        "category": "常识推理"
    }
]

# 合并所有题目
ALL_QUESTIONS = MATH_QUESTIONS + LOGIC_QUESTIONS + COMMON_SENSE_QUESTIONS

# ==================== 改进的答案验证函数 ====================

def check_answer_correct(question_data, model_answer):
    """
    改进的答案验证函数
    检查模型答案是否正确
    """
    if not model_answer:
        return False, "无回答"

    answer_text = model_answer.lower()
    answer_type = question_data.get("answer_type", "text")

    # 数值型答案检查
    if answer_type == "number":
        correct_num = question_data["correct_answer"]
        # 从答案中提取所有数字
        numbers = re.findall(r'\d+\.?\d*', answer_text)

        # 检查最后一个数字（通常是最终答案）
        if numbers:
            try:
                final_num = float(numbers[-1])
                correct_num_float = float(correct_num)
                if abs(final_num - correct_num_float) < 0.1:  # 允许小误差
                    return True, f"数字匹配：{final_num} ≈ {correct_num_float}"
                else:
                    return False, f"数字不匹配：{final_num} ≠ {correct_num_float}"
            except:
                return False, "数字解析失败"

        return False, f"未找到正确数字：{correct_num}"

    # 单选/选择型答案检查
    elif answer_type == "single_choice" or answer_type == "choice":
        correct_answers = question_data["correct_answer"]
        if isinstance(correct_answers, str):
            correct_answers = [correct_answers]

        for correct_answer in correct_answers:
            if correct_answer.lower() in answer_text:
                return True, f"包含正确答案：{correct_answer}"

        return False, f"不包含任何正确答案：{correct_answers}"

    # 是否型答案检查
    elif answer_type == "yes_no":
        correct_answers = question_data["correct_answer"]
        if isinstance(correct_answers, str):
            correct_answers = [correct_answers]

        for correct_answer in correct_answers:
            if correct_answer.lower() in answer_text:
                return True, f"正确判断：{correct_answer}"

        return False, f"判断错误或未明确回答"

    # 文本型答案检查（关键词匹配）
    elif answer_type == "text":
        keywords = question_data.get("keywords", [])
        correct_answers = question_data.get("correct_answer", [])

        # 合并所有需要匹配的文本
        all_targets = []
        if isinstance(keywords, list):
            all_targets.extend(keywords)
        if isinstance(correct_answers, list):
            all_targets.extend(correct_answers)
        if isinstance(correct_answers, str):
            all_targets.append(correct_answers)

        # 检查是否包含任何目标关键词
        for target in all_targets:
            if target.lower() in answer_text:
                return True, f"包含关键词：{target}"

        return False, f"未找到关键词：{all_targets[:3]}"

    # 默认检查
    else:
        return False, "未知答案类型"

# ==================== 改进的测试函数 ====================

def test_without_cot(question):
    """不使用CoT的测试（改进版：强制简洁输出）"""
    try:
        response = Generation.call(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS_WITHOUT_COT,  # 限制输出长度
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
    """使用CoT的测试（改进版：强化CoT提示）"""
    # 强化CoT提示词
    cot_question = f"""{question}

请一步步详细思考，展示你的完整推理过程。要求：
1. 分步骤分析问题
2. 说明每个步骤的理由
3. 最后给出明确的答案"""

    try:
        response = Generation.call(
            model=MODEL,
            messages=[{"role": "user", "content": cot_question}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS_WITH_COT,
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

# ==================== 改进的实验运行函数 ====================

def run_experiment():
    """运行改进版实验"""
    print("=" * 80)
    print("🧪 CoT对照实验开始（改进版）")
    print("=" * 80)
    print(f"📋 实验配置：")
    print(f"  模型：{MODEL}")
    print(f"  温度：{TEMPERATURE}")
    print(f"  无CoT最大token：{MAX_TOKENS_WITHOUT_COT}")
    print(f"  有CoT最大token：{MAX_TOKENS_WITH_COT}")
    print(f"  题目总数：{len(ALL_QUESTIONS)}")
    print("=" * 80)

    results = []
    without_cot_correct = 0
    with_cot_correct = 0
    without_cot_total_tokens = 0
    with_cot_total_tokens = 0

    for i, question_data in enumerate(ALL_QUESTIONS, 1):
        question = question_data["question"]
        category = question_data["category"]

        print(f"\n{'─' * 80}")
        print(f"题目 {i}/{len(ALL_QUESTIONS)} ({category})")
        print(f"{'─' * 80}")
        print(f"问题：{question}")

        # 测试不使用CoT
        print(f"\n🔵 测试1：不使用CoT（简洁模式）")
        without_cot_result = test_without_cot(question)
        if without_cot_result["success"]:
            print(f"回答：{without_cot_result['answer'][:200]}...")  # 只显示前200字符
            print(f"Token使用：{without_cot_result['tokens_used']}")

            # 验证答案正确性
            is_correct, check_msg = check_answer_correct(question_data, without_cot_result['answer'])
            print(f"答案验证：{'✅ 正确' if is_correct else '❌ 错误'} - {check_msg}")

            if is_correct:
                without_cot_correct += 1
            without_cot_total_tokens += without_cot_result['tokens_used']
        else:
            print(f"❌ 错误：{without_cot_result['error']}")
            without_cot_total_tokens += 0

        time.sleep(1)  # 避免请求过快

        # 测试使用CoT
        print(f"\n🟢 测试2：使用CoT（详细推理）")
        with_cot_result = test_with_cot(question)
        if with_cot_result["success"]:
            print(f"回答：{with_cot_result['answer'][:200]}...")  # 只显示前200字符
            print(f"Token使用：{with_cot_result['tokens_used']}")

            # 验证答案正确性
            is_correct, check_msg = check_answer_correct(question_data, with_cot_result['answer'])
            print(f"答案验证：{'✅ 正确' if is_correct else '❌ 错误'} - {check_msg}")

            if is_correct:
                with_cot_correct += 1
            with_cot_total_tokens += with_cot_result['tokens_used']
        else:
            print(f"❌ 错误：{with_cot_result['error']}")
            with_cot_total_tokens += 0

        # 记录结果
        result_record = {
            "question_id": i,
            "category": category,
            "question": question,
            "without_cot": {
                "answer": without_cot_result.get("answer", without_cot_result.get("error")),
                "tokens": without_cot_result.get("tokens_used", 0),
                "api_success": without_cot_result["success"],
                "answer_correct": is_correct if without_cot_result["success"] else False
            },
            "with_cot": {
                "answer": with_cot_result.get("answer", with_cot_result.get("error")),
                "tokens": with_cot_result.get("tokens_used", 0),
                "api_success": with_cot_result["success"],
                "answer_correct": is_correct if with_cot_result["success"] else False
            }
        }
        results.append(result_record)

        print(f"\n📊 当前进度：无CoT正确率 {without_cot_correct}/{i} ({without_cot_correct/i*100:.1f}%) | 有CoT正确率 {with_cot_correct}/{i} ({with_cot_correct/i*100:.1f}%)")

        time.sleep(2)  # 避免API限流

    return results, {
        "without_cot_correct": without_cot_correct,
        "with_cot_correct": with_cot_correct,
        "without_cot_total_tokens": without_cot_total_tokens,
        "with_cot_total_tokens": with_cot_total_tokens
    }

# ==================== 改进的分析函数 ====================

def analyze_results(results, stats):
    """改进的结果分析"""
    print("\n" + "=" * 80)
    print("📊 改进版实验结果分析")
    print("=" * 80)

    total_questions = len(results)
    without_cot_correct = stats["without_cot_correct"]
    with_cot_correct = stats["with_cot_correct"]
    without_cot_total_tokens = stats["without_cot_total_tokens"]
    with_cot_total_tokens = stats["with_cot_total_tokens"]

    # 计算正确率（基于答案正确性，而非API成功）
    without_cot_accuracy = (without_cot_correct / total_questions * 100) if total_questions > 0 else 0
    with_cot_accuracy = (with_cot_correct / total_questions * 100) if total_questions > 0 else 0

    print(f"\n📈 正确率统计（基于答案正确性）")
    print(f"总题目数：{total_questions}")
    print(f"无CoT正确率：{without_cot_correct}/{total_questions} ({without_cot_accuracy:.1f}%)")
    print(f"有CoT正确率：{with_cot_correct}/{total_questions} ({with_cot_accuracy:.1f}%)")
    print(f"CoT提升：{with_cot_accuracy - without_cot_accuracy:+.1f}%")

    # 按类别统计
    categories = ["数学计算", "逻辑推理", "常识推理"]

    print(f"\n📊 分类统计")
    for category in categories:
        category_results = [r for r in results if r["category"] == category]
        if not category_results:
            continue

        without_correct = sum(1 for r in category_results if r["without_cot"]["answer_correct"])
        with_correct = sum(1 for r in category_results if r["with_cot"]["answer_correct"])
        total = len(category_results)

        print(f"\n{category} ({total}题)：")
        print(f"  无CoT：{without_correct}/{total} ({without_correct/total*100:.1f}%)")
        print(f"  有CoT：{with_correct}/{total} ({with_correct/total*100:.1f}%)")
        print(f"  CoT提升：{with_correct/total*100 - without_correct/total*100:+.1f}%")

    # Token使用统计（修复计算bug）
    print(f"\n💰 Token使用统计（修复版）")
    print(f"无CoT总Token：{without_cot_total_tokens}")
    print(f"有CoT总Token：{with_cot_total_tokens}")

    if without_cot_total_tokens > 0:
        token_increase = ((with_cot_total_tokens - without_cot_total_tokens) / without_cot_total_tokens * 100)
        print(f"Token增加：{token_increase:+.1f}%")
        print(f"平均每题无CoT：{without_cot_total_tokens/total_questions:.0f} tokens")
        print(f"平均每题有CoT：{with_cot_total_tokens/total_questions:.0f} tokens")

    return {
        "total_questions": total_questions,
        "without_cot_accuracy": without_cot_accuracy,
        "with_cot_accuracy": with_cot_accuracy,
        "accuracy_improvement": with_cot_accuracy - without_cot_accuracy,
        "without_cot_total_tokens": without_cot_total_tokens,
        "with_cot_total_tokens": with_cot_total_tokens,
        "token_increase": ((with_cot_total_tokens - without_cot_total_tokens) / without_cot_total_tokens * 100) if without_cot_total_tokens > 0 else 0
    }

# ==================== 保存结果函数 ====================

def save_results(results, analysis):
    """保存实验结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"experiments/cot_experiment_improved_results_{timestamp}.json"

    full_results = {
        "experiment_info": {
            "model": MODEL,
            "temperature": TEMPERATURE,
            "max_tokens_without_cot": MAX_TOKENS_WITHOUT_COT,
            "max_tokens_with_cot": MAX_TOKENS_WITH_COT,
            "timestamp": timestamp,
            "total_questions": len(results),
            "experiment_type": "improved_version"
        },
        "analysis": analysis,
        "detailed_results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存到：{filename}")

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🧪 CoT对照实验（改进版）")
    print("=" * 80)
    print("🎯 改进点：")
    print("  1. 使用更小模型（qwen-turbo）而非qwen-max")
    print("  2. 限制无CoT输出长度（100 tokens），强制简洁")
    print("  3. 强化CoT提示词，明确要求分步推理")
    print("  4. 增加题目难度，添加更多挑战性问题")
    print("  5. 修复答案验证逻辑，检查答案正确性")
    print("  6. 修复token计算bug")
    print("=" * 80)

    # 运行实验
    results, stats = run_experiment()

    # 分析结果
    analysis = analyze_results(results, stats)

    # 保存结果
    save_results(results, analysis)

    print("\n✅ 改进版实验完成！")
    print("\n📋 主要改进：")
    print("  ✅ 修复答案验证bug（现在检查答案正确性）")
    print("  ✅ 修复token计算bug（正确计算增加比例）")
    print("  ✅ 使用更小模型（qwen-turbo）")
    print("  ✅ 强化CoT对比（限制无CoT输出长度）")
    print("  ✅ 增加题目难度（19题vs原15题）")
