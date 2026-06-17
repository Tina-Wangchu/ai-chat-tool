"""
配置加载模块

这个模块提供了两个简单的函数，用于：
1. 从 YAML 文件加载配置
2. 创建配置好的 API 客户端

使用示例：
    from config_load import load_config, get_client

    # 方式1：加载配置
    config = load_config()
    print(config['api']['model'])

    # 方式2：直接获取客户端
    client = get_client()

    # 一定要先加载配置再创建客户端

"""

import yaml  # 导入 yaml 库，用于读取 YAML 格式的配置文件
import os    # 导入 os 库，用于读取环境变量


def _get_config_path():
    """
    获取配置文件的绝对路径

    优先级：
    1. 当前目录的 config.yaml
    2. 脚本所在目录的 config.yaml
    3. 上级目录的 config.yaml
    """
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 可能的配置文件路径（按优先级）
    possible_paths = [
        'config.yaml',                          # 当前目录
        os.path.join(script_dir, 'config.yaml'), # 脚本所在目录
        os.path.join(script_dir, '..', 'config.yaml'),  # 上级目录
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果都找不到，返回脚本所在目录的路径（默认）
    return os.path.join(script_dir, 'config.yaml')


def load_config(path='config.yaml'):
    """
    加载 YAML 配置文件

    参数：
        path: 配置文件的路径，默认自动查找

    返回：
        一个字典（dict），包含配置文件中的所有数据

    示例：
        config = load_config()
        # 如果 config.yaml 内容是：
        #   api:
        #     model: "qwen-plus"
        # 那么 config 就是 {'api': {'model': 'qwen-plus'}}
    """
    # 如果没有指定路径，自动查找配置文件
    if path == 'config.yaml':
        path = _get_config_path()

    #读文件

    with open(path, 'r', encoding='utf-8') as f:
        # yaml.safe_load() 将 YAML 文件内容转换为 Python 字典
        # safe_load 是安全的加载方式，只支持标准的 YAML 标签
        return yaml.safe_load(f)


def get_client():
    """
    创建并返回一个配置好的 API 客户端

    这个函数会：
    1. 加载配置文件
    2. 从环境变量获取 API Key
    3. 使用配置创建 OpenAI 客户端

    返回：
        一个配置好的 OpenAI 客户端对象

    示例：
        client = get_client()
        # 然后就可以直接使用 client 调用 API
        completion = client.chat.completions.create(...)
    """

    # 第1步：加载配置文件
    # load_config() 会读取 config.yaml 并返回字典
    config = load_config()

    # 第2步：导入 OpenAI 类
    from openai import OpenAI

    # 第3步：创建并返回 OpenAI 客户端
    return OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 从环境变量获取 API Key
        base_url=config['api']['base_url']       # 从配置文件获取 API 地址
    )


def get_config():
    """
    获取完整的配置字典
    """
    return load_config()


def get_model_params():
    """
    获取模型参数配置
    """
    config = load_config()

    return {
        'model': config['api']['model'],
        'temperature': config['model_parameters']['temperature'],
        'top_p': config['model_parameters'].get('top_p'),
        'max_tokens': config['model_parameters'].get('max_tokens'),
    }


# 使用示例（取消注释可以运行测试）
# if __name__ == '__main__':
#     # 测试加载配置
#     config = load_config()
#     print("配置加载成功：")
#     print(f"  模型: {config['api']['model']}")
#     print(f"  温度: {config['model_parameters']['temperature']}")
#
#     # 测试获取客户端
#     client = get_client()
#     print("\n客户端创建成功！")
#     print(f"  API Key: {client.api_key[:8]}...")  # 只显示前8位
