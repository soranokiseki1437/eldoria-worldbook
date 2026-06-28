# -*- coding: utf-8 -*-
"""
assign_chapters.py — 章节-事件映射权威数据源
=============================
DEFAULT_CHAPTERS 是章节↔事件映射的唯一权威数据。
被 update_chapter_map.py / build_eldoria.py / generate_event_browser.py 导入使用。

V9.0: 单线纯爱NTRS融合线，170事件纯数字编号(01-170)，9章节目录。

用法:
  python scripts/assign_chapters.py              # 打印章节统计
  python scripts/assign_chapters.py --check      # 验证 DEFAULT_CHAPTERS 数据完整性
"""

import re, sys, os
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'event')

# ============================================================
# 权威章节定义 (V9.0 — 2026-06-28)
# 单线纯爱NTRS融合线：170事件纯数字编号(01-170)
# 修改事件列表后运行 renumber_events.py 自动更新范围。
# ============================================================
DEFAULT_CHAPTERS = OrderedDict()

# 工具函数：生成数字ID范围
def _ids(start, end):
    return [f"{i:02d}" for i in range(start, end + 1)]

# —— 第0章：序章 (01-39) ——
DEFAULT_CHAPTERS[0] = {
    'title': '序章：苏醒与相遇',
    'stage': '序章',
    'events': _ids(1, 62),
    'anchor': '苏醒→相遇→VII班集结→告白→契约→第三者登场→回归仪式→温泉→森林意志',
}

# —— 第1章：试探和暧昧 (40-63) ——
DEFAULT_CHAPTERS[1] = {
    'title': '试探和暧昧',
    'stage': '试探和暧昧',
    'events': _ids(63, 98),
    'anchor': '坦白→建框→注视→蹭触→第三者风格确立→第一次共享(低语者)→回归仪式',
}

# —— 第2章：挑逗和接受 (64-75) ——
DEFAULT_CHAPTERS[2] = {
    'title': '挑逗和接受',
    'stage': '挑逗和接受',
    'events': _ids(99, 116),
    'anchor': '主动展示→扣穴试探→第三者指交→口交初体验→主动邀请→回归仪式',
}

# —— 第3章：渐进接触 (76-102) ——
DEFAULT_CHAPTERS[3] = {
    'title': '渐进接触',
    'stage': '渐进接触',
    'events': _ids(117, 153),
    'anchor': '足交→手交→乳交→口交→隐奸→一对二→边界→逼近跨线→回归仪式',
}

# —— 第4章：跨线 (103-115) ——
DEFAULT_CHAPTERS[4] = {
    'title': '跨线',
    'stage': '跨线',
    'events': _ids(154, 176),
    'anchor': '低语者失败→疗愈→首次人类插入(凯尔)→雷恩插入→自主选择→回归仪式',
}

# —— 第5章：享受和掌控 (116-148) ——
DEFAULT_CHAPTERS[5] = {
    'title': '享受和掌控',
    'stage': '享受和掌控',
    'events': _ids(177, 228),
    'anchor': '主动设计隐奸→多第三者本番→3P→轮奸→极限体验→日常缓冲',
}

# —— 第6章：放纵 (149-167) ——
DEFAULT_CHAPTERS[6] = {
    'title': '放纵',
    'stage': '放纵',
    'events': _ids(229, 259),
    'anchor': '主动服务→反向服务→极限→低语者轮奸→回归仪式',
}

# —— 第7章：终局 (168-170) ——
DEFAULT_CHAPTERS[7] = {
    'title': '终局',
    'stage': '终局',
    'events': _ids(260, 262),
    'anchor': '决战前夜→净化回归→情书',
}

# —— 第8章：后日谈（暂无事件） ——
DEFAULT_CHAPTERS[8] = {
    'title': '后日谈',
    'stage': '后日谈',
    'events': _ids(263, 280),
    'anchor': '（暂无事件）',
}


