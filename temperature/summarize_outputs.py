#!/usr/bin/env python3
"""
Temperature Outputs 日志总结脚本

将所有 temperature:*_outputs.log 文件的内容总结到一个 MD 文件中。
"""

import os
import re
from pathlib import Path
from datetime import datetime

def parse_output_log(log_file):
    """
    解析单个 outputs.log 文件

    Args:
        log_file: 日志文件路径

    Returns:
        list: 包含所有输出条目的列表
    """
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 按分隔线分割每个条目
        separator = "=" * 80
        entries = content.split(separator)

        parsed_entries = []
        for entry in entries:
            entry = entry.strip()
            if not entry or entry == '\n':
                continue

            # 提取信息
            entry_data = {}
            lines = entry.split('\n')

            for line in lines:
                line = line.strip()
                if line.startswith("📅 时间:"):
                    entry_data['time'] = line.split(":", 1)[1].strip()
                elif line.startswith("🌡️ Temperature:"):
                    entry_data['temperature'] = line.split(":", 1)[1].strip()
                elif line.startswith("👤 用户问题:"):
                    entry_data['question'] = line.split(":", 1)[1].strip()
                elif line.startswith("🤖 AI 回复:"):
                    # 提取回复内容（可能在后续行）
                    reply_idx = lines.index(line)
                    reply_lines = lines[reply_idx+1:]
                    entry_data['reply'] = '\n'.join(reply_lines).strip()
                    break

            if entry_data:
                parsed_entries.append(entry_data)

        return parsed_entries

    except Exception as e:
        print(f"❌ 解析文件 {log_file} 出错：{e}")
        return []

def generate_summary_markdown(log_dir="logs", output_file="TEMPERATURE_OUTPUTS_SUMMARY.md"):
    """
    生成总结 Markdown 文件

    Args:
        log_dir: 日志目录
        output_file: 输出文件路径
    """
    log_path = Path(log_dir)

    # 查找所有 outputs.log 文件
    output_files_list = sorted(log_path.glob("temperature:*_outputs.log"))

    if not output_files_list:
        print(f"❌ 在 {log_dir} 中找不到 outputs.log 文件")
        return

    print(f"📄 找到 {len(output_files_list)} 个 outputs.log 文件")

    # 收集所有数据
    all_data = {}

    for output_file_path in output_files_list:  # ✅ 重命名循环变量，避免覆盖参数
        # 提取 temperature 值
        temp_match = re.search(r'temperature:([\d.]+)_outputs\.log', output_file_path.name)
        if temp_match:
            temp = temp_match.group(1)
            entries = parse_output_log(output_file_path)
            if entries:
                all_data[temp] = entries
                print(f"  ✅ Temperature {temp}: {len(entries)} 条输出")

    if not all_data:
        print("❌ 没有解析到任何数据")
        return

    # 生成 Markdown 内容
    md_content = []
    md_content.append(f"# Temperature Outputs 日志总结\n")
    md_content.append(f"\n**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append(f"**日志目录：** {log_dir}\n")
    md_content.append(f"**包含的 Temperature：** {', '.join(sorted(all_data.keys()))}\n")
    md_content.append(f"**总输出条数：** {sum(len(v) for v in all_data.values())}\n")
    md_content.append("\n---\n\n")

    # 按 Temperature 组织内容
    sorted_temps = sorted(all_data.keys(), key=lambda x: float(x))

    for temp in sorted_temps:
        entries = all_data[temp]
        md_content.append(f"## Temperature: {temp}\n\n")
        md_content.append(f"**输出条数：** {len(entries)}\n\n")

        for idx, entry in enumerate(entries, 1):
            md_content.append(f"### 输出 {idx}/{len(entries)}\n\n")

            if 'time' in entry:
                md_content.append(f"**时间：** {entry['time']}\n\n")

            if 'question' in entry:
                # 移除运行序号标签，让问题更清晰
                question = entry['question']
                # 移除 [运行 X/Y] 标签
                question = re.sub(r'\[运行 \d+/\d+\]\s*', '', question)
                md_content.append(f"**用户问题：** {question}\n\n")

            if 'reply' in entry:
                reply = entry['reply']
                md_content.append(f"**AI 回复：**\n\n{reply}\n\n")

            md_content.append("---\n\n")

        md_content.append("\n")

    # 添加对比分析部分
    md_content.append("## 📊 Temperature 对比分析\n\n")
    md_content.append("### 快速对比\n\n")
    md_content.append("| Temperature | 输出条数 | 平均回复长度 |\n")
    md_content.append("|:-----------|:---------|:------------|\n")

    for temp in sorted_temps:
        entries = all_data[temp]
        avg_length = sum(len(e.get('reply', '')) for e in entries) / len(entries) if entries else 0
        md_content.append(f"| {temp} | {len(entries)} | {avg_length:.1f} 字符 |\n")

    md_content.append("\n### 观察要点\n\n")
    md_content.append("#### 1. 回复一致性\n")
    md_content.append("- **Temperature 0.0**: 3次运行应该基本相同（确定性高）\n")
    md_content.append("- **Temperature 0.5**: 3次运行有轻微变化\n")
    md_content.append("- **Temperature 1.0**: 3次运行应该明显不同（随机性高）\n\n")

    md_content.append("#### 2. 回复风格\n")
    md_content.append("- 对比不同 temperature 对同一问题的回答风格\n")
    md_content.append("- 观察建议的语气和详细程度\n")
    md_content.append("- 注意表达方式的差异\n\n")

    md_content.append("#### 3. 回复质量\n")
    md_content.append("- 检查信息是否完整\n")
    md_content.append("- 验证推理是否合理\n")
    md_content.append("- 评估建议的实用性\n\n")

    # 写入文件
    try:
        print(f"\n📝 准备写入总结文件...")
        print(f"   输出文件名：{output_file}")
        print(f"   当前工作目录：{os.getcwd()}")

        output_path = Path(output_file)
        print(f"   完整路径：{output_path.absolute()}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(md_content)

        file_size = output_path.stat().st_size
        print(f"\n✅ 总结文件已生成：{output_path}")
        print(f"   文件大小：{file_size} 字节")
        print(f"   相对路径：{output_path}")
    except Exception as e:
        print(f"\n❌ 写入文件失败：{e}")
        print(f"   尝试写入的路径：{output_path.absolute()}")
        print(f"   当前工作目录：{os.getcwd()}")

        # 尝试备用路径
        try:
            backup_path = Path(".") / output_file
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(md_content)
            print(f"✅ 已写入到备用路径：{backup_path}")
        except:
            print("❌ 备用路径也失败")

if __name__ == "__main__":
    import sys

    # 支持命令行参数
    log_dir = sys.argv[1] if len(sys.argv) > 1 else "logs"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "TEMPERATURE_OUTPUTS_SUMMARY.md"

    print("=" * 70)
    print("📊 Temperature Outputs 日志总结")
    print("=" * 70)
    print()
    print(f"日志目录：{log_dir}")
    print(f"输出文件：{output_file}")
    print()

    generate_summary_markdown(log_dir, output_file)

    print()
    print("=" * 70)
    print("🎉 总结完成！")
    print("=" * 70)
    print()
    print(f"📄 查看总结文件：")
    print(f"   cat {output_file}")
    print()
