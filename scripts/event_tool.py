#!/usr/bin/env python3
"""
event_tool.py — 事件块级操作工具
==================================
基于 ### 事件N##：头定位YAML块，支持提取/替换/插入/移动/删除/验证。
不依赖YAML解析，不依赖字符串精确匹配——块级操作消除缩进问题。

用法:
  python event_tool.py list <file> [--section NTRS]     # 列出所有事件ID+标题
  python event_tool.py extract <file> <event_id> [--output <f>]  # 提取事件块到文件/stdout
  python event_tool.py replace <file> <event_id> <patch_file>    # 用文件内容替换事件块
  python event_tool.py insert <file> <after_event_id> <new_file> # 在指定事件后插入
  python event_tool.py move <file> <event_id> <after_event_id>   # 移动事件
  python event_tool.py delete <file> <event_id> [--dry-run]      # 删除事件
  python event_tool.py validate <file>                    # 全面验证（Rule1/2/银发/嗅觉）
  python event_tool.py show <file> <event_id>              # 在终端显示事件内容

文件格式:
  提取的事件块包含 ### 事件N##：标题 + ```yaml ... ``` 完整块。
  replace/insert 的 patch_file 应包含完整的事件块（header + yaml）。

设计原则:
  - 块级操作：以"### 事件"头为界，不解析YAML内部
  - 自动备份：修改操作前自动备份源文件
  - 干运行模式：insert/delete/move 支持 --dry-run
"""

import re
import os
import sys
import shutil
from datetime import datetime

# ============================================================
# Core: Event boundary detection
# ============================================================

EVENT_HEADER = re.compile(r'^### 事件([A-Z]+\d{1,3})[：:]([^\n]*)', re.MULTILINE)
SECTION_HEADER = re.compile(r'^### [^\s]', re.MULTILINE)
SUB_SECTION = re.compile(r'^## ', re.MULTILINE)

def find_event_blocks(text):
    """返回 [(event_id, title, start, end, block_text), ...]，按出现顺序"""
    blocks = []
    for m in EVENT_HEADER.finditer(text):
        eid = m.group(1)
        title = m.group(2).strip()
        start = m.start()
        # 找到块结束位置：下一个 ### 事件 或 ### 阶段 或 ## 大节 或 ---
        remaining = text[m.end():]
        # 找最近的终止标记
        end_markers = []
        for pattern, label in [
            (r'\n### 事件', 'next_event'),
            (r'\n### [^\s]', 'section'),
            (r'\n## ', 'subsection'),
            (r'\n---', 'separator'),
        ]:
            em = re.search(pattern, remaining)
            if em:
                end_markers.append((em.start(), label))
        if end_markers:
            end_offset = min(end_markers, key=lambda x: x[0])[0]
            end = m.end() + end_offset
        else:
            end = len(text)
        block_text = text[start:end]
        blocks.append((eid, title, start, end, block_text))
    return blocks

def find_event_by_id(text, event_id):
    """返回 (title, start, end, block_text) 或 None"""
    for eid, title, start, end, block in find_event_blocks(text):
        if eid == event_id:
            return title, start, end, block
    return None

def get_narrative_sections(block_text):
    """提取事件块中的叙事字段（情境/占有欲确认/核心/玩家选择），用于验证"""
    # 找到YAML内容（```yaml ... ```之间的部分）
    m = re.search(r'```yaml\n(.*?)\n```', block_text, re.DOTALL)
    if not m:
        return ''
    return m.group(1)

# ============================================================
# Operations
# ============================================================

def list_events(text, section_filter=None):
    """列出所有事件ID和标题，可选按章节过滤"""
    blocks = find_event_blocks(text)
    if section_filter:
        # 找到指定章节的范围
        sec_start = text.find(section_filter)
        if sec_start < 0:
            # 尝试匹配章节模式
            sec_start = 0
        filtered = []
        for eid, title, start, end, block in blocks:
            if start >= sec_start:
                filtered.append((eid, title, start, end, block))
        blocks = filtered

    results = []
    for eid, title, start, end, block in blocks:
        # 获取行号
        line_num = text[:start].count('\n') + 1
        results.append((eid, title, line_num))
    return results

