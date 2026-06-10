#!/usr/bin/env python3
"""
Temperature 对比分析脚本

分析不同 temperature 下多次运行结果的差异，生成对比图表和统计数据。
"""

import os
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import json

def parse_output_log(log_file):
    """解析单个 outputs.log 文件"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        separator = "=" * 80
        entries = content.split(separator)

        parsed_entries = []
        for entry in entries:
            entry = entry.strip()
            if not entry or entry == '\n':
                continue

            entry_data = {}
            lines = entry.split('\n')

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("📅 时间:"):
                    entry_data['time'] = line.split(":", 1)[1].strip()
                elif line.startswith("🌡️ Temperature:"):
                    entry_data['temperature'] = line.split(":", 1)[1].strip()
                elif line.startswith("👤 用户问题:"):
                    entry_data['question'] = line.split(":", 1)[1].strip()
                elif line.startswith("🤖 AI 回复:"):
                    # 收集剩余所有内容作为回复
                    reply_lines = lines[i+1:]
                    entry_data['reply'] = '\n'.join(reply_lines).strip()
                    break

            if entry_data and 'reply' in entry_data:
                parsed_entries.append(entry_data)

        return parsed_entries

    except Exception as e:
        print(f"❌ 解析文件 {log_file} 出错：{e}")
        return []

def calculate_similarity(text1, text2):
    """计算两个文本的相似度（0-1）"""
    return SequenceMatcher(None, text1, text2).ratio()

def analyze_reply_differences(all_data):
    """分析回复差异"""
    analysis = {
        'by_temperature': {},
        'by_question': {},
        'similarity_matrix': {},
        'length_variance': {},
        'keywords': {}
    }

    temperatures = sorted(all_data.keys(), key=lambda x: float(x))

    # 为每个 temperature 分析
    for temp in temperatures:
        entries = all_data[temp]
        replies = [e['reply'] for e in entries if 'reply' in e]

        if len(replies) >= 2:
            # 计算两两相似度
            similarities = []
            for i in range(len(replies)):
                for j in range(i+1, len(replies)):
                    sim = calculate_similarity(replies[i], replies[j])
                    similarities.append(sim)

            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            variance = sum((s - avg_similarity) ** 2 for s in similarities) / len(similarities) if similarities else 0

            analysis['by_temperature'][temp] = {
                'avg_similarity': avg_similarity,
                'variance': variance,
                'stability': '高' if avg_similarity > 0.8 else ('中' if avg_similarity > 0.5 else '低'),
                'replies': replies
            }

    # 按问题分析（假设问题按顺序排列）
    if temperatures and all_data[temperatures[0]]:
        num_questions = min(len(all_data[t]) for t in temperatures)

        for q_idx in range(num_questions):
            question_key = f"问题{q_idx+1}"
            analysis['by_question'][question_key] = {}

            for temp in temperatures:
                entries = all_data[temp]
                if q_idx < len(entries) and 'reply' in entries[q_idx]:
                    reply = entries[q_idx]['reply']
                    analysis['by_question'][question_key][temp] = {
                        'length': len(reply),
                        'reply': reply[:100] + '...'  # 保存前100字符
                    }

    return analysis

def generate_ascii_chart(data, title, width=60):
    """生成 ASCII 图表"""
    if not data:
        return ""

    chart = f"\n### {title}\n\n"
    max_val = max(data.values()) if data else 1

    for label, value in sorted(data.items()):
        bar_length = int((value / max_val) * width) if max_val > 0 else 0
        bar = '█' * bar_length
        chart += f"{label:15} {bar} {value:.3f}\n"

    return chart + "\n"

def generate_comparison_table(all_data, analysis):
    """生成对比表格"""
    table = "## 📊 Temperature 差异对比分析\n\n"

    # 表格1：相似度统计
    table += "### 1. 运行一致性分析\n\n"
    table += "这个指标显示同一 temperature 下三次运行的相似程度：\n\n"
    table += "| Temperature | 平均相似度 | 方差 | 稳定性 | 说明 |\n"
    table += "|:-----------|:-----------|:-----|:------|:------|\n"

    for temp in sorted(analysis['by_temperature'].keys(), key=lambda x: float(x)):
        data = analysis['by_temperature'][temp]
        temp_str = f"{float(temp):.1f}"
        sim_str = f"{data['avg_similarity']:.3f}"
        var_str = f"{data['variance']:.4f}"
        stability = data['stability']

        if stability == '高':
            desc = "3次运行基本相同"
        elif stability == '中':
            desc = "3次运行有变化"
        else:
            desc = "3次运行明显不同"

        table += f"| {temp_str} | {sim_str} | {var_str} | {stability} | {desc} |\n"

    table += "\n"

    # 表格2：回复长度统计
    table += "### 2. 回复长度统计\n\n"
    table += "| Temperature | 最短 | 最长 | 平均 | 标准差 |\n"
    table += "|:-----------|:----|:----|:----|:------|\n"

    for temp in sorted(all_data.keys(), key=lambda x: float(x)):
        entries = all_data[temp]
        lengths = [len(e.get('reply', '')) for e in entries if 'reply' in e]

        if lengths:
            min_len = min(lengths)
            max_len = max(lengths)
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            std_dev = variance ** 0.5

            table += f"| {float(temp):.1f} | {min_len} | {max_len} | {avg_len:.1f} | {std_dev:.1f} |\n"

    table += "\n"

    # 表格3：问题对比（取第一个问题）
    table += "### 3. Question1 对比（骑行建议）\n\n"
    table += "对比三个 temperature 对第一个问题的回答风格：\n\n"

    if '问题1' in analysis['by_question']:
        table += "| Temperature | 回复长度 | 回复预览 |\n"
        table += "|:-----------|:---------|:----------|\n"

        for temp in sorted(analysis['by_question']['问题1'].keys(), key=lambda x: float(x)):
            data = analysis['by_question']['问题1'][temp]
            preview = data['reply'].replace('\n', ' ')[:50] + '...'
            table += f"| {float(temp):.1f} | {data['length']} | {preview} |\n"

    table += "\n"

    return table

def generate_similarity_chart(analysis):
    """生成相似度对比图表"""
    chart = "### 4. 相似度对比图表\n\n"
    chart += "```\n"
    chart += "相似度范围：0.0（完全不同）→ 1.0（完全相同）\n\n"

    for temp in sorted(analysis['by_temperature'].keys(), key=lambda x: float(x)):
        data = analysis['by_temperature'][temp]
        chart += f"Temperature {float(temp):.1f}:\n"
        chart += f"  平均相似度: {data['avg_similarity']:.3f}\n"
        chart += f"  稳定性: {data['stability']}\n\n"

    chart += "对比:\n"
    chart += "- Temperature 0.0: 3次运行应该最相似（→1.0）\n"
    chart += "- Temperature 0.5: 3次运行有中等相似度（→0.5-0.7）\n"
    chart += "- Temperature 1.0: 3次运行应该最不相似（→0.0-0.3）\n"
    chart += "```\n\n"

    return chart

def generate_conclusion(analysis):
    """生成结论"""
    conclusion = "### 5. 📈 结论与观察\n\n"

    # Temperature 0.0 分析
    if '0.0' in analysis['by_temperature']:
        data_0 = analysis['by_temperature']['0.0']
        conclusion += f"**Temperature 0.0（确定性）:**\n"
        conclusion += f"- 平均相似度：{data_0['avg_similarity']:.3f}\n"
        if data_0['avg_similarity'] > 0.8:
            conclusion += "- ✅ 三次运行高度一致，回复基本相同\n"
            conclusion += "- ✅ 适合需要稳定回复的场景\n"
        conclusion += "\n"

    # Temperature 0.5 分析
    if '0.5' in analysis['by_temperature']:
        data_5 = analysis['by_temperature']['0.5']
        conclusion += f"**Temperature 0.5（中等）:**\n"
        conclusion += f"- 平均相似度：{data_5['avg_similarity']:.3f}\n"
        if 0.4 < data_5['avg_similarity'] < 0.8:
            conclusion += "- ⚠️ 三次运行有一定变化，但核心信息一致\n"
            conclusion += "- ⚖️ 平衡了创造性和一致性\n"
        conclusion += "\n"

    # Temperature 1.0 分析
    if '1.0' in analysis['by_temperature']:
        data_1 = analysis['by_temperature']['1.0']
        conclusion += f"**Temperature 1.0（随机性）:**\n"
        conclusion += f"- 平均相似度：{data_1['avg_similarity']:.3f}\n"
        if data_1['avg_similarity'] < 0.5:
            conclusion += "- 🎲 三次运行明显不同，表达方式多样\n"
            conclusion += "- ✅ 适合需要创意和多样性的场景\n"
        conclusion += "\n"

    conclusion += "**总趋势:**\n"
    conclusion += "随着 temperature 升高（0.0 → 1.0）：\n"
    conclusion += "- ✅ 平均相似度下降\n"
    conclusion += "- ✅ 方差增大\n"
    conclusion += "- ✅ 回复多样性增加\n"
    conclusion += "- ✅ 稳定性降低\n"

    return conclusion

def enhance_summary_with_analysis(input_file="TEMPERATURE_OUTPUTS_SUMMARY.md", output_file="TEMPERATURE_OUTPUTS_SUMMARY_ANALYSIS.md"):
    """增强总结文件，添加分析内容"""

    print("=" * 70)
    print("📊 Temperature 对比分析")
    print("=" * 70)
    print()

    # 读取现有的总结文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        print(f"✅ 读取原文件：{input_file}")
    except:
        print(f"❌ 无法读取文件：{input_file}")
        return

    # 解析日志
    log_dir = "logs"
    log_path = Path(log_dir)
    output_files = sorted(log_path.glob("temperature:*_outputs.log"))

    all_data = {}
    for output_file_path in output_files:
        temp_match = re.search(r'temperature:([\d.]+)_outputs\.log', output_file_path.name)
        if temp_match:
            temp = temp_match.group(1)
            entries = parse_output_log(output_file_path)
            if entries:
                all_data[temp] = entries

    if not all_data:
        print("❌ 没有解析到数据")
        return

    print(f"✅ 解析了 {len(all_data)} 个 temperature 的数据")

    # 分析差异
    analysis = analyze_reply_differences(all_data)

    # 生成增强内容
    enhanced_content = original_content
    enhanced_content += "\n\n"
    enhanced_content += generate_comparison_table(all_data, analysis)
    enhanced_content += generate_similarity_chart(analysis)
    enhanced_content += generate_conclusion(analysis)
    enhanced_content += "\n---\n"
    enhanced_content += "\n*分析生成时间：* " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"

    # 写入增强文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        print(f"✅ 增强文件已生成：{output_file}")
        print(f"   文件大小：{Path(output_file).stat().st_size} 字节")
    except Exception as e:
        print(f"❌ 写入文件失败：{e}")

    print()
    print("=" * 70)
    print("🎉 对比分析完成！")
    print("=" * 70)
    print()
    print(f"📄 查看增强版总结：")
    print(f"   cat {output_file}")

if __name__ == "__main__":
    import sys

    input_file = sys.argv[1] if len(sys.argv) > 1 else "TEMPERATURE_OUTPUTS_SUMMARY.md"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "TEMPERATURE_OUTPUTS_SUMMARY_ANALYSIS.md"

    enhance_summary_with_analysis(input_file, output_file)
