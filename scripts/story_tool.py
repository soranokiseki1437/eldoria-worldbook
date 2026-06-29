#!/usr/bin/env python3
"""
story_tool.py — 章节验证与查看工具 (V10.3 — TXT文件驱动)

用法:
  python story_tool.py validate              # 验证全部TXT章节
  python story_tool.py list                  # 列出所有章节ID+标题
  python story_tool.py show <chapter_id>     # 显示单个章节TXT内容
  python story_tool.py refs <chapter_id>     # 查找所有引用了该章节ID的TXT文件

验证规则:
  Rule1: 禁止事件编号引用（叙事文本中不得出现纯数字事件ID）
  Rule2: 第三者间不得互通性行为进度
  Rule4: Seraphina发色检查（粉色非银色）
  Rule5: 必填字段检查（ID/名称/NSFW/情境/核心）
  Rule6: 禁止否定迂回句式（不是/不再/并非…是… / 没有…只是… / 没有…没有…）
  Rule7: 禁止不良气味描写
  Rule8: 好感值上限检查（单角色单事件≤10）
  Rule9: 阶段字段值合法性（8个合法阶段名）

设计原则:
  - 操作对象: docs/story/{章节}/*.TXT 文件
  - 增删改移章节请操作TXT文件，然后运行 renumber_events.py
"""

import re
import os
import sys
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')

