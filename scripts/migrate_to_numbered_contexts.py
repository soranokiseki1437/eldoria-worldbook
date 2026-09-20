#!/usr/bin/env python3
"""
migrate_to_numbered_contexts.py — 全库标号情境慢推体系自动化迁移脚本

功能:
  1. 为章节TXT的每个情境条目添加数字编号（- 1. xxx, - 2. xxx...）；
  2. 原情境文本100%保真，不做任何字词与标点改动；
  3. 智能提取原「章节终止条件」中的「3.」收束物象文本，去重后作为最后一条情境（第N条）追加；
  4. 新增「总情境数: {N}」字段；
  5. 彻底删除「章节任务」与「章节终止条件」字段；
  6. 支持 --target <id_or_path> 单文件试跑验证与 --all 全量执行。

用法:
  python scripts/migrate_to_numbered_contexts.py --target 306 --dry-run
  python scripts/migrate_to_numbered_contexts.py --target 306
  python scripts/migrate_to_numbered_contexts.py --all
"""

import os
import re
import sys
import argparse
from typing import Dict, List, Tuple, Optional

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')


def extract_condition3(end_cond_text: str) -> str:
    """从章节终止条件文本中提取条件3的内容"""
    if not end_cond_text:
        return ""
    # 匹配 3. 或 3、 或 3: 开头的内容一直到结尾
    m = re.search(r'(?:^|\n)\s*3[.\s、:：]\s*(.+?)(?=\n\s*\d+[.\s、:：]|\Z)', end_cond_text, re.DOTALL)
    if m:
        c3 = m.group(1).strip()
        # 清理内部多余换行，保持为单段叙述
        c3 = re.sub(r'\s*\n\s*', ' ', c3).strip()
        return c3
    return ""


def parse_chapter_txt(content: str) -> Tuple[Dict[str, any], List[str], str]:
    """
    解析章节TXT内容。
    返回: (fields_dict, context_items, cond3_text)
    fields_dict 存储各顶层字段。
    context_items 存储情境列表（去除了前导 '- '）。
    """
    lines = content.splitlines()
    fields: Dict[str, any] = {}
    context_items: List[str] = []
    
    # 顶层已知字段名
    top_keys = [
        'ID', '名称', 'NSFW', '性行为等级', '阶段', '第三者',
        '黎恩知情', '占有欲确认', '好感影响', '总情境数', '情境', '核心',
        '章节任务', '章节终止条件'
    ]
    key_pattern = re.compile(r'^([A-Za-z\u4e00-\u9fa5]+)[：:]\s*(.*)$')
    
    current_key = None
    current_val_lines = []
    
    def save_current():
        nonlocal current_key, current_val_lines
        if current_key:
            val_str = '\n'.join(current_val_lines).strip()
            fields[current_key] = val_str
            current_key = None
            current_val_lines = []

    in_context = False
    context_lines = []

    for line in lines:
        stripped = line.strip()
        
        # 检查是否匹配新的顶级字段
        m = key_pattern.match(line)
        if m and m.group(1) in top_keys:
            if in_context:
                in_context = False
            save_current()
            current_key = m.group(1)
            val_part = m.group(2)
            if current_key == '情境':
                in_context = True
                context_lines = []
                if val_part:
                    context_lines.append(val_part)
            else:
                current_val_lines = [val_part] if val_part else []
        else:
            if in_context:
                context_lines.append(line)
            elif current_key:
                current_val_lines.append(line)

    save_current()

    # 解析 context_lines 得到 context_items
    curr_item = []
    for cl in context_lines:
        scl = cl.strip()
        if not scl:
            continue
        # 匹配列表项开头：形如 - xxx 或 - 1. xxx
        if scl.startswith('-') or scl.startswith('•') or scl.startswith('*'):
            if curr_item:
                context_items.append(' '.join(curr_item).strip())
                curr_item = []
            # 去掉前置 bullet 符号及可能存在的旧编号
            item_body = re.sub(r'^[-•*]\s*(?:\d+[.\s、:：]\s*)?', '', scl)
            curr_item.append(item_body)
        else:
            if curr_item:
                curr_item.append(scl)
            else:
                # 兼容未以 - 开头的情况
                item_body = re.sub(r'^(?:\d+[.\s、:：]\s*)?', '', scl)
                curr_item.append(item_body)
    if curr_item:
        context_items.append(' '.join(curr_item).strip())

    # 提取条件3
    end_cond = fields.get('章节终止条件', '')
    cond3 = extract_condition3(end_cond)

    return fields, context_items, cond3


