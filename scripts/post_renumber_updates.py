#!/usr/bin/env python3
"""
post_renumber_updates.py — 重编号后更新弧线总览和sex索引
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

    # Build split chapter info for arc additions
    split_info = {}
    for base, parts in sorted(split_old.items()):
        parts_sorted = sorted(parts, key=lambda x: x[0])
        new_ids = [simple_map.get(base, base)]
        labels = ['上']
        for dec, nid in parts_sorted:
            new_ids.append(nid)
            labels.append('中' if dec in ('3', '8') else '下')
        split_info[base] = (new_ids, labels)

    # Generate arc entries for split chapters
    # Filter: only include bases that actually correspond to split (上) files
    new_arcs = []
    for base, (new_ids, labels) in sorted(split_info.items()):
        if len(new_ids) < 2:
            continue
        # Skip if this base's (上) file is NOT from a split
        # (e.g., Ch615 is original, Ch615.5 is a separate decimal chapter)
        up_id = new_ids[0]
        up_has_marker = False
        for root, dirs, files in os.walk(STORY_DIR):
            for f in files:
                for prefix in [f'{up_id:03d}：', f'{up_id}：']:
                    if f.startswith(prefix) and '（上）' in f:
                        up_has_marker = True
                        break
                if up_has_marker:
                    break
            if up_has_marker:
                break
        if not up_has_marker:
            continue

        # Get titles
        titles = []
        for nid in new_ids:
            found = ''
            for root, dirs, files in os.walk(STORY_DIR):
                for f in files:
                    for prefix in [f'{nid:03d}：', f'{nid}：']:
                        if f.startswith(prefix):
                            found = f.split('：', 1)[1].replace('.TXT', '')
                            break
                    if found:
                        break
                if found:
                    break
            titles.append(found or f'Ch{nid}')

        ch_refs = ' · '.join(f'Ch{nid}（{lbl}）' for nid, lbl in zip(new_ids, labels))
        title_line = ' → '.join(titles)
        new_arcs.append(f'| {base} | {ch_refs} | {title_line} | 拆分形成连续弧（{len(new_ids)}章） |')

    # Insert new arcs into the document (before the "统计" section or at end)
    if new_arcs:
        arc_header = '\n### 拆分新增弧线（V10.28 章节拆分）\n\n'
        arc_header += '| 原章 | 新编号 | 标题链 | 说明 |\n'
        arc_header += '|:--|:--|:--|:--|\n'
        arc_text = arc_header + '\n'.join(new_arcs) + '\n'

        # Insert before "---" separator or at end
        last_sep = new_content.rfind('\n---\n')
        if last_sep > 0:
            new_content = new_content[:last_sep] + arc_text + new_content[last_sep:]
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

    # For split chapters, add entries for (下) and (中) parts
    added = 0
    for base, (new_ids, labels) in sorted(split_info.items()):
        if len(new_ids) < 2:
            continue

        # Find (上) entry in sex index
        up_id = new_ids[0]
        up_pattern = re.compile(rf'^({up_id}):\s*(.+)', re.MULTILINE)

        for m in up_pattern.finditer(new_content):
            up_title = m.group(2)
            line_end = new_content.find('\n', m.end())
            if line_end < 0:
                line_end = len(new_content)

            insert_pos = line_end + 1

            # Add (中) and (下) entries
            for i, lbl in enumerate(labels[1:], 1):
                nid = new_ids[i]
                new_title = up_title.replace('（上）', f'（{lbl}）')
                new_line = f'{nid}: {new_title}'
                if new_line not in new_content:
                    new_content = (new_content[:insert_pos] + new_line + '\n' + new_content[insert_pos:])
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
    print('  下一步: python scripts/rebuild_all.py')


if __name__ == '__main__':
    main()
