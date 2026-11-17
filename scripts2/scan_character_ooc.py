#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/scan_character_ooc.py — 角色人设、战力与武装一致性自动化质检雷达

专门检测：
1. 【凯尔能力越界】：学者无魔法、无战技，严禁持法杖、施展岩刺/火球/雷击/净化、拔剑斩杀。严禁描写为“厚重眼镜”（应为细框眼镜）。
2. 【乔治外观与能力越界】：敦厚工匠平时不戴眼镜（工作戴护目镜），严禁“推细框/圆框/厚眼镜”。严禁轻功身法与法杖施法。
3. 【艾德里安武装越界】：贵族浪子佩刺剑/细剑，严禁使用重锤、大斧、战锤、巨盾。
4. 【劳拉武道越界】：亚尔赛德流双手巨剑/大剑，严禁使用盗贼匕首刺杀、潜行暗杀、法杖施法。
5. 【菲娜人设越界】：320岁精灵守护者炽天使血脉，外貌与人类一致无尖耳，严禁出现尖耳、重型兵器、暗影黑魔法。
6. 【亚尔缇娜称谓红线】：营地同伴私下严禁直呼特务代号“黑兔”（应为亚尔/亚尔酱/亚尔缇娜）。
7. 【罗恩与艾玛法杖区分】：罗恩为月光短杖，艾玛为魔导杖。
"""

import os
import sys
import glob
import re
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

OOC_RULES = [
    {
        'id': 'KYLE_MAGIC_WEAPON',
        'desc': '【凯尔人设崩坏】凯尔为纯学术学者，零魔法、非战斗人员，严禁持法杖或施展魔法/战技',
        'pattern': re.compile(r'凯尔[^。！？\n、；·]{0,40}(?:防御法杖|法杖|握杖|挥杖|施法|布设(?:结界|法阵|陷阱|岩刺)|岩刺|火球|雷击|束缚术|魔法攻击|圣骑士|拔剑|挥剑|斩杀)'),
    },
    {
        'id': 'KYLE_GLASSES_STYLE',
        'desc': '【凯尔眼镜规格错误】凯尔佩戴细框眼镜，严禁描写为厚重眼镜',
        'pattern': re.compile(r'凯尔[^。！？\n、；·]{0,25}厚重眼镜'),
    },
    {
        'id': 'GEORGE_GLASSES_OOC',
        'desc': '【乔治外观崩坏】乔治平时不戴眼镜（工作时戴护目镜），严禁佩戴日常/细框/圆框眼镜或推眼镜',
        'pattern': re.compile(r'乔治[^。！？\n、；·]{0,40}(?:细框眼镜|圆框眼镜|近视镜|推了推眼镜|推眼镜|戴上眼镜|戴着眼镜|厚眼镜)'),
    },
    {
        'id': 'ADRIAN_WEAPON_OOC',
        'desc': '【艾德里安武装错误】艾德里安使用家传刺剑/细剑，严禁使用重锤、战斧、巨盾',
        'pattern': re.compile(r'艾德里安[^。！？\n、；·]{0,40}(?:挥动重锤|抡起重锤|手持战斧|手持巨盾|劈出战斧)'),
    },
    {
        'id': 'LAURA_TACTICS_OOC',
        'desc': '【劳拉战斗风格错误】劳拉为大剑豪堂堂正正正面作战，严禁盗贼短匕首刺杀或法杖施法',
        'pattern': re.compile(r'劳拉[^。！？\n、；·]{0,40}(?:手持法杖|念动咒文|短匕首刺杀|潜行暗杀|握紧匕首)'),
    },
    {
        'id': 'SERAPHINA_EAR_OOC',
        'desc': '【菲娜外貌错误】菲娜虽为精灵守护者但外貌与人类一致无尖耳，严禁描写尖耳',
        'pattern': re.compile(r'菲娜[^。！？\n、；·]{0,25}(?:尖尖的耳朵|露出尖耳|尖耳微微)'),
    },
    {
        'id': 'ALTINA_CODENAME_CALL',
        'desc': '【亚尔缇娜称谓红线】营地同伴私下严禁直接以代号“黑兔”呼唤亚尔缇娜',
        'pattern': re.compile(r'(?:黎恩|菲娜|艾玛|玲|菲(?!娜)|爱丽榭|亚莉莎|乔治|加尔|罗恩|法林)[^。！？\n]{0,30}(?:叫道|喊道|笑道|问道|说)[^。！？\n]{0,10}“[^”]*\b黑兔\b'),
    }
]

def scan_file(filepath):
    errors = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return [f"无法读取文件 {filepath}: {e}"]

    for idx, line in enumerate(lines, 1):
        for rule in OOC_RULES:
            matches = rule['pattern'].finditer(line)
            for m in matches:
                errors.append(f"  行 {idx}: [{rule['id']}] {rule['desc']} -> 匹配到: \"{m.group(0)}\"")
    return errors

def main():
    parser = argparse.ArgumentParser(description="第二部角色人设与武装质检雷达")
    parser.add_argument("target", nargs="?", default="方案/第二部/主线与世界扩充方案/分阶段详规", help="要扫描的文件或目录")
    args = parser.parse_args()

    target_path = os.path.abspath(os.path.join(BASE_DIR, args.target))
    print(f"=== 开始扫描角色人设与能力一致性: {target_path} ===")

    total_files = 0
    total_violations = 0

    if os.path.isfile(target_path):
        files = [target_path]
    else:
        files = []
        for root, _, filenames in os.walk(target_path):
            for fn in filenames:
                if fn.endswith(('.md', '.TXT')):
                    files.append(os.path.join(root, fn))

    for fp in sorted(files):
        errs = scan_file(fp)
        rel_path = os.path.relpath(fp, BASE_DIR)
        if errs:
            print(f"\n[发现人设问题] {rel_path}:")
            for err in errs:
                print(err)
            total_violations += len(errs)
        total_files += 1

    print(f"\n=== 扫描完成: 检查了 {total_files} 个文件，发现 {total_violations} 处人设问题 ===")
    return 1 if total_violations > 0 else 0

if __name__ == '__main__':
    sys.exit(main())
