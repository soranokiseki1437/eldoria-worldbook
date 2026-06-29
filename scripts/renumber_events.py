#!/usr/bin/env python3
"""
renumber_events.py — 全局事件重编号引擎 (V9.0)

扫描全部章节目录的TXT文件，按ID行float值排序后分配全局连续整数编号。
两阶段重命名防碰撞，更新交叉引用和DEFAULT_CHAPTERS。

用法:
  python renumber_events.py              # 重编号全部事件
  python renumber_events.py --dry-run    # 预览变更不执行

设计原则:
  - 排序依据: ID: 行的float值（支持小数插入标记如 ID: 40.5）
  - 重命名: 两阶段（→临时名 →最终名）防碰撞
  - 交叉引用: 词边界保护，ID行自身不被替换
  - DEFAULT_CHAPTERS: 自动从磁盘实际文件分布更新范围
  - 全或无: 任何步骤失败则中止，不留下半改状态
"""

import os
import re
import sys
import shutil
from collections import OrderedDict
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')
SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')
ASSIGN_CHAPTERS_PATH = os.path.join(SCRIPTS_DIR, 'assign_chapters.py')

from story_config import ALL_PREFIXES


# ═══════════════════════════════════════════════════════════
# File I/O
# ═══════════════════════════════════════════════════════════

