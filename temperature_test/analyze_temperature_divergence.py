#!/usr/bin/env python3
"""
Temperature 对比分析工具
分析三个temperature下的output的发散性、随机性、语义内容、表达风格
生成Mermaid图表
"""

import re
import json
from difflib import SequenceMatcher
from collections import Counter
import math

# 读取日志文件
def read_outputs_log(temp_value):
    """读取指定temperature的outputs日志"""
    filename = f"logs/temperature:{temp_value}_outputs.log"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_outputs(content)
    except FileNotFoundError:
        print(f"警告: 找不到文件 {filename}")
        return []

def parse_outputs(content):
    """解析outputs日志，提取每个回复"""
    outputs = []
    blocks = re.split(r'🤖 AI 回复:\n', content)[1:]  # 跳过第一个空块

    for block in blocks:
        # 提取回复内容（到下一个分隔符为止）
        lines = block.split('\n')
        response_lines = []
        for line in lines:
            if line.startswith('===='):
                break
            response_lines.append(line)
        response = '\n'.join(response_lines).strip()
        if response:
            outputs.append(response)

    return outputs

def calculate_similarity(text1, text2):
    """计算两个文本的相似度"""
    return SequenceMatcher(None, text1, text2).ratio()

def calculate_diversity(outputs):
    """计算一组输出的发散性（相似度的倒数）"""
    if len(outputs) < 2:
        return 0.0

    similarities = []
    for i in range(len(outputs)):
        for j in range(i + 1, len(outputs)):
            sim = calculate_similarity(outputs[i], outputs[j])
            similarities.append(sim)

    avg_similarity = sum(similarities) / len(similarities)
    diversity = 1 - avg_similarity  # 发散性 = 1 - 相似度
    return diversity

def calculate_randomness(outputs):
    """计算随机性（基于词汇分布的熵）"""
    all_words = []
    for output in outputs:
        words = output.split()
        all_words.extend(words)

    if not all_words:
        return 0.0

    word_counts = Counter(all_words)
    total = sum(word_counts.values())

    # 计算熵
    entropy = 0.0
    for count in word_counts.values():
        prob = count / total
        if prob > 0:
            entropy -= prob * math.log(prob)

    # 归一化熵（除以最大可能熵）
    max_entropy = math.log(len(word_counts))
    if max_entropy > 0:
        normalized_entropy = entropy / max_entropy
    else:
        normalized_entropy = 0.0

    return normalized_entropy

def extract_semantic_elements(outputs):
    """提取语义元素（关键词）"""
    # 常见天气相关关键词
    weather_keywords = [
        '多云', '阴', '晴', '雨', '舒适', '炎热', '凉爽',
        '湿度', '温度', '风力', '防晒', '补水', '户外活动',
        '适合', '建议', '散步', '骑行', '公园', '参观'
    ]

    semantic_counts = {keyword: 0 for keyword in weather_keywords}

    for output in outputs:
        for keyword in weather_keywords:
            if keyword in output:
                semantic_counts[keyword] += 1

    # 只保留出现过的关键词
    return {k: v for k, v in semantic_counts.items() if v > 0}

def analyze_structure_patterns(outputs):
    """分析结构模式"""
    patterns = {
        '列表式': 0,
        '段落式': 0,
        '混合式': 0
    }

    for output in outputs:
        # 检测是否包含列表标记
        list_markers = len(re.findall(r'^\s*[\d\*\-\•]+\s|^\s*\*\*.*\*\*', output, re.MULTILINE))
        has_list = list_markers >= 3

        # 检测是否分段
        paragraphs = len(re.findall(r'\n\n+', output))

        if has_list and paragraphs >= 1:
            patterns['列表式'] += 1
        elif paragraphs >= 2:
            patterns['混合式'] += 1
        else:
            patterns['段落式'] += 1

    return patterns

def extract_style_features(outputs):
    """提取表达风格特征"""
    features = {
        '语气词': 0,
        '具体例子': 0,
        '数据引用': 0,
        '感叹号': 0,
        '问号': 0,
        '第一人称': 0,
        '第二人称': 0,
    }

    for output in outputs:
        # 语气词
        if re.search(r'[哦啊吧呢嘛呗]', output):
            features['语气词'] += 1

        # 具体例子（地名、景点名）
        if re.search(r'(外滩|豫园|世纪公园|静安公园|博物馆|美术馆)', output):
            features['具体例子'] += 1

        # 数据引用
        if re.search(r'\d+°C|\d+%|\d+级', output):
            features['数据引用'] += 1

        # 标点符号
        features['感叹号'] += output.count('！')
        features['问号'] += output.count('？')

        # 人称
        if '我' in output or '我们' in output:
            features['第一人称'] += 1
        if '你' in output or '您' in output:
            features['第二人称'] += 1

    return features

