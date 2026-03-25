import os
import re
from pathlib import Path

def fix_prompt_in_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 正则表达式说明：
    # 1. ("prompt_origin"\s*:\s*") -> 匹配键名和起始双引号
    # 2. ((?:[^"\\]|\\.)*?) -> 匹配双引号内部的值（支持转义引号 \"）
    # 3. (") -> 匹配结束双引号
    pattern = re.compile(r'("prompt_origin"\s*:\s*")((?:[^"\\]|\\.)*?)(")', re.DOTALL)

    def replacement(match):
        prefix = match.group(1) # 前缀: "prompt_origin": "
        value = match.group(2)  # 值内容
        suffix = match.group(3) # 后缀: "
        
        # 在 JSON 原始文本中，换行符通常表现为字符 '\' 和 'n'
        # 匹配连续两个或更多的 \n 字符串，替换为单个 \n
        new_value = re.sub(r'(\\n)+', r'\\n', value)
        
        return prefix + new_value + suffix

    new_content, count = pattern.subn(replacement, content)

    if count > 0 and new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main(target_directory):
    base_path = Path(target_directory)
    if not base_path.exists():
        print(f"错误: 目录 '{target_directory}' 不存在")
        return

    processed_files = 0
    modified_files = 0

    for json_file in base_path.rglob("*.json"):
        processed_files += 1
        try:
            if fix_prompt_in_text(json_file):
                print(f"已修改: {json_file}")
                modified_files += 1
        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")

    print(f"\n任务完成！")
    print(f"扫描文件总数: {processed_files}")
    print(f"实际修改文件数: {modified_files}")

if __name__ == "__main__":
    target_dir = input("请输入 JSON 目录路径 (直接回车表示当前目录): ").strip()
    if not target_dir:
        target_dir = "."
    main(target_dir)