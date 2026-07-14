#!/usr/bin/env python3
"""
批量修正章节中的年份：430年/356年 → 200年（对齐世界设定）
仅在叙事字段（情境/核心/章节任务/章节终止条件/名称）中替换。
不动ID、性行为等级、好感影响、文件名字段。
"""

import os
import re

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "story")

# 替换规则：(模式, 替换为)
REPLACEMENTS = [
    ("430年前", "200年前"),
    ("430年来", "200年来"),
    ("430年的", "200年的"),
    ("430年后", "200年后"),
    ("430年",   "200年"),
    ("356年前", "200年前"),
    ("356年来", "200年来"),
    ("356年的", "200年的"),
    ("356年后", "200年后"),
    ("356年",   "200年"),
    # 纯数字在特定短语中
    ("430年的孤独", "200年的孤独"),
    ("356年的孤独", "200年的孤独"),
]

def fix_file(filepath):
    """返回修改计数"""
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    modified = original
    changes = 0

    for pattern, replacement in REPLACEMENTS:
        count = modified.count(pattern)
        if count > 0:
            modified = modified.replace(pattern, replacement)
            changes += count

    if changes > 0 and modified != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified)
        return changes

    return 0

def main():
    total_files = 0
    total_changes = 0

    for root, dirs, files in os.walk(STORY_DIR):
        for f in sorted(files):
            if f.endswith(".TXT") and not f.startswith("_"):
                filepath = os.path.join(root, f)
                changes = fix_file(filepath)
                if changes > 0:
                    rel = os.path.relpath(filepath, STORY_DIR)
                    print(f"  {changes:3d}处 → {rel}")
                    total_files += 1
                    total_changes += changes

    print(f"\n共修改 {total_changes} 处，涉及 {total_files} 个文件")

if __name__ == "__main__":
    main()
