#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_batch_conversion.py — 将LLM转换结果写回章节TXT文件

用法：
    python scripts/apply_batch_conversion.py <result_file>

    result_file: LLM返回的转换结果文本文件。
    格式要求：每个章节以 "## ID: {id}" 开头，随后是 "章节终止条件: 1....\n2....\n3...."，以 "---" 结尾。

也支持直接传入包含多个章节结果的目录：
    python scripts/apply_batch_conversion.py --dir <results_dir>

安全措施：
    - 写回前先备份原始TXT到 backup/ 目录
    - 验证新条件格式（必须是3条数字编号）
    - 更新进度文件
"""

import json
import os
import re
import sys
import shutil
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')
BACKUP_DIR = os.path.join(PROJECT_DIR, 'backup', 'conversion')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
PROGRESS_PATH = os.path.join(OUTPUT_DIR, '_conversion_progress.json')


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_progress():
    """加载进度文件"""
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'total': 0, 'completed': [], 'failed': [], 'last_updated': ''}


def save_progress(progress):
    """保存进度文件"""
    progress['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ensure_dir(OUTPUT_DIR)
    with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def find_chapter_file(chapter_id):
    """根据章节ID查找TXT文件路径"""
    for stage_dir in sorted(os.listdir(STORY_DIR)):
        stage_path = os.path.join(STORY_DIR, stage_dir)
        if not os.path.isdir(stage_path):
            continue

        for fname in os.listdir(stage_path):
            if not fname.upper().endswith('.TXT'):
                continue
            if fname.startswith('_'):
                continue

            fp = os.path.join(stage_path, fname)
            # 从文件名提取ID（格式: 001：名称.TXT）
            fname_id = fname.split('：')[0].split('：')[0].lstrip('0')
            # 也检查文件内的ID字段
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    m = re.match(r'^ID[：:]\s*(\d+)', first_line)
                    if m and m.group(1) == chapter_id:
                        return fp
            except Exception:
                pass

            if fname_id == chapter_id or fname_id == str(int(chapter_id) if chapter_id.isdigit() else chapter_id):
                return fp

    return None


def parse_result_file(filepath):
    """解析LLM返回的转换结果文件，返回 {chapter_id: new_conditions_text, ...}"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    results = {}
    # 匹配 ## ID: {id} ... 章节终止条件: ... ---
    pattern = re.compile(
        r'##\s*ID[：:]\s*(\d+)\s*\n'
        r'(.*?)'
        r'(?=\n##\s*ID[：:]|\n---\s*\n|$)',
        re.DOTALL
    )

    for m in pattern.finditer(content):
        ch_id = m.group(1)
        block = m.group(2)

        # 提取章节终止条件部分
        cond_match = re.search(
            r'章节终止条件[：:]\s*\n?(.*?)(?=\n(?:##|$))',
            block, re.DOTALL
        )
        if cond_match:
            cond_text = cond_match.group(1).strip()
            results[ch_id] = cond_text

    # 也尝试按 "---" 分隔的备选解析
    if not results:
        blocks = content.split('\n---')
        for block in blocks:
            id_match = re.search(r'##\s*ID[：:]\s*(\d+)', block)
            cond_match = re.search(
                r'章节终止条件[：:]\s*\n?(.*?)$',
                block, re.DOTALL
            )
            if id_match and cond_match:
                ch_id = id_match.group(1)
                cond_text = cond_match.group(1).strip()
                results[ch_id] = cond_text

    return results


def validate_conditions(cond_text):
    """验证新条件格式：必须是3条数字编号，每条一句话"""
    lines = [l.strip() for l in cond_text.split('\n') if l.strip()]
    if len(lines) < 2 or len(lines) > 4:
        return False, f"条件条数异常（期望2-4条，实际{len(lines)}条）"

    for i, line in enumerate(lines):
        # 每条应以数字编号开头
        if not re.match(r'^\d+[\.\、\s]', line):
            return False, f"条件{i+1}缺少数字编号: {line[:50]}"

    return True, ""


