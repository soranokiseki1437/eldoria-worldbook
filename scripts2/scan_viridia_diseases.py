#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/scan_viridia_diseases.py — 第二部（维里迪亚王国篇）专属文风、词汇与病灶雷达

与第一部（scripts/scan_narrative_diseases.py）物理隔离。
专门防御：
1. [古风/仙侠/修真黑名单]：碎银、官道、演兵场、路引、四合院、中军大帐、千斤闸、剑意、身法、划拳、品茶、烽火等。
2. [中式传统度量衡]：斤、两、尺、寸、丈、里（如“三寸”、“半尺”、“数十里”、“重达千斤”）。
3. [第一部隐秘/隐奸/NSFW残留污染]：战术隐蔽（用户明确要求拔除）、爱意值、隐秘事件、背德事件等。
4. [翻译腔长定语堆叠与括号英文]：如“高石围墙方庭合院式高级驿舍（Courtyard Coaching Inn）”。
5. [章节元数据字段规范]：主要人物字段必须存在，战术隐蔽严格禁止。
"""

import os
import sys
import glob
import re
import argparse

# 导入第二部配置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
try:
    import story2_config as config
except ImportError:
    from scripts2 import story2_config as config

# ═══════════════════════════════════════════════════════════
# 黑名单词库定义
# ═══════════════════════════════════════════════════════════

# 1. 古风/武侠/仙侠/东方修真黑名单
WUXIA_FORBIDDEN_WORDS = [
    '碎银', '碎银粒', '官道', '演兵场', '路引', '四合院', '中军大帐', '千斤闸',
    '千斤', '划拳', '品茶', '剑意', '身法', '烽火', '烽火台', '驿亭', '盘缠',
    '掌柜', '店小二', '客栈', '修真', '内力', '真气', '轻功', '暗度陈仓',
    '兵荒马乱', '江湖', '武林', '宗门', '演武场', '地宫', '打坐', '吐纳',
    '周天', '真元', '大能', '高人', '尊者', '仙躯', '神识', '洞府',
    '四肢百骸', '气海', '精关', '丹田', '灵气', '飞剑', '遁光', '储物袋'
]

# 2. 中式传统度量衡正则（允许“里格/公顷/公里/厘米/分贝”等，但严禁传统中国市制单位）
# 匹配：一尺、数尺、三寸、数十斤、数里、五里、千斤等
CHINESE_UNIT_PATTERN = re.compile(
    r'(?<![公公分厘纳毫百千])(?<![a-zA-Z0-9])'
    r'([一二三四五六七八九十百千万数几两半]+(斤|两|尺|寸|丈|里))'
    r'(?![米克分厘寸升格])'
)

# 3. 第一部 NSFW / 隐秘系统污染词
PART1_CONTAMINATION_WORDS = [
    '战术隐蔽',   # 用户明确要求第二部不要
    '爱意值',     # 第一部专属
    '隐秘事件',   # 第一部专属
    '背德事件',   # 第一部专属
    '落红', '肉棒', '蜜穴', '淫靡', '淫水', '浪叫', '肉刃', '牝穴', '娇喘'
]

# 4. 恶性翻译腔与括号英文堆叠正则（如：方庭合院式高级驿舍（Courtyard Coaching Inn））
TRANSLATIONESE_PATTERN = re.compile(r'[\u4e00-\u9fa5]{6,}（[A-Za-z\s]+）')

def is_blacklist_definition_line(line):
    """判断某一行是否属于黑名单、规则定义、替换表或版本日志"""
    stripped = line.strip()
    # 规则替换表格或带叉号的黑名单列举
    if stripped.startswith('|') and ('严禁' in stripped or '替换' in stripped or '红线' in stripped or '东方' in stripped or '古风' in stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in ['×', '* ×', '- ×', '× ', '【严禁', '严禁', '拔除', '清除']):
        return True
    if '词汇对照与置换规范表' in stripped or '红线词库' in stripped:
        return True
    return False

def audit_file(filepath):
    """审计单个文件的文风与规范问题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    text = "".join(lines)

    fname = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, config.PROJECT_DIR)
    findings = []

    is_character_card = 'docs2/character' in rel_path.replace('\\', '/')
    is_guide_or_plan = '方案/第二部' in rel_path.replace('\\', '/')
    is_index_file = fname.startswith('_')

    in_blacklist_table = False

    # 按行检查，精准定位并过滤黑名单定义行
    for line_idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # 检测表格状态
        if stripped.startswith('|'):
            if '严禁' in stripped or '替换' in stripped or '红线' in stripped or '黑名单' in stripped:
                in_blacklist_table = True
                continue
            if in_blacklist_table:
                # 处于黑名单对照表格内，跳过此行扫描
                continue
        else:
            in_blacklist_table = False

        if is_guide_or_plan:
            if any(stripped.startswith(p) for p in ['×', '* ×', '- ×', '× ', '【严禁', '严禁', '拔除', '清除']):
                continue
            if '词汇对照与置换规范表' in stripped or '红线词库' in stripped:
                continue

        # 1. 检查武侠/古风禁词
        for word in WUXIA_FORBIDDEN_WORDS:
            if word in line:
                if any(k in line for k in ['拔除', '清除', '严禁', '黑名单', '红线', '置换', '替换', '绝对禁止']):
                    continue
                findings.append(('【古风/武侠禁词】', f"行 {line_idx}: 发现 '{word}' -> {line.strip()[:60]}"))

        # 2. 检查传统中式度量衡
        for m in CHINESE_UNIT_PATTERN.finditer(line):
            unit_str = m.group(1)
            # 排除常用非度量与公制词汇
            if any(ok in line for ok in ['心里', '屋里', '手里', '怀里', '眼里', '公里', '里格', '海里', '拔除', '清除', '严禁']):
                continue
            findings.append(('【中式度量衡】', f"行 {line_idx}: 发现 '{unit_str}' -> {line.strip()[:60]}"))

        # 3. 检查第一部字段/内容污染（角色卡保留自身生理设定，但在其他卡片、章节、方案中严格禁止）
        for pw in PART1_CONTAMINATION_WORDS:
            if pw in line:
                if is_character_card and pw in ['蜜穴', '娇喘']:
                    continue
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范']):
                    continue
                findings.append(('【第一部字段/内容污染】', f"行 {line_idx}: 发现 '{pw}' -> {line.strip()[:60]}"))

    # 4. 章节文件专属检查（针对 docs2/story/ 下的非索引 TXT）
    if 'story' in filepath.lower() and filepath.endswith('.TXT') and not is_index_file:
        if '主要人物:' not in text and '主要人物：' not in text:
            findings.append(('【缺少主要人物字段】', "第二部章节必须显式声明 '主要人物: [角色1, 角色2]'"))
        if '战术隐蔽' in text:
            findings.append(('【违规字段】', "第二部章节严禁包含 '战术隐蔽' 字段"))

    return rel_path, findings

