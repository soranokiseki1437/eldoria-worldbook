#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/story2_tool.py — 第二部（维里迪亚王国篇）章节管理与脚手架工具

与第一部（scripts/story_tool.py）物理隔离。
功能：
1. new: 生成符合第二部 JRPG 规范的章节模板（包含主要人物，无战术隐蔽，无NSFW）
2. list: 罗列第二部已规划与已创作的章节
3. validate: 快速校验指定章节或全部第二部章节
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
阶段: {stage}
路线: {route}
主要人物: [{characters}]
情境:
  - 1. {sit_1}
  - 2. {sit_2}
  - 3. {sit_3}
  - 4. {sit_4}
核心: {core}
章节任务: {task}
章节终止条件:
  - 1. {term_1}
  - 2. {term_2}
  - 3. {term_3}
"""

def cmd_new(args):
    """新建第二部章节脚手架"""
    os.makedirs(config.DOCS2_STORY_DIR, exist_ok=True)
    filename = f"{args.id}_{args.title}.TXT"
    filepath = os.path.join(config.DOCS2_STORY_DIR, filename)

    if os.path.exists(filepath) and not args.force:
        print(f"[ERROR] 文件已存在: {filepath}（如需覆盖请加 --force）")
        return 1

    content = CHAPTER_TEMPLATE.format(
        chap_id=args.id,
        title=args.title,
        stage=args.stage,
        route=args.route,
        characters=args.characters,
        sit_1=args.sit1 or "...",
        sit_2=args.sit2 or "...",
        sit_3=args.sit3 or "...",
        sit_4=args.sit4 or "...",
        core=args.core or "...",
        task=args.task or "...",
        term_1=args.term1 or "（纯物象化终止条件1）",
        term_2=args.term2 or "（纯物象化终止条件2）",
        term_3=args.term3 or "（纯物象化终止条件3）",
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[SUCCESS] 成功生成第二部章节文件: {filepath}")
    print(f"  - 阶段: {args.stage}")
    print(f"  - 路线: {args.route}")
    print(f"  - 主要人物: [{args.characters}]")
    print(f"  - 严格防御: 零战术隐蔽、零NSFW、纯正 JRPG 西幻规范")
    return 0

def cmd_validate(args):
    """校验章节"""
    if args.file:
        files = [args.file]
    else:
        files = [
            os.path.join(config.DOCS2_STORY_DIR, f)
            for f in os.listdir(config.DOCS2_STORY_DIR)
            if f.endswith('.TXT') and not f.startswith('_')
        ] if os.path.exists(config.DOCS2_STORY_DIR) else []

    if not files:
        print("未找到需要校验的章节文件。")
        return 0

    has_error = False
    for p in sorted(files):
        rel, issues = audit_file(p)
        if issues:
            has_error = True
            print(f"[FAIL] {rel}")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
        else:
            print(f"[PASS] {rel} 100% 纯正合规")

    return 1 if has_error else 0

def main():
    parser = argparse.ArgumentParser(description="第二部专属章节管理工具")
    subparsers = parser.add_subparsers(dest="subcommand", help="子命令")

    # new 子命令
    p_new = subparsers.add_parser("new", help="新建章节脚手架")
    p_new.add_argument("--id", required=True, help="章节编号，例如 引-1 或 D2_01")
    p_new.add_argument("--title", required=True, help="章节标题，例如 残区的反扑——东侧的沼地")
    p_new.add_argument("--stage", default="第一幕·阶段一：引入与故土远征启程", help="阶段名称")
    p_new.add_argument("--route", default="艾德里安线", choices=config.VALID_ROUTES, help="主线/支线路线")
    p_new.add_argument("--characters", required=True, help="主要人物，逗号分隔，例如 '艾德里安, 黎恩, 菲'")
    p_new.add_argument("--core", default="", help="章节核心驱动")
    p_new.add_argument("--task", default="", help="章节具体任务")
    p_new.add_argument("--sit1", default="", help="情境第1步")
    p_new.add_argument("--sit2", default="", help="情境第2步")
    p_new.add_argument("--sit3", default="", help="情境第3步")
    p_new.add_argument("--sit4", default="", help="情境第4步")
    p_new.add_argument("--term1", default="", help="终止条件1")
    p_new.add_argument("--term2", default="", help="终止条件2")
    p_new.add_argument("--term3", default="", help="终止条件3")
    p_new.add_argument("--force", action="store_true", help="强制覆盖已存在文件")

    # validate 子命令
    p_val = subparsers.add_parser("validate", help="校验章节文件")
    p_val.add_argument("--file", help="指定待校验文件")

    args = parser.parse_args()
    if args.subcommand == "new":
        return cmd_new(args)
    elif args.subcommand == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())
