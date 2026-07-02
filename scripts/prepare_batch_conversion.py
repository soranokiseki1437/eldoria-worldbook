#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_batch_conversion.py — 章节终止条件转换准备脚本

扫描全部章节TXT，提取上下文信息，生成转换清单和分批prompt文件。

用法：
    python scripts/prepare_batch_conversion.py              # 生成完整清单
    python scripts/prepare_batch_conversion.py --batches N  # 生成清单 + 分N批prompt
"""

import json
import os
import re
import sys
from collections import OrderedDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')

# ─── TXT解析 ───────────────────────────────────────────

def parse_txt(filepath):
    """解析单个章节TXT文件，返回dict"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {}
    current_key = None
    current_value = []

    for line in lines:
        if not line.strip():
            continue
        if line.strip().startswith('#'):
            continue

        m = re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', line)
        if m and not line.lstrip().startswith(('-', 'A.', 'B.', 'C.')):
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_value = [val] if val else []
        else:
            current_value.append(line.rstrip('\n'))

    if current_key:
        data[current_key] = '\n'.join(current_value).strip()

    return data


def classify_chapter(data):
    """分类章节难度：simple / medium / complex"""
    nsfw = data.get('NSFW', '').strip()
    third = data.get('第三者', '').strip()
    end_cond = data.get('章节终止条件', '')

    # 统计终止条件条数
    cond_count = len([c for c in end_cond.split('\n') if c.strip()])

    if nsfw != '是':
        return 'simple'  # SFW章节
    elif third and cond_count >= 4:
        return 'complex'  # NTRS多角色长章节
    elif third:
        return 'complex'  # NTRS章节
    elif cond_count >= 4:
        return 'medium'   # 较长纯爱章节
    else:
        return 'medium'   # 标准NSFW纯爱章节


def scan_all_chapters():
    """扫描全部章节，返回列表"""
    chapters = []

    for stage_dir in sorted(os.listdir(STORY_DIR)):
        stage_path = os.path.join(STORY_DIR, stage_dir)
        if not os.path.isdir(stage_path):
            continue

        for fname in sorted(os.listdir(stage_path)):
            if not fname.upper().endswith('.TXT'):
                continue
            if fname.startswith('_'):
                continue

            fp = os.path.join(stage_path, fname)
            data = parse_txt(fp)

            ch_id = data.get('ID', '')
            if not ch_id:
                continue

            chapters.append({
                'id': ch_id,
                'title': data.get('名称', ''),
                'filepath': fp,
                'nsfw': data.get('NSFW', '') == '是',
                'stage': data.get('阶段', ''),
                'third_party': data.get('第三者', ''),
                'difficulty': classify_chapter(data),
                'context': {
                    'situation': data.get('情境', ''),
                    'core': data.get('核心', ''),
                    'mission': data.get('章节任务', ''),
                    'possessiveness': data.get('占有欲确认', ''),
                },
                'old_conditions': data.get('章节终止条件', ''),
            })

    return chapters


def build_conversion_prompt(chapter):
    """为单个章节构建转换prompt段落"""
    ctx = chapter['context']
    lines = []
    lines.append(f"## ID: {chapter['id']}")
    lines.append(f"标题: {chapter['title']}")
    lines.append(f"NSFW: {'是' if chapter['nsfw'] else '否'} | 阶段: {chapter['stage']}")
    if chapter['third_party']:
        lines.append(f"第三者: {chapter['third_party']}")

    lines.append("")
    lines.append("【情境】:")
    lines.append(ctx['situation'] if ctx['situation'] else '(无)')
    lines.append("")
    lines.append("【核心】:")
    lines.append(ctx['core'] if ctx['core'] else '(无)')
    lines.append("")
    lines.append("【章节任务】:")
    lines.append(ctx['mission'] if ctx['mission'] else '(无)')
    if ctx['possessiveness']:
        lines.append("")
        lines.append("【占有欲确认】:")
        lines.append(ctx['possessiveness'])
    lines.append("")
    lines.append("【旧·章节终止条件】:")
    lines.append(chapter['old_conditions'] if chapter['old_conditions'] else '(无)')
    lines.append("")

    return '\n'.join(lines)


