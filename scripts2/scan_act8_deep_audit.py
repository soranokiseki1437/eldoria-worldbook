#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/scan_act8_deep_audit.py — 第八幕深度设定穿透、角色武器契约与戏腔台词雷达
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACT8_DIR = os.path.join(BASE_DIR, "方案", "第二部", "主线与世界扩充方案", "分阶段详规", "08_第八幕_血色伏击·至暗大溃败")

# 1. 角色-武器/能力非法绑定规则表 (子句级匹配，避免跨分句误伤)
ROLE_WEAPON_RULES = [
    {
        "role": "菲",
        "pattern": r"(?:菲|克劳塞尔)[^，。；\n]{0,25}?(短铳|火铳|燧发枪|手枪|左轮|刺刀短铳)",
        "desc": "【武器错误】菲官方武器为『双枪剑（Gunblade）』，兼具斩击与射击，严禁缩减为单纯短铳或火铳",
    },
    {
        "role": "爱丽榭",
        "pattern": r"(?:爱丽榭|舒华泽)[^，。；\n]{0,25}?(法杖|魔杖|短杖|魔导杖|施法|法术|咒文|魔法光芒)",
        "desc": "【人设/能力错误】爱丽榭不是魔法师，营地生活料理支柱，绝无法杖",
    },
    {
        "role": "菲娜",
        "pattern": r"(?:菲娜|塞拉菲娜|Seraphina)[^，。；\n]{0,25}?(短杖|银质短杖|魔杖|权杖)",
        "desc": "【武器捏造】菲娜施法为『双手祈祷式释放纯圣光』，绝无短杖",
    },
    {
        "role": "劳拉",
        "pattern": r"(?:劳拉|亚尔赛德)[^，。；\n]{0,25}?(单手剑|短剑|金发|金黄色双瞳|剑气|丹田)",
        "desc": "【武器/外貌冲突】劳拉为双手大剑、靛蓝色长发高马尾、琥珀色双瞳",
    },
    {
        "role": "亚尔缇娜",
        "pattern": r"(?:亚尔缇娜|Altina)[^，。；\n]{0,25}?(金色双眼|金发|双枪)",
        "desc": "【外貌冲突】亚尔缇娜为黄绿双瞳、银白发、黑色贝雷帽",
    },
    {
        "role": "玲",
        "pattern": r"(?:玲|Renne)[^，。；\n]{0,35}?(八音盒留在王都|工坊齿轮箱底藏着八音盒)",
        "desc": "【证物时空分身】EVD-08八音盒始终由玲随身收纳，王都齿轮箱底是糖纸与钟表图谱",
    },
    {
        "role": "雷恩",
        "pattern": r"(?:雷恩|Rayne)[^，。；\n]{0,25}?(巨剑|双手大剑|暗器|短铳|双手重剑)",
        "desc": "【武器冲突】雷恩武器为晨光长剑与沉野生铁重盾",
    },
]

# 2. 中式古代朝堂/公案/评书戏腔黑名单
COURT_CLICHE_PATTERNS = [
    (r"万万不可", "中式朝堂忠臣死谏套话，JRPG置换为『别乱来！/ 请等一下！/ 现在太危险了！』"),
    (r"何出此言", "中式古装文言套话，JRPG置换为『怎么突然这么说？/ 为什么这么想？』"),
    (r"不可造次", "古风训斥套话，JRPG置换为『退后！/ 别轻举妄动！』"),
    (r"万死不辞", "中式誓言套话，JRPG置换为『哪怕赌上性命也……』"),
    (r"微臣|老臣|末将|卑职|臣等", "中式朝廷臣属自称，西幻封建使用『受封骑士/我等/在下/名字』"),
    (r"草民|奴才|奴婢|(?:^|[^\u4e00-\u9fa5])小的(?:[，。！？\s]|$)", "中式市井奴仆谦称，西幻使用『我们/老汉/平民/名字』"),
    (r"启奏|圣裁|圣躬|皇恩|叩首|请安", "中式帝制宫廷词汇，严禁出现在西幻王国中"),
    (r"成何体统|休得无礼|休要多言", "中式古装长辈训斥腔"),
    (r"纳命来|手底下见真章", "中式武侠绿林叫阵词"),
]

# 3. 圣殿与教廷混淆
ORGANIZATION_CONFUSION = [
    (r"(?<!严禁)(?<!禁止)(?<!杜绝)(教廷骑士|教会骑士)", "教廷无骑士建制，应为『异端审问厅执行官/首席裁决剑士』"),
    (r"(?<!严禁)(?<!禁止)(?<!杜绝)(圣殿主教|圣殿神官|圣殿修道院)", "圣殿为武装修会，主教/神官/修道院属于晨光教廷"),
]


def scan_file(filepath):
    rel_path = os.path.relpath(filepath, BASE_DIR)
    issues = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines, start=1):
        # 1. 检查角色武器/能力绑定
        for rule in ROLE_WEAPON_RULES:
            match = re.search(rule["pattern"], line)
            if match:
                issues.append({
                    "line": idx,
                    "type": "ROLE_WEAPON_MISMATCH",
                    "role": rule["role"],
                    "matched": match.group(0),
                    "desc": rule["desc"],
                    "content": line.strip()
                })
                
        # 2. 检查戏腔台词
        if not ("严禁" in line and "违规红线防御" in line):
            for pattern, desc in COURT_CLICHE_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    issues.append({
                        "line": idx,
                        "type": "COURT_CLICHE",
                        "matched": match.group(0),
                        "desc": desc,
                        "content": line.strip()
                    })
                
        # 3. 检查组织混淆
        if not ("严禁" in line or "违规红线防御" in line):
            for pattern, desc in ORGANIZATION_CONFUSION:
                match = re.search(pattern, line)
                if match:
                    issues.append({
                        "line": idx,
                        "type": "ORG_CONFUSION",
                        "matched": match.group(0),
                        "desc": desc,
                        "content": line.strip()
                    })
                
    return rel_path, issues


def main():
    if not os.path.exists(ACT8_DIR):
        print(f"Error: 目标目录不存在: {ACT8_DIR}")
        sys.exit(1)
        
    files = sorted([
        os.path.join(ACT8_DIR, f)
        for f in os.listdir(ACT8_DIR)
        if f.endswith(".md")
    ])
    
    total_issues = 0
    print("=" * 80)
    print("第八幕深度设定穿透与文风死角自动化排查雷达 (ACT 8 Deep Audit)")
    print("=" * 80)
    
    for f in files:
        rel_path, issues = scan_file(f)
        total_issues += len(issues)
        if issues:
            print(f"\n📂 文件: {rel_path} (发现 {len(issues)} 处违规/隐患)")
            for it in issues:
                print(f"  Line {it['line']:<4} [{it['type']}] 命中: 『{it['matched']}』")
                print(f"        说明: {it['desc']}")
                print(f"        片段: {it['content'][:80]}...")
        else:
            print(f"\n✅ 文件: {rel_path} — 0 违规，契约核验通过")
            
    print("\n" + "=" * 80)
    print(f"排查完成！累计发现真实违规/隐患: {total_issues} 处。")
    print("=" * 80)
    return total_issues


if __name__ == "__main__":
    sys.exit(main())
