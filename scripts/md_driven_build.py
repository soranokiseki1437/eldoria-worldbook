"""
MD驱动构建：从05_事件系统.md解析NTRS事件 → 自动生成build.py条目内容
"""
import re, yaml, os

PROJECT = 'C:/Users/lx/Desktop/世界书'
MD_FILE = f'{PROJECT}/docs/05_事件系统.md'
BP_FILE = f'{PROJECT}/scripts/build_eldoria.py'

# ============================================================
# Step 1: Parse all NTRS events from md
# ============================================================
with open(MD_FILE, 'r', encoding='utf-8') as f:
    md = f.read()

ntrs_start = md.find('## 四、NTRS路线事件')
ntrs_end = md.find('\n## 五、', ntrs_start)
ntrs_section = md[ntrs_start:ntrs_end]

events = {}
for m in re.finditer(r'### 事件(N\d{2})[：:]([^\n]+)\n\n```yaml\n(.*?)\n```', ntrs_section, re.DOTALL):
    eid = m.group(1)
    title = m.group(2).strip()
    yaml_text = m.group(3)

    # Parse YAML
    try:
        data = yaml.safe_load(yaml_text)
        if not isinstance(data, dict):
            data = {}
    except:
        data = {}

    events[eid] = {
        'title': title,
        'yaml': yaml_text,
        'data': data,
    }

print(f'Parsed {len(events)} NTRS events from md: N01-N{max(int(k[1:]) for k in events):02d}')

# ============================================================
# Step 2: Build the parser function code to inject
# ============================================================
parser_code = '''
# ═══════════════════════════════════════════════════════════
# MD驱动：从05_事件系统.md读取NTRS事件内容（单源权威）
# ═══════════════════════════════════════════════════════════
import re as _re
import os as _os

_NTRS_CACHE = None

def _load_ntrs_events():
    """解析05_事件系统.md中所有NTRS事件YAML，返回 {N##: content_string}"""
    global _NTRS_CACHE
    if _NTRS_CACHE is not None:
        return _NTRS_CACHE

    md_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                             'docs', '05_事件系统.md')
    with open(md_path, 'r', encoding='utf-8') as _f:
        _md = _f.read()

    _start = _md.find('## 四、NTRS路线事件')
    _end = _md.find('\\n## 五、', _start)
    _section = _md[_start:_end] if _end > 0 else _md[_start:]

    _NTRS_CACHE = {}
    for _m in _re.finditer(r'### 事件(N\\d{2})[：:]([^\\n]+)\\n\\n```yaml\\n(.*?)\\n```', _section, _re.DOTALL):
        _eid = _m.group(1)
        _title = _m.group(2).strip()
        _yaml_text = _m.group(3)

        # Build content string from YAML fields
        try:
            import yaml as _yaml
            _data = _yaml.safe_load(_yaml_text)
            if not isinstance(_data, dict):
                _data = {}
        except:
            _data = {}

        # Auto-generate content string
        _lines = [f'【NTRS事件——{_eid}：{_title}】', '']

        # Trigger condition
        if _data.get('触发条件'):
            _lines.append(f"触发条件：{_data['触发条件']}")
        elif _data.get('触发'):
            _lines.append(f"触发条件：{_data['触发']}")

        # Sex level
        if _data.get('性行为等级'):
            _lines.append(f"性行为等级：{_data['性行为等级']}")
        elif _data.get('性行为'):
            _lines.append(f"性行为等级：{_data['性行为']}")

        # Emotion stage
        if _data.get('情感阶段'):
            _lines.append(f"情感阶段：{_data['情感阶段']}")
        elif _data.get('情感'):
            _lines.append(f"情感阶段：{_data['情感']}")

        # 黎恩知情
        if _data.get('黎恩知情'):
            _lines.append(f"黎恩知情：{_data['黎恩知情']}")

        _lines.append('')

        # Process fields to flatten
        def _flatten(val, indent=''):
            """Flatten nested YAML structures into text lines"""
            if isinstance(val, str):
                return [indent + val]
            elif isinstance(val, list):
                result = []
                for item in val:
                    result.extend(_flatten(item, indent))
                return result
            elif isinstance(val, dict):
                result = []
                for k, v in val.items():
                    if isinstance(v, (list, dict)):
                        result.append(f'{indent}{k}：')
                        result.extend(_flatten(v, indent + '  '))
                    else:
                        result.append(f'{indent}{k}：{v}')
                return result
            else:
                return [indent + str(val)]

        # 情境
        if _data.get('情境'):
            _lines.append('情境：')
            _lines.extend(_flatten(_data['情境'], '  '))

        # 占有欲确认
        if _data.get('占有欲确认'):
            _lines.append('')
            _lines.append('占有欲确认：')
            _lines.extend(_flatten(_data['占有欲确认'], '  '))

        # 玩家选择
        if _data.get('玩家选择'):
            _lines.append('')
            _lines.append('玩家选择：')
            _lines.extend(_flatten(_data['玩家选择'], '  '))

        # 变量
        if _data.get('变量'):
            _lines.append('')
            _lines.append(f"变量：{_data['变量']}")

        # 核心
        if _data.get('核心'):
            _lines.append('')
            _lines.append(f"核心：{_data['核心']}")

        _NTRS_CACHE[_eid] = '\\n'.join(_lines)

    return _NTRS_CACHE

def ntrs_content(event_id):
    """获取NTRS事件内容。event_id如'N21'"""
    events = _load_ntrs_events()
    if event_id in events:
        return events[event_id]
    raise KeyError(f'NTRS event {event_id} not found in 05_事件系统.md (available: {sorted(events.keys())})')

def ntrs_comment(event_id):
    """获取NTRS事件注释。event_id如'N21'"""
    events = _load_ntrs_events()
    # Return a short comment; full title is in content
    return f"【NTRS事件】 {event_id} — MD驱动"
'''

