"""
Full renumber: extract all NTRS events in current file order,
renumber N01-N?? sequentially, update all cross-references.
"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# === STEP 1: Find NTRS section boundaries ===
ntrs_start = c.find('## 四、NTRS路线事件')
assert ntrs_start != -1
ntrs_end = c.find('\n## 五、', ntrs_start)
assert ntrs_end != -1

pre = c[:ntrs_start]
block = c[ntrs_start:ntrs_end]
post = c[ntrs_end:]

# === STEP 2: Extract all NTRS events in order ===
# Match ### 事件N##...：... headers + their YAML blocks
event_pattern = r'(### 事件N\d{2}[.\d]*[：:][^\n]*\n+```yaml\n.+?\n```)'
events = []
for m in re.finditer(event_pattern, block, re.DOTALL):
    events.append(m.group(1))

print(f'Extracted {len(events)} NTRS events')

# === STEP 3: Parse old IDs and build mapping ===
old_ids = []
for ev in events:
    hdr = re.match(r'### 事件(N\d{2}[.\d]*)[：:]', ev)
    if hdr:
        old_ids.append(hdr.group(1))

old_to_new = {}
for i, oid in enumerate(old_ids, 1):
    new_id = f'N{i:02d}'
    old_to_new[oid] = new_id
    if oid != new_id:
        print(f'  {oid} → {new_id}')

print(f'Total: N01-N{len(events):02d}')

# === STEP 4: Rebuild the NTRS block with new numbering ===
# Stage labels
stage_map = {}
stages_order = ['A', 'B', 'BC', 'C', 'CD', 'D', 'End']
stage_ranges = {}

# Determine stages based on original position in block
# Find stage markers in the original block
stage_positions = {}
for stage_name in ['A阶段', 'B阶段', 'B→C阶段', 'C阶段', 'C→D阶段', 'D阶段', '终局']:
    pos = block.find(stage_name)
    if pos != -1:
        stage_positions[stage_name] = pos

# Assign stage based on which section the event header falls in
def get_stage_label(ev_text, ev_idx_in_block):
    # Find this event's position in the original block
    pos = block.find(ev_text.split('\n')[0])  # header line
    if pos == -1:
        return None

    # Sort stage positions by position
    sorted_stages = sorted(stage_positions.items(), key=lambda x: x[1])
    for i, (stage_name, stage_pos) in enumerate(sorted_stages):
        next_pos = sorted_stages[i+1][1] if i+1 < len(sorted_stages) else float('inf')
        if stage_pos <= pos < next_pos:
            if 'A→B' in stage_name or 'A阶段' in stage_name:
                return 'A'
            elif 'B→C' in stage_name:
                return 'BC'
            elif 'B阶段' in stage_name and 'B→C' not in stage_name:
                return 'B'
            elif 'C→D' in stage_name:
                return 'CD'
            elif 'C阶段' in stage_name and 'C→D' not in stage_name:
                return 'C'
            elif 'D阶段' in stage_name:
                return 'D'
            elif '终局' in stage_name:
                return 'End'
    return '?'

# Count events per stage for section headers
stage_labels = {
    'A': 'A阶段——探索与试探',
    'B': 'B阶段——挑逗与萌芽',
    'BC': 'B→C阶段——过渡与深入',
    'C': 'C阶段——放开与享受',
    'CD': 'C→D阶段——信任巅峰',
    'D': 'D阶段——极限与反转',
    'End': '终局——确认与抉择',
}

new_block_lines = []
new_block_lines.append('## 四、NTRS路线事件（N01-N{:02d}·按叙事顺序）'.format(len(events)))
new_block_lines.append('')
new_block_lines.append(f'> **重编号日期**: 2026-06-25 | **N01-N{len(events):02d}** | 起因补全+艾德里安引入+凯尔两段式+N25拆分')
new_block_lines.append('')

current_stage = None
for idx, (ev, oid) in enumerate(zip(events, old_ids), 1):
    new_id = f'N{idx:02d}'

    # Determine stage from section headers in original block
    stage = get_stage_label(ev, block.find(ev.split('\n')[0]))

    # Override for known events that changed stages
    if oid == 'N19':
        stage = 'BC'  # was moved to B→C

    if stage != current_stage and stage in stage_labels:
        current_stage = stage
        new_block_lines.append(f'### {stage_labels[stage]}')
        new_block_lines.append('')

    # Update the event header
    ev_lines = ev.split('\n')
    # Update header line
    ev_lines[0] = re.sub(r'### 事件N\d{2}[.\d]*[：:]', f'### 事件{new_id}：', ev_lines[0])
    # Update YAML event: line
    for j, line in enumerate(ev_lines):
        if line.strip().startswith('事件:'):
            ev_lines[j] = re.sub(r'事件:\s*N\d{2}[.\d]*\s', f'事件: {new_id} ', ev_lines[j])

    ev = '\n'.join(ev_lines)
    new_block_lines.append(ev)
    new_block_lines.append('')
    new_block_lines.append('---')
    new_block_lines.append('')

new_block = '\n'.join(new_block_lines)

# === STEP 5: Update cross-references in trigger conditions ===
# Scan the entire file for N## references in trigger lines and replace
def replace_nrefs(text, old_to_new_map):
    """Replace old N## references with new ones, protecting PN/EN prefixes"""
    # Build regex: match old IDs with word boundary protection
    sorted_old = sorted(old_to_new_map.keys(), key=len, reverse=True)  # longest first
    for oid in sorted_old:
        new_id = old_to_new_map[oid]
        if oid == new_id:
            continue
        # Match N## or N##.# not preceded by P, E, W, H, G, R, C
        pattern = r'(?<![A-Za-z])' + re.escape(oid) + r'(?=[^.\d]|$)'

        def make_replacer(nid):
            return lambda m: nid

        # Only replace in trigger/条件 lines, not in narrative text
        # But for safety, do global replacement with prefix protection
        text = re.sub(pattern, new_id, text)
    return text

# Update references in the new block itself
new_block = replace_nrefs(new_block, old_to_new)

# Update references in the REST of the file (pre and post sections)
pre = replace_nrefs(pre, old_to_new)
post = replace_nrefs(post, old_to_new)

# === STEP 6: Rebuild ===
c = pre + new_block + '\n' + post

# Clean up
while '\n\n\n\n' in c:
    c = c.replace('\n\n\n\n', '\n\n\n')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

print(f'\nWritten: {len(c)} chars')
print(f'Events: N01-N{len(events):02d}')

# Verify
final_events = re.findall(r'### 事件(N\d+)：', c)
print(f'Final event headers: {len(final_events)}')
expected = [f'N{i:02d}' for i in range(1, len(events)+1)]
missing = [e for e in expected if e not in final_events]
dupes = [e for e in final_events if final_events.count(e) > 1]
if missing: print(f'MISSING: {missing}')
if dupes: print(f'DUPES: {set(dupes)}')
if not missing and not dupes:
    print('All events present, no dupes!')
