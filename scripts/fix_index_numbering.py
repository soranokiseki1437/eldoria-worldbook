#!/usr/bin/env python3
"""扫描所有章节文件，建立ID→名称映射，找出索引中编号错误的条目并修正"""
import os, re

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

def parse_index():
    """返回 [(tag, ch_id, name, line_num)]"""
    entries = []
    current_tag = None
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            raw = line.strip()
            if raw.startswith('##'):
                m = re.match(r'##\s*(.+?)\s*\(', raw)
                if m: current_tag = m.group(1).strip()
                continue
            m = re.match(r'(\d+):\s*(.+)', raw)
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

    # Build name→id lookup from files
    name_to_id = {v: k for k, v in file_map.items()}

    # Check each index entry
    print("\n检查编号...")
    issues = []
    matched = 0
    for tag, idx_id, idx_name, line_num in index_entries:
        # Check if the index ID exists in files
        if idx_id in file_map:
            # ID exists - check if name matches
            file_name = file_map[idx_id]
            if file_name == idx_name:
                matched += 1
            else:
                # ID exists but different name - wrong ID
                correct_id = name_to_id.get(idx_name)
                if correct_id and correct_id != idx_id:
                    issues.append(('wrong_id', tag, idx_id, idx_name, correct_id, line_num))
                else:
                    issues.append(('name_mismatch', tag, idx_id, idx_name, file_name, line_num))
        else:
            # ID not found - try finding by name
            correct_id = name_to_id.get(idx_name)
            if correct_id:
                issues.append(('missing_id', tag, idx_id, idx_name, correct_id, line_num))
            else:
                issues.append(('not_found', tag, idx_id, idx_name, '?', line_num))

    print(f"\n{'='*60}")
    print(f"匹配正确: {matched} 条目")
    print(f"编号问题: {len(issues)} 条目")
    print(f"{'='*60}\n")

    if not issues:
        print("✓ 无编号问题！")
        return

    # Group by issue type
    by_type = {}
    for typ, tag, idx_id, idx_name, correct_id, line in issues:
        if typ not in by_type: by_type[typ] = []
        by_type[typ].append((tag, idx_id, idx_name, correct_id, line))

    for typ, items in by_type.items():
        print(f"\n--- {typ} ({len(items)}个) ---")
        for tag, idx_id, idx_name, correct_id, line in items[:30]:
            print(f"  [{tag}] 索引{idx_id}→应为{correct_id}: {idx_name}")
        if len(items) > 30:
            print(f"  ... 还有 {len(items)-30} 个")

    # Generate corrected index
    print(f"\n生成修正索引...")

    # Build corrections dict: (old_id, tag) → new_id
    corrections = {}
    for typ, tag, idx_id, idx_name, correct_id, line in issues:
        if typ in ('wrong_id', 'missing_id') and correct_id != '?':
            key = (idx_id, idx_name)  # match by name too for safety
            corrections[(idx_id, tag, idx_name)] = correct_id

    # Write corrected index
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

                m = re.match(r'(\d+):\s*(.+)', raw)
                if not m or not current_tag:
                    out.write(raw + '\n')
                    continue

                old_id, name = m.group(1), m.group(2).strip()
                key = (old_id, current_tag, name)
                if key in corrections:
                    new_id = corrections[key]
                    out.write(f"{new_id}: {name}\n")
                else:
                    out.write(raw + '\n')

    print(f"修正索引: {output}")
    print(f"请用此文件替换原_index.txt后重新构建浏览器")

if __name__ == '__main__':
    main()
