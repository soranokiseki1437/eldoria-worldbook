#!/usr/bin/env python3
"""
扫描所有章节TXT内部字段中的阿拉伯数字。
排除: ID / 性行为等级 / 好感影响 / 章节终止条件的结构编号(1. 2. 3.)
排除: 黎恩知情 / 占有欲确认 (纯metadata好感数值)
输出到根目录 arabic_numerals_report.txt
"""

import os
import re

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "story")
OUTPUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "arabic_numerals_report.txt")

# 完全排除的字段
EXCLUDED_FIELDS = {"ID", "性行为等级", "好感影响", "黎恩知情", "占有欲确认"}

# 章节终止条件的行首编号 (如 "1." "2.")
TERM_NUM_RE = re.compile(r'^(\d+)\.\s*')

def find_chapters():
    chapters = []
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if f.endswith(".TXT") and not f.startswith("_"):
                chapters.append(os.path.join(root, f))
    return sorted(chapters)

def scan_file(filepath):
    """返回 [(章节名, 行号, 字段名, 数字, 所在句段), ...]"""
    results = []
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    current_field = None
    in_termination = False

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        # === 字段名检测：行首无 "-" 前缀，有冒号 ===
        # 字段名行特征：不以 "-" 或数字开头，包含 ":"
        is_field_line = False
        if not stripped.startswith("-") and not re.match(r'^\d', stripped):
            m = re.match(r'^([^:]+):\s*(.*)', stripped)
            if m:
                field_name = m.group(1).strip()
                # 排除已知的非字段模式（如纯数字后跟冒号）
                if field_name and not re.match(r'^\d+$', field_name):
                    is_field_line = True

        if is_field_line:
            m = re.match(r'^([^:]+):\s*(.*)', stripped)
            field_name = m.group(1).strip()
            rest = m.group(2).strip()

            if field_name in EXCLUDED_FIELDS:
                current_field = None
                in_termination = False
                continue

            current_field = field_name
            in_termination = (field_name == "章节终止条件")

            # 检查同行值中的数字
            if rest:
                if in_termination:
                    m2 = TERM_NUM_RE.match(rest)
                    if m2:
                        rest = rest[m2.end():].strip()
                for n in re.findall(r'\d+', rest):
                    results.append((filename, lineno, field_name, n, stripped[:250]))
            continue

        # === 非字段名行：必须是某字段的内容 ===
        if current_field is None or current_field in EXCLUDED_FIELDS:
            continue

        # 提取纯内容
        content = stripped
        if content.startswith("- "):
            content = content[2:]
        elif content.startswith("-"):
            content = content[1:]

        # 章节终止条件中排除编号
        if in_termination:
            m = TERM_NUM_RE.match(content)
            if m:
                content = content[m.end():].strip()

        for n in re.findall(r'\d+', content):
            results.append((filename, lineno, current_field, n, stripped[:250]))

    return results

def main():
    chapters = find_chapters()
    print(f"扫描 {len(chapters)} 个章节文件...")

    all_results = []
    for i, ch in enumerate(chapters):
        if i % 50 == 0:
            print(f"  进度: {i}/{len(chapters)} — {os.path.basename(ch)}")
        all_results.extend(scan_file(ch))

    print(f"\n共发现 {len(all_results)} 处阿拉伯数字")

    by_chapter = {}
    for r in all_results:
        by_chapter.setdefault(r[0], []).append(r)

    with open(OUTPUT, "w", encoding="utf-8") as out:
        out.write("=" * 80 + "\n")
        out.write("章节阿拉伯数字扫描报告\n")
        out.write("排除: ID / 性行为等级 / 好感影响 / 黎恩知情 / 占有欲确认\n")
        out.write("排除: 章节终止条件的结构编号(1. 2. 3.)\n")
        out.write(f"共 {len(all_results)} 处\n")
        out.write("=" * 80 + "\n\n")
        out.write("格式: 行号 [字段名] 数字 «所在句段»\n")
        out.write("-" * 80 + "\n\n")

        for fn in sorted(by_chapter.keys()):
            entries = by_chapter[fn]
            out.write(f"\n{'─' * 70}\n")
            out.write(f"【{fn}】共 {len(entries)} 处\n")
            out.write(f"{'─' * 70}\n")
            for (_, lineno, field, num, text) in entries:
                out.write(f"  L{lineno:04d} [{field}] {num} «{text}»\n")

    print(f"报告已输出到: {OUTPUT}")

    by_field = {}
    for r in all_results:
        f = r[2]
        by_field[f] = by_field.get(f, 0) + 1
    print("按字段分布:")
    for f, c in sorted(by_field.items(), key=lambda x: -x[1]):
        print(f"  {f}: {c}")

if __name__ == "__main__":
    main()
