#!/usr/bin/env python3
"""列出所有>=2000字的章节，标注拆分类型"""
import os, re

story_dir = "docs/story"
chapters = []

for root, dirs, files in os.walk(story_dir):
    for f in files:
        if not f.endswith('.TXT') or f.startswith('_'):
            continue
        m = re.match(r'^(\d+(?:\.\d+)?)：', f)
        if not m:
            continue
        ch_id = m.group(1)
        try:
            ch_num = float(ch_id)
        except ValueError:
            continue
        if ch_num < 187:
            continue
        filepath = os.path.join(root, f)
        with open(filepath, 'r', encoding='utf-8') as fh:
            content = fh.read()
        chinese = len(re.findall(r'[一-鿿]', content))
        english = len(re.findall(r'[a-zA-Z]+', content))
        wc = chinese + english
        if wc >= 2000:
            split = "上/中/下" if wc >= 3500 else "上/下"
            chapters.append((ch_num, ch_id, wc, split, os.path.basename(root), f))

chapters.sort(key=lambda x: x[0])
print(f"=== 需拆分章节 (>= 2000字): {len(chapters)}章 ===\n")
for i, (num, cid, wc, split, stage, fname) in enumerate(chapters):
    print(f"{i+1:>2}. Ch{cid:<7} {wc:>5}字 [{split:>6}] [{stage}] {fname}")
