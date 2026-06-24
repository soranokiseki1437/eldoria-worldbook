"""
Robust full renumber V2: extract NTRS events, renumber, update all refs.
"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# === STEP 1: Find NTRS section ===
ntrs_start = c.find('## 四、NTRS路线事件')
assert ntrs_start != -1, 'NTRS section not found'
ntrs_end = c.find('\n## 五、', ntrs_start)
assert ntrs_end != -1, 'Section 五 not found'

pre = c[:ntrs_start]
block = c[ntrs_start:ntrs_end]
post = c[ntrs_end:]

# === STEP 2: Extract events within the NTRS block ===
# Match: ### 事件N##... header line followed by ```yaml ... ``` block
events = []
pattern = r'### 事件(N\d{2}[.\d]*)[：:][^\n]*\n\n```yaml\n(.*?)\n```'
for m in re.finditer(pattern, block, re.DOTALL):
    oid = m.group(1)
    yaml_body = m.group(2)
    # Get the full match text
    full = m.group(0)
    events.append({'old_id': oid, 'yaml': yaml_body, 'full': full})
    print(f'  Found: {oid}')

print(f'\nTotal: {len(events)} events')

# === STEP 3: Build old→new mapping ===
old_to_new = {}
new_to_old = {}
for i, ev in enumerate(events, 1):
    new_id = f'N{i:02d}'
    old_to_new[ev['old_id']] = new_id
    new_to_old[new_id] = ev['old_id']

# === STEP 4: Detect stage boundaries in the original block ===
# Find section headers
stage_headers = []
for m in re.finditer(r'### (A阶段|B阶段|B→C阶段|C阶段|C→D阶段|D阶段|终局)[^\n]*', block):
    stage_headers.append((m.start(), m.group(1)))

def get_stage(pos_in_block):
    """Determine stage based on position in block and nearest preceding stage header"""
    stage = 'B'  # default
    for sh_pos, sh_name in reversed(stage_headers):
        if sh_pos <= pos_in_block:
            if 'A' in sh_name and 'B' not in sh_name:
                return 'A'
            elif 'B→C' in sh_name:
                return 'BC'
            elif 'B' in sh_name and '→' not in sh_name:
                return 'B'
            elif 'C→D' in sh_name:
                return 'CD'
            elif 'C' in sh_name and '→' not in sh_name:
                return 'C'
            elif 'D' in sh_name:
                return 'D'
            elif '终局' in sh_name:
                return 'End'
    return stage

stage_labels = {
    'A': 'A阶段——探索与试探',
    'B': 'B阶段——挑逗与萌芽',
    'BC': 'B→C阶段——过渡与深入',
    'C': 'C阶段——放开与享受',
    'CD': 'C→D阶段——信任巅峰',
    'D': 'D阶段——极限与反转',
    'End': '终局——确认与抉择',
}

# === STEP 5: Rebuild the block ===
new_lines = []
new_lines.append(f'## 四、NTRS路线事件（N01-N{len(events):02d}·按叙事顺序）')
new_lines.append('')
new_lines.append(f'> **重编号日期**: 2026-06-25 | **N01-N{len(events):02d}** | 起因补全·艾德里安引入·凯尔两段式·N25拆分·全面重编号')
new_lines.append('')

current_stage = None
event_idx = 0

# Find position of each event in original block
for ev in events:
    oid = ev['old_id']
    # Find this event's position in the block
    ev_pos = block.find(f'### 事件{oid}：')
    if ev_pos == -1:
        ev_pos = block.find(f'### 事件{oid}:')
    stage = get_stage(ev_pos) if ev_pos != -1 else '?'

    if stage != current_stage and stage in stage_labels:
        current_stage = stage
        new_lines.append(f'### {stage_labels[stage]}')
        new_lines.append('')

    event_idx += 1
    new_id = f'N{event_idx:02d}'

    # Rebuild the event
    yaml = ev['yaml']
    # Update 事件: line
    yaml = re.sub(r'^(\s*事件:\s*)N\d{2}[.\d]*(\s)', r'\1' + new_id + r'\2', yaml, flags=re.M)

    # Update cross-references in trigger conditions within this YAML
    for oid2, nid2 in old_to_new.items():
        if oid2 == nid2:
            continue
        # Only in trigger-related fields (触发条件, 触发)
        yaml = re.sub(
            r'(?<![A-Za-z])' + re.escape(oid2) + r'(?=[^.\d]|$)',
            nid2, yaml
        )

    # Get title from old full text
    old_full = ev['full']
    title_match = re.match(r'### 事件' + re.escape(oid) + r'[：:](.+)', old_full)
    title = title_match.group(1) if title_match else ''

    new_lines.append(f'### 事件{new_id}：{title}')
    new_lines.append('')
    new_lines.append('```yaml')
    new_lines.append(yaml)
    new_lines.append('```')
    new_lines.append('')
    new_lines.append('---')
    new_lines.append('')

new_block = '\n'.join(new_lines)

# === STEP 6: Update cross-references in pre and post ===
def update_refs(text):
    for oid, nid in old_to_new.items():
        if oid == nid:
            continue
        text = re.sub(
            r'(?<![A-Za-z])' + re.escape(oid) + r'(?=[^.\d]|$)',
            nid, text
        )
    return text

pre = update_refs(pre)
post = update_refs(post)

# === STEP 7: Rebuild ===
c = pre + new_block + '\n' + post

while '\n\n\n\n' in c:
    c = c.replace('\n\n\n\n', '\n\n\n')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

# === STEP 8: Verify ===
print(f'\nWritten: {len(c)} chars')
final_n = re.findall(r'### 事件(N\d+)：', c)
n_only = [x for x in final_n if x.startswith('N')]
expected = [f'N{i:02d}' for i in range(1, len(events)+1)]
print(f'Found {len(n_only)} N-events')

# Check duplicates in NTRS section only
ntrs_block_new = c[c.find('## 四、NTRS'):c.find('\n## 五、', c.find('## 四、NTRS'))]
ntrs_events = re.findall(r'### 事件(N\d+)：', ntrs_block_new)
print(f'NTRS section events: {len(ntrs_events)}')
missing = [e for e in expected if e not in ntrs_events]
dupes = sorted(set([e for e in ntrs_events if ntrs_events.count(e) > 1]))
if missing:
    print(f'MISSING: {missing}')
if dupes:
    print(f'DUPES: {dupes}')
if not missing and not dupes:
    print('✓ All N01-N{:02d} present, no dupes!'.format(len(events)))
