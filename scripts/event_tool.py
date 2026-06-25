#!/usr/bin/env python3
"""
event_tool.py — 事件验证与查看工具 (TXT文件驱动)

用法:
  python event_tool.py validate [prefix]     # 验证所有/指定前缀TXT
  python event_tool.py list [prefix]          # 列出事件ID+标题
  python event_tool.py show <event_id>        # 显示单个事件TXT内容
  python event_tool.py refs <event_id>        # 查找所有引用了该事件ID的TXT文件

设计原则:
  - 操作对象: docs/event/{prefix}/*.TXT 文件
  - 增删改移事件请直接操作TXT文件，然后运行 renumber_events.py + assemble_md.py
"""

import re
import os
import sys
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'event')

from event_config import SECTION_TITLES as SECTION_CONFIG

# ═══════════════════════════════════════════════════════════
# TXT 解析
# ═══════════════════════════════════════════════════════════

def parse_txt(filepath):
    """解析单个 .TXT 事件文件，返回 dict"""
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


def list_txt_files(prefix=None):
    """列出TXT文件，返回 [(event_id, title, filepath), ...]"""
    results = []
    prefixes = [prefix] if prefix else SECTION_CONFIG
    for pfx in prefixes:
        pfx_dir = os.path.join(EVENT_DIR, pfx)
        if not os.path.isdir(pfx_dir):
            continue
        for fname in sorted(os.listdir(pfx_dir)):
            if not fname.upper().endswith('.TXT'):
                continue
            fp = os.path.join(pfx_dir, fname)
            data = parse_txt(fp)
            eid = data.get('ID', fname.replace('.TXT', ''))
            name = data.get('名称', '')
            results.append((eid, name, fp, data))
    return results


# ═══════════════════════════════════════════════════════════
# 验证规则
# ═══════════════════════════════════════════════════════════