def scan_all(include_archive=False):
    """全量扫描第二部方案库与设定库"""
    print("=" * 60)
    print(" 维里迪亚王国篇（第二部）专属文风与病灶透视雷达")
    print(" 监控目标：docs2/ 设定库、方案/第二部/ 方案库、docs2/story/ 章节库")
    print("=" * 60)

    target_files = []

    # 1. docs2/ 所有的 TXT 文件
    if os.path.exists(config.DOCS2_DIR):
        target_files.extend(glob.glob(os.path.join(config.DOCS2_DIR, '**', '*.TXT'), recursive=True))

    # 2. 方案/第二部/ 所有的 MD 文件（默认排除历史归档 已执行/）
    if os.path.exists(config.SCHEME2_DIR):
        all_mds = glob.glob(os.path.join(config.SCHEME2_DIR, '**', '*.md'), recursive=True)
        for md_path in all_mds:
            if not include_archive and '已执行' in md_path:
                continue
            target_files.append(md_path)

    total = len(target_files)
    issues_count = 0
    problem_files = []

    for fpath in sorted(target_files):
        rel_path, issues = audit_file(fpath)
        if issues:
            issues_count += len(issues)
            problem_files.append((rel_path, issues))

    print(f"\n扫描完成：共检查 {total} 个文件，发现 {issues_count} 处异常。")

    if not problem_files:
        print("\n[OK] 恭喜！第二部所有活跃设定与方案文件纯度 100%，无任何古风、中式度量衡或第一部字段污染！")
        return 0
    else:
        print("\n" + "!" * 60)
        print(" 发现以下文件存在文风或字段病灶，需立即修复：")
        print("!" * 60)
        for rpath, issues in problem_files:
            print(f"\n文件: {rpath}")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="第二部专属文风与病灶透视雷达")
    parser.add_argument('--file', type=str, help="扫描指定文件")
    args = parser.parse_args()

    if args.file:
        rpath, issues = audit_file(os.path.abspath(args.file))
        if issues:
            print(f"文件 {rpath} 发现 {len(issues)} 处问题：")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
            sys.exit(1)
        else:
            print(f"文件 {rpath} 纯度 100%，无违规项。")
            sys.exit(0)
    else:
        sys.exit(scan_all())
