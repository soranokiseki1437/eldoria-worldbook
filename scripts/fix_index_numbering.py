#!/usr/bin/env python3
"""扫描所有章节文件，建立ID→名称映射，找出索引中编号错误的条目并修正 (V2.0)

V2.0 改进（2026-08-04）:
  - 支持非整数编号（如 615.5）：显式报告，不再静默忽略
  - 拆分章节展开：索引条目缺（上/中/下）后缀时，按文件系统实际分部自动展开
  - 标题格式归一化：引号差异（温泉的"不知道你在" vs 温泉的不知道你在）可匹配
  - 输出自校验：生成后自动核对，报告剩余不匹配数
"""
import os, re
from collections import defaultdict

STORY_DIR = "docs/story"
INDEX_FILE = "docs/story/_sex_index.txt"


def scan_files():
    """返回 {ID: 名称}"""
    mapping = {}
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'): continue
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as fp:
                    content = fp.read()
            except: continue
            m_id = re.search(r'ID:\s*(\d+)', content)
            m_name = re.search(r'名称:\s*(.+)', content)
            if m_id and m_name:
                mapping[m_id.group(1)] = m_name.group(1).strip()
    return mapping


def normalize_title(t):
    """去（上/中/下）后缀 + 去引号，用于模糊匹配"""
    t = re.sub(r'[（(](上|中|下)[)）]', '', t)
    return t.replace('"', '').replace('"', '')


def parse_index():
    """返回 [(tag, ch_id, name, line_num)]，ch_id 支持小数"""
    entries = []
    current_tag = None
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            raw = line.strip()
            if raw.startswith('##'):
                m = re.match(r'##\s*(.+?)\s*\(', raw)
                if m: current_tag = m.group(1).strip()
                continue
            m = re.match(r'([\d.]+):\s*(.+)', raw)
            if m and current_tag:
                entries.append((current_tag, m.group(1), m.group(2).strip(), i))
    return entries


