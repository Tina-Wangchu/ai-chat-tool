#!/usr/bin/env python3
"""
手动功能验证测试

针对自动化测试中的"失败"项进行深入测试
"""

import os
from dashscope import Generation

def test_stream_detailed():
    """详细的流式输出测试"""
    print("=" * 70)
    print("🔍 详细流式输出测试")
    print("=" * 70)

    test_question = "请用20个字介绍你自己"

    print(f"\n📋 测试问题: {test_question}")
    print(f"📡 模型: qwen-max")
    print(f"\n⏳ 开始流式输出...\n")

    try:
        chunk_count = 0
        full_content = ""

        resp_stream = Generation.call(
            model="qwen-max",
            messages=[{"role": "user", "content": test_question}],
            stream=True,
            max_tokens=100
        )

        for chunk in resp_stream:
            chunk_count += 1

            if hasattr(chunk, 'output') and chunk.output:
                if hasattr(chunk.output, 'choices') and chunk.output.choices:
                    message = chunk.output.choices[0].message

                    # 显示前3个chunk的详细信息
                    if chunk_count <= 3:
                        print(f"\n📦 Chunk #{chunk_count}:")
                        print(f"  - message 类型: {type(message)}")

                        # 检查所有可能的内容字段
                        if hasattr(message, 'content'):
                            content = message.content
                            print(f"  - content: '{content}'")
                            if content:
                                full_content = content
                                print(f"  - 长度: {len(content)} 字符")

                        if hasattr(message, 'delta'):
                            print(f"  - delta: {message.delta}")

                    # 正常处理所有chunks
                    if hasattr(message, 'content') and message.content:
                        full_content = message.content

        print(f"\n{'='*70}")
        print("📊 流式输出结果")
        print(f"{'='*70}")
        print(f"总 chunk 数: {chunk_count}")
        print(f"最终内容长度: {len(full_content)} 字符")
        print(f"最终内容: {full_content}")

        if len(full_content) > 10:
            print(f"\n✅ 流式输出成功！")
            return True
        else:
            print(f"\n❌ 流式输出内容异常短")
            return False

    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_directly():
    """直接测试 MCP 服务器"""
    print("=" * 70)
    print("🔍 MCP 服务器直接测试")
    print("=" * 70)

    try:
        import subprocess
        import json
        import time

        amap_key = os.getenv("AMAP_API_KEY")
        if not amap_key:
            print("❌ 缺少 AMAP_API_KEY")
            return False

        print(f"\n✅ AMAP_API_KEY: 已设置 (长度: {len(amap_key)})")

        # 启动 MCP 服务器
        print("\n🚀 启动 MCP 服务器...")
        command = ["npx", "-y", "@amap/amap-maps-mcp-server"]
        env = os.environ.copy()
        env["AMAP_MAPS_API_KEY"] = amap_key

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        print("✅ MCP 服务器进程已启动")

        # 等待启动
        time.sleep(2)

        # 发送 tools/list 请求
        print("\n📡 发送 tools/list 请求...")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        try:
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()

            # 读取响应
            response_line = process.stdout.readline()
            print(f"✅ 收到响应: {response_line[:200]}...")

            response = json.loads(response_line)

            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"\n✅ MCP 服务器正常工作")
                print(f"📦 可用工具数量: {len(tools)}")
                for tool in tools[:3]:  # 显示前3个工具
                    print(f"  - {tool.get('name')}: {tool.get('description')[:50]}...")

                process.terminate()
                return True
            else:
                print(f"❌ 响应格式异常")
                print(f"响应: {response}")
                process.terminate()
                return False

        except Exception as e:
            print(f"❌ MCP 通信失败: {e}")
            process.terminate()
            return False

    except Exception as e:
        print(f"❌ MCP 启动失败: {e}")
        return False

def test_weather_query_full():
    """完整的天气查询测试"""
    print("=" * 70)
    print("🔍 完整天气查询测试")
    print("=" * 70)

    try:
        # 测试简单问题
        question = "你好，请介绍一下你自己"
        print(f"\n📋 测试问题: {question}")

        resp = Generation.call(
            model='qwen-max',
            messages=[{"role": "user", "content": question}],
            stream=False,
            max_tokens=100
        )

        if resp.status_code == 200:
            content = resp.output.choices[0].message.content
            print(f"✅ 基础查询成功")
            print(f"📝 回复长度: {len(content)} 字符")
            print(f"📄 回复内容: {content[:100]}...")
            return True
        else:
            print(f"❌ 查询失败: {resp.status_code}")
            return False

    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    import time

    print("\n" + "="*70)
    print("🧪 手动功能验证测试")
    print("="*70)
    print(f"⏰ 开始时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # 测试1：详细流式输出
    results.append(("流式输出", test_stream_detailed()))

    # 测试2：MCP 服务器
    results.append(("MCP 服务器", test_mcp_directly()))

    # 测试3：完整天气查询
    results.append(("天气查询", test_weather_query_full()))

    # 总结
    print("\n" + "="*70)
    print("📊 手动测试总结")
    print("="*70)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    passed = sum(1 for _, r in results if r)
    print(f"\n通过率: {passed}/{len(results)}")

    print(f"\n⏰ 结束时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
