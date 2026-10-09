#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/story2_tool.py — 第二部（维里迪亚王国篇）章节管理与脚手架工具

与第一部（scripts/story_tool.py）物理隔离。
功能：
1. new: 生成符合第二部 JRPG 规范的章节模板（标准 9 字段白名单）
2. list: 罗列第二部已规划与已创作的章节
3. validate/lint: 快速校验指定章节或全部第二部章节
"""

import os
import sys
import argparse
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
try:
    import story2_config as config
    from scan_viridia_diseases import audit_file
except ImportError:
    from scripts2 import story2_config as config
    from scripts2.scan_viridia_diseases import audit_file

CHAPTER_TEMPLATE = """ID: {chap_id}
名称: {title}
NSFW: {nsfw}
性行为等级: {sex_level}
黎恩知情: {rean_aware}
主要人物: {characters}
总情境数: {total_sits}
情境:
{situations}
核心: {core}
"""

def cmd_new(args):
    """新建第二部章节脚手架"""
    target_dir = os.path.join(config.DOCS2_STORY_DIR, args.act) if getattr(args, 'act', None) else config.DOCS2_STORY_DIR
    os.makedirs(target_dir, exist_ok=True)
    filename = f"{args.id}：{args.title}.TXT"
    filepath = os.path.join(target_dir, filename)

    if os.path.exists(filepath) and not args.force:
        print(f"[ERROR] 文件已存在: {filepath}（如需覆盖请加 --force）")
        return 1

    sits = []
    if args.situations:
        for idx, sit in enumerate(args.situations, 1):
            sits.append(f"  - {idx}. {sit}")
    else:
        sits = [
            "  - 1. ...",
            "  - 2. ...",
            "  - 3. ...",
            "  - 4. ...",
        ]

    content = CHAPTER_TEMPLATE.format(
        chap_id=args.id,
        title=args.title,
        nsfw="是" if getattr(args, 'nsfw', False) else "否",
        sex_level=getattr(args, 'sex_level', '') or '',
        rean_aware=getattr(args, 'rean_aware', '') or '',
        characters=args.characters,
        total_sits=len(sits),
        situations="\n".join(sits),
        core=args.core or "...",
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[SUCCESS] 成功生成第二部章节文件: {filepath}")
    print(f"  - 幕次: {args.act}")
    print(f"  - 主要人物: {args.characters}")
    print(f"  - 规范保障: 9 字段白名单，纯正 JRPG 西幻文风")
    return 0

def check_chapter_schema(filepath):
    """校验单个章节文件的 Schema 规范"""
    issues = []
    fname = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 必填字段
    for req in config.REQUIRED_CHAPTER_FIELDS:
        pattern = rf'^{req}[:：]'
        if not re.search(pattern, content, re.M):
            issues.append(('【缺少必需字段】', f"缺少字段 '{req}'"))

    # 2. 禁用字段
    for fbd in config.FORBIDDEN_CHAPTER_FIELDS:
        pattern = rf'^{fbd}[:：]'
        if re.search(pattern, content, re.M):
            issues.append(('【违规遗留字段】', f"存在禁用字段 '{fbd}'"))

    # 3. 主要人物非空
    chars_m = re.search(r'^主要人物[:：]\s*(.+)', content, re.M)
    if chars_m:
        chars_val = chars_m.group(1).strip()
        if not chars_val or chars_val in ['[]', '无']:
            issues.append(('【主要人物异常】', "'主要人物' 字段不可为空"))

    # 4. 标题规范与假玄学术语拦截
    title_m = re.search(r'^名称[:：]\s*(.+)', content, re.M)
    if title_m:
        title_val = title_m.group(1).strip()
        if '——' not in title_val:
            issues.append(('【标题格式异常】', "标题必须使用 '前半段——后半段' 双半段破折号结构"))
        else:
            xuanxue_words = ['敕印', '探阵', '微澜', '法印', '宝印', '战端', '气劲', '剑意']
            for xw in xuanxue_words:
                if xw in title_val:
                    issues.append(('【标题修真玄学拦截】', f"标题中包含仙侠玄学术语 '{xw}'，请使用具象 JRPG 西幻物象与行动！"))

    # 5. 对白覆盖率校验（彻底根除全员哑剧流水账）
    dialogue_matches = re.findall(r'[“"][^“”"]{2,}[”"]', content)
    sit_lines = [line for line in content.splitlines() if re.match(r'^\s*-\s*\d+[\.、]', line)]
    if len(sit_lines) >= 4 and len(dialogue_matches) == 0:
        issues.append(('【严重文风失准：全员哑剧】', "章节情境中完全缺失角色现场直接对白（“...”），严禁无声流水账与提线木偶！每章至少需有 2 条以上情境包含生动角色台词"))

    # 6. 公文汇报腔与间接转述拦截
    bureaucratic_words = ['平静说出', '明确敲定', '逐项核对', '逐项核验', '言明', '坦言自己', '达成共识表示', '正式敲定']
    for bw in bureaucratic_words:
        if bw in content:
            issues.append(('【公文汇报腔拦截】', f"检测到间接引语汇报词 '{bw}'，严禁会议总结式叙述，请直接使用角色现场直接对白与微动作！"))

    return issues

def cmd_validate(args):
    """校验章节（包含文风雷达与 Schema 规范）"""
    if args.file:
        files = [args.file]
    else:
        files = [
            os.path.join(root, f)
            for root, _, fs in os.walk(config.DOCS2_STORY_DIR)
            for f in fs
            if f.endswith('.TXT') and not f.startswith('_')
        ] if os.path.exists(config.DOCS2_STORY_DIR) else []

    if not files:
        print("未找到需要校验的章节文件。")
        return 0

    has_error = False
    for p in sorted(files):
        rel, issues = audit_file(p)
        schema_issues = check_chapter_schema(p)
        all_issues = issues + schema_issues
        if all_issues:
            has_error = True
            print(f"[FAIL] {rel}")
            for itype, idesc in all_issues:
                print(f"  - {itype} {idesc}")
        else:
            print(f"[PASS] {rel} 100% 纯正合规 (文风雷达0违规，Schema9字段完全匹配)")

    return 1 if has_error else 0

def main():
    parser = argparse.ArgumentParser(description="第二部专属章节管理工具")
    subparsers = parser.add_subparsers(dest="subcommand", help="子命令")

    # new 子命令
    p_new = subparsers.add_parser("new", help="新建章节脚手架")
    p_new.add_argument("--id", required=True, help="章节编号，例如 001")
    p_new.add_argument("--title", required=True, help="章节标题，例如 泥沼残兽——青石初芽")
    p_new.add_argument("--act", default="第一幕", choices=config.ACTS, help="所属幕次")
    p_new.add_argument("--nsfw", action="store_true", help="是否为NSFW章节")
    p_new.add_argument("--sex-level", default="", help="性行为等级（0-10）")
    p_new.add_argument("--rean-aware", default="", help="黎恩知情状态描述")
    p_new.add_argument("--characters", required=True, help="主要人物，逗号分隔，例如 '雷恩, 菲, 黎恩, 菲娜'")
    p_new.add_argument("--core", default="", help="章节核心意图与戏剧功能")
    p_new.add_argument("--situations", nargs="+", help="情境列表文本")
    p_new.add_argument("--force", action="store_true", help="强制覆盖已存在文件")

    # validate 子命令
    p_val = subparsers.add_parser("validate", help="校验章节文件")
    p_val.add_argument("--file", help="指定待校验文件")

    # lint 子命令（validate 的等价别名，与 _WORKFLOW.md 对齐）
    p_lint = subparsers.add_parser("lint", help="校验章节文件（validate别名）")
    p_lint.add_argument("--file", help="指定待校验文件")

    args = parser.parse_args()
    if args.subcommand == "new":
        return cmd_new(args)
    elif args.subcommand in ("validate", "lint"):
        return cmd_validate(args)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())
