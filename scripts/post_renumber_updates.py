#!/usr/bin/env python3
"""
post_renumber_updates.py — 重编号后更新弧线总览和sex索引 (V2.0)

V2.0 修复（2026-08-04）:
  - 拆分弧线表已存在时改为替换，不再重复插入第二张表
  - （上/中/下）标签从文件系统文件名推导，不再按小数位猜（615.5 是"上"而非"下"）
  - 支持"上"分部来自小数（如 615.5→644 暮色里的通讯），自动生成缺失的拆分弧行
  - sex索引分部条目用文件系统权威标题生成
"""

import os, re, sys
from collections import defaultdict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY_RUN_FILE = os.path.join(PROJECT_DIR, 'scripts', '_renumber_mapping.txt')
ARC_FILE = os.path.join(PROJECT_DIR, 'docs', 'story', '_连续叙事弧线章节总览.md')
SEX_INDEX_FILE = os.path.join(PROJECT_DIR, 'docs', 'story', '_sex_index.txt')
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')


def parse_dry_run(filepath):
    """Parse dry-run output. Extracts old ID from FILENAME at end of each line.

    Format: "    207 (小数插入) → 208  [3：渐进接触] 207.5：title.TXT"
    The actual old ID is in the filename: "207.5" or "208".
    """
    old_to_new = {}
    split_old = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(
                r'\s+[\d.]+\s*(?:\(小数插入\))?\s*→\s*(\d+)\s+\[[^\]]+\]\s*([\d.]+)：',
                line
            )
            if not m:
                continue
            new_id = int(m.group(1))
            old_str = m.group(2)
            old_to_new[old_str] = new_id

            if '.' in old_str:
                parts = old_str.split('.')
                base = int(parts[0])
                dec = parts[1]
                split_old[base].append((dec, new_id))

    # Identity mappings for Ch1-206 (unchanged, not in dry-run)
    for i in range(1, 207):
        s = str(i)
        if s not in old_to_new:
            old_to_new[s] = i

    return old_to_new, split_old


def build_simple_old_to_new(old_to_new):
    """int→int mapping for ALL integer old IDs (including unchanged ones)."""
    simple = {}
    for old_str, new_id in old_to_new.items():
        if '.' not in old_str:
            simple[int(old_str)] = new_id
    # Add identity for unchanged IDs (not in dry-run)
    max_old = max(simple.keys()) if simple else 799
    for i in range(1, max_old + 1):
        if i not in simple:
            simple[i] = i
    return simple


def replace_chapter_numbers(text, simple_map):
    """Replace old chapter numbers with new numbers.
    Sorts by old_id descending to avoid partial matches (e.g., 20 vs 200).
    """
    for old_id in sorted(simple_map.keys(), reverse=True):
        new_id = simple_map[old_id]
        text = re.sub(rf'(?<!\d){old_id}(?![\d.])', str(new_id), text)
    return text


def fs_title(nid):
    """按编号查找章节文件，返回标题（含（上/中/下）后缀），未找到返回''"""
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            for prefix in [f'{nid:03d}：', f'{nid}：']:
                if f.startswith(prefix):
                    return f.split('：', 1)[1].replace('.TXT', '')
    return ''


def fs_suffix(nid):
    """返回该章节标题中的（上/中/下）后缀，无则返回''"""
    t = fs_title(nid)
    if not t:
        return ''
    m = re.search(r'（(上|中|下)）', t)
    return m.group(1) if m else ''


def build_split_info(simple_map, split_old):
    """构建拆分章节信息: {base: [(nid, 标签), ...]}，标签取自文件系统。

    - base 分部文件带（上）→ 拆分 = base + 小数分部（如 616 暴雨古树 → 647/648）
    - base 无后缀但首个小数分部带（上）→ 拆分的"上"来自小数（如 615.5→644 暮色里的通讯）
    - 否则视为无关章节，跳过
    """
    split_info = {}
    for base, parts in sorted(split_old.items()):
        parts_sorted = sorted(parts, key=lambda x: x[0])
        base_new = simple_map.get(base, base)
        part_ids = [nid for _, nid in parts_sorted]
        base_sfx = fs_suffix(base_new)
        if base_sfx == '上':
            seq = [(base_new, base_sfx)] + [(nid, fs_suffix(nid)) for nid in part_ids]
        elif part_ids and fs_suffix(part_ids[0]) == '上':
            seq = [(nid, fs_suffix(nid)) for nid in part_ids]
        else:
            continue
        seq = [s for s in seq if s[1]]
        if len(seq) >= 2:
            split_info[base] = seq
    return split_info


