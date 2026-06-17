# 批量测试功能使用指南

## 📋 概述

`temperature_tester.py` 现在支持 **批量测试模式**，可以自动读取 `temperature_experiment.txt` 文件，在所有指定的温度下测试所有问题。

---

## 🎯 功能特点

- ✅ 自动读取实验配置文件
- ✅ 在多个 temperature 值下测试
- ✅ 测试所有问题
- ✅ 自动清空旧日志（可选）
- ✅ 详细的进度显示
- ✅ 完整的日志记录

---

## 📄 实验文件格式

**文件名：** `temperature_experiment.txt`

**格式示例：**
```
Temperature to be tested: 0.1 0.5 0.7 1.0
Question1: 帮我查询今天北京市的实时气温、风力和天气状况。
Question2: 依次查询上海、广州、成都、哈尔滨这四座城市明天一整天的天气，并分城市列出结果。
Question3: 查询杭州未来 3 天的天气，再根据天气告诉我是否适合户外骑行，并给出简单出行提醒。
Question4: 最近几天深圳那边冷不冷啊，出门需不需要带伞？
Question5: 对比一下西安和昆明本周的天气差异，重点对比气温和降雨情况。
```

**格式说明：**
- 第一行：`Temperature to be tested:` 后跟温度值（空格分隔）
- 后续行：`Question1:`, `Question2:`, ... 后跟问题内容
- 支持任意数量的温度值和问题

---

## 🚀 使用方法

### 基本用法

```bash
cd "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool"

# 运行批量测试
python temperature_tester.py --batch-test
```

### 带参数的用法

```bash
# 指定实验文件
python temperature_tester.py --batch-test --experiment-file my_experiment.txt

# 运行前清空日志
python temperature_tester.py --batch-test --clear-logs

# 指定日志目录
python temperature_tester.py --batch-test --log-dir test_logs

# 启用思考模式
python temperature_tester.py --batch-test --thinking-mode on

# 完整示例
python temperature_tester.py \
    --batch-test \
    --clear-logs \
    --experiment-file temperature_experiment.txt \
    --thinking-mode off \
    --log-dir logs
```

---

## 📊 运行示例

### 示例输出

```
🌤️ 高德地图天气查询系统（本地 MCP 服务器 + 思考模式 + 日志）
============================================================
   🧠 思考模式：❌ 未启用
   ⚡ 快速回答模式
   🎯 适用场景：简单查询、快速问答
   🌡️ Temperature：0.7（控制随机性，0=确定性，1=随机）
   📋 日志目录：logs
   📁 日志文件：temperature:0.7.log
============================================================

🚀 启动 MCP 服务器...
✅ MCP 服务器已启动

============================================================
🧪 批量测试模式已启用
============================================================

🗑️  清理旧日志文件...
✅ 已清空 42 个 temperature 日志文件

📄 读取实验文件：temperature_experiment.txt
✅ 成功读取配置：
   - 温度值（4个）：[0.1, 0.5, 0.7, 1.0]
   - 问题数量（5个）

======================================================================
🌡️ Temperature: 0.1 (1/4)
======================================================================

[1/20] 问题 1/5
问题：帮我查询今天北京市的实时气温、风力和天气状况...
🔧 正在查询 北京 的天气... (1/1)
🤖 AI 正在生成回复...
✅ 回复成功（156 字符）

[2/20] 问题 2/5
问题：依次查询上海、广州、成都、哈尔滨这四座城市明天一整天的天气...
🔧 检测到 4 个工具调用（parallel function calling）
🔧 正在查询 上海 的天气... (1/4)
🔧 正在查询 广州 的天气... (2/4)
🔧 正在查询 成都 的天气... (3/4)
🔧 正在查询 哈尔滨 的天气... (4/4)
🤖 AI 正在生成回复...
✅ 回复成功（423 字符）

...（继续测试所有问题和温度）

======================================================================
🌡️ Temperature: 0.5 (2/4)
======================================================================
...（继续测试）

======================================================================
🎉 批量测试全部完成！
======================================================================
总测试次数：20
测试的温度：[0.1, 0.5, 0.7, 1.0]
日志目录：logs

📁 查看日志：
   - logs/temperature:0.1.log
   - logs/temperature:0.1_outputs.log
   - logs/temperature:0.5.log
   - logs/temperature:0.5_outputs.log
   - logs/temperature:0.7.log
   - logs/temperature:0.7_outputs.log
   - logs/temperature:1.0.log
   - logs/temperature:1.0_outputs.log
```

