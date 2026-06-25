#!/usr/bin/env python3
"""
assemble_md.py — 从 docs/event/{prefix}/*.TXT 组装 05_事件系统.md 索引

零硬编码：事件ID/名称/排序全部由TXT文件驱动。
章节分组由 assign_chapters.DEFAULT_CHAPTERS 提供。
Section标题映射为30行元数据config，不含任何事件数据。

输出：docs/05_事件系统.md（仅索引——无事件正文）
"""

import os, re, sys
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'event')
MD_PATH = os.path.join(PROJECT_DIR, 'docs', '05_事件系统.md')
BACKUP_DIR = os.path.join(PROJECT_DIR, 'backups')

# 元数据从共享模块导入
from event_config import SECTION_TITLES, SHORT_LABELS, ALL_PREFIXES
SECTION_NUMBERING = ['二', '三', '四', '五', '六', '七', '八', '九']

# ═══════════════════════════════════════════════════════════
# TXT解析（复用 new_event.py parse_template 逻辑）
# ═══════════════════════════════════════════════════════════

def parse_txt(filepath):
    """Parse an individual .TXT event file, return dict of field→value."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {}
    current_key = None
    current_value = []

    for line in lines:
        # Skip empty lines and comments
        if not line.strip():
            continue
        if line.strip().startswith('#'):
            continue

        # Check for key: value line (not indented, not bullet)
        m = re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', line)
        if m and not line.lstrip().startswith(('-', 'A.', 'B.', 'C.')):
            # Save previous key
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_value = [val] if val else []
        else:
            # Continuation line
            current_value.append(line.rstrip('\n'))

    if current_key:
        data[current_key] = '\n'.join(current_value).strip()

    return data


def list_all_events():
    """Scan docs/event/ and return OrderedDict {eid: {prefix, name, filepath}}."""
    events = OrderedDict()
    for prefix in SECTION_TITLES:
        pfx_dir = os.path.join(EVENT_DIR, prefix)
        if not os.path.isdir(pfx_dir):
            continue
        txt_files = sorted(
            [f for f in os.listdir(pfx_dir) if f.upper().endswith('.TXT')],
            key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)]
        )
        for fname in txt_files:
            fp = os.path.join(pfx_dir, fname)
            data = parse_txt(fp)
            eid = data.get('ID', '')
            name = data.get('名称', '')
            if eid:
                events[eid] = {
                    'prefix': prefix,
                    'name': name,
                    'filepath': fp,
                }
    return events


# ═══════════════════════════════════════════════════════════
# 章节分组（从 DEFAULT_CHAPTERS 导入）
# ═══════════════════════════════════════════════════════════

def load_chapter_map():
    """Import DEFAULT_CHAPTERS from assign_chapters.py."""
    sys.path.insert(0, os.path.join(PROJECT_DIR, 'scripts'))
    try:
        from assign_chapters import DEFAULT_CHAPTERS
        return DEFAULT_CHAPTERS
    except ImportError as e:
        print(f'[WARN] 无法导入 assign_chapters.DEFAULT_CHAPTERS: {e}')
        return OrderedDict()


def build_event_chapter_lookup(chapters):
    """Build {event_id: chapter_num} from DEFAULT_CHAPTERS.
    DEFAULT_CHAPTERS values are dicts: {title, stage, events, anchor}"""
    lookup = {}
    for ch_num, ch_data in chapters.items():
        for eid in ch_data.get('events', []):
            lookup[eid] = ch_num
    return lookup


# ═══════════════════════════════════════════════════════════
# MD生成
# ═══════════════════════════════════════════════════════════

def generate_header():
    """Preserve the existing MD header (lines before ## 一、)."""
    if os.path.exists(MD_PATH):
        with open(MD_PATH, 'r', encoding='utf-8') as f:
            old = f.read()
        m = re.search(r'^(.*?)(?=\n## 一、事件系统总览)', old, re.DOTALL)
        if m:
            return m.group(1).rstrip() + '\n'
    # Fallback header
    return (
        '# 05 — 事件系统\n\n'
        '> **版本**: v6.5 | **自动生成** | 事件本体在 docs/event/ 子文件中\n'
        '> 本文档为**索引**——不含事件正文。增删改移事件请操作 docs/event/ 目录下的TXT文件。\n\n'
        '---\n'
    )


def generate_summary(events):
    """Generate ## 一、事件系统总览 section."""
    counts = OrderedDict()
    for eid, info in events.items():
        pfx = info['prefix']
        counts[pfx] = counts.get(pfx, 0) + 1

    lines = ['## 一、事件系统总览（脚本自动生成）', '', '```yaml']
    total = 0
    for pfx in SECTION_TITLES:
        if pfx in counts:
            label = SHORT_LABELS.get(pfx, pfx)
            lines.append(f'  {label}: {counts[pfx]}个')
            total += counts[pfx]
    lines.append('  ──')
    lines.append(f'  总计: {total}个事件')
    lines.append('```')
    return '\n'.join(lines)


def generate_event_list_section(events, chapter_lookup):
    """Generate section blocks: ## 二、阶段零事件... with event ID lists."""
    sections = []
    for i, (prefix, title) in enumerate(SECTION_TITLES.items()):
        num = SECTION_NUMBERING[i]
        pfx_events = [(eid, info) for eid, info in events.items()
                       if info['prefix'] == prefix]

        if not pfx_events:
            continue

        lines = [f'## {num}、{title}（{pfx_events[0][0]}-{pfx_events[-1][0]}）', '']

        # Group by chapter if chapter_lookup exists
        if chapter_lookup:
            # Determine if events in this prefix span multiple chapters
            chapters_seen = OrderedDict()
            for eid, info in pfx_events:
                ch = chapter_lookup.get(eid)
                if ch:
                    if ch not in chapters_seen:
                        chapters_seen[ch] = []
                    chapters_seen[ch].append((eid, info))

            if len(chapters_seen) > 1:
                # Multi-chapter: group by chapter
                for ch_num, ch_events in chapters_seen.items():
                    lines.append(f'### 第{ch_num}章（{ch_events[0][0]}-{ch_events[-1][0]}）')
                    for eid, info in ch_events:
                        lines.append(f'  - {eid} {info["name"]}')
                    lines.append('')
            else:
                # Single chapter: just list events
                for eid, info in pfx_events:
                    lines.append(f'- {eid} {info["name"]}')
        else:
            # No chapter info: flat list
            for eid, info in pfx_events:
                lines.append(f'- {eid} {info["name"]}')

        lines.append('')
        sections.append('\n'.join(lines))

    return '\n'.join(sections)


def generate_chapter_architecture(chapters):
    """Generate ## 章节架构 YAML from DEFAULT_CHAPTERS.
    chapters values are dicts: {title, stage, events, anchor}"""
    lines = ['## 章节架构（脚本自动生成，勿手动编辑）', '', '```yaml']
    for ch_num in sorted(chapters.keys()):
        ch = chapters[ch_num]
        ids_str = ', '.join(ch.get('events', []))
        lines.append(f'- 编号: {ch_num}')
        lines.append(f'  标题: "{ch["title"]}"')
        lines.append(f'  阶段: {ch.get("stage", "")}')
        lines.append(f'  事件: [{ids_str}]')
        if ch.get('anchor'):
            lines.append(f'  主线锚点: {ch["anchor"]}')
    lines.append('```')
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def assemble_md(dry_run=False):
    """Assemble 05_事件系统.md from TXT files."""
    print('[assemble] 扫描 docs/event/ ...')
    events = list_all_events()
    print(f'  发现 {len(events)} 个事件 ({len(SECTION_TITLES)} 个类别)')

    print('[assemble] 加载章节映射 ...')
    chapters = load_chapter_map()
    chapter_lookup = build_event_chapter_lookup(chapters)
    print(f'  加载 {len(chapters)} 个章节')

    print('[assemble] 生成MD ...')
    header = generate_header()
    summary = generate_summary(events)
    event_sections = generate_event_list_section(events, chapter_lookup)
    chapter_arch = generate_chapter_architecture(chapters)

    # Assemble full MD
    md_content = '\n\n'.join([
        header.rstrip(),
        summary,
        event_sections.rstrip(),
        chapter_arch,
    ]) + '\n'

    if dry_run:
        print(f'[dry-run] 将写入 {len(md_content)} 字符到 {MD_PATH}')
        print(md_content[:2000])
        return md_content

    # Backup existing MD
    if os.path.exists(MD_PATH):
        from datetime import datetime
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak_path = os.path.join(BACKUP_DIR, f'05_事件系统.md.{ts}.bak')
        import shutil
        shutil.copy2(MD_PATH, bak_path)
        print(f'  已备份: {bak_path}')

    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f'  已写入: {MD_PATH} ({len(md_content)} 字符)')

    return md_content


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    assemble_md(dry_run=dry_run)
