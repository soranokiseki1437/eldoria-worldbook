# -*- coding: utf-8 -*-
"""Insert PN8-PN17 erosion events into build_eldoria.py"""
import re

with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    md = f.read()

with open('scripts/build_eldoria.py', 'r', encoding='utf-8') as f:
    build = f.read()

# Extract PN8-PN17 event blocks
events = {}
for pn in range(8, 18):
    # Find the event block: from ### 事件PN##： to the closing ```
    start_pattern = f'### 事件PN{pn}：'
    start = md.find(start_pattern)
    if start < 0:
        print(f'PN{pn}: NOT FOUND')
        continue

    # Find the yaml block
    yaml_start = md.find('```yaml', start)
    yaml_content_start = md.find('\n', yaml_start) + 1
    yaml_end = md.find('\n```', yaml_content_start)

    if yaml_end < 0:
        print(f'PN{pn}: YAML end not found')
        continue

    yaml_body = md[yaml_content_start:yaml_end]

    # Get the title line (between ### and ```yaml)
    title_section = md[start:yaml_start]
    title_match = re.search(r'### 事件PN\d+：(.+)', title_section)
    title = title_match.group(1).strip() if title_match else f'PN{pn}'

    events[pn] = {'title': title, 'yaml': yaml_body}
    print(f'PN{pn}: {title[:70]} ({len(yaml_body)} chars)')

print(f'\nExtracted {len(events)} events')

# Generate make_entry code for each event
entries_code = []
for pn in sorted(events.keys()):
    e = events[pn]
    title = e['title']
    yaml = e['yaml']

    # Build key words
    key_words = ['被动ntr', f'pn{pn}', 'thalion', '侵蚀']
    if '甜言' in title: key_words.extend(['甜言蜜语', '言语', '孤独'])
    elif '腐蚀' in title: key_words.extend(['腐蚀', '低语', '梦境'])
    elif '药' in title: key_words.extend(['药酒', '酒精', '安神酒'])
    elif '肉体' in title: key_words.extend(['肉体', '展示', '视觉诱惑'])
    elif '手' in title: key_words.extend(['手交', '被迫', '隐奸'])
    elif '指交' in title: key_words.extend(['指交', '陷阱', '技术'])
    elif '口' in title: key_words.extend(['口交', '被迫', '干呕'])
    elif '乳' in title: key_words.extend(['乳交', '耻辱', '亵渎'])
    elif '半推半就' in title: key_words.extend(['半推半就', '临界', '体力对抗'])
    elif '无法回头' in title: key_words.extend(['无法回头', '骑虎难下', '心理审判'])

    key_str = str(key_words)

    # Build content string with proper Python escaping
    content_parts = []
    # First line is the event header
    content_parts.append(f'事件: PN{pn} {title}')
    # Then the YAML body
    for line in yaml.strip().split('\n'):
        content_parts.append(line.strip())

    # Join with \n and wrap in Python string
    content_full = '\\n'.join(content_parts)

    # Escape any double quotes in the content
    content_full = content_full.replace('"', '\\"')

    entry = f'''    # === PN{pn}: {title} ===
    entries.append(make_entry(
        uid=None,  # placeholder
        keys={key_str},
        comment="【被动NTR侵蚀】PN{pn} {title}",
        order={400 + pn * 2},
        probability=80,
        depth=4,
        content=(
            "{content_full}"
        ),
    ))
'''
    entries_code.append(entry)

# Generate the function
function_code = '''
def get_uid_pn_erosion_entries():
    """返回PN8-PN17 被动NTR Thalion侵蚀渐进事件"""
    entries = []

''' + '\n'.join(entries_code) + '''
    return entries
'''

print(function_code[:500])
print('...')

# 1. Insert function definition before get_uid211_entries
func_insert = build.find('\ndef get_uid211_entries():')
new_build = build[:func_insert] + '\n' + function_code + '\n' + build[func_insert:]

# 2. Insert function call after get_uid209_210_entries block
call_pos = new_build.find('get_uid209_210_entries()')
# Find end of the print line after this call
print_line_end = new_build.find('\n', call_pos)
next_block = new_build.find('\n    #', print_line_end + 1)

call_block = '''
    # 2r2. PN8-PN17 Thalion侵蚀渐进事件
    new_pn_erosion = get_uid_pn_erosion_entries()
    print(f"[step 2r2] 新增 PN8-PN17 (Thalion侵蚀渐进): {len(new_pn_erosion)} 条")
    all_entries.extend(new_pn_erosion)
'''
new_build = new_build[:next_block] + call_block + new_build[next_block:]

# 3. Renumber all uids contiguously
import re as re2
uid_pattern = re2.compile(r'\buid=(\d+)\b')
all_uids = sorted(set(int(m.group(1)) for m in uid_pattern.finditer(new_build)))
uid_map = {}
for new_uid, old_uid in enumerate(all_uids):
    uid_map[old_uid] = new_uid

for old_uid in sorted(uid_map.keys(), reverse=True):
    pattern = re2.compile(r'\buid=' + str(old_uid) + r'\b')
    new_build = pattern.sub(f'_UIDX_{old_uid}_', new_build)

for old_uid in sorted(uid_map.keys(), reverse=True):
    new_uid = uid_map[old_uid]
    new_build = new_build.replace(f'_UIDX_{old_uid}_', f'uid={new_uid}')

remaining = re2.findall(r'_UIDX_\d+_', new_build)
print(f'Placeholders remaining: {len(remaining)}')

# Verify
final_uids = sorted(set(int(m.group(1)) for m in uid_pattern.finditer(new_build)))
max_uid = max(final_uids)
missing = set(range(max_uid + 1)) - set(final_uids)
print(f'Uids: {len(final_uids)} entries, range [0-{max_uid}]')
none_msg = "None!"
print(f'Missing: {sorted(missing)[:10] if missing else none_msg}')

with open('scripts/build_eldoria.py', 'w', encoding='utf-8') as f:
    f.write(new_build)
print('build_eldoria.py updated!')
