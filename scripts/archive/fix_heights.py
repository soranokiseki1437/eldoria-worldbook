#!/usr/bin/env python3
"""
修正章节中被renumber误伤的叙事数字：身高/年龄/年份/章节引用
对照 _character_attributes.txt 权威数据
"""

import os
import re

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "story")

# (文件glob片段, 旧值, 新值, 说明)
# 按文件精确匹配，避免误伤
FIXES = [
    # ═══ 身高修正 ═══
    # 多尔金: 167cm → 148cm
    ("040：岩丘之行", "167cm", "148cm", "多尔金身高"),
    ("409：多尔金", "167cm", "148cm", "多尔金身高"),
    # 亚尔缇娜: 161cm → 142cm (6个文件)
    ("042：人偶与矮人", "161cm", "142cm", "亚尔缇娜身高"),
    ("174：银匕首", "161cm", "142cm", "亚尔缇娜身高"),
    ("383：清晨的唤醒", "161cm", "142cm", "亚尔缇娜身高"),
    ("406：矮人的回礼", "161cm", "142cm", "亚尔缇娜身高"),
    ("494：只属于一个人", "161cm", "142cm", "亚尔缇娜身高"),
    # 奥蕾莉亚: 209cm → 178cm
    ("050：聊聊", "209cm", "178cm", "奥蕾莉亚身高"),
    ("091：剑与酒", "209cm", "178cm", "奥蕾莉亚身高"),
    # 雷恩: 223cm → 188cm
    ("117：她的标准", "223cm", "188cm", "雷恩身高"),
    ("412：两个人的沉默", "223cm", "188cm", "雷恩身高"),
    ("457：告发", "223cm", "188cm", "雷恩身高"),
    # 凯尔: 206cm → 175cm
    ("148：意外的请求", "206cm", "175cm", "凯尔身高"),
    ("328：不是真的", "206cm", "175cm", "凯尔身高"),
    # Seraphina: 194cm → 168cm
    ("328：不是真的", "194cm", "168cm", "Seraphina身高"),
    # 劳拉: 197cm → 170cm
    ("412：两个人的沉默", "197cm", "170cm", "劳拉身高"),
    # 艾玛: 181cm → 159cm
    ("294：白兔与巨根", "181cm", "159cm", "艾玛身高"),
    ("329：被填满的魔女", "181cm", "159cm", "艾玛身高"),
    # 罗恩(常态): 188cm → 183cm
    ("081：狼人使者", "188cm", "183cm", "罗恩身高"),
    # 月语者满月: 263cm → 215cm
    ("454：满月之夜", "263cm", "215cm", "月语者满月身高"),
    ("462：满月双人", "263cm", "215cm", "月语者满月身高"),
    # 月语者: 187cm→185cm, 219cm→215cm
    ("490：满月夜的狼尾巴", "187cm", "185cm", "月语者常态身高"),
    ("490：满月夜的狼尾巴", "219cm", "215cm", "月语者满月身高"),
    # 牛头人: 461cm → 364cm
    ("220：矿道深处", "461cm", "364cm", "牛头人身高"),
    ("294：白兔与巨根", "461cm", "364cm", "牛头人身高"),
    ("329：被填满的魔女", "461cm", "364cm", "牛头人身高"),
    ("361：她的密码", "461cm", "364cm", "牛头人身高"),

    # ═══ 年龄/年份修正 ═══
    # 482岁 → ~320 (Seraphina年龄)
    ("087：影牙的战术", "482岁", "320岁", "Seraphina年龄"),
    ("088：爱丽榭的厨房", "482岁的精灵", "320岁的精灵", "Seraphina年龄"),
    ("154：玲的裂痕", "482年孤独", "200年孤独", "Seraphina孤独年数"),
    ("342：拼接的长桌", "482年来第一次", "200年来第一次", "Seraphina孤独年数"),
    ("434：玲与天使", "482年守护者", "200年守护者", "Seraphina孤独年数"),
    # 287年 → 200年 (孤独/守护)
    ("433：劳拉的守夜", "287年", "200年", "Seraphina孤独年数"),
    ("441：菲娜的眼泪", "287年", "200年", "Seraphina孤独年数"),
    ("441：菲娜的眼泪", "444年", "200年", "Seraphina孤独年数"),
    ("472：玲的坦白", "287年", "200年", "Seraphina孤独年数"),
    ("479：菲娜的散步", "287年", "200年", "Seraphina孤独年数"),
    ("481：家人的晚餐", "287年", "200年", "Seraphina孤独年数"),

    # ═══ 章节编号引用 → 描述性语言 ═══
]

def main():
    total = 0
    for root, dirs, files in os.walk(STORY_DIR):
        for fname in files:
            if not fname.endswith(".TXT") or fname.startswith("_"):
                continue
            fpath = os.path.join(root, fname)
            modified = False

            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            for pattern, old, new, desc in FIXES:
                if pattern in fname:
                    if old in content:
                        content = content.replace(old, new)
                        print(f"  [{desc}] {old}→{new}  {fname}")
                        modified = True
                        total += 1

            if modified:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)

    print(f"\n共修改 {total} 处")

if __name__ == "__main__":
    main()
