# Temperature 参数测试指南

## 📋 概述

`main copy.py` 已更新支持 **混合 temperature 模式**：
- ✅ 支持命令行参数 `--temperature` 覆盖配置
- ✅ 日志文件按 temperature 值分文件保存
- ✅ 向后兼容：不传参数时使用 config.yaml 中的值
- ✅ API 调用正确传递 temperature 参数

---

## 🎯 修改总结

### 1. AgentLogger 类（混合模式）

**修改位置：** 第 135 行

**修改内容：**
```python
def __init__(self, log_dir="logs", agent_name="weather_agent", temperature=None):
    # 优先使用传入的参数，否则从 config 读取
    if temperature is not None:
        self.temperature = temperature
    else:
        self.temperature = config.get('model_parameters', {}).get('temperature', 0.7)
```

### 2. 日志文件命名统一

**修改位置：** 第 160、186、200、216、232、248 行

**修改前：**
- `temperature0.7.log` ❌
- `weather_agent_json_temperature0.7.jsonl` ❌

**修改后：**
- `temperature:0.7.log` ✅
- `temperature:0.7.jsonl` ✅
- `temperature:0.7_api.log` ✅
- `temperature:0.7_tool.log` ✅
- `temperature:0.7_thinking.log` ✅
- `temperature:0.7_error.log` ✅

### 3. 命令行参数

**修改位置：** 第 1122 行

**新增参数：**
```python
parser.add_argument('--temperature', type=float, default=None,
                   help='Temperature参数（默认：使用config.yaml中的值）')
```

### 4. API 调用传递 temperature

**修改位置：** 第 845、931、994 行

**修改内容：**
```python
resp = Generation.call(
    model=config['api']['model'],
    messages=[...],
    temperature=actual_temperature,  # ✅ 添加
    ...
)
```

### 5. 函数签名更新

**修改位置：** 第 755 行

**修改内容：**
```python
def ask_weather_with_mcp(..., temperature=None):
    # 处理 temperature 参数
    if temperature is not None:
        actual_temperature = temperature
    else:
        actual_temperature = config.get('model_parameters', {}).get('temperature', 0.7)
```

---

## 🚀 使用方法

### 方法 1：命令行参数（推荐）

```bash
# Temperature 0.1（更确定性）
python "main copy.py" --temperature 0.1

# Temperature 0.5（平衡）
python "main copy.py" --temperature 0.5

# Temperature 0.9（更随机）
python "main copy.py" --temperature 0.9

# 不指定参数（使用 config.yaml 中的值）
python "main copy.py"
```

### 方法 2：使用 config.yaml

编辑 `config.yaml`：
```yaml
model_parameters:
  temperature: 0.3  # 修改这个值
```

然后运行：
```bash
python "main copy.py"
```

### 方法 3：编程方式

```python
from main_copy import AgentLogger

# 创建不同 temperature 的 logger
logger1 = AgentLogger(log_dir="logs", agent_name="weather_agent", temperature=0.1)
logger2 = AgentLogger(log_dir="logs", agent_name="weather_agent", temperature=0.5)
logger3 = AgentLogger(log_dir="logs", agent_name="weather_agent", temperature=0.9)

# 日志将保存在不同文件
# temperature:0.1.log
# temperature:0.5.log
# temperature:0.9.log
```

---

## 🧪 测试示例

### 手动测试

```bash
# 1. 清理旧日志
rm -f logs/temperature:*.log*

# 2. 测试 temperature 0.1
python "main copy.py" --temperature 0.1
# 提问：今天南京的天气如何
# 输入：quit

# 3. 检查日志
cat logs/temperature:0.1.log

# 4. 测试 temperature 0.9
python "main copy.py" --temperature 0.9
# 提问：今天南京的天气如何
# 输入：quit

# 5. 检查日志
cat logs/temperature:0.9.log
```

### 自动化测试

