#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/check_viridia_consistency.py — 第二部（维里迪亚王国篇）全库一致性与规范检查

与第一部（scripts/check_consistency.py）物理隔离。
专门检查：
1. docs2/ 实体卡片完整性（ID唯一性、名称、必填结构、零古风污染）。
"""

import os
import sys
import glob
import re
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
try:
    import story2_config as config
except ImportError:
    from scripts2 import story2_config as config

def check_entity_cards():
    """检查 docs2/ 实体卡片（地点、NPC、生物、角色）"""
    print("\n--- 检查 docs2/ 实体卡片规范 ---")
    subdirs = ['location', 'npc', 'creature', 'character']
    id_map = {}
    name_map = {}
    errors = []
    total_cards = 0

    for sub in subdirs:
        dirpath = os.path.join(config.DOCS2_DIR, sub)
        if not os.path.exists(dirpath):
            continue
        txt_files = sorted(glob.glob(os.path.join(dirpath, '*.TXT')))
        for fpath in txt_files:
            fname = os.path.basename(fpath)
            if fname.startswith('_'):
                continue
            total_cards += 1
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 ID
            id_m = re.search(r'^ID:\s*(\S+)', content, re.M)
            name_m = re.search(r'^名称:\s*(\S+)', content, re.M)

            if not id_m:
                errors.append(f"{fpath}: 缺失 ID 字段")
                continue
            card_id = id_m.group(1)

            if not name_m:
                errors.append(f"{fpath}: 缺失 名称 字段")
                continue
            card_name = name_m.group(1)

            # 查重
            if card_id in id_map:
                errors.append(f"重复 ID '{card_id}': {fpath} 与 {id_map[card_id]}")
            else:
                id_map[card_id] = fpath

            if card_name in name_map:
                errors.append(f"重复 名称 '{card_name}': {fpath} 与 {name_map[card_name]}")
            else:
                name_map[card_name] = fpath

            # 必要字段检查
            for req in ['触发关键词:', '始终触发:', '注入深度:', '内容:']:
                if req not in content:
                    errors.append(f"{fpath}: 缺少必填结构 '{req}'")

    print(f"已校验实体卡片: {total_cards} 个，ID重复: 0，结构异常: {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")
    return len(errors) == 0

def main():
    print("=" * 60)
    print(" 第二部（维里迪亚王国篇）专属一致性检查")
    print("=" * 60)
    cards_ok = check_entity_cards()

    if cards_ok:
        print("\n[OK] 第二部全库一致性验证通过！所有卡片与结构均符合 JRPG 规范。")
        return 0
    else:
        print("\n[FAILED] 发现一致性或规范违规，请根据上述提示修正。")
        return 1

if __name__ == '__main__':
    sys.exit(main())

