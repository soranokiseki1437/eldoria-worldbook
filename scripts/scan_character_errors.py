#!/usr/bin/env python3
"""
扫描所有章节TXT，对照_character_attributes.txt检查角色外貌描述错误。
输出所有可疑行供人工逐条确认。
"""

import os
import re
import sys

# ============================================================
# 权威数据源：从_character_attributes.txt提取
# ============================================================

GROUND_TRUTH = {
    "Seraphina": {
        "names": ["Seraphina", "菲娜", "炽天使"],
        "hair_correct": ["粉色", "粉发", "粉红", "粉"],
        "hair_wrong": ["金色", "银发", "银色", "白", "黑发", "蓝色", "紫色"],
        "eye_correct": ["琥珀", "琥珀色"],
        "eye_wrong": ["青紫", "深蓝", "黄绿", "红色", "绯红", "紫色", "绿色"],
        "special": ["无尖耳", "走路无声", "行走无声"],
        "forbidden": ["尖耳", "精灵耳"],  # 她是精灵但无尖耳 — 需要逐个判断
    },
    "黎恩": {
        "names": ["黎恩", "舒华泽"],
        "hair_correct": ["黑色", "黑发", "黑"],
        "hair_wrong": ["金色", "银色", "白色", "蓝色", "棕色", "粉色"],
        "eye_correct": ["青紫", "青紫色"],
        "eye_wrong": ["琥珀", "金色", "红色", "黄色", "绿色", "蓝色"],
    },
    "奥蕾莉亚": {
        "names": ["奥蕾莉亚", "黄金罗刹", "罗刹"],
        "hair_correct": ["银色", "银发", "银"],
        "hair_wrong": ["金色", "粉色", "黑色", "白色", "蓝色"],
        "eye_correct": ["紫色", "紫瞳", "紫"],
        "eye_wrong": ["琥珀", "金色", "红色", "绿色", "蓝色", "青紫"],
        "special": ["G杯", "G罩杯"],
    },
    "劳拉": {
        "names": ["劳拉", "亚尔赛德"],
        "hair_correct": ["靛蓝", "靛蓝色"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": ["琥珀", "琥珀色"],
        "eye_wrong": ["青紫", "金色", "红色", "绿色", "蓝色", "紫色"],
    },
    "亚尔缇娜": {
        "names": ["亚尔缇娜", "黑兔"],
        "hair_correct": ["银白", "银白色"],
        "hair_wrong": ["金色", "粉色", "黑色", "纯白", "银色"],  # "银色"容易与"银白"混淆
        "eye_correct": ["黄绿", "黄绿色"],
        "eye_wrong": ["深蓝", "蓝色", "琥珀", "青紫", "红色", "紫色", "绯红"],
    },
    "艾玛": {
        "names": ["艾玛", "米尔斯汀"],
        "hair_correct": ["李子色", "李子"],
        "hair_wrong": ["金色", "银色", "黑色", "白色", "粉色"],
        "eye_correct": ["薄荷蓝", "薄荷蓝色"],
        "eye_wrong": ["琥珀", "青紫", "红色", "绿色", "紫色", "深蓝"],
    },
    "菲": {
        "names": ["菲", "克劳塞尔"],
        "hair_correct": ["白色", "白发", "白"],
        "hair_wrong": ["银色", "金色", "粉色", "黑色", "蓝色"],
        "eye_correct": ["黄绿", "黄绿色"],
        "eye_wrong": ["琥珀", "青紫", "红色", "紫色", "蓝色", "深蓝"],
    },
    "凯尔": {
        "names": ["凯尔"],
        "hair_correct": ["深蓝", "深蓝色"],
        "hair_wrong": ["金色", "银色", "黑色", "白色", "棕色", "粉色"],
        "eye_correct": ["异色瞳", "异色"],
        "eye_wrong": [],  # 只要不是写异色瞳就是错的
        "special": ["戴.*眼镜", "细框眼镜", "眼镜"],
        "forbidden_special": ["不戴眼镜"],
    },
    "亚莉莎": {
        "names": ["亚莉莎", "莱恩福尔特"],
        "hair_correct": ["金色", "金发", "金"],
        "hair_wrong": ["银色", "粉色", "黑色", "白色", "蓝色"],
        "eye_correct": ["绯红", "绯红色"],
        "eye_wrong": ["琥珀", "青紫", "绿色", "蓝色", "紫色"],
    },
    "爱丽榭": {
        "names": ["爱丽榭"],
        "hair_correct": ["深紫", "深紫色"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": ["深紫", "深紫色"],
        "eye_wrong": ["琥珀", "青紫", "绿色", "蓝色", "绯红"],
    },
    "玲": {
        "names": ["玲·布莱特", "玲"],
        "hair_correct": ["紫色", "紫发"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": ["红色", "红瞳", "红"],
        "eye_wrong": ["琥珀", "青紫", "绿色", "蓝色", "绯红", "黄绿"],
    },
    "艾德里安": {
        "names": ["艾德里安"],
        "hair_correct": ["银灰", "银灰色"],
        "hair_wrong": ["金色", "粉色", "黑色", "白色", "棕色"],
        "eye_correct": ["琥珀", "琥珀色"],
        "eye_wrong": ["青紫", "红色", "绿色", "蓝色", "紫色", "绯红"],
    },
    "雷恩": {
        "names": ["雷恩"],
        "hair_correct": ["深棕", "深棕色"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色", "蓝色"],
        "eye_correct": ["深绿", "深绿色"],
        "eye_wrong": ["琥珀", "青紫", "红色", "蓝色", "紫色", "绯红", "黄绿"],
    },
    "乔治": {
        "names": ["乔治", "诺姆"],
        "hair_correct": ["棕色", "棕发", "棕"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色", "蓝色"],
        "special": ["摸后脑勺", "铅笔滚落"],
        "forbidden_special": ["推眼镜", "戴眼镜", "眼镜"],
    },
    "多尔金": {
        "names": ["多尔金"],
        "hair_correct": ["暗棕", "暗棕色"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": [],
        "eye_wrong": [],
    },
    "哈根": {
        "names": ["哈根"],
        "hair_correct": ["棕色", "棕发", "棕"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": ["灰蓝", "灰蓝色"],
        "eye_wrong": ["琥珀", "青紫", "红色", "绿色", "紫色", "黄绿"],
    },
    "法林": {
        "names": ["法林"],
        "hair_correct": ["暗棕", "暗棕色"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": ["深绿", "深绿色"],
        "eye_wrong": ["琥珀", "青紫", "红色", "蓝色", "紫色", "灰蓝"],
    },
    "罗恩": {
        "names": ["罗恩"],
        "hair_correct": ["灰棕", "灰棕色"],
        "hair_wrong": ["金色", "银色", "粉色", "黑色", "白色"],
        "eye_correct": ["绯红", "绯红色"],
        "eye_wrong": ["琥珀", "青紫", "绿色", "紫色", "黄绿"],
        "special": ["满月.*蓝", "变蓝"],
    },
    "月语者": {
        "names": ["月语者"],
        "hair_correct": ["灰黑", "灰黑色"],
        "hair_wrong": ["金色", "银色", "粉色", "白色"],
        "eye_correct": ["绯红", "绯红色"],
        "eye_wrong": ["琥珀", "青紫", "绿色", "紫色"],
    },
    "加尔": {
        "names": ["加尔"],
        "hair_correct": [],  # 鳞甲
        "hair_wrong": [],
        "eye_correct": [],
        "eye_wrong": [],
        "special": ["墨绿", "鳞甲"],
    },
    "Thalion": {
        "names": ["Thalion"],
        "hair_correct": ["银色", "银发"],
        "hair_wrong": ["金色", "粉色", "黑色", "白色"],
        "eye_correct": [],
        "eye_wrong": [],
    },
}

# ============================================================
# 扫描逻辑
# ============================================================

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "story")

def find_all_chapters():
    """递归查找所有章节TXT文件"""
    chapters = []
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if f.endswith(".TXT") and not f.startswith("_"):
                chapters.append(os.path.join(root, f))
    return sorted(chapters)

def scan_file(filepath):
    """扫描单个文件，返回所有可疑行"""
    flags = []
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    for lineno, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        for char_key, char_data in GROUND_TRUTH.items():
            # Check if any character name appears in this line
            name_found = None
            for name in char_data["names"]:
                if name in line_stripped:
                    name_found = name
                    break
            if not name_found:
                continue

            # Check hair color descriptions
            for hw in char_data.get("hair_wrong", []):
                # More precise matching: the wrong color word near the character name
                if hw in line_stripped:
                    # Skip if a correct hair color is also present
                    correct_nearby = any(hc in line_stripped for hc in char_data.get("hair_correct", []))
                    if not correct_nearby:
                        flags.append({
                            "file": filename,
                            "line": lineno,
                            "char": char_key,
                            "type": "发色",
                            "text": line_stripped[:200],
                            "issue": f"可能错误的发色描述'{hw}'",
                        })

            # Check eye color descriptions
            for ew in char_data.get("eye_wrong", []):
                if ew in line_stripped:
                    correct_nearby = any(ec in line_stripped for ec in char_data.get("eye_correct", []))
                    if not correct_nearby:
                        # Check it's actually describing this character's eyes
                        if any(eye_word in line_stripped for eye_word in ["瞳", "眼", "目光", "视线", "眸"]):
                            flags.append({
                                "file": filename,
                                "line": lineno,
                                "char": char_key,
                                "type": "瞳色",
                                "text": line_stripped[:200],
                                "issue": f"可能错误的瞳色描述'{ew}'",
                            })

            # Check forbidden special features
            for fs in char_data.get("forbidden_special", []):
                if fs in line_stripped:
                    flags.append({
                        "file": filename,
                        "line": lineno,
                        "char": char_key,
                        "type": "特征",
                        "text": line_stripped[:200],
                        "issue": f"不应出现的特征'{fs}'",
                    })

            # Check for glasses on 乔治
            for forbidden in char_data.get("forbidden_special", []):
                if forbidden in line_stripped:
                    flags.append({
                        "file": filename,
                        "line": lineno,
                        "char": char_key,
                        "type": "特征",
                        "text": line_stripped[:200],
                        "issue": f"不应出现的描述'{forbidden}'",
                    })

    return flags

def check_special_cases(filepath):
    """检查特殊规则：亚尔缇娜深蓝瞳、Seraphina尖耳等"""
    flags = []
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()
        lines = content.split("\n")

    for lineno, line in enumerate(lines, 1):
        ls = line.strip()

        # 亚尔缇娜 + 深蓝
        if ("亚尔缇娜" in ls or "黑兔" in ls) and "深蓝" in ls and ("瞳" in ls or "眼" in ls or "目光" in ls):
            flags.append({
                "file": filename, "line": lineno, "char": "亚尔缇娜",
                "type": "瞳色", "text": ls[:200],
                "issue": "亚尔缇娜瞳色应为黄绿，非深蓝",
            })

        # Seraphina + 尖耳/精灵耳
        if ("Seraphina" in ls or "菲娜" in ls) and ("尖耳" in ls or "精灵耳" in ls):
            flags.append({
                "file": filename, "line": lineno, "char": "Seraphina",
                "type": "特征", "text": ls[:200],
                "issue": "Seraphina无尖耳，不应出现尖耳/精灵耳描述",
            })

        # 菲 + 尖耳
        if "菲" in ls and "尖耳" in ls:
            flags.append({
                "file": filename, "line": lineno, "char": "菲",
                "type": "特征", "text": ls[:200],
                "issue": "菲无尖耳",
            })

        # 乔治 + 眼镜/推眼镜
        if "乔治" in ls and ("眼镜" in ls or "推眼镜" in ls):
            flags.append({
                "file": filename, "line": lineno, "char": "乔治",
                "type": "特征", "text": ls[:200],
                "issue": "乔治不戴眼镜",
            })

        # 黎恩发色错误
        if "黎恩" in ls:
            for wrong in ["金发", "银发", "白发", "棕发"]:
                if wrong in ls and "黑" not in ls:
                    flags.append({
                        "file": filename, "line": lineno, "char": "黎恩",
                        "type": "发色", "text": ls[:200],
                        "issue": f"黎恩是黑发，非{wrong}",
                    })

        # 奥蕾莉亚发色错误
        if ("奥蕾莉亚" in ls or "罗刹" in ls) and "金发" in ls:
            flags.append({
                "file": filename, "line": lineno, "char": "奥蕾莉亚",
                "type": "发色", "text": ls[:200],
                "issue": "奥蕾莉亚是银发，非金发",
            })

        # 菲发色: 白色不是银色
        if "菲" in ls and "银发" in ls:
            flags.append({
                "file": filename, "line": lineno, "char": "菲",
                "type": "发色", "text": ls[:200],
                "issue": "菲是白发，非银发",
            })

        # 艾玛发色: 李子色不是紫色
        if "艾玛" in ls and "紫发" in ls and "深紫" not in ls:
            flags.append({
                "file": filename, "line": lineno, "char": "艾玛",
                "type": "发色", "text": ls[:200],
                "issue": "艾玛是李子色发，非紫发",
            })

    return flags

def main():
    chapters = find_all_chapters()
    print(f"扫描 {len(chapters)} 个章节文件...\n")

    all_flags = []

    for i, ch in enumerate(chapters):
        rel_path = os.path.relpath(ch, STORY_DIR)
        if i % 50 == 0:
            print(f"  进度: {i}/{len(chapters)} — {rel_path}")

        flags1 = scan_file(ch)
        flags2 = check_special_cases(ch)
        all_flags.extend(flags1)
        all_flags.extend(flags2)

    print(f"\n{'='*80}")
    print(f"共发现 {len(all_flags)} 条可疑项\n")

    if not all_flags:
        print("✅ 未发现明显错误！")
        return

    # 按角色分组输出
    by_char = {}
    for f in all_flags:
        c = f["char"]
        if c not in by_char:
            by_char[c] = []
        by_char[c].append(f)

    for char, flags in sorted(by_char.items()):
        print(f"\n{'─'*60}")
        print(f"【{char}】共 {len(flags)} 条可疑项:")
        for f in flags[:50]:  # 限制每个角色最多显示50条
            print(f"  {f['file']}:L{f['line']} [{f['type']}] {f['issue']}")
            print(f"    → {f['text'][:150]}")
        if len(flags) > 50:
            print(f"  ... 还有 {len(flags) - 50} 条")

    # 输出汇总
    print(f"\n{'='*80}")
    print(f"总计: {len(all_flags)} 条可疑项需要人工确认")
    by_type = {}
    for f in all_flags:
        t = f["type"]
        by_type[t] = by_type.get(t, 0) + 1
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}条")

if __name__ == "__main__":
    main()
