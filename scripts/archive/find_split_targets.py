#!/usr/bin/env python3
"""Find exact file paths for chapters to split"""
import os, re

targets = [
    # 上/中/下
    "247", "264", "361", "406", "615.5",
    # 上/下
    "207", "224", "274", "304", "307", "326",
    "343", "362", "363", "407", "438", "473",
    "474", "479", "491", "511", "517", "527",
    "543", "556", "616", "633", "743",
]

story_dir = "docs/story"
found = {}

for root, dirs, files in os.walk(story_dir):
    for f in files:
        if not f.endswith('.TXT') or f.startswith('_'):
            continue
        m = re.match(r'^(\d+(?:\.\d+)?)：', f)
        if not m:
            continue
        ch_id = m.group(1)
        if ch_id in targets:
            found[ch_id] = os.path.join(root, f)

for tid in targets:
    if tid in found:
        print(f"{tid}|{found[tid]}")
    else:
        print(f"{tid}|NOT FOUND")
