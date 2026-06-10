# 阿里云百练高德地图天气查询工具 - 任务清单

## 项目概述

使用阿里云百练的高德地图（AMap）工具调用功能，实现天气查询。

---

## 📋 任务清单

### 任务 1：了解高德地图工具定义格式

**目标：** 理解如何在阿里云百练中定义高德地图工具

#### 步骤清单

- [ ] 1.1 查阅阿里云百练文档
  - 访问：https://help.aliyun.com/zh/dashscope/
  - 搜索关键词："工具调用"、"高德地图"
  - 阅读官方示例和 API 说明

- [ ] 1.2 了解工具定义格式
  ```json
  {
    "type": "function",
    "function": {
      "name": "amap_weather",
      "description": "...",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
      }
    }
  }
  ```

- [ ] 1.3 了解高德地图天气 API 参数
  - 支持的查询类型：实时天气、天气预报、查询城市、POI 搜索
  - 参数格式要求

- [ ] 1.4 创建测试文档
  - 记录工具定义格式
  - 记录示例请求和响应

#### 交付物
- [ ] 高德地图工具定义文档
- [ ] 参数说明文档

---

### 任务 2：创建工具调用示例

**目标：** 创建一个完整的高德地图天气查询示例

#### 步骤清单

- [ ] 2.1 创建基础文件结构
  ```
  amap_weather_tool/
  ├── amap_weather.py         # 主程序
  ├── config.yaml              # 配置文件
  └── README.md               # 说明文档
  ```

- [ ] 2.2 编写工具定义
  ```python
  tools = [
      {
          "type": "function",
          "function": {
              "name": "amap_weather",
              "description": "查询指定城市的实时天气信息",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "city": {
                          "type": "string",
                          "description": "城市名称，如：北京、上海"
                      },
                      "type": {
                          "type": "string",
                          "enum": ["base", "all"],
                          "description": "返回类型：base=基础信息, all=全部信息"
                      }
                  },
                  "required": ["city"]
              }
          }
      }
  ]
  ```

- [ ] 2.3 实现工具执行函数
  ```python
  def execute_amap_weather(args):
      city = args.get("city")
      # 调用高德地图 API
      # 返回天气信息
  ```

- [ ] 2.4 集成到对话流程
  - 从 config.yaml 读取配置
  - 创建 OpenAI 客户端
  - 实现多轮对话

- [ ] 2.5 测试基础功能
  - 单城市查询
  - 多城市查询
  - 参数验证

#### 交付物
- [ ] 可运行的 amap_weather.py
- [ ] 测试用例和结果

---

### 任务 3：实现流式输出 + 工具调用

**目标：** 将高德地图工具与流式输出结合

#### 步骤清单

- [ ] 3.1 理解流式工具调用机制
  - 参考 stream_ali.py 的实现
  - 理解工具调用的流式传输
  - 学习如何收集流式工具调用

- [ ] 3.2 创建流式版本
  ```python
  # amap_weather_stream.py
  def collect_streaming_tool_calls(stream):
      """收集流式工具调用"""
      # ... 实现

  def run_streaming_conversation(message):
      """运行流式对话"""
      # ... 实现
  ```

- [ ] 3.3 实现三阶段流程
  ```
  阶段1：收集工具调用（流式）
      ↓
  阶段2：执行高德地图 API
      ↓
  阶段3：流式输出结果
  ```

- [ ] 3.4 处理边界情况
  - 空块处理（choices 为空）
  - 超时处理
  - 错误处理

- [ ] 3.5 性能优化
  - 并行查询多个城市
  - 缓存结果
  - 限流控制

- [ ] 3.6 测试流式输出
  - 单城市流式查询
  - 多城市并行流式查询
  - 对比流式和非流式性能

#### 交付物
- [ ] amap_weather_stream.py
- [ ] 性能对比报告

---

## 📊 进度跟踪表

| 任务 | 状态 | 完成度 | 备注 |
|------|------|--------|------|
| 任务1：了解工具定义 | 🔄 进行中 | 0% | 待开始 |
| 任务2：创建示例 | ⏳ 待开始 | 0% | 依赖任务1 |
| 任务3：流式输出 | ⏳ 待开始 | 0% | 依赖任务2 |

---

## 🎯 关键注意事项

### 配置要求
- ✅ 需要有效的阿里云百练 API Key
- ✅ 需要启用高德地图工具权限
- ✅ config.yaml 正确配置

### 高德地图 API 特点
- 支持的城市范围
- 调用频率限制
- 返回数据格式

### 流式输出要点
- 流只能遍历一次
- 需要重新创建请求来多次遍历
- 空块需要安全处理

---

## 📚 参考资料

- [阿里云百练文档](https://help.aliyun.com/zh/dashscope/)
- [高德地图 API 文档](https://lbs.amap.com/api/)
- [工具调用最佳实践](https://help.aliyun.com/zh/dashscope/developer-reference/tool-calling)

---

## 🔄 下一步行动

1. **立即开始：** 任务 1.1 - 查阅阿里云百练文档
2. **本周完成：** 任务 1 - 了解工具定义格式
3. **下周目标：** 任务 2 - 创建工具调用示例

---

*创建日期：2026-06-04*
*最后更新：2026-06-04*