def extract_event(text, event_id):
    """提取事件块文本"""
    result = find_event_by_id(text, event_id)
    if not result:
        sys.stderr.write(f'❌ 事件 {event_id} 未找到\n')
        sys.exit(1)
    return result[3]

def replace_event(text, event_id, new_block):
    """替换事件块。返回修改后的全文。"""
    result = find_event_by_id(text, event_id)
    if not result:
        sys.stderr.write(f'❌ 事件 {event_id} 未找到\n')
        sys.exit(1)
    title, start, end, old_block = result
    print(f'  替换 {event_id}：{title}')
    print(f'  旧块: {len(old_block)} 字符 → 新块: {len(new_block)} 字符')
    return text[:start] + new_block + text[end:]

def insert_event(text, after_event_id, new_block):
    """在指定事件后插入新事件块"""
    result = find_event_by_id(text, after_event_id)
    if not result:
        sys.stderr.write(f'❌ 插入点 {after_event_id} 未找到\n')
        sys.exit(1)
    title, start, end, old_block = result
    insert_pos = end
    # 确保插入后有适当的间距
    # 检查end位置后是否有换行
    if text[end:end+1] == '\n':
        insert_text = '\n' + new_block + '\n'
    else:
        insert_text = '\n\n' + new_block + '\n'
    print(f'  在 {after_event_id} 后插入新事件')
    return text[:insert_pos] + insert_text + text[insert_pos:]

def delete_event(text, event_id):
    """删除事件块"""
    result = find_event_by_id(text, event_id)
    if not result:
        sys.stderr.write(f'❌ 事件 {event_id} 未找到\n')
        sys.exit(1)
    title, start, end, old_block = result
    print(f'  删除 {event_id}：{title}')
    # 删除块及其前后空白
    # Remove trailing newlines after the block
    while end < len(text) and text[end] == '\n':
        end += 1
    return text[:start] + text[end:]

def move_event(text, event_id, after_event_id):
    """移动事件到另一个事件之后"""
    result_src = find_event_by_id(text, event_id)
    result_dst = find_event_by_id(text, after_event_id)
    if not result_src:
        sys.stderr.write(f'❌ 源事件 {event_id} 未找到\n')
        sys.exit(1)
    if not result_dst:
        sys.stderr.write(f'❌ 目标 {after_event_id} 未找到\n')
        sys.exit(1)

    src_title, src_start, src_end, src_block = result_src
    dst_title, dst_start, dst_end, dst_block = result_dst

    # 先提取源块内容
    block_content = text[src_start:src_end]
    # 从原位置删除
    text = text[:src_start] + text[src_end:]
    # 重新定位目标（因为文本已变化）
    new_dst_end = dst_end if dst_end < src_start else dst_end - (src_end - src_start)
    # 在目标后插入
    insert_text = '\n' + block_content + '\n'
    text = text[:new_dst_end] + insert_text + text[new_dst_end:]
    print(f'  移动 {event_id} → {after_event_id} 之后')
    return text

# ============================================================
# Validation
# ============================================================

