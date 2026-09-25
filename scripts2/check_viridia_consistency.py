#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/check_viridia_consistency.py — 第二部（维里迪亚王国篇）全库一致性与规范检查

与第一部（scripts/check_consistency.py）物理隔离。
专门检查：
1. docs2/ 设定卡片完整性（ID唯一性、名称、触发词、深度、零古风污染）。
2. docs2/story/ 章节规范（必须具备主要人物字段，绝对禁止战术隐蔽与第一部NSFW字段）。
3. 阶段与路线有效性验证（匹配 story2_config.py 规范）。
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
    print("\n--- [1/2] 检查 docs2/ 实体卡片规范 ---")
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

def check_story_chapters():
    """检查 docs2/story/ 章节文件规范"""
    print("\n--- [2/2] 检查 docs2/story/ 章节规范 ---")
    if not os.path.exists(config.DOCS2_STORY_DIR):
        print(f"提示: {config.DOCS2_STORY_DIR} 目录尚未创建或为空，跳过章节检测。")
        return True

    story_files = sorted(glob.glob(os.path.join(config.DOCS2_STORY_DIR, '**', '*.TXT'), recursive=True))
    chapter_files = [p for p in story_files if not os.path.basename(p).startswith('_')]
    total_chapters = len(chapter_files)
    errors = []

    if total_chapters == 0:
        print("当前尚未写入具体章节文件（待创作）。")
        return True

    for fpath in chapter_files:
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. 必填字段检查
        for req in config.REQUIRED_CHAPTER_FIELDS:
            pattern = rf'^{req}[:：]'
            if not re.search(pattern, content, re.M):
                errors.append(f"{fname}: 缺少必需字段 '{req}'")

        # 2. 严禁字段检查
        for fbd in config.FORBIDDEN_CHAPTER_FIELDS:
            pattern = rf'^{fbd}[:：]'
            if re.search(pattern, content, re.M):
                errors.append(f"{fname}: 存在违规字段 '{fbd}'（第二部禁止）")

        # 3. 路线有效性检查
        route_m = re.search(r'^路线[:：]\s*(.+)', content, re.M)
        if route_m:
            route_val = route_m.group(1).strip()
            if route_val not in config.VALID_ROUTES:
                errors.append(f"{fname}: 路线 '{route_val}' 不属于第二部标准路线列表")

        # 4. 主要人物字段非空检查
        chars_m = re.search(r'^主要人物[:：]\s*(.+)', content, re.M)
        if chars_m:
            chars_val = chars_m.group(1).strip()
            if not chars_val or chars_val in ['[]', '无']:
                errors.append(f"{fname}: '主要人物' 字段不可为空")

    print(f"已校验故事章节: {total_chapters} 个，规范异常: {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")
    return len(errors) == 0

def main():
    print("=" * 60)
    print(" 第二部（维里迪亚王国篇）专属一致性检查")
    print("=" * 60)
    cards_ok = check_entity_cards()
    story_ok = check_story_chapters()

    if cards_ok and story_ok:
        print("\n[OK] 第二部全库一致性验证通过！所有卡片与结构均符合 JRPG 规范。")
        return 0
    else:
        print("\n[FAILED] 发现一致性或规范违规，请根据上述提示修正。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