def analyze_length_stats(outputs):
    """分析长度统计"""
    lengths = [len(output) for output in outputs]

    if not lengths:
        return {'min': 0, 'max': 0, 'avg': 0, 'std': 0}

    avg_length = sum(lengths) / len(lengths)
    variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
    std_length = math.sqrt(variance)

    return {
        'min': min(lengths),
        'max': max(lengths),
        'avg': avg_length,
        'std': std_length
    }

def generate_mermaid_charts(question_num):
    """生成Mermaid图表"""

    temperatures = ['0.0', '0.5', '1.0']
    all_data = {}

    for temp in temperatures:
        outputs = read_outputs_log(temp)
        if not outputs:
            continue

        # 分离两个问题的输出
        question1_outputs = outputs[0:5]  # 前5个是问题1
        question2_outputs = outputs[5:10]  # 后5个是问题2

        current_outputs = question1_outputs if question_num == 1 else question2_outputs

        all_data[temp] = {
            'outputs': current_outputs,
            'diversity': calculate_diversity(current_outputs),
            'randomness': calculate_randomness(current_outputs),
            'semantic': extract_semantic_elements(current_outputs),
            'structure': analyze_structure_patterns(current_outputs),
            'style': extract_style_features(current_outputs),
            'length': analyze_length_stats(current_outputs)
        }

    question_name = "南京天气感觉描述" if question_num == 1 else "上海活动建议"

    # 生成Mermaid图表
    mermaid_content = f"""# Temperature 对比分析 - 问题{question_num}: {question_name}

## 1. 发散性与随机性对比

```mermaid
graph TD
    A[Temperature 参数影响]
    B[0.0]
    C[0.5]
    D[1.0]

    A --> B
    A --> C
    A --> D

    B --> B1[发散性: {all_data['0.0']['diversity']:.3f}]
    B --> B2[随机性: {all_data['0.0']['randomness']:.3f}]

    C --> C1[发散性: {all_data['0.5']['diversity']:.3f}]
    C --> C2[随机性: {all_data['0.5']['randomness']:.3f}]

    D --> D1[发散性: {all_data['1.0']['diversity']:.3f}]
    D --> D2[随机性: {all_data['1.0']['randomness']:.3f}]

    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#ffe1f5
```

## 2. 发散性横向对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[发散性: {all_data['0.0']['diversity']:.3f}]
    B --> B1[发散性: {all_data['0.5']['diversity']:.3f}]
    C --> C1[发散性: {all_data['1.0']['diversity']:.3f}]

    A1 --> A2[低: 结构固定,表达一致]
    B1 --> B2[中: 有一定变化]
    C1 --> C2[高: 多样化表达]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 3. 随机性横向对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[随机性: {all_data['0.0']['randomness']:.3f}]
    B --> B1[随机性: {all_data['0.5']['randomness']:.3f}]
    C --> C1[随机性: {all_data['1.0']['randomness']:.3f}]

    A1 --> A2[词汇重复率高]
    B1 --> B2[词汇多样性中等]
    C1 --> C2[词汇丰富多样]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 4. 结构模式分布对比

```mermaid
pie title Temperature 0.0 - 结构模式
    \"列表式\" : {all_data['0.0']['structure']['列表式']}
    \"段落式\" : {all_data['0.0']['structure']['段落式']}
    \"混合式\" : {all_data['0.0']['structure']['混合式']}
```

```mermaid
pie title Temperature 0.5 - 结构模式
    \"列表式\" : {all_data['0.5']['structure']['列表式']}
    \"段落式\" : {all_data['0.5']['structure']['段落式']}
    \"混合式\" : {all_data['0.5']['structure']['混合式']}
```

```mermaid
pie title Temperature 1.0 - 结构模式
    \"列表式\" : {all_data['1.0']['structure']['列表式']}
    \"段落式\" : {all_data['1.0']['structure']['段落式']}
    \"混合式\" : {all_data['1.0']['structure']['混合式']}
```

## 5. 表达风格特征对比

```mermaid
graph TB
    subgraph Temperature0.0
    A1[语气词: {all_data['0.0']['style']['语气词']}次]
    A2[具体例子: {all_data['0.0']['style']['具体例子']}次]
    A3[数据引用: {all_data['0.0']['style']['数据引用']}次]
    end

    subgraph Temperature0.5
    B1[语气词: {all_data['0.5']['style']['语气词']}次]
    B2[具体例子: {all_data['0.5']['style']['具体例子']}次]
    B3[数据引用: {all_data['0.5']['style']['数据引用']}次]
    end

    subgraph Temperature1.0
    C1[语气词: {all_data['1.0']['style']['语气词']}次]
    C2[具体例子: {all_data['1.0']['style']['具体例子']}次]
    C3[数据引用: {all_data['1.0']['style']['数据引用']}次]
    end

    style Temperature0.0 fill:#e1f5ff
    style Temperature0.5 fill:#fff4e1
    style Temperature1.0 fill:#ffe1f5
```

## 6. 回复长度统计对比

| Temperature | 最短 | 最长 | 平均 | 标准差 |
|:-----------|:----|:----|:----|:------|
| 0.0 | {all_data['0.0']['length']['min']} | {all_data['0.0']['length']['max']} | {all_data['0.0']['length']['avg']:.1f} | {all_data['0.0']['length']['std']:.1f} |
| 0.5 | {all_data['0.5']['length']['min']} | {all_data['0.5']['length']['max']} | {all_data['0.5']['length']['avg']:.1f} | {all_data['0.5']['length']['std']:.1f} |
| 1.0 | {all_data['1.0']['length']['min']} | {all_data['1.0']['length']['max']} | {all_data['1.0']['length']['avg']:.1f} | {all_data['1.0']['length']['std']:.1f} |

## 7. 长度稳定性对比

```mermaid
graph LR
    A[Temperature 0.0]
    B[Temperature 0.5]
    C[Temperature 1.0]

    A --> A1[标准差: {all_data['0.0']['length']['std']:.1f}]
    B --> B1[标准差: {all_data['0.5']['length']['std']:.1f}]
    C --> C1[标准差: {all_data['1.0']['length']['std']:.1f}]

    A1 --> A2[{'高稳定' if all_data['0.0']['length']['std'] < 10 else '中等稳定' if all_data['0.0']['length']['std'] < 20 else '不稳定'}]
    B1 --> B2[{'高稳定' if all_data['0.5']['length']['std'] < 10 else '中等稳定' if all_data['0.5']['length']['std'] < 20 else '不稳定'}]
    C1 --> C2[{'高稳定' if all_data['1.0']['length']['std'] < 10 else '中等稳定' if all_data['1.0']['length']['std'] < 20 else '不稳定'}]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

## 8. 语义内容关键词对比

```mermaid
graph TB
    subgraph Temperature0.0
    A0[关键词频率]
    """

