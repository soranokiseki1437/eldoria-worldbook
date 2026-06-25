#!/usr/bin/env python3
"""
renumber_events.py — 事件TXT文件批量重编号 + 交叉引用更新

对指定前缀的事件进行连续重编号，填补空缺。同时更新所有TXT文件中的交叉引用。

用法:
  python renumber_events.py <prefix>            # 重编号指定前缀
  python renumber_events.py --all               # 重编号所有前缀
  python renumber_events.py --dry-run <prefix>  # 预览变更不执行

工作流:
  1. 手创TXT文件（按模板填好内容，文件名随意）
  2. python renumber_events.py <prefix>        # 重编号
  3. python assemble_md.py                     # 刷新05MD索引
"""

import os, re, sys, glob
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'event')

from event_config import ALL_PREFIXES


# ═══════════════════════════════════════════════════════════
# Core: Parse + Renumber
# ═══════════════════════════════════════════════════════════

def read_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_txt(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def get_id_from_txt(filepath):
    """Extract event ID from TXT file's first ID: line."""
    content = read_txt(filepath)
    m = re.match(r'^ID:\s*(\S+)', content)
    return m.group(1) if m else None


def get_numeric(eid):
    """Extract numeric part from event ID. 'N01' → 1, 'PN12' → 12, 'E1' → 1"""
    m = re.search(r'(\d+)', eid)
    return int(m.group(1)) if m else 0


def get_prefix(eid):
    """Extract prefix from event ID. 'N01' → 'N', 'PN12' → 'PN', 'E1' → 'E'"""
    m = re.match(r'^([A-Z]+)', eid)
    return m.group(1) if m else 'E'


def list_prefix_files(prefix):
    """Return sorted list of (filepath, old_eid, num) tuples for a prefix directory."""
    dir_path = os.path.join(EVENT_DIR, prefix)
    if not os.path.isdir(dir_path):
        return []
    results = []
    for fname in os.listdir(dir_path):
        if not fname.upper().endswith('.TXT'):
            continue
        fp = os.path.join(dir_path, fname)
        eid = get_id_from_txt(fp)
        if eid:
            num = get_numeric(eid)
            results.append((fp, eid, num))
    # Sort by current numeric value
    results.sort(key=lambda x: x[2])
    return results


def renumber_prefix(prefix, dry_run=False):
    """
    Renumber all events in a prefix directory to consecutive numbers.

    1. Sort files by current numeric value
    2. Determine minimum existing number as base
    3. Assign new consecutive IDs
    4. Build old→new mapping
    5. Rename files (two-phase to avoid collisions)
    6. Update ID: line in each file
    7. Update cross-references across ALL files

    Returns mapping dict {old_id: new_id} or None if no changes.
    """
    files = list_prefix_files(prefix)
    if not files:
        print(f'  {prefix}: (empty)')
        return None

    # Determine minimum existing number
    min_num = min(num for _, _, num in files)

    # Build mapping
    mapping = {}
    for i, (fp, old_eid, _) in enumerate(files):
        new_num = min_num + i
        # Preserve the original digit format (zero-padded or not)
        # Check if original uses leading zeros
        if re.match(r'^[A-Z]+0', old_eid):
            new_id = f'{prefix}{new_num:02d}'
        else:
            new_id = f'{prefix}{new_num}'

        if old_eid != new_id:
            mapping[old_eid] = new_id

    if not mapping:
        print(f'  {prefix}: {len(files)} events — already consecutive')
        return None

    if dry_run:
        print(f'  {prefix} [DRY-RUN]: {len(files)} events, {len(mapping)} changes:')
        for old_id in sorted(mapping.keys(), key=lambda x: (len(x), x)):
            print(f'    {old_id} → {mapping[old_id]}')
        return mapping

    print(f'  {prefix}: {len(files)} events, {len(mapping)} to renumber')

    dir_path = os.path.join(EVENT_DIR, prefix)

    # Phase 1: Rename all to temp names
    temp_map = {}
    counter = 0
    for fp, old_eid, _ in files:
        temp_name = f'__RENUM_{counter:04d}.tmp'
        temp_path = os.path.join(dir_path, temp_name)
        os.rename(fp, temp_path)
        new_id = mapping.get(old_eid, old_eid)
        temp_map[temp_path] = (old_eid, new_id)
        counter += 1

    # Phase 2: Update ID: line in each temp file
    for temp_path, (old_id, new_id) in temp_map.items():
        content = read_txt(temp_path)
        # Update the ID: line (first line of file)
        content = re.sub(r'^ID:\s*\S+', f'ID: {new_id}', content, count=1)
        write_txt(temp_path, content)

    # Phase 3: Update cross-references across ALL files (all prefixes)
    if mapping:
        _update_all_cross_references(mapping)

    # Phase 4: Rename temp files to final names
    for temp_path, (old_id, new_id) in temp_map.items():
        final_path = os.path.join(dir_path, f'{new_id}.TXT')
        os.rename(temp_path, final_path)
        print(f'    {old_id} → {new_id}')

    return mapping


def _update_all_cross_references(mapping):
    """Scan every .TXT file across ALL prefixes and replace old IDs with new IDs.
    Uses word-boundary-aware regex to prevent partial matches."""
    sorted_old = sorted(mapping.keys(), key=lambda x: -len(x))  # longest first
    pattern = '|'.join(re.escape(o) for o in sorted_old)
    full_re = re.compile(rf'(?<![A-Za-z0-9])({pattern})(?!\d)')

    changed_files = 0
    for pfx_dir in os.listdir(EVENT_DIR):
        pfx_path = os.path.join(EVENT_DIR, pfx_dir)
        if not os.path.isdir(pfx_path):
            continue
        # Match both .TXT and .tmp (temp files during renumber)
        for fname in os.listdir(pfx_path):
            if not (fname.upper().endswith('.TXT') or fname.endswith('.tmp')):
                continue
            fp = os.path.join(pfx_path, fname)
            content = read_txt(fp)
            # Split into first line (ID:) and rest — protect ID line from replacement
            parts = content.split('\n', 1)
            if len(parts) == 2:
                id_line, rest = parts
                new_rest = full_re.sub(lambda m: mapping.get(m.group(0), m.group(0)), rest)
                if new_rest != rest:
                    write_txt(fp, id_line + '\n' + new_rest)
                    changed_files += 1
            else:
                new_content = full_re.sub(lambda m: mapping.get(m.group(0), m.group(0)), content)
                if new_content != content:
                    write_txt(fp, new_content)
                    changed_files += 1

    if changed_files:
        print(f'    (updated cross-references in {changed_files} files)')


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    dry_run = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--dry-run']

    if '--all' in args:
        prefixes = ALL_PREFIXES
    elif args:
        prefixes = [p for p in args if p in ALL_PREFIXES]
        if not prefixes:
            print(f'未知前缀: {args}')
            print(f'有效前缀: {ALL_PREFIXES}')
            sys.exit(1)
    else:
        print(__doc__)
        sys.exit(1)

    mode = '[DRY-RUN] ' if dry_run else ''
    print(f'{mode}重编号: {", ".join(prefixes)}')

    all_mappings = {}
    for pfx in prefixes:
        mapping = renumber_prefix(pfx, dry_run=dry_run)
        if mapping:
            all_mappings.update(mapping)

    if dry_run:
        total = len(all_mappings)
        print(f'\n[DRY-RUN] {total} IDs would change across all prefixes')
    else:
        total = len(all_mappings)
        if total > 0:
            print(f'\n✅ {total} IDs renumbered. Run assemble_md.py next.')
        else:
            print('\n✅ All prefixes already consecutive.')


if __name__ == '__main__':
    main()
