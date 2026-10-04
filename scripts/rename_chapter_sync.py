#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rename_chapter_sync.py — 章节标题原子化同步重命名工具

功能：
  1. 重命名磁盘上的 .TXT 文件：`{ID}：{新名称}.TXT`
  2. 同步更新文件内部头部：`名称: {新名称}`
  3. 同步重写 docs/story/_sex_index.txt 对应条目
  4. 同步更新 docs/story/_连续叙事弧线章节总览.md 中的引用（阶段首尾章、弧列表等）
  5. 自动调用 scripts/check_consistency.py 执行全库一致性强校验

用法：
  python scripts/rename_chapter_sync.py --id 013 --title "菲娜的小习惯——日常中的发现"
  python scripts/rename_chapter_sync.py --batch-file batch_titles.json
"""

import os
import sys
import glob
import re
import json
import argparse
import subprocess

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')
SEX_INDEX = os.path.join(STORY_DIR, '_sex_index.txt')
ARC_FILE = os.path.join(STORY_DIR, '_连续叙事弧线章节总览.md')


def find_chapter_file(cid_str):
    """查找对应章节的物理文件路径"""
    # 尝试匹配原样、去除前导0、或浮点数
    patterns = [
        os.path.join(STORY_DIR, '*', f'{cid_str}：*.TXT'),
    ]
    if cid_str.isdigit():
        int_id = str(int(cid_str))
        patterns.append(os.path.join(STORY_DIR, '*', f'{int_id}：*.TXT'))
        z_id = f'{int(cid_str):03d}'
        patterns.append(os.path.join(STORY_DIR, '*', f'{z_id}：*.TXT'))

    for p in patterns:
        matched = glob.glob(p)
        if matched:
            return matched[0]
    return None


def sync_rename(cid_str, new_title, dry_run=False):
    """执行单个章节的原子化同步更新"""
    if '——' not in new_title:
        raise ValueError(f"新标题必须包含双破折号 '——' : {new_title}")

    old_path = find_chapter_file(cid_str)
    if not old_path:
        raise FileNotFoundError(f"找不到章节 ID={cid_str} 对应的 TXT 文件")

    dir_name = os.path.dirname(old_path)
    old_fname = os.path.basename(old_path)
    
    # 解析旧 ID 与旧名称
    prefix_id = old_fname.split('：')[0]
    with open(old_path, 'r', encoding='utf-8') as f:
        content = f.read()

    m_name = re.search(r'^名称:\s*(.+)', content, re.M)
    if not m_name:
        raise ValueError(f"{old_path} 内部未找到 '名称:' 字段")
    old_title = m_name.group(1).strip()

    new_fname = f"{prefix_id}：{new_title}.TXT"
    new_path = os.path.join(dir_name, new_fname)

    print(f"[*] 准备更新 Ch{cid_str}:")
    print(f"    旧文件: {old_fname}")
    print(f"    新文件: {new_fname}")
    print(f"    旧标题: {old_title}")
    print(f"    新标题: {new_title}")

    if dry_run:
        print("    [Dry-run] 模拟完成，不修改物理文件。")
        return True

    # 1. 更新文件内文本
    new_content = re.sub(r'^名称:\s*.+', f'名称: {new_title}', content, count=1, flags=re.M)
    with open(old_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # 2. 重命名磁盘文件
    if old_path != new_path:
        os.rename(old_path, new_path)

    # 3. 同步 _sex_index.txt
    if os.path.exists(SEX_INDEX):
        with open(SEX_INDEX, 'r', encoding='utf-8') as f:
            sex_lines = f.readlines()
        
        updated_sex = False
        new_sex_lines = []
        for line in sex_lines:
            # 匹配行: e.g. "66: 温泉的清晨——晨光里的她"
            m = re.match(r'^([\d.]+):\s*(.+)', line)
            if m:
                line_id = m.group(1)
                same_id = (float(line_id) == float(cid_str)) if ('.' in line_id or '.' in cid_str) else (int(line_id) == int(cid_str))
                if same_id:
                    new_sex_lines.append(f"{line_id}: {new_title}\n")
                    updated_sex = True
                    continue
            new_sex_lines.append(line)
        
        if updated_sex:
            with open(SEX_INDEX, 'w', encoding='utf-8') as f:
                f.writelines(new_sex_lines)
            print(f"    ✓ 已同步更新 _sex_index.txt")

    # 4. 同步 _连续叙事弧线章节总览.md
    if os.path.exists(ARC_FILE):
        with open(ARC_FILE, 'r', encoding='utf-8') as f:
            arc_txt = f.read()
        
        # 4a. 阶段首尾章: "| 0：序章 | 1 ... | 70 深夜的噩梦——门那边的她 | 70 |"
        # 4b. 弧引用: "**70** 深夜的噩梦——门那边的她"
        norm_cid = str(int(cid_str)) if cid_str.isdigit() else cid_str
        
        # 替换弧总览中的特定引用
        # 1) 首尾章表格: "| 0：序章 | ... | 70 {old_title} |"
        p_table = rf'(\|\s*{norm_cid}\s+){re.escape(old_title)}(\s*\|)'
        arc_txt, count_t = re.subn(p_table, rf'\g<1>{new_title}\g<2>', arc_txt)
        
        # 2) 弧详情条目: "**70** {old_title}"
        p_arc = rf'(\*\*{norm_cid}\*\*\s*){re.escape(old_title)}'
        arc_txt, count_a = re.subn(p_arc, rf'\g<1>{new_title}', arc_txt)

        # 3) 拆分表: "Ch70（上）{old_title}"
        p_split = rf'(Ch{norm_cid}（[上中下]）\s*){re.escape(old_title)}'
        arc_txt, count_s = re.subn(p_split, rf'\g<1>{new_title}', arc_txt)

        # 4) 拆分表右侧链条: "→ {old_title}"
        p_chain = rf'(→\s*){re.escape(old_title)}'
        arc_txt, count_c = re.subn(p_chain, rf'\g<1>{new_title}', arc_txt)

        with open(ARC_FILE, 'w', encoding='utf-8') as f:
            f.write(arc_txt)
        if count_t + count_a + count_s + count_c > 0:
            print(f"    ✓ 已同步更新 _连续叙事弧线章节总览.md ({count_t + count_a + count_s + count_c} 处)")

    return True


def run_consistency_check():
    """运行 check_consistency.py 校验"""
    print("\n" + "=" * 60)
    print("  正在执行全库一致性校验...")
    print("=" * 60)
    res = subprocess.run([sys.executable, os.path.join(PROJECT_DIR, 'scripts', 'check_consistency.py')],
                         capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        raise RuntimeError("全库一致性校验失败，请检查报错项！")
    print("  ✅ 全库一致性校验 100% 通过！\n")


def main():
    parser = argparse.ArgumentParser(description="原子化同步重命名章节标题")
    parser.add_argument('--id', type=str, help="章节编号，例如 013")
    parser.add_argument('--title', type=str, help="新标题，例如 菲娜的小习惯——日常中的发现")
    parser.add_argument('--batch-file', type=str, help="批量重命名 JSON 文件路径")
    parser.add_argument('--dry-run', action='store_true', help="模拟运行，不实际修改")
    args = parser.parse_args()

    if args.id and args.title:
        sync_rename(args.id, args.title, dry_run=args.dry_run)
        if not args.dry_run:
            run_consistency_check()
    elif args.batch_file:
        with open(args.batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
        for item in batch_data:
            sync_rename(str(item['id']), item['title'], dry_run=args.dry_run)
        if not args.dry_run:
            run_consistency_check()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