{'<br/>'.join([f'{k}: {v}' for k, v in list(all_data['0.0']['semantic'].items())[:5]])}

    """
    end

    subgraph Temperature0.5
    B0[关键词频率]
    """

{'<br/>'.join([f'{k}: {v}' for k, v in list(all_data['0.5']['semantic'].items())[:5]])}

    """
    end

    subgraph Temperature1.0
    C0[关键词频率]
    """

{'<br/>'.join([f'{k}: {v}' for k, v in list(all_data['1.0']['semantic'].items())[:5]])}

    """
    end

    style Temperature0.0 fill:#e1f5ff
    style Temperature0.5 fill:#fff4e1
    style Temperature1.0 fill:#ffe1f5
```

## 9. 综合对比雷达图数据

| 维度 | Temperature 0.0 | Temperature 0.5 | Temperature 1.0 |
|:-----|:----------------|:----------------|:----------------|
| 发散性 | {all_data['0.0']['diversity']:.3f} | {all_data['0.5']['diversity']:.3f} | {all_data['1.0']['diversity']:.3f} |
| 随机性 | {all_data['0.0']['randomness']:.3f} | {all_data['0.5']['randomness']:.3f} | {all_data['1.0']['randomness']:.3f} |
| 列表化倾向 | {all_data['0.0']['structure']['列表式']/5:.1f} | {all_data['0.5']['structure']['列表式']/5:.1f} | {all_data['1.0']['structure']['列表式']/5:.1f} |
| 长度稳定性 | {1 - all_data['0.0']['length']['std']/100:.1f} | {1 - all_data['0.5']['length']['std']/100:.1f} | {1 - all_data['1.0']['length']['std']/100:.1f} |
| 表达丰富度 | {all_data['0.0']['style']['语气词'] + all_data['0.0']['style']['具体例子']}/10 | {all_data['0.5']['style']['语气词'] + all_data['0.5']['style']['具体例子']}/10 | {all_data['1.0']['style']['语气词'] + all_data['1.0']['style']['具体例子']}/10 |

---

**分析时间**: 自动生成
**数据来源**: temperature:*_outputs.log
"""

    return mermaid_content

if __name__ == "__main__":
    import os

    # 确保在正确的目录
    os.chdir("/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool")

    print("正在分析问题1（南京天气感觉描述）...")
    content1 = generate_mermaid_charts(1)

    print("正在分析问题2（上海活动建议）...")
    content2 = generate_mermaid_charts(2)

    # 保存到文件
    output_file1 = "TEMPERATURE_COMPARISON_Q1.md"
    output_file2 = "TEMPERATURE_COMPARISON_Q2.md"

    with open(output_file1, 'w', encoding='utf-8') as f:
        f.write(content1)

    with open(output_file2, 'w', encoding='utf-8') as f:
        f.write(content2)

    print(f"\n✅ 分析完成！")
    print(f"📄 问题1分析报告: {output_file1}")
    print(f"📄 问题2分析报告: {output_file2}")
