# -*- coding: utf-8 -*-
"""add_chapter_fields.py — 给所有章节TXT新增三字段（章节核心目标/章节任务/章节终止条件）

对齐俺妹ver1.41章节格式。自动从现有字段推导值。
幂等：已有新字段的文件跳过。

用法：
    python scripts/add_chapter_fields.py           # 正式写入
    python scripts/add_chapter_fields.py --dry-run # 仅预览
"""

import os
import sys
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'event')

NEW_FIELDS = ['章节核心目标', '章节任务', '章节终止条件']


def parse_txt(filepath):
    """解析TXT文件，返回(header_lines, fields_dict, footer_lines)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {}
    current_key = None
    current_value = []
    field_order = []  # track insertion order

    for line in lines:
        if not line.strip():
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
                current_key = None
                current_value = []
            continue
        if line.strip().startswith('#'):
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
                current_key = None
                current_value = []
            continue

        m = re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', line)
        if m and not line.lstrip().startswith(('-', '•', '>', '·')):
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_value = [val] if val else []
            if current_key not in field_order:
                field_order.append(current_key)
        else:
            current_value.append(line.rstrip('\n'))

    if current_key:
        data[current_key] = '\n'.join(current_value).strip()

    return data, field_order


def derive_fields(data):
    """从现有字段自动推导三个新字段"""
    core = data.get('核心', '')
    situation = data.get('情境', '')

    # 章节核心目标 ← 核心（直接复制）
    core_goal = core if core else '（待填写）'

    # 章节任务 ← 核心首句
    mission = data.get('章节任务', '')
    if not mission and core:
        first_sent = core.split('。')[0].split('——')[0].strip()
        mission = first_sent + '。' if not first_sent.endswith('。') else first_sent
    if not mission:
        mission = '（待填写）'

    # 章节终止条件 ← 情境bullet
    end_cond = data.get('章节终止条件', '')
    if not end_cond and situation:
        bullets = []
        for b in situation.split('\n'):
            b = b.strip()
            if b.startswith('- '):
                b = b[2:]
            elif b.startswith('-'):
                b = b[1:]
            else:
                continue
            # 取首句
            b_first = b.split('——')[0].split('。')[0].strip()
            bullets.append(b_first)

        if bullets:
            cond_lines = []
            for i, b in enumerate(bullets[:5], 1):
                cond_lines.append(f'{i}.{b}')
            end_cond = '\n'.join(cond_lines)
        else:
            end_cond = '（待填写）'
    if not end_cond:
        end_cond = '（待填写）'

    return {
        '章节核心目标': core_goal,
        '章节任务': mission,
        '章节终止条件': end_cond,
    }


def needs_update(data):
    """检查是否缺少新字段"""
    return any(f not in data or not data[f] or data[f] == '（待填写）'
               for f in NEW_FIELDS)


def rewrite_txt(filepath, data, field_order, new_fields, dry_run=False):
    """重写TXT文件，在核心字段后插入新字段"""
    # 找到核心字段的位置
    core_idx = None
    for i, f in enumerate(field_order):
        if f == '核心':
            core_idx = i
            break

    if core_idx is None:
        print(f'  ⚠ 未找到"核心"字段，跳过')
        return 0

    # 构建新的字段顺序：在核心之后插入新字段
    insert_pos = core_idx + 1
    new_order = list(field_order)
    for nf in reversed(NEW_FIELDS):
        if nf not in new_order:
            new_order.insert(insert_pos, nf)

    if dry_run:
        return len([f for f in NEW_FIELDS if f not in field_order])

    # 合并data
    merged = dict(data)
    merged.update(new_fields)

    # 重建文件内容
    # 先读取原文件找到格式
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    # 简单策略：在"核心: ..."块之后追加新字段
    # 找到核心字段的结束位置
    core_pattern = re.compile(r'(核心[：:][^\n]*(?:\n(?!\S+[：:])[^\n]*)*)')
    match = core_pattern.search(original)
    if not match:
        print(f'  ⚠ 无法定位核心字段内容，跳过')
        return 0

    core_end = match.end()

    # 构建追加文本
    append_lines = ['', '']
    for nf in NEW_FIELDS:
        val = new_fields.get(nf, '（待填写）')
        if '\n' in val:
            append_lines.append(f'{nf}: {val.split(chr(10))[0]}')
            for vl in val.split('\n')[1:]:
                append_lines.append(f'  {vl}')
        else:
            append_lines.append(f'{nf}: {val}')
        append_lines.append('')

    append_text = '\n'.join(append_lines)

    new_content = original[:core_end] + append_text + original[core_end:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len([f for f in NEW_FIELDS if f not in data])


def main():
    dry_run = '--dry-run' in sys.argv
    mode = '[DRY RUN] ' if dry_run else ''

    print(f"{mode}扫描: {EVENT_DIR}")
    print()

    total_files = 0
    updated_files = 0
    skipped_files = 0
    total_added = 0

    for root, dirs, files in os.walk(EVENT_DIR):
        for fname in sorted(files):
            if not fname.upper().endswith('.TXT'):
                continue
            if fname.startswith('_TEMPLATE'):
                continue
            if '备份' in root:
                continue  # 跳过备份目录

            fpath = os.path.join(root, fname)
            total_files += 1

            data, field_order = parse_txt(fpath)

            # 检查是否需要更新
            has_all = all(f in data for f in NEW_FIELDS)
            all_filled = has_all and all(data.get(f, '').strip() for f in NEW_FIELDS)

            if all_filled:
                skipped_files += 1
                continue

            # 推导新字段
            new_fields = derive_fields(data)

            # 确定新增数量
            n_added = len([f for f in NEW_FIELDS if f not in data])

            relpath = os.path.relpath(fpath, PROJECT_DIR)
            if dry_run:
                print(f'  {relpath}:')
                for nf in NEW_FIELDS:
                    val = new_fields[nf]
                    preview = val[:60].replace('\n', '\\n') + ('...' if len(val) > 60 else '')
                    tag = ' [NEW]' if nf not in data else ' [FILL]'
                    print(f'    {nf}{tag}: {preview}')
                updated_files += 1
                total_added += n_added
            else:
                n = rewrite_txt(fpath, data, field_order, new_fields, dry_run=False)
                status = f'+{n} fields' if n > 0 else 'filled'
                print(f'  {relpath}: {status}')
                updated_files += 1
                total_added += n

    print()
    print(f"{mode}完成: {total_files} 文件")
    print(f"  新增/填充: {updated_files} 文件, {total_added} 字段")
    print(f"  跳过(已有): {skipped_files} 文件")

    if dry_run:
        print()
        print(">>> 这是干跑预览。运行 'python scripts/add_chapter_fields.py' 正式写入。")


if __name__ == '__main__':
    main()