def build_migrated_txt(fields: Dict[str, any], context_items: List[str], cond3: str) -> str:
    """根据提取结果生成全新的标准章节 TXT"""
    # 检查条件3是否需要追加
    final_items = list(context_items)
    if cond3:
        # 检查最后一条是否已经包含条件3内容
        last_item = final_items[-1] if final_items else ""
        # 比较相似度或包含性：如果条件3的主要短语不在最后一条，则作为独立收束追加
        # 取条件3前15个字符或去标点比对
        cond3_sample = re.sub(r'[，。！？；\s]', '', cond3)[:15]
        last_sample = re.sub(r'[，。！？；\s]', '', last_item)
        if cond3_sample and cond3_sample not in last_sample:
            final_items.append(cond3)

    total_n = len(final_items)

    out = []
    
    # 1. ID
    out.append(f"ID: {fields.get('ID', '')}")
    out.append("")
    # 2. 名称
    out.append(f"名称: {fields.get('名称', '')}")
    out.append("")
    # 3. NSFW
    out.append(f"NSFW: {fields.get('NSFW', '否')}")
    out.append("")
    # 4. 性行为等级
    sex_lvl = fields.get('性行为等级', '')
    out.append(f"性行为等级: {sex_lvl}".rstrip())
    out.append("")
    # 5. 阶段
    out.append(f"阶段: {fields.get('阶段', '')}")
    out.append("")
    # 6. 第三者
    third = fields.get('第三者', '')
    out.append(f"第三者: {third}".rstrip())
    out.append("")
    # 7. 黎恩知情
    lean = fields.get('黎恩知情', '')
    out.append(f"黎恩知情: {lean}".rstrip())
    out.append("")
    # 8. 占有欲确认（有内容则输出）
    possession = fields.get('占有欲确认', '')
    if possession:
        out.append("占有欲确认:")
        for pline in possession.splitlines():
            pline_s = pline.strip()
            if pline_s:
                if not pline_s.startswith('-'):
                    out.append(f"  - {pline_s}")
                else:
                    out.append(f"  {pline_s}")
        out.append("")
    else:
        out.append("占有欲确认:")
        out.append("")

    # 9. 好感影响
    favor = fields.get('好感影响', '')
    if favor:
        out.append("好感影响:")
        for fline in favor.splitlines():
            fline_s = fline.strip()
            if fline_s:
                if not fline_s.startswith('-'):
                    out.append(f"  - {fline_s}")
                else:
                    out.append(f"  {fline_s}")
        out.append("")
    else:
        out.append("好感影响:")
        out.append("")

    is_free = '自由探索' in fields.get('名称', '') or fields.get('总情境数', '') == '自由探索章节'

    # 10. 总情境数
    if is_free:
        out.append("总情境数: 自由探索章节")
    else:
        out.append(f"总情境数: {total_n}")
    out.append("")

    # 11. 情境（带标号或自由探索纯列表）
    out.append("情境:")
    for idx, item in enumerate(final_items, 1):
        # 100% 保真 item 文本，不修改任何字词
        if is_free:
            out.append(f"  - {item}")
        else:
            out.append(f"  - {idx}. {item}")
    out.append("")

    # 12. 核心
    core = fields.get('核心', '')
    out.append(f"核心: {core}")

    return '\n'.join(out) + '\n'


def find_chapter_file(target: str) -> Optional[str]:
    """根据ID或文件名或路径定位单个章节文件"""
    if os.path.isfile(target):
        return os.path.abspath(target)
    
    # 纯数字ID或带前缀
    target_clean = re.sub(r'^[^\d]*', '', target)
    target_clean = re.sub(r'\D.*$', '', target_clean) # 仅取开头的数字
    
    for root, _, files in os.walk(STORY_DIR):
        for f in files:
            if not f.upper().endswith('.TXT'):
                continue
            if f == target or f == f"{target}.TXT":
                return os.path.join(root, f)
            m = re.match(r'^(\d+)[：:]', f)
            if m and target_clean and int(m.group(1)) == int(target_clean):
                return os.path.join(root, f)
    return None


def get_all_chapter_files() -> List[str]:
    """获取全库所有章节TXT文件列表，按ID升序排序"""
    results = []
    for root, _, files in os.walk(STORY_DIR):
        # 排除非阶段目录
        for f in files:
            if not f.upper().endswith('.TXT'):
                continue
            if f.startswith('_'):
                continue
            fp = os.path.join(root, f)
            results.append(fp)
    
    def sort_key(p):
        fname = os.path.basename(p)
        m = re.match(r'^(\d+)', fname)
        return int(m.group(1)) if m else 99999
    
    results.sort(key=sort_key)
    return results


def main():
    parser = argparse.ArgumentParser(description="全库标号情境慢推体系自动化迁移脚本")
    parser.add_argument('--target', type=str, help="指定测试的章节ID或文件路径（如 306 或 001）")
    parser.add_argument('--all', action='store_true', help="全量处理所有章节文件")
    parser.add_argument('--dry-run', action='store_true', help="只打印结果，不写回文件")
    args = parser.parse_args()

    if not args.target and not args.all:
        parser.print_help()
        print("\n请指定 --target <ID> 进行小规模测试，或 --all 执行全库迁移。")
        sys.exit(1)

    targets = []
    if args.target:
        fpath = find_chapter_file(args.target)
        if not fpath:
            print(f"❌ 未找到章节文件: {args.target}")
            sys.exit(1)
        targets.append(fpath)
    elif args.all:
        targets = get_all_chapter_files()
        print(f"📦 共检索到 {len(targets)} 个章节文件待处理。")

    success_count = 0
    for fpath in targets:
        rel_path = os.path.relpath(fpath, PROJECT_DIR)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()

            fields, context_items, cond3 = parse_chapter_txt(content)
            if not context_items:
                print(f"⚠️ 跳过（未解析到情境条目）: {rel_path}")
                continue

            new_content = build_migrated_txt(fields, context_items, cond3)

            if args.dry_run:
                print(f"\n{'='*60}")
                print(f"📄 [DRY-RUN] {rel_path}")
                print(f"{'='*60}")
                print(new_content)
            else:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ 已成功迁移: {rel_path} (总情境数: {len(context_items) + (1 if cond3 and cond3[:15] not in context_items[-1] else 0)})")
            
            success_count += 1
        except Exception as e:
            print(f"❌ 处理失败: {rel_path} — 错误: {e}")

    print(f"\n🎉 处理完毕！成功: {success_count}/{len(targets)} 个文件。")


if __name__ == '__main__':
    main()
