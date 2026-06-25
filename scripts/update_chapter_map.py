# -*- coding: utf-8 -*-
"""
update_chapter_map.py — 章节映射报告（只读）
=============================
从 assign_chapters.DEFAULT_CHAPTERS 读取章节-事件映射，打印统计报告。

用法:
  python scripts/update_chapter_map.py
"""
import os, sys
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_DIR, 'scripts'))

from assign_chapters import DEFAULT_CHAPTERS

chapters = OrderedDict()
for ch_num in sorted(DEFAULT_CHAPTERS.keys()):
    ch = DEFAULT_CHAPTERS[ch_num]
    chapters[ch_num] = ch

print(f"事件-章节映射报告（从 assign_chapters.DEFAULT_CHAPTERS 读取）\n")
print(f"{'章':<6} {'标题':<22} {'阶段':<10} {'事件数':<8} {'路线'}")
print("-" * 75)

for ch_num, ch in chapters.items():
    route = ('NTRS' if 12 <= ch_num <= 20 else
             '被动NTR' if 22 <= ch_num <= 30 else
             '断章' if ch_num == 99 else '主线')
    print(f"第{ch_num:<3}章 {ch['title']:<22} {ch.get('stage',''):<10} {len(ch['events']):<8} {route}")

total = sum(len(ch['events']) for ch in chapters.values())
print(f"\n总计: {len(chapters)}章, {total}个事件")
