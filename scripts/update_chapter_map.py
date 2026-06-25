# -*- coding: utf-8 -*-
"""
update_chapter_map.py — 可复用章节-事件映射表自动生成器
=============================
从05_事件系统.md中提取所有事件，按情感阶段自动分组，
生成/更新"事件-章节映射表"章节。

用法：
  python update_chapter_map.py [--dry-run]

规则：
  - 按 情感阶段 字段自动分组事件
  - 阶段映射: A→Ch13-15, B→Ch16-18, B→C→Ch19-21, C→Ch22-24, C→D→Ch25-26, D→Ch27, 终局→Ch28
  - N01（坦白之夜）→Ch12
  - 纯爱/被动NTR事件不纳入此表（各自独立章节）
  - 单次pass生成，覆盖旧映射表
"""
import re
import sys
import os
from datetime import datetime
from collections import OrderedDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
MD_PATH = os.path.join(PROJECT_DIR, 'docs', '05_事件系统.md')

# 情感阶段→章节映射
PHASE_TO_CHAPTER = OrderedDict([
    ('A', 'Ch13-15：探索与试探（A阶段）'),
    ('B', 'Ch16-18：挑逗与萌芽（B阶段）'),
    ('B→C', 'Ch19-21：过渡与深入（B→C阶段）'),
    ('C', 'Ch22-24：放开与享受（C阶段）'),
    ('C→D', 'Ch25-26：信任巅峰（C→D阶段）'),
    ('D', 'Ch27：极限与反转（D阶段）'),
    ('终局', 'Ch28：确认与抉择（终局）'),
    ('通用', 'Ch22-26间：跨阶段通用（共享维度——黎恩与其他女性）'),
])

# 特殊事件→章节（不在阶段映射中的）
SPECIAL_MAP = {
    'N01': 'Ch12：坦白之夜·路线分支',
}


def extract_phase(yaml_text):
    """从YAML文本提取情感阶段"""
    m = re.search(r'^\s*情感阶段[：:]\s*(.+)$', yaml_text, re.MULTILINE)
    if not m:
        m = re.search(r'^\s*情感[：:]\s*(.+)$', yaml_text, re.MULTILINE)
    if not m:
        m = re.search(r'^\s*阶段[：:]\s*(.+)$', yaml_text, re.MULTILINE)
    return m.group(1).strip() if m else ''


def extract_third_party(yaml_text):
    """提取第三者"""
    m = re.search(r'^\s*第三者[：:]\s*(.+)$', yaml_text, re.MULTILINE)
    return m.group(1).strip() if m else '—'


def extract_all_events():
    """从MD提取所有事件"""
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md = f.read()

    events = []
    for m in re.finditer(
        r'### 事件(N\d{2})[：:]([^\n]+)\n\n```yaml\n(.*?)\n```',
        md, re.DOTALL
    ):
        eid = m.group(1)
        title = m.group(2).strip()
        yaml_text = m.group(3)
        phase = extract_phase(yaml_text)
        third = extract_third_party(yaml_text)
        events.append({'id': eid, 'title': title, 'phase': phase, 'third': third})

    return events


def group_by_chapter(events):
    """按章节分组事件——长前缀优先，防止B误匹配B→C"""
    chapters = OrderedDict()

    # Ch12特殊事件
    special = [e for e in events if e['id'] in SPECIAL_MAP]
    remaining = [e for e in events if e['id'] not in SPECIAL_MAP]
    if special:
        chapters[list(SPECIAL_MAP.values())[0]] = special

    # 阶段匹配规则（长前缀优先）
    def match_phase(phase_text, target):
        """phase_text是否匹配target阶段——前缀匹配，长→短优先级"""
        stripped = phase_text.strip()
        # 精确匹配：通用/终局
        if target in ('通用', '终局'):
            return target in stripped
        # 前缀匹配：'B→C'匹配'B→C', 'B'不匹配'B→C'
        if stripped.startswith(target):
            if target == 'B' and len(stripped) > 1 and stripped[1] == '→':
                return False
            if target == 'C' and len(stripped) > 1 and stripped[1] == '→':
                return False
            return True
        return False

    # 按定义顺序匹配（PHASE_TO_CHAPTER保持插入顺序）
    assigned = set()
    for phase_key, ch_name in PHASE_TO_CHAPTER.items():
        ch_events = []
        for ev in remaining:
            if ev['id'] in assigned:
                continue
            if match_phase(ev['phase'], phase_key):
                ch_events.append(ev)
                assigned.add(ev['id'])
        if ch_events:
            chapters[ch_name] = ch_events

    return chapters


def generate_table(chapters):
    """生成映射表markdown"""
    lines = ['## 事件-章节映射表', '']

    for ch_name, events in chapters.items():
        lines.append(f'### {ch_name}')
        lines.append('| 事件ID | 事件名称 | 第三者 |')
        lines.append('|--------|---------|--------|')
        for ev in events:
            lines.append(f'| {ev["id"]} | {ev["title"]} | {ev["third"]} |')
        lines.append('')

    # 统计
    total = sum(len(evs) for evs in chapters.values())
    lines.append(f'> **NTRS事件总计: {total}个** | 自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('')

    return '\n'.join(lines)


def update_md(dry_run=False):
    """更新MD文件中的映射表"""
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md = f.read()

    events = extract_all_events()
    chapters = group_by_chapter(events)
    new_table = generate_table(chapters)

    if dry_run:
        print(new_table)
        print(f"\n[干运行] 共 {sum(len(evs) for evs in chapters.values())} 个NTRS事件，未修改文件")
        return True

    # 替换旧映射表（从 "## 事件-章节映射表" 到下一个 "## " 或 "---"）
    pattern = r'(## 事件-章节映射表\n).*?(?=\n## 一、|\n---\n\n## 一、)'
    replacement = new_table + '\n\n'
    new_md = re.sub(pattern, replacement, md, flags=re.DOTALL)

    if new_md == md:
        print("⚠️ 未找到映射表或无需更新")
        return False

    # 备份
    backup_path = os.path.join(PROJECT_DIR, 'backups',
                               f'05_事件系统.md.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"📦 备份: {backup_path}")

    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(new_md)

    # 统计
    for ch_name, evs in chapters.items():
        ids = ', '.join(e['id'] for e in evs)
        print(f"  {ch_name}: {len(evs)}个 → {ids}")
    print(f"✅ 映射表已更新: {sum(len(evs) for evs in chapters.values())} 个NTRS事件")
    return True


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    update_md(dry_run)