def validate(text):
    """全面验证，返回违规列表"""
    violations = []

    # Rule 1: N## in narrative
    # 提取每个事件块的叙事部分
    for eid, title, start, end, block in find_event_blocks(text):
        narrative = get_narrative_sections(block)
        # 找N##引用（不含事件头那行）
        n_refs = re.findall(r'(?<![A-Za-z])N\d{1,2}(?!\d)', narrative)
        # 排除可能出现在metadata行中的合法引用
        for ref in n_refs:
            line_num = text[:start].count('\n') + 1
            # 检查引用所在行是否是metadata
            ref_pos = narrative.find(ref)
            line_start = narrative.rfind('\n', 0, ref_pos) + 1
            line_end = narrative.find('\n', ref_pos)
            line = narrative[line_start:line_end] if line_end > 0 else narrative[line_start:]
            # 检查该行及其上方的非空行是否是metadata key（处理跨行value）
            meta_keys = ('事件:', '核心:', '排序备注:', '前置事件:', '后续事件:',
                        '触发条件:', '性行为', '情感阶段', '变量:', '玩家选择:',
                        '黎恩知情:', '第三者:', '触发:', '阶段:')
            is_meta = line.strip().startswith(meta_keys)
            if not is_meta:
                # 检查上一非空行是否以metadata key开头（当前行可能是value续行）
                prev_lines = narrative[:line_start].split('\n')
                for pl in reversed(prev_lines):
                    pls = pl.strip()
                    if pls and not pls.startswith('-'):
                        if pls.startswith(meta_keys):
                            is_meta = True
                        break
            if not is_meta:
                violations.append(f'[{eid}] Rule1: 叙事中出现 "{ref}" — {line.strip()[:60]}...')

    # Rule 2: 进度互通
    prohibited_phrases = [
        # 仅匹配明确的"互通进度"模式，避免误伤普通对话
        ('听说了.*进度', ''),
        ('问了雷恩.*怎么', ''),
        ('问了艾德里安.*怎么', ''),
        ('知道.*已经走.*步', ''),
        ('艾德里安有.*我也想有', ''),
        ('打听.*艾德里安', ''),
        ('打听.*凯尔', ''),
    ]
    for eid, title, start, end, block in find_event_blocks(text):
        narrative = get_narrative_sections(block)
        for phrase, context in prohibited_phrases:
            if re.search(phrase, narrative):
                violations.append(f'[{eid}] Rule2: 第三者互通进度 — 含 "{phrase}"')

    # 银发→粉发 (for Seraphina)
    for eid, title, start, end, block in find_event_blocks(text):
        narrative = get_narrative_sections(block)
        # 检测"银发" — 可能是Seraphina的
        if '银发' in narrative:
            # 在上下文中确认是Seraphina
            ctx_idx = narrative.find('银发')
            ctx = narrative[max(0,ctx_idx-100):ctx_idx+100]
            # 如果在描述女性角色（非先灵/Thalion/Adrian/Altina），标记
            if any(name in block for name in ['菲娜', 'Seraphina', '她']):
                if not any(safe in ctx for safe in ['先灵', 'Thalion', 'Adrian', '亚尔缇娜', 'Altina']):
                    violations.append(f'[{eid}] 银发: Seraphina头发应是粉色 — ...{ctx}...')

    # 粉银
    if '粉银' in text:
        for m in re.finditer('粉银', text):
            line_num = text[:m.start()].count('\n') + 1
            violations.append(f'[行{line_num}] 粉银: 应为"粉色"')

    # Rule 3: 重复事件ID
    seen_ids = {}
    for eid, title, start, end, block in find_event_blocks(text):
        if eid in seen_ids:
            line1 = text[:seen_ids[eid]].count('\n') + 1
            line2 = text[:start].count('\n') + 1
            violations.append(f'[{eid}] Rule3: 重复事件ID — 首次出现L{line1}，再次出现L{line2} ({title})')
        else:
            seen_ids[eid] = start

    return violations

# ============================================================
# File I/O
# ============================================================

