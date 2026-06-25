# -*- coding: utf-8 -*-
"""
clean_ntrs_hardcodes.py — 从build_eldoria.py中移除所有硬编码add_ntrs_entry()调用
=============================
替换为自动生成的get_ntrs_entries()函数。
先分析后执行，带备份。
"""
import re
import sys
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
BUILD_PY = os.path.join(SCRIPT_DIR, 'build_eldoria.py')


def analyze():
    """分析当前build_eldoria.py中的add_ntrs_entry调用分布"""
    with open(BUILD_PY, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到所有包含 add_ntrs_entry 的行
    ntrs_lines = []
    current_func = None
    for i, line in enumerate(lines):
        # 跟踪当前函数
        fm = re.match(r'^def (get_\w+)\(\):', line)
        if fm:
            current_func = fm.group(1)
        if 'add_ntrs_entry(' in line:
            ntrs_lines.append((i + 1, current_func, line.rstrip()))

    # 按函数分组
    from collections import Counter
    func_counts = Counter(f[1] for f in ntrs_lines)

    print("=== add_ntrs_entry 调用分布 ===")
    for func, count in sorted(func_counts.items()):
        print(f"  {func}: {count} 处")

    # 检查哪些函数只包含add_ntrs_entry（可能变为空函数）
    print("\n=== 函数内容分析 ===")
    func_bodies = {}
    current_func = None
    func_start = None
    for i, line in enumerate(lines):
        fm = re.match(r'^def (get_\w+)\(\):', line)
        if fm:
            if current_func:
                func_bodies[current_func] = (func_start, i)
            current_func = fm.group(1)
            func_start = i
        # 检测下一个def或class
    if current_func:
        func_bodies[current_func] = (func_start, len(lines))

    for func, (start, end) in sorted(func_bodies.items(), key=lambda x: x[1][0]):
        if func not in func_counts:
            continue
        body_lines = lines[start:end]
        # 统计make_entry调用（非NTRS的）
        non_ntrs_entries = sum(1 for l in body_lines if 'make_entry(' in l and 'add_ntrs_entry' not in l)
        ntrs_entries = func_counts.get(func, 0)
        print(f"  {func}: NTRS={ntrs_entries}, 非NTRS={non_ntrs_entries} → {'纯NTRS(可删)' if non_ntrs_entries == 0 else '混合(保留非NTRS)'}")

    return func_counts


def execute():
    """移除所有add_ntrs_entry行，清理空函数，添加get_ntrs_entries到build pipeline"""
    with open(BUILD_PY, 'r', encoding='utf-8') as f:
        text = f.read()

    # 备份
    backup_path = os.path.join(PROJECT_DIR, 'backups',
                               f'build_eldoria.py.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"📦 备份: {backup_path}")

    lines = text.split('\n')
    new_lines = []
    i = 0
    removed_count = 0
    removed_funcs = []

    while i < len(lines):
        line = lines[i]

        # 跳过包含 add_ntrs_entry( 的行
        if 'add_ntrs_entry(' in line:
            removed_count += 1
            i += 1
            continue

        # 检测纯NTRS空函数：def get_xxx(): 之后直到下一个def之间只有空白/注释/return []
        fm = re.match(r'^def (get_\w+)\(\):', line)
        if fm:
            func_name = fm.group(1)
            func_start = i
            # 向前扫描函数体
            j = i + 1
            body_lines = []
            while j < len(lines):
                next_line = lines[j]
                # 遇到下一个def或空行后跟def → 函数结束
                if re.match(r'^def ', next_line):
                    break
                body_lines.append(next_line)
                j += 1

            # 检查函数体是否只有空白/注释/return [] / pass
            non_trivial = [l for l in body_lines
                          if l.strip()
                          and not l.strip().startswith('#')
                          and not l.strip().startswith('"""')
                          and not l.strip().startswith("'''")
                          and l.strip() not in ('return []', 'pass', 'return', 'entries = []')
                          and 'add_ntrs_entry' not in l]
            # 也检查有没有 make_entry 调用
            has_make_entry = any('make_entry(' in l for l in body_lines)

            if not has_make_entry and len(non_trivial) <= 1:
                # 空函数或只剩return []——删除整个函数
                removed_funcs.append(func_name)
                i = j
                continue

        new_lines.append(line)
        i += 1

    # 写回
    new_text = '\n'.join(new_lines)

    # 在build函数中添加 get_ntrs_entries 调用
    # 找到 step 2z 之后的位置，添加新行
    insert_marker = 'collect(get_uid224_240_entries,     "uid 224-240 NTRS路线17新事件", "2z")'
    new_collect_line = '    collect(get_ntrs_entries,              "NTRS路线76事件(自动生成)", "2ntrs")'

    if insert_marker in new_text:
        new_text = new_text.replace(
            insert_marker,
            insert_marker + '\n' + new_collect_line
        )
        print(f"✅ 已添加 get_ntrs_entries 到构建流水线")
    else:
        # 回退：在原插入点附近寻找
        alt_marker = 'collect(get_uid212_213_entries,     "uid 212-213 P17/P18 纯爱NSFW", "2x")'
        if alt_marker in new_text:
            new_text = new_text.replace(
                alt_marker,
                alt_marker + '\n' + new_collect_line
            )
            print(f"✅ 已添加 get_ntrs_entries 到构建流水线 (备用位置)")

    with open(BUILD_PY, 'w', encoding='utf-8') as f:
        f.write(new_text)

    print(f"\n=== 清理完成 ===")
    print(f"  移除 add_ntrs_entry 行: {removed_count} 处")
    print(f"  删除空函数: {len(removed_funcs)} 个")
    if removed_funcs:
        for fn in removed_funcs:
            print(f"    - {fn}()")

    return removed_count


if __name__ == '__main__':
    if '--analyze' in sys.argv:
        analyze()
    else:
        print("=== 分析阶段 ===")
        analyze()
        print("\n=== 执行阶段 ===")
        execute()
        print("\n✅ 完成。请运行 python scripts/build_eldoria.py 验证构建。")