# ============================================================
# Step 3: Inject parser code into build.py
# ============================================================
with open(BP_FILE, 'r', encoding='utf-8') as f:
    bp = f.read()

# Find insertion point: right after the imports, before make_entry
insert_marker = 'def make_entry(uid, keys, comment, content, order,'
if parser_code.strip() not in bp:
    bp = bp.replace(insert_marker, parser_code + '\n' + insert_marker, 1)
    print('✅ Parser function injected into build.py')
else:
    print('⚠️ Parser already exists in build.py')

# ============================================================
# Step 4: Build title→event_id mapping for auto-matching
# ============================================================
title_map = {}
for eid, info in events.items():
    title_map[info['title']] = eid
    # Also add short forms
    short = info['title'].split('——')[0].strip()
    if short not in title_map:
        title_map[short] = eid

# ============================================================
# Step 5: Find all NTRS content entries in build.py and report
# ============================================================
ntrs_entries_found = []
for m in re.finditer(r'comment="【NTRS事件】\s*(N?\d+)\s*[——\-]\s*([^"]+)"', bp):
    old_num = m.group(1)
    title_hint = m.group(2)
    pos = m.start()
    # Find surrounding context
    ctx_start = max(0, pos - 300)
    ctx_end = min(len(bp), pos + 300)
    ntrs_entries_found.append({
        'old_num': old_num,
        'title_hint': title_hint,
        'pos': pos,
    })

print(f'\nFound {len(ntrs_entries_found)} NTRS-tagged entries in build.py')
for e in ntrs_entries_found:
    print(f'  old={e["old_num"]:6s}  hint={e["title_hint"][:60]}')

# ============================================================
# Step 6: Create mapping table
# This maps build.py entries → md event IDs based on title matching
# ============================================================
MAPPING = {
    # These are confirmed mappings from our earlier sync work
    # Old build.py number → correct md event ID
}

# Try auto-matching
for entry in ntrs_entries_found:
    hint = entry['title_hint']
    # Try direct title match
    matched = None
    for title, eid in title_map.items():
        if hint in title or title in hint:
            matched = eid
            break

    if matched:
        MAPPING[entry['old_num']] = matched
        print(f'  AUTO: {entry["old_num"]} → {matched} ({title_map.get(matched, "?")})')
    else:
        print(f'  NO MATCH: {entry["old_num"]} hint="{hint}"')

print(f'\nAuto-mapped {len(MAPPING)} entries')
print('\n=== Done parsing. Ready for entry-by-entry update. ===')