def validate_prefix(prefix):
    """验证指定前缀的所有TXT文件，返回违规列表"""
    violations = []
    events = list_txt_files(prefix)

    if not events:
        return violations

    # Rule 3: 重复ID (filename-based — impossible with file system, but check ID field)
    seen_ids = {}
    for eid, name, fp, data in events:
        if eid in seen_ids:
            violations.append(
                f'[{eid}] Rule3: 重复事件ID — '
                f'{os.path.basename(seen_ids[eid])} vs {os.path.basename(fp)}'
            )
        else:
            seen_ids[eid] = fp

    # Rule 1 (铁律): 事件内容中禁止引用任何事件编号
    # 编号引用会导致未来重编号时连锁失效——描述叙事状态，不偷懒用编号。
    # 匹配所有前缀: PN01, N01, P1, E1, W1, H1, G1, R1 等
    _EVENT_ID_RE = re.compile(
        r'(?<![A-Za-z0-9])'
        r'(?:'
        r'PN\d{1,2}'           # PN1-PN99
        r'|P(?!N)\d{1,2}'      # P1-P99 (排除PN)
        r'|N\d{2,3}'           # N01-N999
        r'|[EWHGR]\d{1,2}'     # E/W/H/G/R 1-99
        r')'
        r'(?!\d)'
    )
    for eid, name, fp, data in events:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        # 分离ID行（允许自身ID出现在首行）
        body = content.split('\n', 1)
        body = body[1] if len(body) > 1 else ''
        for m in _EVENT_ID_RE.finditer(body):
            ref = m.group(0).upper()
            if ref == eid.upper():
                continue  # 自身ID行不报
            # 提取上下文行
            line_start = body.rfind('\n', 0, m.start()) + 1
            line_end = body.find('\n', m.end())
            ctx_line = body[line_start:line_end] if line_end > 0 else body[line_start:]
            ctx = ctx_line.strip()[:100]
            violations.append(
                f'[{eid}] Rule1: 禁止编号引用 — "{ref}" 出现在: {ctx}...'
            )

    # Rule 2: 进度互通
    prohibited = [
        r'听说了.*进度', r'问了雷恩.*怎么', r'问了艾德里安.*怎么',
        r'知道.*已经走.*步', r'艾德里安有.*我也想有',
        r'打听.*艾德里安', r'打听.*凯尔',
    ]
    for eid, name, fp, data in events:
        for field in ['情境', '核心']:
            text = data.get(field, '')
            for phrase in prohibited:
                if re.search(phrase, text):
                    violations.append(
                        f'[{eid}] Rule2: 第三者互通进度 — "{phrase}" in {field}'
                    )

    # Rule 4 (银发检查): Seraphina hair should be pink
    for eid, name, fp, data in events:
        for field in ['情境', '核心']:
            text = data.get(field, '')
            if '银发' in text:
                # Check context: if describing Seraphina (not Thalion/Adrian/etc)
                idx = text.find('银发')
                ctx = text[max(0, idx-80):idx+80]
                if any(n in ctx for n in ['菲娜', 'Seraphina', '她', '精灵']):
                    if not any(s in ctx for s in ['先灵', 'Thalion', 'Adrian', '亚尔缇娜', 'Altina', '埃尔德莱恩']):
                        violations.append(
                            f'[{eid}] 银发: Seraphina头发应是粉色 — ...{ctx.strip()}...'
                        )
            if '粉银' in text:
                violations.append(f'[{eid}] 粉银: 应为"粉色"')

    # Rule 5: 必填字段 (N/PN events only)
    # 仅对有性行为内容的事件检查（NSFW: 是 或 性行为等级 > 0）
    for eid, name, fp, data in events:
        if not (eid.startswith('N') or eid.startswith('PN')):
            continue
        nsfw = data.get('NSFW', '').strip()
        has_sex = '性行为等级' in data or '性行为' in data
        sex_val = data.get('性行为等级', '') or data.get('性行为', '')
        sex_num = re.search(r'(\d+)', sex_val) if sex_val else None
        sex_level = int(sex_num.group(1)) if sex_num else 0

        # 如果有性行为等级字段或其值>0，或标记为NSFW，则检查必填字段
        if has_sex or nsfw == '是' or sex_level > 0:
            if not has_sex:
                violations.append(f'[{eid}] Rule5: 缺少必填字段「性行为等级」 — {name}')
            if '情感阶段' not in data and '情感' not in data and '阶段' not in data:
                violations.append(f'[{eid}] Rule5: 缺少必填字段「情感阶段」 — {name}')
            if sex_level > 0:
                if '黎恩知情' not in data:
                    violations.append(f'[{eid}] Rule5: 缺少必填字段「黎恩知情」 — {name}')

    # Rule 6 (去AI化): 禁止"不是...是..."对比句式
    # 该句式是AI写作的标志性废话——直接用肯定句描述，不绕弯否定再肯定。
    # 例："不是因为脏——是因为他舍不得放开" → "他舍不得放开"
    #     "不是命令不是允许，是娇羞的点头" → "她娇羞地点了点头"
    _NOT_BUT_PAT = re.compile(r'不是.{1,120}是')
    for eid, name, fp, data in events:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        body = content.split('\n', 1)
        body = body[1] if len(body) > 1 else ''
        for m in _NOT_BUT_PAT.finditer(body):
            ctx = m.group(0)[:100]
            violations.append(
                f'[{eid}] Rule6: 禁止"不是…是…"句式 — {ctx}'
            )

    # Rule 7 (NSFW写作): 禁止不良气味描写
    # 禁止体臭/骚味/体味/汗味/热气等不洁气味。
    # 清新体香、花香、草药香等干净气息可以通过。
    # 禁的是"不好闻"的气味，不是所有嗅觉描写。
    _BAD_SMELL_RE = re.compile(
        r'体臭'
        r'|骚(?:味|臭|气)'
        r'|体味(?!\s{0,2}清)'
        r'|汗(?:臭|[水渍]?味|酸|馊)'
        r'|浊(?:气|息|味)'
        r'|(?:淫|雌|发情)(?:.{0,4})(?:气|息|味)'
        r'|(?:气|息|味)(?:.{0,4})(?:淫|骚|雌)'
        r'|热(?:气|息)\s{0,3}(?:蒸|腾|散|冒|涌|扑|喷|氤|缠|裹|包)'
        r'|蒸(?:腾|发|出)(?:.{0,4})(?:味|气|息)'
        r'|腐烂(?:.{0,4})(?:味|气|息|臭)'
        r'|(?:味|气|息|臭)(?:.{0,4})腐烂'
    )
    for eid, name, fp, data in events:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        body = content.split('\n', 1)
        body = body[1] if len(body) > 1 else ''
        for m in _BAD_SMELL_RE.finditer(body):
            ctx_start = max(0, m.start() - 20)
            ctx_end = min(len(body), m.end() + 20)
            ctx = body[ctx_start:ctx_end].strip().replace('\n', ' ')[:100]
            violations.append(
                f'[{eid}] Rule7: 禁止不良气味 — "{m.group(0)}" 出现在: ...{ctx}...'
            )

    return violations


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def print_usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'validate':
        prefix = sys.argv[2] if len(sys.argv) > 2 else None
        prefixes = [prefix] if prefix else list(SECTION_CONFIG.keys())

        all_violations = []
        total = 0
        for pfx in prefixes:
            violations = validate_prefix(pfx)
            all_violations.extend(violations)
            pfx_events = list_txt_files(pfx)
            total += len(pfx_events)
            if violations:
                print(f'  {pfx}: {len(pfx_events)} events, {len(violations)} violations')
            else:
                print(f'  {pfx}: {len(pfx_events)} events OK')

        if all_violations:
            print(f'\n❌ 发现 {len(all_violations)} 个问题:\n')
            for v in all_violations:
                print(f'  {v}')
            sys.exit(1)
        else:
            print(f'\n✅ 全部验证通过 — {total} 个事件，未发现违规')

    elif cmd == 'list':
        prefix = sys.argv[2] if len(sys.argv) > 2 else None
        events = list_txt_files(prefix)
        # Group by prefix
        pfx_groups = OrderedDict()
        for eid, name, fp, data in events:
            pfx = os.path.basename(os.path.dirname(fp))
            if pfx not in pfx_groups:
                pfx_groups[pfx] = []
            pfx_groups[pfx].append((eid, name))

        for pfx in pfx_groups:
            label = SECTION_CONFIG.get(pfx, pfx)
            print(f'\n## {label} ({len(pfx_groups[pfx])}个)')
            for eid, name in pfx_groups[pfx]:
                print(f'  {eid:6s}  {name}')

        print(f'\n共 {len(events)} 个事件')

    elif cmd == 'refs':
        if len(sys.argv) < 3:
            print('用法: event_tool.py refs <event_id>')
            sys.exit(1)
        target_id = sys.argv[2]

        refs_found = []
        for eid, name, fp, data in list_txt_files():
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            # Skip the ID: line itself (first line)
            body = content.split('\n', 1)[1] if '\n' in content else ''
            # Use word-boundary-aware search
            pattern = re.compile(rf'(?<![A-Za-z0-9]){re.escape(target_id)}(?!\d)')
            for m in pattern.finditer(body):
                # Get line context
                line_start = body.rfind('\n', 0, m.start()) + 1
                line_end = body.find('\n', m.end())
                line = body[line_start:line_end] if line_end > 0 else body[line_start:]
                refs_found.append((eid, name, line.strip()[:100]))

        if refs_found:
            print(f'\n{target_id} 被 {len(refs_found)} 处引用:')
            for eid, name, ctx in refs_found:
                print(f'  [{eid}] {name}')
                print(f'        ...{ctx}...')
        else:
            print(f'\n{target_id} 无外部引用（可安全删除）')

    elif cmd == 'show':
        if len(sys.argv) < 3:
            print('用法: event_tool.py show <event_id>')
            sys.exit(1)
        event_id = sys.argv[2]

        # Search all prefixes
        found = None
        for eid, name, fp, data in list_txt_files():
            if eid == event_id:
                found = (eid, name, fp, data)
                break

        if not found:
            print(f'❌ 事件 {event_id} 未找到')
            sys.exit(1)

        eid, name, fp, data = found
        print(f'=== {eid}：{name} ===')
        print(f'文件: {fp}')
        print()
        with open(fp, 'r', encoding='utf-8') as f:
            print(f.read())

    else:
        print(f'未知命令: {cmd}')
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
