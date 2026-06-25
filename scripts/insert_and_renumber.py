# -*- coding: utf-8 -*-
"""
insert_and_renumber.py — 可复用事件插入+级联重编号脚本
=============================
在事件文件中指定位置插入新事件，并对后续事件进行级联重编号。
所有N##引用（标题+YAML内的触发条件/核心等字段）同步更新。
使用单次pass正则替换防止级联匹配。

用法：
  python insert_and_renumber.py <md_file> <after_id> <new_event_file> [--dry-run]

示例：
  python insert_and_renumber.py docs/05_事件系统.md N74 scripts/tmp_new.txt
  → 在N74后插入新事件，N75→N76, N76→N77 ...
"""
import re
import sys
import os
from datetime import datetime
from collections import OrderedDict


def find_event_blocks(text):
    """提取所有事件块（复用event_tool.py的逻辑）"""
    blocks = []
    for m in re.finditer(r'^### 事件([A-Z]+\d{1,3})[：:]([^\n]*)', text, re.MULTILINE):
        eid = m.group(1)
        title = m.group(2).strip()
        start = m.start()
        # 找到块结束
        rest = text[m.end():]
        end_match = re.search(r'\n### 事件|\n### [^\s]|\n## |\n---', rest)
        end = m.end() + (end_match.start() if end_match else len(rest))
        blocks.append({'id': eid, 'title': title, 'start': start, 'end': end,
                       'text': text[start:end]})
    return blocks


def insert_event(md_path, after_id, new_file, dry_run=False):
    """在after_id后插入新事件，级联重编号后续N##事件"""
    import re as _re

    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    with open(new_file, 'r', encoding='utf-8') as f:
        new_block = f.read().strip()

    blocks = find_event_blocks(text)
    block_map = {b['id']: b for b in blocks}

    if after_id not in block_map:
        print(f"❌ 找不到目标事件: {after_id}")
        return False

    # 提取新事件ID
    new_id_match = _re.search(r'事件[：:]\s*([A-Z]+\d{1,3})', new_block)
    if not new_id_match:
        print("❌ 新事件文件中找不到事件ID")
        return False
    new_id = new_id_match.group(1)
    new_prefix = _re.match(r'([A-Z]+)', new_id).group(1)

    # 确定重编号范围：所有在after_id之后的同前缀事件
    after_num = int(_re.search(r'\d+', after_id).group())
    to_renumber = []
    for bid, b in block_map.items():
        bprefix = _re.match(r'([A-Z]+)', bid).group(1)
        bnum = int(_re.search(r'\d+', bid).group())
        if bprefix == new_prefix and bnum > after_num:
            to_renumber.append((bnum, bid))

    to_renumber.sort()

    # 构建重编号映射（单次pass用）
    # 计算新编号：所有后续事件+1
    renumber_map = {}  # old_id → new_id
    used_nums = set()
    for old_num, old_id in to_renumber:
        new_num = old_num + 1
        new_id_str = f"{new_prefix}{new_num:02d}"
        renumber_map[old_id] = new_id_str
        used_nums.add(new_num)

    print(f"插入: {new_id} 在 {after_id} 之后")
    print(f"重编号: {len(renumber_map)} 个事件")
    for old_id, new_id in sorted(renumber_map.items()):
        print(f"  {old_id} → {new_id}")

    if dry_run:
        print("\n[干运行] 未修改文件")
        return True

    # 备份
    backup_path = os.path.join(os.path.dirname(md_path), '..', 'backups',
                               f'{os.path.basename(md_path)}.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
    backup_path = os.path.abspath(backup_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"📦 备份: {backup_path}")

    # Step 1: 插入新事件（在after_id事件块之后）
    after_block = block_map[after_id]
    insert_pos = after_block['end']
    # 确保有换行
    if not text[insert_pos:].startswith('\n'):
        new_block = '\n' + new_block
    if not new_block.endswith('\n'):
        new_block = new_block + '\n'
    # 在插入位置后添加分隔和换行
    insert_text = '\n' + new_block + '\n---\n\n'
    text = text[:insert_pos] + insert_text + text[insert_pos:]

    # Step 2: 级联重编号 — 单次pass回调替换，防止N75→N76→N77级联
    # 构建联合pattern匹配所有旧ID，回调中查表替换
    sorted_old_ids = sorted(renumber_map.keys(), key=lambda x: -len(x))
    _combined_pattern = '|'.join(_re.escape(oid) for oid in sorted_old_ids)
    _full_re = _re.compile(rf'(?<![A-Za-z0-9])({_combined_pattern})(?!\d)')

    def _cb(m):
        return renumber_map[m.group(0)]

    text = _full_re.sub(_cb, text)

    # Step 3: 写回
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✅ 完成：插入{new_id}，重编号{len(renumber_map)}个后续事件")
    return True


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--dry-run']

    if len(args) < 3:
        print("用法: python insert_and_renumber.py <md_file> <after_id> <new_event_file> [--dry-run]")
        sys.exit(1)

    md_file, after_id, new_file = args[0], args[1], args[2]
    success = insert_event(md_file, after_id, new_file, dry_run)
    sys.exit(0 if success else 1)