---

## 📁 生成的日志文件

运行批量测试后，会在 `logs/` 目录生成：

```
logs/
├── temperature:0.1.log              # Temperature 0.1 的标准日志
├── temperature:0.1.jsonl            # Temperature 0.1 的 JSON 日志
├── temperature:0.1_api.log         # Temperature 0.1 的 API 日志
├── temperature:0.1_tool.log         # Temperature 0.1 的工具调用日志
├── temperature:0.1_thinking.log    # Temperature 0.1 的思考日志
├── temperature:0.1_error.log       # Temperature 0.1 的错误日志
├── temperature:0.1_outputs.log     # ✅ Temperature 0.1 的 AI 输出
├── temperature:0.5.log              # Temperature 0.5 的日志
├── temperature:0.5_outputs.log     # ✅ Temperature 0.5 的 AI 输出
├── temperature:0.7.log              # Temperature 0.7 的日志
├── temperature:0.7_outputs.log     # ✅ Temperature 0.7 的 AI 输出
├── temperature:1.0.log              # Temperature 1.0 的日志
└── temperature:1.0_outputs.log     # ✅ Temperature 1.0 的 AI 输出
```

---

## 🔍 查看结果

### 方法 1：查看 AI 输出

```bash
# 查看 Temperature 0.1 的所有 AI 回复
cat logs/temperature:0.1_outputs.log

# 查看 Temperature 0.7 的所有 AI 回复
cat logs/temperature:0.7_outputs.log
```

### 方法 2：对比不同 Temperature 的回复

```bash
# 对比 Temperature 0.1 和 1.0 的第一个问题的回复
echo "=== Temperature 0.1 ===" && head -30 logs/temperature:0.1_outputs.log
echo "=== Temperature 1.0 ===" && head -30 logs/temperature:1.0_outputs.log
```

### 方法 3：统计测试结果

```bash
# 统计每个 temperature 的对话数量
for temp in 0.1 0.5 0.7 1.0; do
    count=$(grep "🤖 AI 回复:" logs/temperature:${temp}_outputs.log | wc -l | tr -d ' ')
    echo "Temperature $temp: $count 条回复"
done
```

### 方法 4：查看错误日志

```bash
# 查看是否有错误
cat logs/temperature:0.1_error.log
cat logs/temperature:0.5_error.log
cat logs/temperature:0.7_error.log
cat logs/temperature:1.0_error.log
```

---

## 📊 分析 Temperature 效果

### 分析维度

**1. 回复多样性**
- Temperature 0.1：回复更一致、确定性
- Temperature 0.5：回复有一定变化
- Temperature 0.7：回复变化较多
- Temperature 1.0：回复最随机

**2. 回复质量**
- 检查回复是否完整
- 检查回复是否准确
- 检查回复是否相关

**3. 回复风格**
- 语言表达的差异
- 信息组织的差异
- 详细程度的差异

### 示例分析

```bash
# 提取所有 temperature 的第一个问题的回复
for temp in 0.1 0.5 0.7 1.0; do
    echo "=== Temperature $temp ===" 
    awk '/Question1:/{p=1} p{print} /====/{if(p) exit}' logs/temperature:${temp}_outputs.log
    echo
done
```

---

## 🎯 实验场景

### 场景 1：测试 Temperature 对回复的影响

**目的：** 对比不同 temperature 的回复差异

**步骤：**
1. 准备相同的问题集
2. 使用不同的 temperature 测试
3. 对比回复内容
4. 分析差异

### 场景 2：选择最优 Temperature