def main():
    print("扫描文件系统...")
    file_map = scan_files()
    print(f"  找到 {len(file_map)} 个章节文件")

    print("解析索引...")
    index_entries = parse_index()
    print(f"  找到 {len(index_entries)} 个索引条目")

    # 精确标题→ID；归一化标题→[IDs]（多ID=拆分章节）
    name_to_id = {v: k for k, v in file_map.items()}
    norm_to_ids = defaultdict(list)
    for k, v in file_map.items():
        norm_to_ids[normalize_title(v)].append(k)

    print("\n检查编号...")
    issues = []
    matched = 0
    non_int = 0
    for tag, idx_id, idx_name, line_num in index_entries:
        if '.' in idx_id:
            non_int += 1
            issues.append(('non_int', tag, idx_id, idx_name, '?', line_num))
            continue
        if idx_id in file_map:
            file_name = file_map[idx_id]
            if file_name == idx_name:
                matched += 1
            else:
                correct_id = name_to_id.get(idx_name)
                if correct_id and correct_id != idx_id:
                    issues.append(('wrong_id', tag, idx_id, idx_name, correct_id, line_num))
                else:
                    issues.append(('name_mismatch', tag, idx_id, idx_name, file_name, line_num))
        else:
            correct_id = name_to_id.get(idx_name)
            if correct_id:
                issues.append(('missing_id', tag, idx_id, idx_name, correct_id, line_num))
            else:
                issues.append(('not_found', tag, idx_id, idx_name, '?', line_num))

    print(f"\n{'='*60}")
    print(f"匹配正确: {matched} 条目")
    print(f"编号问题: {len(issues)} 条目 (含非整数 {non_int})")
    print(f"{'='*60}\n")

    if not issues:
        print("✓ 无编号问题！")
        return

    by_type = {}
    for typ, tag, idx_id, idx_name, correct_id, line in issues:
        if typ not in by_type: by_type[typ] = []
        by_type[typ].append((tag, idx_id, idx_name, correct_id, line))

    for typ, items in by_type.items():
        print(f"\n--- {typ} ({len(items)}个) ---")
        for tag, idx_id, idx_name, correct_id, line in items[:30]:
            if typ == 'non_int':
                print(f"  [{tag}] 非整数编号{idx_id}: {idx_name}（需手工处理）")
            elif typ == 'name_mismatch':
                cands = norm_to_ids.get(normalize_title(idx_name), [])
                print(f"  [{tag}] 索引{idx_id}标题与fs不符: {idx_name} → 归一化候选 {cands}（需人工确认）")
            else:
                print(f"  [{tag}] 索引{idx_id}→应为{correct_id}: {idx_name}")
        if len(items) > 30:
            print(f"  ... 还有 {len(items)-30} 个")

    # 生成修正索引：wrong_id/missing_id 直接换号；name_mismatch 归一化命中则修正；
    # 归一化命中多ID（拆分章节）→ 展开为分部条目；non_int/not_found 原样保留并报告
    print(f"\n生成修正索引...")

    corrections = {}
    expansions = {}
    unhandled = []
    for typ, tag, idx_id, idx_name, correct_id, line in issues:
        if typ in ('wrong_id', 'missing_id') and correct_id != '?':
            corrections[(idx_id, tag, idx_name)] = correct_id
        elif typ == 'name_mismatch':
            cands = norm_to_ids.get(normalize_title(idx_name), [])
            if len(cands) == 1:
                corrections[(idx_id, tag, idx_name)] = cands[0]
            elif len(cands) > 1:
                cands.sort(key=int)
                expansions[(idx_id, tag, idx_name)] = cands
            else:
                unhandled.append((tag, idx_id, idx_name))
        else:
            unhandled.append((tag, idx_id, idx_name))

    output = INDEX_FILE.replace('.txt', '_numbered.txt')
    with open(output, 'w', encoding='utf-8') as out:
        current_tag = None
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                raw = line.rstrip('\n')

                if raw.startswith('##'):
                    current_tag = None
                    m = re.match(r'##\s*(.+?)\s*\(', raw)
                    if m: current_tag = m.group(1).strip()
                    out.write(raw + '\n')
                    continue

                if not raw.strip():
                    out.write('\n')
                    continue

                m = re.match(r'([\d.]+):\s*(.+)', raw)
                if not m or not current_tag:
                    out.write(raw + '\n')
                    continue

                old_id, name = m.group(1), m.group(2).strip()
                key = (old_id, current_tag, name)
                if key in corrections:
                    out.write(f"{corrections[key]}: {name}\n")
                elif key in expansions:
                    for nid in expansions[key]:
                        out.write(f"{nid}: {file_map[nid]}\n")
                else:
                    out.write(raw + '\n')

    print(f"修正索引: {output}")

    # 自动校验输出
    new_map = {}
    cur_tag = None
    for line in open(output, encoding='utf-8'):
        line = line.strip()
        if not line: continue
        if line.startswith('##'):
            cur_tag = line.split()[1].split('(')[0] if len(line.split()) > 1 else '?'
            continue
        m = re.match(r'^(\d+):\s*(.+)', line)
        if m:
            new_map[m.group(1)] = m.group(2).strip()
    remain = [k for k, v in new_map.items() if file_map.get(k) != v]
    print(f"校验: {len(new_map)} 条, 仍不匹配 {len(remain)} 条")
    for k in remain[:10]:
        print(f"  ⚠ Ch{k}: 索引={new_map[k]!r} vs fs={file_map.get(k, '?')!r}")
    if unhandled:
        print(f"\n需手工处理 {len(unhandled)} 条:")
        for tag, idx_id, idx_name in unhandled:
            print(f"  [{tag}] {idx_id}: {idx_name}")
    print(f"请检查后用此文件替换原_index.txt，再运行 python scripts/check_consistency.py")


if __name__ == '__main__':
    main()