def update_arc_document(simple_map, split_old, old_to_new):
    """Update _连续叙事弧线章节总览.md"""
    print('\n=== 更新连续叙事弧线总览 ===')

    with open(ARC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = replace_chapter_numbers(content, simple_map)

    # Count changes
    old_nums = re.findall(r'\b\d+\b', content)
    new_nums = re.findall(r'\b\d+\b', new_content)
    changes = sum(1 for o, n in zip(old_nums, new_nums) if o != n)
    print(f'  {changes} 处编号已替换')

    split_info = build_split_info(simple_map, split_old)

    # Generate arc entries for split chapters
    new_arcs = []
    for base, seq in sorted(split_info.items()):
        new_ids = [nid for nid, _ in seq]
        labels = [lbl for _, lbl in seq]
        titles = [fs_title(nid) for nid in new_ids]
        ch_refs = ' · '.join(f'Ch{nid}（{lbl}）' for nid, lbl in seq)
        title_line = ' → '.join(titles)
        new_arcs.append(f'| {base} | {ch_refs} | {title_line} | 拆分形成连续弧（{len(new_ids)}章） |')

    # Insert or REPLACE the split-arc table (V2.0: 已存在则替换，不再重复插入)
    if new_arcs:
        arc_header = '### 拆分新增弧线（V10.28 章节拆分）\n\n'
        arc_text = (arc_header + '| 原章 | 新编号 | 标题链 | 说明 |\n'
                    + '|:--|:--|:--|:--|\n' + '\n'.join(new_arcs) + '\n')

        if '拆分新增弧线' in new_content:
            start = new_content.index('### 拆分新增弧线')
            end = new_content.find('\n---\n', start)
            if end == -1:
                new_content = new_content[:start] + arc_text + '\n'
            else:
                new_content = new_content[:start] + arc_text + '\n---\n' + new_content[end + len('\n---\n'):]
            print(f'  替换已有拆分弧线表: {len(new_arcs)} 条')
        else:
            last_sep = new_content.rfind('\n---\n')
            if last_sep > 0:
                new_content = new_content[:last_sep] + '\n' + arc_text + new_content[last_sep:]
            else:
                new_content += '\n' + arc_text
            print(f'  新增 {len(new_arcs)} 条拆分弧线已写入文档')

    with open(ARC_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  弧线文档已更新')
    return split_info


def update_sex_index(simple_map, split_old, old_to_new, split_info):
    """Update _sex_index.txt"""
    print('\n=== 更新sex索引 ===')

    with open(SEX_INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = replace_chapter_numbers(content, simple_map)

    changed_lines = sum(1 for ol, nl in zip(content.split('\n'), new_content.split('\n')) if ol != nl)
    print(f'  {changed_lines} 行编号已替换')

    # For split chapters: 以"上"分部在索引中的条目为锚点，为（中/下）分部补条目
    # V2.0: 分部条目标题一律取文件系统权威标题
    added = 0
    for base, seq in sorted(split_info.items()):
        new_ids = [nid for nid, _ in seq]
        up_id = new_ids[0]
        up_pattern = re.compile(rf'^({up_id}):\s*(.+)', re.MULTILINE)

        for m in up_pattern.finditer(new_content):
            line_end = new_content.find('\n', m.end())
            if line_end < 0:
                line_end = len(new_content)
            insert_pos = line_end + 1

            for nid in new_ids[1:]:
                new_line = f'{nid}: {fs_title(nid)}'
                if new_line not in new_content:
                    new_content = (new_content[:insert_pos] + new_line + '\n'
                                   + new_content[insert_pos:])
                    insert_pos += len(new_line) + 1
                    added += 1

    if added:
        print(f'  为拆分章节新增 {added} 条索引')

    with open(SEX_INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  sex索引已更新')


def main():
    print('=== 重编号后文档更新 ===\n')

    print('[1/3] 解析重编号映射...')
    old_to_new, split_old = parse_dry_run(DRY_RUN_FILE)
    simple_map = build_simple_old_to_new(old_to_new)

    print(f'  总映射条目: {len(old_to_new)}')
    print(f'  拆分章节: {len(split_old)} 个')
    for base, parts in sorted(split_old.items()):
        up_new = simple_map.get(base, '?')
        part_str = ', '.join(f'.{d}→{n}' for d, n in sorted(parts))
        print(f'    Ch{base} → Ch{up_new}(上) + {part_str}')

    print('\n[2/3] 更新连续叙事弧线总览...')
    split_info = update_arc_document(simple_map, split_old, old_to_new)

    print('\n[3/3] 更新sex索引...')
    update_sex_index(simple_map, split_old, old_to_new, split_info)

    print('\n✅ 文档更新完成')
    print('  下一步: python scripts/rebuild_all.py 然后 python scripts/check_consistency.py')


if __name__ == '__main__':
    main()