def update_ranges_from_disk():
    """
    Scan chapter directories on disk and update DEFAULT_CHAPTERS event ranges
    to match actual file distribution. Called by renumber_events.py after renumber.

    Reads all TXT files from each chapter dir, extracts IDs, and rewrites
    the _ids() calls in DEFAULT_CHAPTERS.
    """
    from event_config import ALL_PREFIXES

    ch_ranges = OrderedDict()
    for ch_idx, ch_dir in enumerate(ALL_PREFIXES):
        ch_path = os.path.join(EVENT_DIR, ch_dir)
        ids = []
        if os.path.isdir(ch_path):
            for fname in os.listdir(ch_path):
                if not fname.upper().endswith('.TXT'):
                    continue
                fp = os.path.join(ch_path, fname)
                try:
                    with open(fp, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                    m = re.match(r'^ID:\s*(\d+)', first_line)
                    if m:
                        ids.append(int(m.group(1)))
                except Exception:
                    continue
        ids.sort()
        ch_ranges[ch_idx] = (min(ids), max(ids)) if ids else None

    # Rewrite DEFAULT_CHAPTERS events lines
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assign_chapters.py')
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for ch_idx, id_range in ch_ranges.items():
        ch_key = str(ch_idx)
        block_start = content.find(f"DEFAULT_CHAPTERS[{ch_key}]")
        if block_start < 0:
            continue
        next_ch = content.find(f"DEFAULT_CHAPTERS[", block_start + 1)
        if next_ch < 0:
            next_ch = len(content)

        if id_range is None:
            new_events_str = '[]'
        elif id_range[0] == id_range[1]:
            new_events_str = f'["{id_range[0]:02d}"]'
        else:
            new_events_str = f'_ids({id_range[0]}, {id_range[1]})'

        # Replace the events line in this chapter's block
        block = content[block_start:next_ch]
        old_match = re.search(r"('events':\s*)(_ids\(\d+,\s*\d+\)|\[[^\]]*\])", block)
        if old_match:
            content = content.replace(old_match.group(0), f"'events': {new_events_str}", 1)

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return ch_ranges


def generate_summary():
    """从DEFAULT_CHAPTERS统计事件数量，生成总览"""
    total = sum(len(ch['events']) for ch in DEFAULT_CHAPTERS.values())

    lines = ['## 一、事件系统总览（脚本自动生成）', '',
             '```yaml',
             '  事件系统:']
    lines.append(f'    总章节: {len(DEFAULT_CHAPTERS)}章 (第0章~第{max(DEFAULT_CHAPTERS.keys())}章)')
    lines.append(f'    总事件: {total}个 (编号01-{total})')
    lines.append(f'    架构: 单线纯爱NTRS融合线 — 共享时刻 ⇄ 回归时刻')
    lines.append(f'    路线: 唯一一条NTRS融合线')
    lines.append('```')
    return '\n'.join(lines)


def generate_chapter_architecture():
    """生成章节架构YAML"""
    lines = ['## 章节架构（脚本自动生成，勿手动编辑）', '',
             '> `scripts/assign_chapters.py` 自动生成。修改章节事件列表请运行 `renumber_events.py`。', '',
             '```yaml', '章节:']
    for ch_num in sorted(DEFAULT_CHAPTERS.keys()):
        ch = DEFAULT_CHAPTERS[ch_num]
        lines.append(f'  - 编号: {ch_num}')
        lines.append(f'    标题: "{ch["title"]}"')
        lines.append(f'    阶段: {ch["stage"]}')
        lines.append(f'    事件: [{", ".join(ch["events"])}]')
        lines.append(f'    主线锚点: "{ch["anchor"]}"')
    lines.append('```')
    return '\n'.join(lines)


if __name__ == '__main__':
    check_only = '--check' in sys.argv
    total = sum(len(ch_data['events']) for ch_data in DEFAULT_CHAPTERS.values())
    print(f'DEFAULT_CHAPTERS: {len(DEFAULT_CHAPTERS)}章, {total}事件')

    if check_only:
        all_eids = []
        for ch_num, ch_data in DEFAULT_CHAPTERS.items():
            for eid in ch_data['events']:
                if eid in all_eids:
                    print(f'  ⚠️ 重复: {eid}')
                all_eids.append(eid)
        if len(all_eids) == len(set(all_eids)):
            print(f'  ✅ 无重复事件ID')
        sys.exit(0)

    # Print chapter summary
    for ch_num in sorted(DEFAULT_CHAPTERS.keys()):
        ch = DEFAULT_CHAPTERS[ch_num]
        n = len(ch['events'])
        rng = f'{ch["events"][0]}-{ch["events"][-1]}' if n > 0 else '(空)'
        print(f'  第{ch_num}章 [{ch["stage"]}]: {n}事件 ({rng})  {ch["title"]}')