**目的：** 找到最适合你应用的 temperature 值

**步骤：**
1. 设计测试问题集
2. 运行批量测试
3. 评估每个 temperature 的回复质量
4. 选择最优值

### 场景 3：压力测试

**目的：** 测试系统稳定性和性能

**步骤：**
1. 设计大量问题
2. 运行批量测试
3. 检查错误率
4. 分析性能指标

---

## 💡 提示和技巧

### 技巧 1：清空日志

**每次测试前清空日志，避免混淆：**
```bash
python temperature_tester.py --batch-test --clear-logs
```

### 技巧 2：自定义实验文件

**创建不同的实验文件测试不同场景：**
```bash
# 创建简单的实验文件
cat > simple_test.txt << EOF
Temperature to be tested: 0.3 0.7
Question1: 今天南京的天气如何？
Question2: 上海天气怎么样？
EOF

# 运行自定义实验
python temperature_tester.py --batch-test --experiment-file simple_test.txt
```

### 技巧 3：监控进度

**批量测试可能需要较长时间，可以：**
1. 使用 `--clear-logs` 确保使用新日志
2. 查看终端输出了解进度
3. 在另一个终端查看日志文件：
   ```bash
   tail -f logs/temperature:0.7_outputs.log
   ```

### 技巧 4：分析结果

**使用脚本分析结果：**
```bash
# 统计每个 temperature 的平均回复长度
for temp in 0.1 0.5 0.7 1.0; do
    echo "Temperature $temp:"
    grep "AI 回复:" logs/temperature:${temp}_outputs.log | \
        awk '{print sum+length} END {print "平均长度:", sum/NR}'
done
```

---

## ⚙️ 命令行参数

| 参数 | 说明 | 默认值 | 示例 |
|:-----|:-----|:-------|:-----|
| `--batch-test` | 启用批量测试模式 | False | `--batch-test` |
| `--experiment-file` | 实验文件路径 | `temperature_experiment.txt` | `--experiment-file my_test.txt` |
| `--clear-logs` | 运行前清空日志 | False | `--clear-logs` |
| `--thinking-mode` | 思考模式 | config.yaml | `--thinking-mode off` |
| `--log-dir` | 日志目录 | `logs` | `--log-dir test_logs` |

---

## 🔧 故障排查

### 问题 1：无法读取实验文件

**错误信息：**
```
❌ 错误：找不到文件 temperature_experiment.txt
```

**解决方案：**
- 确认文件存在于当前目录
- 使用绝对路径或相对路径
- 检查文件权限

### 问题 2：日志未清空

**原因：** 未使用 `--clear-logs` 参数

**解决方案：**
```bash
python temperature_tester.py --batch-test --clear-logs
```

### 问题 3：测试中断

**如果测试中断：**
- 查看日志文件确定哪些测试已完成
- 修改实验文件，只包含未完成的问题
- 重新运行测试

---

## ✅ 快速开始

```bash
cd "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool"

# 1. 查看实验文件
cat temperature_experiment.txt

# 2. 运行批量测试
python temperature_tester.py --batch-test --clear-logs

# 3. 查看结果
cat logs/temperature:0.1_outputs.log
cat logs/temperature:0.7_outputs.log
cat logs/temperature:1.0_outputs.log
```

---

## 📚 相关文档

- [temperature_tester.py](temperature_tester.py) - 主程序文件
- [PARALLEL_FUNCTION_CALLING_GUIDE.md](PARALLEL_FUNCTION_CALLING_GUIDE.md) - Parallel Function Calling 说明
- [TEMPERATURE_TEST_GUIDE.md](Test/TEMPERATURE_TEST_GUIDE.md) - Temperature 测试指南
- [temperature_experiment.txt](temperature_experiment.txt) - 实验配置文件

---

## 🎉 总结

**批量测试功能让你可以：**
- ✅ 自动化测试多个 temperature 值
- ✅ 测试所有问题
- ✅ 生成完整的日志记录
- ✅ 便于比较和分析

**立即开始批量测试！** 🚀
