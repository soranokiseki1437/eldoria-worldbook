#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/scan_classical_inversions.py — 文言倒装句式（如“裹以”、“覆以”、“饰以”）自动化扫描与白话化拦截器
"""

import os
import sys
import re
import glob
import argparse

# 匹配 动词 + 以 + 宾语 倒装模式
# 例如：裹以厚羊毛毡、覆以鹿皮、饰以金线、佐以黑麦面包、拭以烈酒、系以丝带、填以铅粒等
INVERSION_VERBS = [
    '裹', '覆', '饰', '佐', '辅', '缀', '系', '缠', '拭', '浸', '封', '施', '附', '示',
    '涂', '灌', '填', '冠', '绑', '贴', '衬', '托', '砌', '架', '铺', '抹', '盖', '套',
    '压', '扣', '束', '锁', '炙', '染', '烙', '焚', '浇', '饮'
]

INVERSION_PATTERN = re.compile(
    r'([^\w]|^)([' + ''.join(INVERSION_VERBS) + r'])以([^\s，。！？；、：”’]{1,15})'
)

# 匹配 "动词 + 之以" 格式（如授之以、晓之以、诱之以、动之以）
ZHI_YI_PATTERN = re.compile(r'([\u4e00-\u9fa5]{1,2})之以([\u4e00-\u9fa5]{1,6})')

# 现代白话正常词汇白名单
WHITELIST_WORDS = {
    '可以', '难以', '得以', '足以', '何以', '所以', '以此', '以便', '以及', '以为', '借以',
    '予以', '给以', '配以', '加以', '自以为', '难以置信', '得以喘息', '足以匹敌', '何以至此'
}

# 规则与白名单免检词汇
RULE_EXEMPTIONS = [
    '不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '违规',
    '倒装', '文言', '白话', '去套路化'
]

def check_line_inversions(line, line_idx=1):
    """
    检查单行文本是否存在文言倒装句式
    返回: list of (issue_type, message)
    """
    issues = []
    
    # 规则防护跳过
    if any(ex in line for ex in RULE_EXEMPTIONS):
        return issues

    # 1. 检测 "动词+以+宾语" 倒装
    for m in INVERSION_PATTERN.finditer(line):
        verb = m.group(2)
        obj = m.group(3)
        full_match = verb + '以' + obj
        
        # 检查是否命中白名单
        if verb + '以' in WHITELIST_WORDS or any(w in full_match for w in WHITELIST_WORDS):
            continue
        
        # 排除以...结尾的常见合规词（如"以此为"、"以为"）
        if obj.startswith(('此', '为', '及', '便', '期', '免', '至')):
            continue

        suggest = f"用{obj}{verb} / {verb}着{obj}"
        issues.append((
            '【文言倒装句式违规】',
            f"行 {line_idx}: 发现文言介词倒装 '{verb}以{obj}'（现代日轻白话建议改为 '{suggest}'） -> {line.strip()[:60]}"
        ))

    # 2. 检测 "动词+之以" 倒装
    for m in ZHI_YI_PATTERN.finditer(line):
        v = m.group(1)
        o = m.group(2)
        phrase = v + '之以' + o
        if '嗤之以鼻' in phrase:
            continue
        issues.append((
            '【文言倒装句式违规】',
            f"行 {line_idx}: 发现话本文言倒装 '{phrase}'（建议改用现代白话直陈句） -> {line.strip()[:60]}"
        ))

    # 3. 检测中式单字文言行路/移动动词“动词+至”（如行至、移步至、趋步至、走至、步至、踱至）
    VERB_ZHI_PATTERN = re.compile(r'(?<![一-龥])(行至|移步至|趋步至|踱步至|走至|步至|踱至)([一-龥]{1,10})')
    for m in VERB_ZHI_PATTERN.finditer(line):
        verb_zhi = m.group(1)
        target = m.group(2)
        issues.append((
            '【文言行路动作违规】',
            f"行 {line_idx}: 发现中式话本文言动词 '{verb_zhi}{target}'（JRPG现代日轻建议改为 '走到/快步来到/驶到……'） -> {line.strip()[:60]}"
        ))

    # 4. 检测中式文言介词倒装“动词+于+宾语”（如端坐于、正襟危坐于、垂于、贯注于、跪伏于、立于、伏于、卧于、倚于）
    VERB_YU_PATTERN = re.compile(r'(?<![一-龥])(端坐|正襟危坐|垂|贯注|跪伏|立|伏|卧|倚)于([一-龥]{1,10})')
    WHITELIST_YU = {'位于', '处于', '对立于', '独立于', '自立于', '立于不败之地', '忠于', '勇于', '敢于', '善于', '急于', '乐于', '忙于', '致力于', '终于', '关于', '对于', '至于', '由于', '鉴于', '基于', '等于', '类似于', '属于', '见于'}
    for m in VERB_YU_PATTERN.finditer(line):
        v_yu = m.group(1) + '于'
        target = m.group(2)
        if v_yu in WHITELIST_YU or m.group(0) in WHITELIST_YU:
            continue
        issues.append((
            '【文言介词倒装违规】',
            f"行 {line_idx}: 发现文言介词倒装 '{m.group(0)}'（JRPG现代日轻建议改为 '在……[动词]'，如'站在门边/握剑垂在身侧/坐在……'） -> {line.strip()[:60]}"
        ))

    return issues

def audit_file_inversions(filepath):
    """
    扫描单个文件中的文言倒装问题
    """
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f, 1):
                line_issues = check_line_inversions(line, idx)
                issues.extend(line_issues)
    except Exception as e:
        issues.append(('【读取异常】', f"无法读取文件: {e}"))
    return os.path.relpath(filepath), issues

def scan_all_inversions(target_dirs=None):
    """
    扫描全库第二部目标文件
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if target_dirs is None:
        target_dirs = [
            os.path.join(base_dir, 'docs2'),
            os.path.join(base_dir, '方案', '第二部')
        ]

    target_files = []
    for d in target_dirs:
        if os.path.exists(d):
            for ext in ('*.md', '*.TXT', '*.txt'):
                for p in glob.glob(os.path.join(d, '**', ext), recursive=True):
                    if '已执行' in p or 'NSFW' in p:
                        continue
                    target_files.append(p)

    target_files = sorted(list(set(target_files)))
    total = len(target_files)
    issues_count = 0
    problem_files = []

    for fpath in target_files:
        rpath, issues = audit_file_inversions(fpath)
        if issues:
            issues_count += len(issues)
            problem_files.append((rpath, issues))

    print(f"\n[文言倒装检测雷达] 共检查 {total} 个文件，发现 {issues_count} 处文言倒装病灶。")
    if not problem_files:
        print("[OK] 纯度 100%！未发现任何‘裹以/覆以/饰以’等文言介词倒装或‘之以’古风句式！")
        return 0
    else:
        print("\n" + "=" * 60)
        print(" 发现以下文件存在文言倒装句式，请改为现代白话：")
        print("=" * 60)
        for rpath, issues in problem_files:
            print(f"\n文件: {rpath}")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="文言倒装句式（动词+以）检测雷达")
    parser.add_argument('--file', type=str, help="扫描指定文件")
    args = parser.parse_args()

    if args.file:
        rpath, issues = audit_file_inversions(os.path.abspath(args.file))
        if issues:
            print(f"文件 {rpath} 发现 {len(issues)} 处文言倒装：")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
            sys.exit(1)
        else:
            print(f"文件 {rpath} 纯度 100%，无文言倒装。")
            sys.exit(0)
    else:
        sys.exit(scan_all_inversions())