def apply_conversion(chapter_id, new_conditions, dry_run=False):
    """将新的终止条件写回章节TXT"""
    fp = find_chapter_file(chapter_id)
    if not fp:
        return False, f"找不到章节文件: ID={chapter_id}"

    # 读取原文件
    with open(fp, 'r', encoding='utf-8') as f:
        original = f.read()

    # 备份原文件
    if not dry_run:
        backup_path = os.path.join(BACKUP_DIR, os.path.basename(fp))
        ensure_dir(BACKUP_DIR)
        shutil.copy2(fp, backup_path)

    # 验证新条件
    valid, msg = validate_conditions(new_conditions)
    if not valid:
        return False, f"格式验证失败: {msg}"

    # 替换章节终止条件
    # 匹配 "章节终止条件: ..." 直到下一个字段（以非缩进行开头，中文key）
    pattern = re.compile(
        r'(章节终止条件[：:]\s*)'
        r'(.*?)'
        r'(\n(?![\d\s\-\.])(?=[^\s])|$)',
        re.DOTALL
    )

    def replace_cond(m):
        prefix = m.group(1)
        suffix = m.group(3) if m.group(3) else ''
        # 确保新条件后有换行
        new_text = prefix + new_conditions
        if suffix and not suffix.startswith('\n'):
            new_text += '\n'
        new_text += suffix
        return new_text

    new_content = pattern.sub(replace_cond, original, count=1)

    # 检查是否替换成功
    if new_content == original:
        # 尝试备用匹配：章节终止条件后面直接就是下一个key
        pattern2 = re.compile(
            r'(章节终止条件[：:]\s*)'
            r'([^\n]*(?:\n(?!\n*\S+[：:])[^\n]*)*)',
            re.DOTALL
        )

        def replace_cond2(m):
            return m.group(1) + new_conditions

        new_content = pattern2.sub(replace_cond2, original, count=1)

    if new_content == original:
        return False, "未能匹配到章节终止条件段落"

    # 写回
    if not dry_run:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return True, f"已更新: {os.path.basename(fp)}"


def process_results(results, dry_run=False):
    """批量处理转换结果"""
    progress = load_progress()
    success_count = 0
    fail_count = 0
    skip_count = 0

    for ch_id, cond_text in sorted(results.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        # 跳过已完成的
        if ch_id in progress['completed']:
            print(f"  [{ch_id}] 已处理，跳过")
            skip_count += 1
            continue

        print(f"  [{ch_id}] 处理中...", end=' ')
        ok, msg = apply_conversion(ch_id, cond_text, dry_run)
        if ok:
            progress['completed'].append(ch_id)
            if ch_id in progress['failed']:
                progress['failed'].remove(ch_id)
            success_count += 1
            print("✓")
        else:
            if ch_id not in progress['failed']:
                progress['failed'].append(ch_id)
            fail_count += 1
            print(f"✗ {msg}")

    save_progress(progress)
    print(f"\n结果: {success_count} 成功, {fail_count} 失败, {skip_count} 跳过")
    print(f"总进度: {len(progress['completed'])}/{progress['total']}")

    return success_count, fail_count, skip_count


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dry_run = '--dry-run' in sys.argv

    if '--dir' in sys.argv:
        # 批量处理目录下的所有结果文件
        try:
            idx = sys.argv.index('--dir')
            results_dir = sys.argv[idx + 1]
        except (ValueError, IndexError):
            print("用法: --dir <results_dir>")
            sys.exit(1)

        all_results = {}
        for fname in sorted(os.listdir(results_dir)):
            if fname.startswith('_'):
                continue
            fp = os.path.join(results_dir, fname)
            if os.path.isfile(fp):
                print(f"解析: {fname}")
                file_results = parse_result_file(fp)
                all_results.update(file_results)
                print(f"  提取 {len(file_results)} 条结果")

        print(f"\n共提取 {len(all_results)} 条结果\n")
        if dry_run:
            print("[DRY RUN] 不写入文件\n")
        process_results(all_results, dry_run)

    else:
        # 单个结果文件
        result_file = sys.argv[1]
        if not os.path.exists(result_file):
            print(f"错误: 文件不存在 - {result_file}")
            sys.exit(1)

        print(f"解析: {result_file}")
        results = parse_result_file(result_file)
        print(f"提取 {len(results)} 条结果\n")

        if dry_run:
            print("[DRY RUN] 不写入文件\n")
        process_results(results, dry_run)


if __name__ == '__main__':
    main()
