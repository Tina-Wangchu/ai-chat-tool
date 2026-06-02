#用 dashscope 库发送请求，获取回复
import os

# 从 dashscope 库导入 Generation 类，用于调用大语言模型
from dashscope import Generation

# 导入 dashscope 主模块，用于配置全局参数
import dashscope

# ============================================================================
# 第1步：配置 API 地址
# ============================================================================
# 设置阿里云百炼平台的 HTTP API 地址
# 这里使用华北2（北京）地域的 URL
# 不同地域的 URL 不同：
#   - 华北2（北京）: https://dashscope.aliyuncs.com/api/v1
#   - 美国（弗吉尼亚）: https://dashscope-us.aliyuncs.com/api/v1
#   - 新加坡: https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# ============================================================================
# 第2步：构建对话消息
# ============================================================================
# messages 是一个列表，存储对话历史
# 每个元素是一个字典，包含 'role'（角色）和 'content'（内容）
#
# role 的可选值：
#   - 'system': 系统提示词，定义 AI 的行为和角色
#   - 'user': 用户的消息
#   - 'assistant': AI 的回复（用于多轮对话的历史记录）
messages = [
    # system 消息：设置 AI 的角色和风格
    {'role': 'system', 'content': 'You are a helpful assistant.'},

    # user 消息：用户的问题
    {'role': 'user', 'content': '你是谁？'}
]

# ============================================================================
# 第3步：调用大语言模型
# ============================================================================
# Generation.call() 是核心方法，用于调用通义千问模型
response = Generation.call(
    # api_key: 认证密钥
    # os.getenv("DASHSCOPE_API_KEY") 从环境变量中读取 API Key
    # 如果环境变量未设置，可以替换为：api_key="sk-你的真实密钥"
    api_key=os.getenv("DASHSCOPE_API_KEY"),

    # model: 指定使用的模型
    # 常用模型：
    #   - qwen-turbo: 快速响应，适合简单任务
    #   - qwen-plus: 平衡性能和速度（推荐）
    #   - qwen-max: 最强性能，适合复杂任务
    #   - qwen3.6-plus: 最新版本
    # 完整模型列表：https://help.aliyun.com/model-studio/getting-started/models
    model="qwen-plus",

    # messages: 对话历史（上文已定义）
    messages=messages,

    # result_format: 返回结果格式
    #   - "message": 返回完整的消息对象（推荐）
    #   - "text": 仅返回文本内容
    result_format="message"
)

# ============================================================================
# 第4步：处理响应结果
# ============================================================================
# response.status_code: HTTP 状态码
#   - 200: 请求成功
#   - 401: API Key 错误或未授权
#   - 400: 请求参数错误
#   - 500: 服务器内部错误
if response.status_code == 200:
    # 请求成功，提取并打印 AI 的回复
    # response.output.choices[0].message.content 的结构说明：
    #   - response: 完整的响应对象
    #   - .output: 输出内容部分
    #   - .choices[0]: 第一个候选答案（通常只有一个）
    #   - .message.content: 消息的文本内容
    print(response.output.choices[0].message.content)
else:
    # 请求失败，打印错误信息
    print(f"HTTP返回码：{response.status_code}")  # HTTP 状态码
    print(f"错误码：{response.code}")            # 阿里云业务错误码
    print(f"错误信息：{response.message}")        # 错误描述
    # 打印错误码参考文档链接
    print("请参考文档：https://help.aliyun.com/model-studio/developer-reference/error-code")