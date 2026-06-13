# 工具调用详细过程分析报告

## 分析时间
2026-06-13 14:15

## 🔍 **工具调用流程分析**

### 1. **完整的对话流程**

根据日志文件分析，一次完整的天气查询包含以下步骤：

#### **步骤1：用户提问**
```
用户问题: "南京今天的天气怎么样？"
对话历史长度: 2
```

#### **步骤2：第一轮API调用（触发工具调用）**
```json
{
  "question": "南京今天的天气怎么样？",
  "model": "qwen-max",
  "thinking_mode": false,
  "tools": [{
    "type": "function",
    "function": {
      "name": "amapMaps.weather",
      "description": "查询指定城市的实时天气信息，包括温度、湿度、风向等",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {
            "type": "string",
            "description": "城市名称，如：北京、上海、广州、苏州"
          }
        },
        "required": ["city"]
      }
    }
  }]
}
```

**响应**：
```json
{
  "round": 1,
  "status_code": 200,
  "finish_reason": "tool_calls",  // ✅ AI决定调用工具
  "latency_ms": "1355.28"
}
```

#### **步骤3：工具执行（并行）**
- **MCP服务器启动**：成功启动，找到12个工具
- **工具列表**：`["maps_regeocode", "maps_geo", "maps_ip_location", "maps_weather", ...]`
- **工具调用**：AI要求调用 `amapMaps.weather` 工具
- **执行过程**：并行执行工具调用

#### **步骤4：第二轮API调用（提供工具结果）**
```json
{
  "round": 2,
  "messages_count": 4,
  "tool_result_provided": true,  // ✅ 工具结果已提供
  "thinking_mode": false
}
```

**响应**：
```json
{
  "round": 2,
  "status_code": "stream",
  "latency_ms": "5637.82"
}
```

#### **步骤5：AI回复生成**
```
AI回复: "哎呀，看起来我们没法直接查到南京今天的天气。不过你可以自己查一下最新的天气预报哦..."
```

---

## ⚠️ **发现的问题**

### 1. **工具名称不匹配**

**问题**：Dashscope API 返回的工具名称与内部函数名称不匹配

- **API返回的工具名称**：`amapMaps.weather`
- **内部函数期望的名称**：`get_weather`

**代码位置**：`execute_single_tool` 函数（第596行）
```python
if tool_name == "get_weather":  # ❌ 这里检查的是 "get_weather"
    city = tool_args.get("city", "")
    weather_data = get_weather_data(city, client, logger)
    return json.dumps(weather_data, ensure_ascii=False)
else:
    return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
```

**结果**：当 `tool_name` 是 `"amapMaps.weather"` 时，代码返回错误

### 2. **工具日志文件为空**

**问题**：`weather_agent_tool_20260613.log` 文件大小为 0 字节

**原因分析**：
1. 工具名称不匹配，导致 `execute_single_tool` 返回错误
2. 错误情况下没有记录工具调用日志
3. 只有成功的工具调用才会被记录

### 3. **AI回复暗示工具调用失败**

**AI回复内容**：
> "由于我无法直接调用或访问外部工具如'ammapMaps.weather'的数据"

这说明：
- AI知道应该调用工具
- 但是工具调用可能没有返回有效数据
- 所以AI基于常识知识给出了建议

---

## 🔧 **工具调用架构分析**

### **当前架构流程**

```
1. 用户提问
   ↓
2. Dashscope API 分析
   ↓
3. API返回 tool_calls (工具名称: amapMaps.weather)
   ↓
4. execute_tools_parallel 处理
   ↓
5. execute_single_tool (检查工具名称)
   ↓
6. 工具名称不匹配 ❌
   ↓
7. 返回错误 {"error": "未知工具: amapMaps.weather"}
   ↓
8. AI接收到错误结果
   ↓
9. AI基于常识知识回复
```

### **正确的架构流程（应该是）**

```
1. 用户提问
   ↓
2. Dashscope API 分析
   ↓
3. API返回 tool_calls (工具名称: amapMaps.weather)
   ↓
4. execute_tools_parallel 处理
   ↓
5. execute_single_tool (应该支持 amapMaps.weather)
   ↓
6. 调用 get_weather_data
   ↓
7. 通过MCP客户端查询高德API
   ↓
8. 返回真实天气数据 ✅
   ↓
9. AI基于真实数据回复
```

---

## 🎯 **根本原因**

### **工具名称映射问题**

**MCP服务器提供的工具**：
- `maps_weather` (MCP服务器内部名称)
- `amapMaps.weather` (Dashscope API使用的名称)

**内部函数定义**：
- `execute_single_tool(tool_name: str, ...)`
- 只支持 `tool_name == "get_weather"`

**映射关系缺失**：
```python
# ❌ 当前代码
if tool_name == "get_weather":
    # 执行天气查询

# ✅ 应该支持
if tool_name in ["get_weather", "amapMaps.weather", "maps_weather"]:
    # 执行天气查询
```

---

## 📊 **数据流分析**

### **第一轮API调用（触发工具）**

**请求**：
- 工具定义：`amapMaps.weather`
- 期望参数：`{"city": "string"}`

**响应**：
- `finish_reason: "tool_calls"` ✅
- 工具被正确识别

### **工具执行阶段**

**问题点**：
1. ✅ MCP服务器成功启动（12个工具）
2. ✅ 工具调用被正确触发
3. ❌ 工具名称映射失败
4. ❌ 返回错误而不是天气数据

### **第二轮API调用（生成回复）**

