# CoT学习实验项目

本文件夹包含CoT（Chain of Thought，思维链）学习的所有实验代码、文档和结果。

---

## 📁 文件结构

```
CoT/
├── README.md                           # 本文件，项目说明
├── cot_experiment.py                   # CoT对照实验脚本
├── CoT_Papers_Abstract_Official.md     # 论文Abstract官方版本（从PDF提取）
├── CoT_Papers_Abstract_Collection.md   # 论文Abstract完整版本（包含推荐论文）
├── experiments/                        # 实验结果文件夹（运行实验后生成）
│   └── cot_experiment_results_*.json   # 实验结果JSON文件
└── docs/                              # 额外文档（待添加）
    └── cot_analysis.md               # 实验分析报告（待创建）
```

---

## 🎯 项目目标

1. **理论理解**：深入理解CoT、Zero-Shot CoT、Self-Consistency、ToT等核心概念
2. **实验验证**：通过对照实验验证CoT对模型推理能力的影响
3. **工程实现**：在项目中实现可配置的思考开关，支持CoT模式

---

## 📚 学习资源

### 核心论文（Abstract已收录）
1. **Chain-of-Thought Prompting Elicits Reasoning in LLMs** (Wei et al., NeurIPS 2022)
2. **Self-Consistency Improves CoT Reasoning in Language Models** (Wang et al., 2023)
3. **LLMs are Zero-Shot Reasoners** (Kojima et al., NeurIPS 2022)
4. **Incentivizing Reasoning Capability in LLMs via Reinforcement Learning** (OpenAI, 2024)
5. **ThinkDial: An Open Recipe** (ThinkDial Team, 2024)

### 文档说明
- **CoT_Papers_Abstract_Official.md**：从Paper文件夹PDF中提取的真实Abstract，逐段中英文对照
- **CoT_Papers_Abstract_Collection.md**：包含推荐的补充论文，完整的Abstract合集

---

## 🧪 实验设计

### 测试题库（15题）
- **数学计算题**（5题）：多步算术推理
- **逻辑推理题**（5题）：逻辑分析和演绎推理
- **常识推理题**（5题）：常识应用和因果推理

### 实验变量
- **自变量**：CoT模式（开 vs 关）
- **因变量**：答案正确率、推理过程质量、输出token数
- **控制变量**：模型选择、温度参数、测试题目

### 实验模型
- **主模型**：qwen-max（最强推理能力）
- **备选模型**：qwen3.6-plus（平衡性能）

---

## 🚀 快速开始

### 运行实验
```bash
cd CoT
python cot_experiment.py
```

### 查看结果
实验结果会自动保存为JSON文件，包含：
- 详细的问题和回答
- 成功率统计
- Token使用分析
- 分类性能对比

---

## 📊 实验结果示例

### 预期输出
```
🧪 CoT对照实验开始
────────────────────────────────────────────────────────────
题目 1/15 (数学计算)
────────────────────────────────────────────────────────────
问题：小明有15个弹珠，给了小红3个，又买了8个...
正确答案：18

🔵 测试1：不使用CoT
回答：小明现在有18个弹珠。
Token使用：45

🟢 测试2：使用CoT
回答：让我一步步思考：①初始有15个弹珠 ②给小红3个...
Token使用：87
```

### 统计分析
```
📊 实验结果分析
────────────────────────────────────────────────────────────
📈 基本统计
总题目数：15
无CoT成功率：8/15 (53.3%)
有CoT成功率：12/15 (80.0%)

💰 Token使用统计
无CoT总Token：450
有CoT总Token：1200
增加比例：166.7%
```

---

## 🔧 配置和自定义

### 修改实验参数
编辑 `cot_experiment.py` 中的配置部分：

```python
# 实验配置
MODEL = "qwen-max"        # 可改为 qwen3.6-plus
TEMPERATURE = 0.7         # 可改为 0（确定性）或 1（创造性）
MAX_TOKENS = 2000         # 可调整输出长度限制
```

### 添加自定义题目
在题库部分添加新的测试题目：

```python
MATH_QUESTIONS = [
    {
        "question": "你的问题",
        "correct_answer": "正确答案",
        "category": "数学计算"
    },
    # 添加更多题目...
]
```

---

## 📖 学习路径建议

### 初学者路径
1. 阅读 `CoT_Papers_Abstract_Official.md` 中的论文1和论文3
2. 运行基础实验观察效果差异
3. 理解CoT触发词"Let's think step by step"的作用

### 进阶研究者路径
1. 精读所有5篇论文的Abstract
2. 分析实验结果中的错误模式
3. 尝试修改题库进行深度实验

### 工程实践者路径
1. 直接运行实验获取基准数据
2. 根据结果优化CoT提示词
3. 集成到实际项目中

---

## 📝 待完成任务

### 理论学习
- [ ] 完成CoT原理自测题
- [ ] 阅读完整论文（不仅是Abstract）
- [ ] 理解Zero-Shot vs Few-Shot CoT差异

### 实验验证
- [ ] 运行基础对照实验
- [ ] 分析不同类别的性能差异
- [ ] 调整参数进行对比实验

### 工程实现
- [ ] 在config.yaml中添加thinking配置项
- [ ] 实现enable_thought_mode开关代码
- [ ] 集成到chat_with_tool.py中

---

## 🎯 下一步行动

### 立即可做
1. **运行实验**：`python cot_experiment.py`
2. **查看结果**：分析JSON输出文件
3. **理解差异**：对比有无CoT的输出差异

### 短期计划
1. **理论深化**：完成论文精读
2. **实验扩展**：添加更多测试题目
3. **代码集成**：实现YAML配置开关

### 长期目标
1. **生产部署**：在实际应用中启用CoT模式
2. **性能优化**：平衡推理质量和token成本
3. **效果监控**：建立CoT效果评估体系

---

## 📧 技术支持

如有问题或建议，请通过以下方式联系：
- 项目仓库：[GitHub链接]
- 技术讨论：[讨论区链接]

---

**创建时间**：2026-06-07
**最后更新**：2026-06-07
**维护者**：CoT学习项目组

---

*本文件夹致力于CoT技术的学习和实践，欢迎贡献和建议！*