运行测试脚本：
```bash
cd Test
python test_temperature_logs.py
```

---

## 📊 日志文件结构

运行后，`logs/` 目录将包含：

```
logs/
├── temperature:0.1.log              # Temperature 0.1 的标准日志
├── temperature:0.1.jsonl            # Temperature 0.1 的 JSON 日志
├── temperature:0.1_api.log         # Temperature 0.1 的 API 日志
├── temperature:0.1_tool.log         # Temperature 0.1 的工具调用日志
├── temperature:0.1_thinking.log     # Temperature 0.1 的思考过程日志
├── temperature:0.1_error.log        # Temperature 0.1 的错误日志
├── temperature:0.5.log              # Temperature 0.5 的日志
├── temperature:0.9.log              # Temperature 0.9 的日志
└── ...
```

---

## 💡 Temperature 参数说明

**Temperature** 控制模型输出的随机性：

| 值 | 效果 | 适用场景 | 行为特点 |
|:---|:-----|:---------|:---------|
| **0.0 - 0.3** | 更确定性 | 事实查询、编程、数学 | 回复更一致、可预测 |
| **0.4 - 0.7** | 平衡 | 日常对话、一般问答 | 平衡创造性和一致性 |
| **0.8 - 1.0** | 更随机 | 创意写作、头脑风暴 | 回复更多样、不可预测 |

**示例：**
```python
# 相同问题，不同 temperature 的回复可能不同：

# temperature: 0.1
问：南京今天的天气如何？
答：根据查询结果，南京今天多云，温度 22-28°C。

# temperature: 0.9（可能多次提问得到不同表达）
问：南京今天的天气如何？
答1：今天南京的天气是多云，气温在22到28度之间。
答2：根据天气预报，南京今日多云，最高温度28度，最低温度22度。
答3：查询显示，南京今天天气多云，气温范围22-28摄氏度。
```

---

## ✅ 验证清单

测试完成后，请验证：

- [ ] 命令行参数 `--temperature` 可以覆盖配置文件值
- [ ] 日志文件命名格式为 `temperature:{value}.log`
- [ ] 不同 temperature 的日志保存在不同文件
- [ ] 不传参数时使用 config.yaml 中的值
- [ ] 日志文件中记录了使用的 temperature 值
- [ ] API 调用正确传递了 temperature 参数

---

## 🔧 故障排查

### 问题 1：日志文件没有生成

**检查：**
```bash
ls -la logs/temperature:*.log
```

**可能原因：**
- 日志目录权限问题
- 程序运行错误
- 命令行参数未正确传递

### 问题 2：所有日志保存在同一个文件

**检查命令：**
```bash
# 应该看到多个 temperature:*.log 文件
ls logs/
```

**可能原因：**
- AgentLogger 未正确接收 temperature 参数
- 文件命名逻辑错误

### 问题 3：API 调用没有使用指定的 temperature

**检查日志：**
```bash
grep "temperature" logs/temperature:0.5.log
```

**应该看到：**
```json
{
  "round": 1,
  "temperature": 0.5,
  ...
}
```

---

## 📚 相关文档

- [main copy.py](../main%20copy.py) - 主程序文件
- [config.yaml](../config.yaml) - 配置文件
- [test_temperature_logs.py](test_temperature_logs.py) - 自动化测试脚本
- [agent_logger_explanation.md](../agent_logger_explanation.md) - AgentLogger 说明

---

## ✅ 完成状态

- ✅ AgentLogger 构造函数支持 temperature 参数
- ✅ 日志文件命名统一为 `temperature:{value}` 格式
- ✅ 命令行参数 `--temperature` 已添加
- ✅ API 调用传递 temperature 参数（3 处）
- ✅ 主程序传递 temperature 给 AgentLogger
- ✅ 日志请求中记录 temperature 值
- ✅ 显示当前 temperature 值
- ✅ 测试脚本已创建

**所有修改已完成！🎉**
