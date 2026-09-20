#!/usr/bin/env python3
"""update_free_exploration_chapters.py

将全库 118 个自由探索章节：
1. 「总情境数: {数字}」更新为「总情境数: 自由探索章节」
2. 将「情境:」列表中的「  - 1. xxx」标号还原为无序列表「  - xxx」，去除误导 LLM 进行单步递增推大纲的序号。
"""

import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')


def process_file(fp: str) -> bool:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 替换总情境数
    new_content = re.sub(r'总情境数:\s*\d+', '总情境数: 自由探索章节', content)

    # 2. 还原情境列表中的序号
    new_content = re.sub(
        r'(\n情境:\n(?:  - \d+\. .*\n)+)',
        lambda m: re.sub(r'  - \d+\.\s*', '  - ', m.group(1)),
        new_content
    )

    if new_content != content:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    count = 0
    total = 0
    for root, _, files in os.walk(STORY_DIR):
        for f in files:
            if f.endswith('.TXT') and '自由探索' in f:
                total += 1
                fp = os.path.join(root, f)
                if process_file(fp):
                    count += 1

    print(f"处理完成: 共找到 {total} 个自由探索章节，成功更新 {count} 个。")


if __name__ == '__main__':
    main()
