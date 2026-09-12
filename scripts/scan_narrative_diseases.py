#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eldoria 叙事质感与隐性病灶透视雷达 (Narrative Disease Scanner)

  1. [A-元叙事与打卡清单]：先是X...然后Y、轮换上场、差嘴/差口、核心字段流程图箭头「→」
  2. [B-NPC式干瘪短对白]：连续极短对白（如“舒服？”“还行……吧”“该我了”）
  3. [C-明确主语优先]：确保主语明确，严禁滥用“他/她”造成指代不明（主语反复出现是正确的设定规范）
  4. [D-隐性伪文言残留]：唯有、唯余、步入、未曾、已然、徐徐、若是、施为、自若、榻上、虚悬
"""

import os
import sys
import glob
import re
import argparse

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')

FORBIDDEN_WORDS = [
    '遂', '相询', '端坐', '榻上', '四肢百骸', '精关', '气海', '云雨', '仙躯', 
    '神识', '洞府', '徐徐', '宛若', '状若', '若是', '几息', '未曾', '已然', 
    '言毕', '施为', '唯有', '唯余', '自若', '步入', '踱至', '横陈', '虚悬', '亵渎'
]

STERILE_DIALOGUE_PATTERNS = [
    r'“舒服？”',
    r'“还行……吧。”',
    r'“还行。”',
    r'“舒服吗？”\s*“嗯。”',
    r'“该我了。”',
    r'“有一点痒。”'
]

def audit_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    fname = os.path.basename(filepath)
    findings = []

    # 1. 核心与情境的元叙事/打卡
    m_meta = re.search(r'先是(足|脚|手|胸|口|嘴|阴|穴|舌).*?然后', text)
    if m_meta:
        findings.append(('A-元叙事清单', m_meta.group(0)[:40]))
    
    task_cl = re.findall(r'(轮换上场|轮番服务|前置步骤|差嘴|差口)', text)
    if task_cl:
        findings.append(('A-打卡式词汇', task_cl))

    core_m = re.search(r'核心:\s*(.*)', text)
    if core_m:
        core_t = core_m.group(1)
        if '→' in core_t:
            findings.append(('A-核心流程图箭头', '→'))
        if '落差' in core_t and ('轮换' in core_t or '轮流' in core_t):
            findings.append(('A-核心机械描述', '落差/轮换'))

    # 2. 干瘪短对白
    for sp in STERILE_DIALOGUE_PATTERNS:
        if re.search(sp, text):
            findings.append(('B-干瘪NPC对白', sp))

    # 3. 明确主语优先（用户明确要求：主语反复出现是正确的，严禁滥用他/她指代不明）
    # 不再限制主语艾玛出现频次，反向鼓励明确主语指代

    # 4. 文言与伪文言禁词
    found_bw = [w for w in FORBIDDEN_WORDS if w in text]
    if found_bw:
        findings.append(('D-文言禁词残留', sorted(list(set(found_bw)))))

    return fname, filepath, findings

def main():
    parser = argparse.ArgumentParser(description='扫描章节中的叙事质感与隐性病灶')
    parser.add_argument('--all', action='store_true', help='扫描全库所有故事章节')
    parser.add_argument('--emma', action='store_true', default=True, help='仅扫描艾玛相关章节（默认）')
    parser.add_argument('--file', type=str, help='扫描指定章节文件')
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        all_files = sorted(glob.glob(os.path.join(STORY_DIR, '**', '*.TXT'), recursive=True))
        if args.all:
            files = all_files
        else:
            files = []
            for p in all_files:
                if os.path.basename(p).startswith('_'):
                    continue
                with open(p, 'r', encoding='utf-8') as f:
                    c = f.read()
                if '艾玛' in c:
                    files.append(p)

    total_scanned = len(files)
    problematic = []

    for p in files:
        fn, fp, fnds = audit_file(p)
        if fnds:
            problematic.append((fn, fp, fnds))

    print(f'============================================================')
    print(f'  Eldoria 叙事病灶透视雷达扫描完成')
    print(f'  扫描范围: {total_scanned} 篇 | 检出存在病灶: {len(problematic)} 篇')
    print(f'============================================================\n')

    if not problematic:
        print('  ✅ 未检出任何元叙事、NPC短对白、人名泛滥或文言残留病灶！')
        return

    for fn, fp, fnds in problematic:
        print(f'【{fn}】')
        for cat, det in fnds:
            print(f'   • [{cat}]: {det}')
        print()

if __name__ == '__main__':
    main()