**请求**：
- 包含4条消息（用户问题 + 系统提示 + assistant工具调用 + tool结果）
- `tool_result_provided: true` ✅

**响应**：
- AI生成的回复基于常识知识，不是真实天气数据

---

## 🔬 **详细问题定位**

### **问题1：execute_single_tool 函数**

**位置**：main.py 第583-601行

**问题代码**：
```python
def execute_single_tool(tool_name: str, tool_args: dict, client: AmapMCPClient, logger=None) -> str:
    if tool_name == "get_weather":  # ❌ 只支持一个名称
        city = tool_args.get("city", "")
        weather_data = get_weather_data(city, client, logger)
        return json.dumps(weather_data, ensure_ascii=False)
    else:
        return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
```

**问题**：
- 只支持工具名称 `"get_weather"`
- Dashscope API返回的是 `"amapMaps.weather"`
- 导致工具执行失败

### **问题2：MCP客户端调用流程**

**正确的调用路径应该是**：
```python
用户问题 → Dashscope API → 返回 amapMaps.weather 
→ execute_tools_parallel → execute_single_tool 
→ AmapMCPClient.get_weather() → 高德API → 返回真实数据
```

**实际发生的路径**：
```python
用户问题 → Dashscope API → 返回 amapMaps.weather 
→ execute_tools_parallel → execute_single_tool 
→ 工具名称不匹配 ❌ → 返回错误
→ AI基于常识知识回复
```

### **问题3：日志记录缺失**

**工具日志为空的原因**：
1. 工具调用失败，没有成功记录
2. `log_tool_call` 只在成功时被调用
3. 失败情况没有被记录到工具日志

---

## 📝 **建议的修复方案**

### **修复1：支持多种工具名称**

```python
def execute_single_tool(tool_name: str, tool_args: dict, client: AmapMCPClient, logger=None) -> str:
    """执行单个工具调用"""
    # ✅ 支持多种工具名称映射
    weather_tools = ["get_weather", "amapMaps.weather", "maps_weather"]
    
    if tool_name in weather_tools:
        city = tool_args.get("city", "")
        if logger:
            logger.logger.info(f"🔧 执行工具: {tool_name}, 城市: {city}")
        
        weather_data = get_weather_data(city, client, logger)
        
        if logger:
            logger.logger.info(f"✅ 工具执行完成: {tool_name}")
        
        return json.dumps(weather_data, ensure_ascii=False)
    else:
        if logger:
            logger.logger.warning(f"⚠️ 未知工具: {tool_name}")
        return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
```

### **修复2：增强日志记录**

在 `execute_tools_parallel` 函数中添加日志：
```python
for tc in tool_calls:
    try:
        # 解析工具信息
        if isinstance(tc, dict):
            tc_id = tc.get("id")
            tc_function_name = tc.get("function", {}).get("name")
            tc_arguments = tc.get("function", {}).get("arguments", "{}")
        else:
            tc_id = tc.id
            tc_function_name = tc.function.name
            tc_arguments = tc.function.arguments

        if logger:
            logger.logger.info(f"🔧 开始执行工具: {tc_function_name} (ID: {tc_id})")
            logger.log_tool_call(tc_function_name, json.loads(tc_arguments), "started")

        result = futures[tc_id].result(timeout=15)
        
        if logger:
            logger.log_tool_call(tc_function_name, json.loads(tc_arguments), {
                "status": "success",
                "result": result
            })
```

### **修复3：错误处理改进**

```python
except Exception as e:
    if logger:
        logger.logger.error(f"❌ 工具执行失败: {tc_function_name} - {str(e)}")
        logger.log_tool_call(tc_function_name, json.loads(tc_arguments), {
            "status": "failed",
            "error": str(e)
        })
```

---

## 🎓 **学习要点**

### 1. **工具名称映射的重要性**

在AI应用中，工具名称可能在多个层面被定义：
- **MCP服务器**：内部工具名称
- **Dashscope API**：API层面的工具名称
- **应用代码**：内部函数名称

**最佳实践**：建立统一的工具名称映射表

### 2. **日志记录的完整性**

日志应该记录：
- ✅ 工具调用开始
- ✅ 工具参数
- ✅ 工具执行过程
- ✅ 工具执行结果
- ✅ 工具调用失败原因

### 3. **错误处理的可见性**

当工具调用失败时：
- ✅ 应该有详细的错误日志
- ✅ 应该记录失败的工具和参数
- ✅ 应该记录失败的具体原因

---

## 📊 **当前状态总结**

| 组件 | 状态 | 说明 |
|------|------|------|
| **MCP服务器** | ✅ 正常 | 成功启动，找到12个工具 |
| **Dashscope API** | ✅ 正常 | 正确返回tool_calls |
| **工具触发** | ✅ 正常 | AI正确识别需要调用工具 |
| **工具名称映射** | ❌ 失败 | 名称不匹配 |
| **工具执行** | ❌ 失败 | 返回错误而非天气数据 |
| **日志记录** | ⚠️ 不完整 | 工具日志为空 |
| **AI回复生成** | ✅ 正常 | 基于常识知识生成回复 |

---

## 💡 **下一步行动**

1. **立即修复**：修改 `execute_single_tool` 函数支持多种工具名称
2. **验证修复**：重新运行测试，查看工具日志是否被记录
3. **完善日志**：增强工具调用的日志记录
4. **测试真实数据**：确认高德API返回真实天气数据

---

**分析完成时间**：2026-06-13 14:15
**分析人员**：Claude Code Agent
**日志数据来源**：ai-chat-tool/logs/ (20260613)
