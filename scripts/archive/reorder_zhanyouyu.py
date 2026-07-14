#!/usr/bin/env python3
"""
将 story TXT 文件中的"占有欲确认"字段从"好感影响"之前移动到"情境"之后。

旧顺序: ...黎恩知情 → 占有欲确认 → 好感影响 → 情境 → 核心...
新顺序: ...黎恩知情 → 好感影响 → 情境 → 占有欲确认 → 核心...
"""

import os
import sys

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'story')


def reorder_file(filepath):
    """Reorders 占有欲确认 field in a single TXT file. Returns True if changed."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')

    # Find line indices of key fields
    zhanyouyu_idx = None
    haogan_idx = None
    qingjing_idx = None
    next_idx = None  # 核心: or 章节任务: after 情境

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('占有欲确认:') and zhanyouyu_idx is None:
            zhanyouyu_idx = i
        elif stripped.startswith('好感影响:') and haogan_idx is None:
            haogan_idx = i
        elif stripped.startswith('情境:') and qingjing_idx is None:
            qingjing_idx = i
        elif (stripped.startswith('核心:') or stripped.startswith('章节任务:')) and next_idx is None and qingjing_idx is not None:
            next_idx = i

    # Validate all indices found and in correct original order
    if None in (zhanyouyu_idx, haogan_idx, qingjing_idx, next_idx):
        return False  # Can't reorder, skip

    if not (zhanyouyu_idx < haogan_idx < qingjing_idx < next_idx):
        # Already reordered or unexpected structure
        if haogan_idx < qingjing_idx < zhanyouyu_idx:
            return False  # Already in new order
        return False  # Unexpected order, skip

    # Extract blocks
    before = lines[:zhanyouyu_idx]
    zhanyouyu_block = lines[zhanyouyu_idx:haogan_idx]
    haogan_block = lines[haogan_idx:qingjing_idx]
    qingjing_block = lines[qingjing_idx:next_idx]
    after = lines[next_idx:]

    # New order: before + haogan + qingjing + zhanyouyu + after
    result = before + haogan_block + qingjing_block + zhanyouyu_block + after
    new_text = '\n'.join(result)

    if new_text != text:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        return True

    return False


def main():
    changed = 0
    skipped = 0
    errors = 0

    for root, dirs, files in os.walk(STORY_DIR):
        for fname in files:
            if not fname.endswith('.TXT'):
                continue
            if fname.startswith('_'):
                continue  # Skip _TEMPLATE.TXT, _sex_index.txt etc.

            filepath = os.path.join(root, fname)
            try:
                if reorder_file(filepath):
                    changed += 1
                    print(f'  ✓ {fname}')
                else:
                    skipped += 1
            except Exception as e:
                errors += 1
                print(f'  ✗ {fname}: {e}')

    print(f'\nDone: {changed} changed, {skipped} skipped, {errors} errors')


if __name__ == '__main__':
    main()
