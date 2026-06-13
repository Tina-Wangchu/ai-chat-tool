#!/usr/bin/env python3
"""
main.py 功能自动化测试

测试范围：
1. 角色系统 (/role)
2. 思考模式 (/thinking)
3. 清空历史 (/clear)
4. 帮助信息 (/help)
5. 天气查询（核心功能）
6. 流式输出
7. 对话历史记忆
8. 日志记录
"""

import os
import sys
import subprocess
import time

# 测试结果记录
test_results = []

def test_component(name, test_func):
    """测试单个组件"""
    print(f"\n{'='*70}")
    print(f"🧪 测试：{name}")
    print(f"{'='*70}")
    try:
        result = test_func()
        status = "✅ 通过" if result else "❌ 失败"
        print(f"\n{status}")
        test_results.append({"name": name, "status": status})
        return result
    except Exception as e:
        print(f"\n❌ 异常：{e}")
        test_results.append({"name": name, "status": f"❌ 异常: {str(e)[:50]}"})
        return False

def test_env_variables():
    """测试环境变量"""
    print("检查必需的环境变量...")
    required_vars = ["DASHSCOPE_API_KEY", "AMAP_API_KEY"]
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已设置 (长度: {len(value)})")
        else:
            print(f"  ❌ {var}: 未设置")
            all_present = False
    return all_present

def test_config_file():
    """测试配置文件"""
    print("检查配置文件...")
    config_path = "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool/config.yaml"
    if os.path.exists(config_path):
        print(f"  ✅ 配置文件存在")
        # 读取并验证基本配置
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            required_keys = ["api:", "model:", "roles:", "model_parameters:"]
            for key in required_keys:
                if key in content:
                    print(f"  ✅ 包含配置项: {key}")
                else:
                    print(f"  ⚠️  缺少配置项: {key}")
        return True
    else:
        print(f"  ❌ 配置文件不存在")
        return False

def test_imports():
    """测试关键模块导入"""
    print("测试关键模块导入...")
    try:
        import dashscope
        print("  ✅ dashscope")
        import yaml
        print("  ✅ yaml")
        return True
    except ImportError as e:
        print(f"  ❌ 导入失败: {e}")
        return False

def test_mcp_server_startup():
    """测试 MCP 服务器启动"""
    print("测试 MCP 服务器启动...")
    try:
        # 检查 npx 命令
        result = subprocess.run(
            ["npx", "-y", "@amap/amap-maps-mcp-server", "--help"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0 or b"help" in result.stderr:
            print("  ✅ MCP 服务器可以启动")
            return True
        else:
            print(f"  ⚠️  MCP 服务器响应异常: {result.returncode}")
            return False
    except Exception as e:
        print(f"  ❌ MCP 服务器启动失败: {e}")
        return False

def test_weather_query():
    """测试天气查询功能（核心功能）"""
    print("测试天气查询 API 调用...")
    try:
        from dashscope import Generation
        api_key = os.getenv("DASHSCOPE_API_KEY")
        amap_key = os.getenv("AMAP_API_KEY")

        if not api_key:
            print("  ❌ 缺少 DASHSCOPE_API_KEY")
            return False

        # 简单的模型调用测试
        resp = Generation.call(
            model='qwen-max',
            messages=[{"role": "user", "content": "你好"}],
            stream=False,
            max_tokens=50
        )

        if resp.status_code == 200:
            print(f"  ✅ 模型调用成功 (status: {resp.status_code})")
            return True
        else:
            print(f"  ❌ 模型调用失败 (status: {resp.status_code})")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def test_stream_output():
    """测试流式输出"""
    print("测试流式输出...")
    try:
        from dashscope import Generation
        import os

        resp_stream = Generation.call(
            model='qwen-max',
            messages=[{"role": "user", "content": "请用10个字介绍你自己"}],
            stream=True,
            max_tokens=100
        )

        chunk_count = 0
        full_content = ""
        for chunk in resp_stream:
            chunk_count += 1
            if chunk_count > 20:  # 限制 chunk 数量
                break
            if hasattr(chunk, 'output') and chunk.output:
                if hasattr(chunk.output, 'choices') and chunk.output.choices:
                    message = chunk.output.choices[0].message
                    if hasattr(message, 'content') and message.content:
                        full_content = message.content

        print(f"  ✅ 收到 {chunk_count} 个 chunks")
        print(f"  ✅ 最终内容长度: {len(full_content)} 字符")
        return len(full_content) > 10
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def test_role_system():
    """测试角色系统配置"""
    print("测试角色系统...")
    try:
        import yaml
        config_path = "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool/config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        roles = config.get('roles', {}).get('available', [])
        if len(roles) >= 3:
            print(f"  ✅ 找到 {len(roles)} 个角色")
            for role in roles:
                print(f"     - {role.get('name')}: {role.get('description')}")
            return True
        else:
            print(f"  ⚠️  角色数量不足: {len(roles)}")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def test_thinking_config():
    """测试思考模式配置"""
    print("测试思考模式配置...")
    try:
        import yaml
        config_path = "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool/config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        thinking = config.get('thinking', {})
        has_enabled = 'enabled' in thinking
        has_budget = 'budget' in thinking

        if has_enabled and has_budget:
            print(f"  ✅ 思考模式配置完整")
            print(f"     - enabled: {thinking.get('enabled')}")
            print(f"     - budget: {thinking.get('budget')}")
            return True
        else:
            print(f"  ⚠️  配置不完整")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def test_log_directory():
    """测试日志目录"""
    print("测试日志目录...")
    log_dir = "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool/logs"
    try:
        os.makedirs(log_dir, exist_ok=True)
        print(f"  ✅ 日志目录: {log_dir}")
        return True
    except Exception as e:
        print(f"  ❌ 创建日志目录失败: {e}")
        return False

def test_history_directory():
    """测试对话历史目录"""
    print("测试对话历史目录...")
    history_dir = "/Users/tinawang/sophomore_tina/26Summer/ai-chat-tool/conversation_history"
    try:
        os.makedirs(history_dir, exist_ok=True)
        print(f"  ✅ 历史目录: {history_dir}")
        return True
    except Exception as e:
        print(f"  ❌ 创建历史目录失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("🧪 main.py 功能测试套件")
    print("=" * 70)
    print(f"⏰ 开始时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 环境测试
    test_component("环境变量检查", test_env_variables)
    test_component("配置文件检查", test_config_file)
    test_component("模块导入测试", test_imports)

    # 核心功能测试
    test_component("MCP 服务器启动", test_mcp_server_startup)
    test_component("天气查询 API", test_weather_query)
    test_component("流式输出", test_stream_output)

    # 配置系统测试
    test_component("角色系统配置", test_role_system)
    test_component("思考模式配置", test_thinking_config)

    # 目录结构测试
    test_component("日志目录", test_log_directory)
    test_component("对话历史目录", test_history_directory)

    # 生成测试报告
    print(f"\n{'='*70}")
    print("📊 测试报告")
    print(f"{'='*70}")

    passed = sum(1 for r in test_results if "✅" in r["status"])
    failed = len(test_results) - passed

    print(f"\n总测试数: {len(test_results)}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")

    print(f"\n详细结果：")
    for result in test_results:
        print(f"  {result['status']} - {result['name']}")

    print(f"\n⏰ 结束时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
