# 测试日志系统
# 验证 AgentLogger 的各个功能

import os
import sys
import json
from pathlib import Path

# 确保可以导入 chat_with_tool_thinking.py 中的 AgentLogger
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logger():
    """测试 AgentLogger 的基本功能"""

    print("=" * 60)
    print("🧪 测试日志系统")
    print("=" * 60)

    # 导入 AgentLogger
    try:
        # 需要从 chat_with_tool_thinking.py 中导入 AgentLogger
        # 为了测试，我们在这里创建一个简化版本
        import logging
        import logging.handlers
        from datetime import datetime
        from pathlib import Path

        class TestAgentLogger:
            """测试用的简化版 AgentLogger"""

            def __init__(self, log_dir="test_logs", agent_name="test_agent"):
                self.agent_name = agent_name
                self.log_dir = Path(log_dir)
                self.current_date = datetime.now().strftime('%Y%m%d')

                # 创建日志目录
                self.log_dir.mkdir(exist_ok=True)

                # 配置日志记录器
                self.logger = self._setup_logger()
                self.json_logger = self._setup_json_logger()

            def _setup_logger(self):
                """配置标准日志记录器"""
                logger = logging.getLogger(f"{self.agent_name}.logger")
                logger.setLevel(logging.DEBUG)
                logger.handlers.clear()

                log_file = self.log_dir / f"{self.agent_name}_{self.current_date}.log"
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)

                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)

                detailed_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

                file_handler.setFormatter(detailed_formatter)
                console_handler.setFormatter(simple_formatter)

                logger.addHandler(file_handler)
                logger.addHandler(console_handler)

                return logger

            def _setup_json_logger(self):
                """配置JSON专用日志记录器"""
                json_logger = logging.getLogger(f"{self.agent_name}.json")
                json_logger.setLevel(logging.DEBUG)
                json_logger.handlers.clear()

                json_log_file = self.log_dir / f"{self.agent_name}_json_{self.current_date}.jsonl"
                json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
                json_handler.setLevel(logging.DEBUG)
                json_handler.setFormatter(logging.Formatter('%(message)s'))

                json_logger.addHandler(json_handler)
                return json_logger

            def log_request(self, request_data):
                """记录API请求"""
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "request",
                    "agent": self.agent_name,
                    "data": request_data
                }

                self.logger.info(f"📡 API请求: {json.dumps(request_data, ensure_ascii=False)}")
                self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))

            def log_response(self, response_data):
                """记录API响应"""
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "response",
                    "agent": self.agent_name,
                    "data": response_data
                }

                self.logger.info(f"📤 API响应: {json.dumps(response_data, ensure_ascii=False)}")
                self.json_logger.info(json.dumps(log_entry, ensure_ascii=False))

            def log_error(self, error_info):
                """记录错误信息"""
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                    "agent": self.agent_name,
                    "data": error_info
                }

                self.logger.error(f"❌ 错误: {json.dumps(error_info, ensure_ascii=False)}")
                self.json_logger.error(json.dumps(log_entry, ensure_ascii=False))

        logger = TestAgentLogger(log_dir="test_logs", agent_name="test_agent")

        print("\n✅ 日志记录器创建成功")
        print(f"📁 日志目录: {logger.log_dir}")

        # 测试各种日志记录
        print("\n📝 测试日志记录...")

        # 1. 记录请求
        logger.log_request({
            "question": "南京今天的天气怎么样？",
            "model": "qwen-max",
            "thinking_mode": True
        })
        print("  ✅ 请求日志已记录")

        # 2. 记录响应
        logger.log_response({
            "status_code": 200,
            "latency_ms": 1234.5,
            "usage": {
                "input_tokens": 150,
                "output_tokens": 80,
                "total_tokens": 230
            }
        })
        print("  ✅ 响应日志已记录")

        # 3. 记录错误
        logger.log_error({
            "error_type": "TestError",
            "error_message": "这是一个测试错误"
        })
        print("  ✅ 错误日志已记录")

        # 检查日志文件
        print("\n📂 生成的日志文件:")
        log_files = list(logger.log_dir.glob("*.log")) + list(logger.log_dir.glob("*.jsonl"))

        if log_files:
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"  📄 {log_file.name} ({size} bytes)")
        else:
            print("  ⚠️  未找到日志文件")

        # 读取并显示 JSONL 日志示例
        jsonl_file = logger.log_dir / f"{logger.agent_name}_json_{logger.current_date}.jsonl"
        if jsonl_file.exists():
            print("\n📖 JSONL 日志示例:")
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i < 2:  # 只显示前2行
                        log_entry = json.loads(line)
                        print(f"  {json.dumps(log_entry, ensure_ascii=False, indent=2)}")
                    else:
                        break

        print("\n" + "=" * 60)
        print("✅ 日志系统测试完成！")
        print("=" * 60)
        print(f"\n💡 提示：查看完整日志文件: {logger.log_dir}")
        print("   - 标准日志: test_agent_YYYYMMDD.log")
        print("   - JSON日志: test_agent_json_YYYYMMDD.jsonl")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logger()