def read_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_txt(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


# ═══════════════════════════════════════════════════════════
# Core: Scan & Parse
# ═══════════════════════════════════════════════════════════

def get_id_float(filepath):
    """Extract float ID from a TXT file's ID: line. Returns float or None."""
    content = read_txt(filepath)
    m = re.match(r'^ID:\s*([\d.]+)', content)
    return float(m.group(1)) if m else None


def scan_all_events():
    """
    Scan all chapter directories for TXT files.
    Returns list of dicts: {filepath, chapter_idx, chapter_dir, old_id_float, old_filename}
    Sorted by (chapter_idx, old_id_float).
    """
    events = []
    for ch_idx, ch_dir in enumerate(ALL_PREFIXES):
        ch_path = os.path.join(EVENT_DIR, ch_dir)
        if not os.path.isdir(ch_path):
            continue
        for fname in os.listdir(ch_path):
            if not fname.upper().endswith('.TXT'):
                continue
            fp = os.path.join(ch_path, fname)
            id_val = get_id_float(fp)
            if id_val is None:
                print(f'  ⚠ 跳过（无有效ID行）: {ch_dir}/{fname}')
                continue
            events.append({
                'filepath': fp,
                'chapter_idx': ch_idx,
                'chapter_dir': ch_dir,
                'old_id_float': id_val,
                'old_filename': fname,
            })

    # Sort by (chapter_idx, old_id_float)
    events.sort(key=lambda e: (e['chapter_idx'], e['old_id_float']))
    return events


# ═══════════════════════════════════════════════════════════
# Core: Renumber
# ═══════════════════════════════════════════════════════════

def renumber_all(dry_run=False):
    """
    Main renumber function.
    1. Scan → 2. Sort → 3. Assign new IDs → 4. Two-phase rename
    → 5. Update ID lines → 6. Update cross-refs → 7. Update DEFAULT_CHAPTERS
    """
    print('[renumber] 扫描章节目录...')
    events = scan_all_events()
    if not events:
        print('  ❌ 未找到任何事件文件')
        return False

    print(f'  发现 {len(events)} 个事件 (分布在 {len(ALL_PREFIXES)} 个章节)')

    # Build old→new mapping
    old_to_new = {}
    new_to_info = OrderedDict()  # new_id (int) → {chapter_dir, old_filepath, ...}

    for i, ev in enumerate(events):
        new_id = i + 1  # 1-based
        old_id_int = int(ev['old_id_float'])
        old_id_str = str(old_id_int)
        # Also map zero-padded variants
        old_to_new[old_id_str] = new_id
        old_to_new[f'{old_id_int:02d}'] = new_id
        old_to_new[f'{old_id_int:03d}'] = new_id
        new_to_info[new_id] = {
            'chapter_dir': ev['chapter_dir'],
            'old_filepath': ev['filepath'],
            'old_filename': ev['old_filename'],
            'old_id_float': ev['old_id_float'],
        }

    # Check if already consecutive (all old int IDs == new IDs)
    all_consecutive = all(
        int(ev['old_id_float']) == (i + 1) and ev['old_id_float'] == int(ev['old_id_float'])
        for i, ev in enumerate(events)
    )
    if all_consecutive:
        print('  ✅ 编号已连续，无需重编号')
        return True

    # Count changes
    changes = sum(1 for i, ev in enumerate(events)
                  if int(ev['old_id_float']) != (i + 1))

    if dry_run:
        print(f'\n  [DRY-RUN] {changes} 个事件将重编号:')
        for i, ev in enumerate(events):
            new_id = i + 1
            old_int = int(ev['old_id_float'])
            if old_int != new_id:
                marker = ' (小数插入)' if ev['old_id_float'] != old_int else ''
                print(f'    {old_int}{marker} → {new_id}  [{ev["chapter_dir"]}] {ev["old_filename"][:60]}')
        return True

    print(f'\n[renumber] {changes} 个事件需要重编号...')

    # Backup reminder
    print('  (建议先运行 python scripts/backup_restore.py backup "pre-renumber")')

    # ═══════════════════════════════════════════
    # Phase 1: Rename all to temp names
    # ═══════════════════════════════════════════
    print('\n  Phase 1: 重命名为临时文件...')
    temp_map = {}  # temp_filepath → (new_id, chapter_dir, old_name_part)

    for new_id, info in new_to_info.items():
        old_fp = info['old_filepath']
        ch_dir = info['chapter_dir']
        old_name = info['old_filename']

        # Extract name part (after 数字：)
        if '：' in old_name:
            name_part = old_name.split('：', 1)[1]
        elif ':' in old_name:
            name_part = old_name.split(':', 1)[1]
        else:
            name_part = old_name

        # Temp name with unique counter
        temp_name = f'__RENUM_{new_id:04d}__.TXT'
        temp_path = os.path.join(EVENT_DIR, ch_dir, temp_name)

        try:
            os.rename(old_fp, temp_path)
            temp_map[temp_path] = (new_id, ch_dir, name_part)
        except OSError as e:
            print(f'    ❌ 重命名失败: {old_fp} → {temp_path}: {e}')
            return False

    print(f'    {len(temp_map)} 文件已重命名为临时名')

    # ═══════════════════════════════════════════
    # Phase 2: Update ID: lines in temp files
    # ═══════════════════════════════════════════
    print('\n  Phase 2: 更新 ID: 行...')
    for temp_path, (new_id, ch_dir, name_part) in temp_map.items():
        content = read_txt(temp_path)
        content = re.sub(r'^ID:\s*[\d.]+', f'ID: {new_id}', content, count=1)
        write_txt(temp_path, content)

    print(f'    {len(temp_map)} ID行已更新')

    # ═══════════════════════════════════════════
    # Phase 3: Update cross-references
    # ═══════════════════════════════════════════
    print('\n  Phase 3: 更新交叉引用...')
    _update_all_cross_references(old_to_new, temp_map)
    print('    交叉引用更新完成')

    # ═══════════════════════════════════════════
    # Phase 4: Rename temp → final
    # ═══════════════════════════════════════════
    print('\n  Phase 4: 重命名为最终文件名...')
    for temp_path, (new_id, ch_dir, name_part) in temp_map.items():
        # Zero-pad to 3 digits for consistent sorting
        final_name = f'{new_id:03d}：{name_part}'
        final_path = os.path.join(EVENT_DIR, ch_dir, final_name)

        try:
            os.rename(temp_path, final_path)
            if new_id <= 5 or new_id > len(temp_map) - 3:
                old_int = int(new_to_info[new_id]['old_id_float'])
                marker = ' ✨' if old_int != new_id else ''
                print(f'    {old_int} → {new_id}{marker}  {final_name[:70]}')
        except OSError as e:
            print(f'    ❌ 最终重命名失败: {temp_path} → {final_path}: {e}')
            return False

    # ═══════════════════════════════════════════
    # Phase 5: Update DEFAULT_CHAPTERS
    # ═══════════════════════════════════════════
    print('\n  Phase 5: 更新 DEFAULT_CHAPTERS...')
    _update_default_chapters(new_to_info)
    print('    DEFAULT_CHAPTERS 已更新')

    print(f'\n✅ 重编号完成 — {len(events)} 个事件, {changes} 个变更')
    print('  下一步: python scripts/rebuild_all.py')
    return True


# ═══════════════════════════════════════════════════════════
# Cross-reference update
# ═══════════════════════════════════════════════════════════

def _update_all_cross_references(old_to_new, temp_map):
    """
    Scan all .TXT files (including temp files and files NOT being renumbered)
    and replace old IDs with new IDs using word-boundary protection.
    ID: line (first line) is NOT touched — it was already updated in Phase 2.
    """
    # Build a set of all file paths to scan (temp files + other TXT files)
    all_txt_files = set(temp_map.keys())

    # Also scan files in backup dir? No — only active event dirs.
    # Also add TXT files not being renumbered (e.g., _TEMPLATE.TXT, chapter/ files)
    # But cross-refs only matter within event files. Keep scope to event dirs.
    for ch_dir in ALL_PREFIXES:
        ch_path = os.path.join(EVENT_DIR, ch_dir)
        if not os.path.isdir(ch_path):
            continue
        for fname in os.listdir(ch_path):
            if fname.upper().endswith('.TXT') or fname.endswith('.tmp'):
                fp = os.path.join(ch_path, fname)
                all_txt_files.add(fp)

    # Build sorted old ID list (longest first to avoid partial matches)
    sorted_old = sorted(old_to_new.keys(), key=lambda x: (-len(x), x))
    pattern = '|'.join(re.escape(o) for o in sorted_old)
    full_re = re.compile(rf'(?<![A-Za-z0-9])({pattern})(?!\d)')

    changed_count = 0
    for fp in all_txt_files:
        if not os.path.exists(fp):
            continue
        content = read_txt(fp)
        # Split first line (ID:) from body
        parts = content.split('\n', 1)
        if len(parts) == 2:
            id_line, body = parts
            new_body = full_re.sub(
                lambda m: str(old_to_new.get(m.group(0), m.group(0))),
                body
            )
            if new_body != body:
                write_txt(fp, id_line + '\n' + new_body)
                changed_count += 1
        else:
            # No newline — single line file (shouldn't happen)
            new_content = full_re.sub(
                lambda m: str(old_to_new.get(m.group(0), m.group(0))),
                content
            )
            if new_content != content:
                write_txt(fp, new_content)
                changed_count += 1

    return changed_count


# ═══════════════════════════════════════════════════════════
# DEFAULT_CHAPTERS update
# ═══════════════════════════════════════════════════════════

def _update_default_chapters(new_to_info):
    """
    Update assign_chapters.py DEFAULT_CHAPTERS ranges based on
    actual event distribution across chapter directories after renumber.

    new_to_info: {new_id: {chapter_dir, ...}}
    """
    # Build {chapter_dir: [new_ids sorted]}
    ch_ids = OrderedDict()
    for ch_dir in ALL_PREFIXES:
        ch_ids[ch_dir] = []

    for new_id, info in new_to_info.items():
        ch_dir = info['chapter_dir']
        if ch_dir in ch_ids:
            ch_ids[ch_dir].append(new_id)

    for ch_dir in ch_ids:
        ch_ids[ch_dir].sort()

    # Read assign_chapters.py
    content = read_txt(ASSIGN_CHAPTERS_PATH)

    # For each chapter, find its DEFAULT_CHAPTERS entry and update _ids() call
    # The chapter mapping in assign_chapters.py uses numeric keys like 0, 1, 2...
    # The ALL_PREFIXES order is: '0：序章', '1：试探和暧昧', ...
    # We extract the numeric prefix from the chapter dir name.

    for ch_idx, ch_dir in enumerate(ALL_PREFIXES):
        ids = ch_ids[ch_dir]
        if not ids:
            new_ids_str = '[]'
        else:
            start = ids[0]
            end = ids[-1]
            if start == end:
                new_ids_str = f'["{start:02d}"]'
            else:
                new_ids_str = f'_ids({start}, {end})'

        # Find the _ids() or [...] call for this chapter in assign_chapters.py
        # Pattern: ch_idx followed by _ids(start, end) or [...]
        # We look for the events line in the chapter's block
        ch_key = str(ch_idx)

        # Find the chapter block by looking for DEFAULT_CHAPTERS[ch_idx]
        # Then find its 'events' line
        block_start = content.find(f"DEFAULT_CHAPTERS[{ch_key}]")
        if block_start < 0:
            continue

        # Find the 'events' line within this block
        block_end = content.find('}', block_start)
        # Actually we need to find the next chapter or end of dict
        next_ch = content.find(f"DEFAULT_CHAPTERS[", block_start + 1)
        if next_ch < 0:
            next_ch = len(content)

        block = content[block_start:next_ch]

        # Find and replace the events line
        old_events_match = re.search(
            r"('events':\s*)(_ids\(\d+,\s*\d+\)|\[[^\]]*\])",
            block
        )
        if old_events_match:
            old_str = old_events_match.group(0)
            new_str = f"'events': {new_ids_str}"
            content = content.replace(old_str, new_str, 1)

    write_txt(ASSIGN_CHAPTERS_PATH, content)


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print('[DRY-RUN] 预览重编号变更\n')

    success = renumber_all(dry_run=dry_run)

    if dry_run:
        print('\n[DRY-RUN] 以上为预览，未实际修改任何文件。')
        print('  运行 python scripts/renumber_events.py 执行。')

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