from story_config import SECTION_TITLES as SECTION_CONFIG

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
    # V9.0: 事件编号为纯数字01-170。匹配2-3位数字（排除明显非事件引用的上下文）。
    _EVENT_ID_RE = re.compile(
        r'(?<![A-Za-z0-9])'
        r'(?:'
        r'0[1-9]'              # 01-09 (zero-padded)
        r'|[1-9]\d'             # 10-99
        r'|1[0-6]\d'            # 100-169
        r'|170'                 # 170
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
            ref = m.group(0)
            if ref.lstrip('0') == eid.lstrip('0'):
                continue  # 自身ID不报
            # 提取上下文行
            line_start = body.rfind('\n', 0, m.start()) + 1
            line_end = body.find('\n', m.end())
            ctx_line = body[line_start:line_end] if line_end > 0 else body[line_start:]
            ctx = ctx_line.strip()[:120]
            # 排除非事件引用的数字语境
            wider_ctx = body[max(0, m.start()-10):min(len(body), m.end()+10)]
            pre_ctx = body[max(0, m.start()-6):m.start()]
            post_ctx = body[m.end():min(len(body), m.end()+3)]
            # 全局排除"69"——在NSFW写作中永远是性行为体位，非事件编号引用
            if ref in ('69', '069'):
                continue
            if re.search(r'[第级等LVlv]\s*$', pre_ctx):
                continue  # "第X" / "等级X" / "LV.X"
            if re.search(r'^[章级人号名个次种条件句\)\]）\s]', post_ctx):
                continue  # "X章" "X级" "X人" "X个"
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

    # Rule 5: 必填字段检查（所有事件）
    # V9.0必填: ID, 名称, NSFW, 情境, 核心
    # 条件字段: 性行为等级(NSFW=是时), 阶段, 第三者, 黎恩知情, 占有欲确认, 好感影响
    REQUIRED_FIELDS = ['ID', '名称', 'NSFW', '情境', '核心']
    for eid, name, fp, data in events:
        for field in REQUIRED_FIELDS:
            if field not in data or not data[field].strip():
                violations.append(
                    f'[{eid}] Rule5: 缺少必填字段「{field}」 — {name}'
                )
        # NSFW事件应有性行为等级
        nsfw = data.get('NSFW', '').strip()
        if nsfw == '是' and '性行为等级' not in data:
            violations.append(
                f'[{eid}] Rule5: NSFW事件缺少「性行为等级」 — {name}'
            )

    # Rule 6 (去AI化): 禁止否定迂回句式
    # 6a. "不是/不再/并非…是/而是…" — 用否定衬托肯定的迂回写法
    #     例："不是因为脏——是因为他舍不得放开" → "他舍不得放开"
    #         "不再对抗，而是融合" → "交融在一起"
    # 6b. "没有…只是…" — 先否定再轻微转折，同样是迂回
    #     例："她没有问为什么。只是微微低下头" → "她微微低下头"
    # 6c. "没有…没有…" — 成对否定（建议审视，可能为AI修辞惯性）
    #     例："没有声音，没有动作" → "寂静。静止。"
    _NEG_AFFIRM_PATS = [
        re.compile(r'不是.{1,150}是'),                  # 不是X是Y / 不是X而是Y
        re.compile(r'不再.{1,150}是'),                  # 不再是X(而)是Y
        re.compile(r'并非.{1,150}是'),                  # 并非X(而)是Y
        re.compile(r'没有.{1,80}只是'),                 # 没有X只是Y
    ]
    _DOUBLE_NEG_RE = re.compile(r'没有.{1,30}没有')      # 没有X没有Y（紧密成对）

    for eid, name, fp, data in events:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        body = content.split('\n', 1)
        body = body[1] if len(body) > 1 else ''

        # 6a/6b: 迂回肯定 + 否定后转折
        for pat in _NEG_AFFIRM_PATS:
            for m in pat.finditer(body):
                ctx = m.group(0)[:100]
                violations.append(
                    f'[{eid}] Rule6: 禁止否定迂回句式 — {ctx}'
                )

        # 6c: 成对否定（警告级别）
        for m in _DOUBLE_NEG_RE.finditer(body):
            ctx = m.group(0)[:100]
            violations.append(
                f'[{eid}] Rule6c: 成对否定（建议审视是否可改为肯定描写） — {ctx}'
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

    # Rule 8: 好感值上限检查 — 单角色单事件 ≤ 10
    for eid, name, fp, data in events:
        affection = data.get('好感影响', '')
        if not affection.strip():
            continue
        # Parse lines like "  - Seraphina: +10" or "  - 凯尔: +8"
        for line in affection.split('\n'):
            line = line.strip().lstrip('-').strip()
            m = re.match(r'^(.+?)[：:]\s*([+-]?\d+)', line)
            if m:
                char_name = m.group(1).strip()
                value = int(m.group(2))
                if abs(value) > 10:
                    violations.append(
                        f'[{eid}] Rule8: 好感值超标 — {char_name}: {value} (上限±10) — {name}'
                    )

    # Rule 9: 阶段字段值合法性检查
    VALID_STAGES = {
        '序章', '试探和暧昧', '挑逗和接受', '渐进接触',
        '跨线', '享受和掌控', '放纵', '终局', '后日谈',
    }
    for eid, name, fp, data in events:
        stage = data.get('阶段', '').strip()
        if not stage:
            continue  # 阶段可留空（非NTRS事件）
        if stage not in VALID_STAGES:
            violations.append(
                f'[{eid}] Rule9: 非法阶段值 — "{stage}" (合法: {", ".join(sorted(VALID_STAGES))}) — {name}'
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
                print(f'  {pfx}: {len(pfx_events)} chapters, {len(violations)} violations')
            else:
                print(f'  {pfx}: {len(pfx_events)} chapters OK')

        if all_violations:
            print(f'\n❌ 发现 {len(all_violations)} 个问题:\n')
            for v in all_violations:
                print(f'  {v}')
            sys.exit(1)
        else:
            print(f'\n✅ 全部验证通过 — {total} 个章节，未发现违规')

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

        print(f'\n共 {len(events)} 个章节')

    elif cmd == 'refs':
        if len(sys.argv) < 3:
            print('用法: story_tool.py refs <chapter_id>')
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
            print('用法: story_tool.py show <chapter_id>')
            sys.exit(1)
        event_id = sys.argv[2]

        # Search all prefixes
        found = None
        for eid, name, fp, data in list_txt_files():
            if eid == event_id:
                found = (eid, name, fp, data)
                break

        if not found:
            print(f'❌ 章节 {event_id} 未找到')
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