def main():
    batches = None
    if '--batches' in sys.argv:
        try:
            idx = sys.argv.index('--batches')
            batches = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print("用法: --batches N (N为分批数量)")
            sys.exit(1)

    print("扫描章节TXT文件...")
    chapters = scan_all_chapters()
    print(f"  共 {len(chapters)} 章")

    # 统计
    simple = [c for c in chapters if c['difficulty'] == 'simple']
    medium = [c for c in chapters if c['difficulty'] == 'medium']
    complex_c = [c for c in chapters if c['difficulty'] == 'complex']
    print(f"  简单(SFW): {len(simple)} | 中等(NSFW纯爱): {len(medium)} | 复杂(NTRS): {len(complex_c)}")

    # 输出完整清单
    ensure_dir(OUTPUT_DIR)
    manifest_path = os.path.join(OUTPUT_DIR, '_conversion_manifest.json')
    manifest = {
        'total': len(chapters),
        'stats': {
            'simple': len(simple),
            'medium': len(medium),
            'complex': len(complex_c),
        },
        'chapters': chapters,
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n清单已保存: {manifest_path}")

    # 输出进度追踪文件
    progress_path = os.path.join(OUTPUT_DIR, '_conversion_progress.json')
    progress = {
        'total': len(chapters),
        'completed': [],
        'failed': [],
        'last_updated': '',
    }
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    print(f"进度文件已初始化: {progress_path}")

    # 分批输出prompt文件
    if batches:
        batch_dir = os.path.join(OUTPUT_DIR, '_conversion_batches')
        ensure_dir(batch_dir)

        # 交错排列：每批混合简单/中等/复杂，避免某批全是复杂章
        mixed = simple + medium + complex_c
        batch_size = (len(mixed) + batches - 1) // batches

        for i in range(batches):
            start = i * batch_size
            end = min(start + batch_size, len(mixed))
            batch_chapters = mixed[start:end]

            batch_lines = []
            batch_lines.append("你将收到一批章节的信息。对每个章节，重写「章节终止条件」的三句话，使其在内涵上形成「前置→核心→余韵」三段：")
            batch_lines.append("")
            batch_lines.append("条件1（前置）：核心事件开始前必须建立的环境、氛围、日常互动或角色心理状态。不含性行为动作。")
            batch_lines.append("条件2（核心）：章节叙事必经节点，从触发到高潮的完整弧线。一句话概括。")
            batch_lines.append("条件3（余韵）：事后情感沉淀 + 时间推进或场景切换的信号。不含新剧情触发。")
            batch_lines.append("")
            batch_lines.append("规则：")
            batch_lines.append("- 每条一个精简肯定陈述句，保持原文用词风格和叙事基调")
            batch_lines.append("- 禁止破折号(——)、否定句式(不/没/非/不是…是…)、比喻、话语/直接引语")
            batch_lines.append("- 条件1从「情境」的前几条提取日常/环境元素，不含性行为动作")
            batch_lines.append("- 条件2从原「章节终止条件」提取核心叙事节点，一条完整弧线")
            batch_lines.append("- 条件3从「核心」推导情感落点，加入时间/场景推进信号")
            batch_lines.append("")
            batch_lines.append("输出格式（每个章节严格按此格式）：")
            batch_lines.append("## ID: {id}")
            batch_lines.append("章节终止条件: 1.{前置一句话}")
            batch_lines.append("2.{核心一句话}")
            batch_lines.append("3.{余韵一句话}")
            batch_lines.append("---")
            batch_lines.append("")
            batch_lines.append(f"=== 第{i+1}批 (共{len(batch_chapters)}章) ===\n")

            for ch in batch_chapters:
                batch_lines.append(build_conversion_prompt(ch))
                batch_lines.append("---\n")

            batch_path = os.path.join(batch_dir, f'batch_{i+1:03d}.txt')
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(batch_lines))
            print(f"  Batch {i+1}: {batch_path} ({len(batch_chapters)}章)")

        print(f"\n分批文件已输出到: {batch_dir}")
        print("用法：将每个batch文件的内容发送给LLM，获取转换结果后运行 apply_batch_conversion.py")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    main()