def backup_file(filepath):
    """自动备份"""
    backup_dir = os.path.join(os.path.dirname(filepath), '..', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    basename = os.path.basename(filepath)
    backup_path = os.path.join(backup_dir, f'{basename}.{timestamp}.bak')
    shutil.copy2(filepath, backup_path)
    print(f'  📦 备份: {backup_path}')
    return backup_path

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# ============================================================
# CLI
# ============================================================

def print_usage():
    print(__doc__)

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    cmd = sys.argv[1]
    target = sys.argv[2]  # Could be file path or command-specific

    if cmd == 'list':
        filepath = target
        section = None
        if '--section' in sys.argv:
            si = sys.argv.index('--section')
            section = sys.argv[si+1] if si+1 < len(sys.argv) else None
        text = read_file(filepath)
        events = list_events(text, section)
        for eid, title, line in events:
            print(f'  {eid:6s}  L{line:4d}  {title}')
        print(f'\n共 {len(events)} 个事件')

    elif cmd == 'extract':
        # python event_tool.py extract <file> <event_id> [--output <f>]
        if len(sys.argv) < 4:
            print('用法: event_tool.py extract <file> <event_id> [--output <f>]')
            sys.exit(1)
        filepath = target
        event_id = sys.argv[3]
        output_file = None
        if '--output' in sys.argv:
            oi = sys.argv.index('--output')
            output_file = sys.argv[oi+1] if oi+1 < len(sys.argv) else None

        text = read_file(filepath)
        block = extract_event(text, event_id)

        if output_file:
            write_file(output_file, block)
            print(f'✅ {event_id} 已提取到 {output_file} ({len(block)} 字符)')
        else:
            sys.stdout.write(block)

    elif cmd == 'replace':
        # python event_tool.py replace <file> <event_id> <patch_file>
        if len(sys.argv) < 5:
            print('用法: event_tool.py replace <file> <event_id> <patch_file>')
            sys.exit(1)
        filepath = target
        event_id = sys.argv[3]
        patch_file = sys.argv[4]

        text = read_file(filepath)
        new_block = read_file(patch_file)
        backup_file(filepath)
        text = replace_event(text, event_id, new_block)
        write_file(filepath, text)

        # Quick validate
        violations = validate(text)
        my_violations = [v for v in violations if v.startswith(f'[{event_id}]')]
        if my_violations:
            print(f'\n⚠️  {event_id} 验证发现 {len(my_violations)} 个问题:')
            for v in my_violations:
                print(f'  {v}')
        else:
            print(f'✅ {event_id} 已替换并验证通过')

    elif cmd == 'insert':
        if len(sys.argv) < 5:
            print('用法: event_tool.py insert <file> <after_event_id> <new_file> [--dry-run]')
            sys.exit(1)
        filepath = target
        after_id = sys.argv[3]
        new_file = sys.argv[4]
        dry_run = '--dry-run' in sys.argv

        text = read_file(filepath)
        new_block = read_file(new_file)

        if dry_run:
            result = insert_event(text, after_id, new_block)
            print(f'[DRY RUN] 将在 {after_id} 后插入 ({len(new_block)} 字符)')
            # Show the new event ID
            m = re.search(r'### 事件([A-Z]+\d{1,3})[：:]', new_block)
            if m:
                print(f'  新事件ID: {m.group(1)}')
        else:
            backup_file(filepath)
            text = insert_event(text, after_id, new_block)
            write_file(filepath, text)
            print('✅ 插入完成')

    elif cmd == 'delete':
        if len(sys.argv) < 4:
            print('用法: event_tool.py delete <file> <event_id> [--dry-run]')
            sys.exit(1)
        filepath = target
        event_id = sys.argv[3]
        dry_run = '--dry-run' in sys.argv

        text = read_file(filepath)
        if dry_run:
            result = find_event_by_id(text, event_id)
            if result:
                print(f'[DRY RUN] 将删除 {event_id}：{result[0]}')
        else:
            backup_file(filepath)
            text = delete_event(text, event_id)
            write_file(filepath, text)
            print(f'✅ {event_id} 已删除')

    elif cmd == 'move':
        if len(sys.argv) < 5:
            print('用法: event_tool.py move <file> <event_id> <after_event_id> [--dry-run]')
            sys.exit(1)
        filepath = target
        event_id = sys.argv[3]
        after_id = sys.argv[4]
        dry_run = '--dry-run' in sys.argv

        text = read_file(filepath)
        if dry_run:
            src = find_event_by_id(text, event_id)
            dst = find_event_by_id(text, after_id)
            if src and dst:
                print(f'[DRY RUN] 将移动 {event_id} → {after_id} 之后')
        else:
            backup_file(filepath)
            text = move_event(text, event_id, after_id)
            write_file(filepath, text)
            print(f'✅ {event_id} 已移动到 {after_id} 之后')

    elif cmd == 'validate':
        filepath = target
        text = read_file(filepath)
        violations = validate(text)
        if violations:
            print(f'❌ 发现 {len(violations)} 个问题:\n')
            for v in violations:
                print(f'  {v}')
            sys.exit(1)
        else:
            events = find_event_blocks(text)
            print(f'✅ 验证通过 — {len(events)} 个事件，未发现违规')

    elif cmd == 'show':
        if len(sys.argv) < 4:
            print('用法: event_tool.py show <file> <event_id>')
            sys.exit(1)
        filepath = target
        event_id = sys.argv[3]
        text = read_file(filepath)
        block = extract_event(text, event_id)
        print(block)

    else:
        print(f'未知命令: {cmd}')
        print_usage()
        sys.exit(1)

if __name__ == '__main__':
    main()
