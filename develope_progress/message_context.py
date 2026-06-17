# Day 4 学习message字段
# 尝试有上下文的多轮对话
import os
import json  # 导入 json 模块，用于格式化打印
from openai import OpenAI

api_key = os.getenv("DASHSCOPE_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

request_params = {
    "model": "qwen3.6-plus",
    "messages": [
    {"role": "system", "content": "你是会加减乘除的小学生 请用中文回答"},
    {"role": "user", "content": "1+1"},
    {"role": "assistant", "content": "等于2"},
    {"role": "user", "content": "再加1"}
    # 有context多轮对话
    ]
}

print("=" * 60)
print("📤 请求 JSON (Request JSON):")
print("=" * 60)
# 使用 json.dumps() 格式化打印，ensure_ascii=False 支持中文，indent=2 美化格式
print(json.dumps(request_params, ensure_ascii=False, indent=2))
print("=" * 60)

completion = client.chat.completions.create(**request_params)

print("\n" + "=" * 60)
print("📥 响应 JSON (Response JSON):")
print("=" * 60)
# 方法1：使用 model_dump_json() 获取完整的 JSON 字符串
response_json = completion.model_dump_json()
print(response_json)
print("=" * 60)

print("\n📝 模型回复内容：")
print(completion.choices[0].message.content)
