# Day3: 用 openai 库发送请求，获取回复
#打印完整的请求 JSON 和响应 JSON

import os
import json  # 导入 json 模块，用于格式化打印
from openai import OpenAI

# 从环境变量获取 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")

# 检查 API Key 是否存在
if not api_key:
    print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
    print("\n请先设置环境变量：")
    print("  临时设置：export DASHSCOPE_API_KEY='your-key-here'")
    print("  永久设置：将上面命令添加到 ~/.zshrc 文件中")
    exit(1)

# 注意: 不同地域的base_url不通用（下方示例使用北京地域的 base_url）
# - 华北2（北京）: https://dashscope.aliyuncs.com/compatible-mode/v1
# - 美国（弗吉尼亚）: https://dashscope-us.aliyuncs.com/compatible-mode/v1
# - 新加坡: https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1，请将WorkspaceId替换为业务空间ID
# - 德国（法兰克福）: https://{WorkspaceId}.eu-central-1.maas.aliyuncs.com/compatible-mode/v1，请将WorkspaceId替换为业务空间ID

print(f"✅ API Key 已加载: {api_key[:8]}...")  # 只显示前8位

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# ============================================================================
# 构建请求参数（用于打印请求 JSON）
# ============================================================================
request_params = {
    "model": "qwen3.6-plus",
    "messages": [
        {'role': 'user', 'content': '你是谁？'}
    ]
}

print("=" * 60)
print("📤 请求 JSON (Request JSON):")
print("=" * 60)
# 使用 json.dumps() 格式化打印，ensure_ascii=False 支持中文，indent=2 美化格式
print(json.dumps(request_params, ensure_ascii=False, indent=2))
print("=" * 60)

print("\n🤖 正在调用模型...")
completion = client.chat.completions.create(**request_params)

print("\n" + "=" * 60)
print("📥 响应 JSON (Response JSON):")
print("=" * 60)
# 方法1：使用 model_dump_json() 获取完整的 JSON 字符串
response_json = completion.model_dump_json()
# 方法2：如果想要更清晰的格式，可以先转成字典再格式化
# response_dict = completion.model_dump()
# response_json = json.dumps(response_dict, ensure_ascii=False, indent=2)
print(response_json)
print("=" * 60)

# 打印所有字段名称
print("响应对象的所有字段：")
print(completion.model_dump().keys())
print("=" * 60)

print("\n📝 模型回复内容：")
print(completion.choices[0].message.content)

# 可选：打印更多响应信息
print(f"\n📊 响应详细信息：")
print(f"  - 模型: {completion.model}")
print(f"  - 使用的 Token: {completion.usage.total_tokens if hasattr(completion, 'usage') and completion.usage else 'N/A'}")

'''
响应json解释:
{
  "id": "chatcmpl-1234567890", //本次请求的唯一标识符，用于追踪和调试
  "object": "chat.completion", //响应对象类型，固定为 "chat.completion"
  "created": 1234567890,   //请求创建的时间戳（Unix 时间，秒）
  "model": "qwen3.6-plus",  //实际使用的模型名称
  "choices": [ //数组，包含一个或多个候选答案
    {
      "index": 0,
      "message": {
        "role": "assistant",  //消息角色，固定为 "assistant"
        "content": "我是通义千问，由阿里云开发的人工智能助手..."
      },
      "finish_reason": "stop"  //结束原因："stop"（正常结束）、"length"（达到长度限制）、"content_filter"（内容过滤）
    }
  ],
  "usage": {
    "prompt_tokens": 10, //输入（用户问题）消耗的 Token 数量
    "completion_tokens": 20,  //输出（AI 回复）消耗的 Token 数量
    "total_tokens": 30 //总共消耗的 Token 数量
  }
}

 
'''