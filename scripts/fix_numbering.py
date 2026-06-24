"""
Fix: 1) Remove '亚莉莎的发现' from NTRS block
     2) Fix broken core field cross-references
     3) Re-renumber N01-N67
"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# === STEP 1: Find NTRS section ===
ntrs_start = c.find('## 四、NTRS路线事件')
ntrs_end = c.find('\n## 五、', ntrs_start)
pre = c[:ntrs_start]
block = c[ntrs_start:ntrs_end]
post = c[ntrs_end:]

# === STEP 2: Extract events, SKIP '亚莉莎的发现' ===
events = []
pattern = r'### 事件(N\d+)：(.+?)\n\n```yaml\n(.*?)\n```'
for m in re.finditer(pattern, block, re.DOTALL):
    oid = m.group(1)
    title = m.group(2)
    yaml = m.group(3)
    if '亚莉莎的发现' in title:
        print(f'  REMOVED: {oid} 亚莉莎的发现')
        continue
    events.append({'old_id': oid, 'title': title, 'yaml': yaml})

print(f'Kept {len(events)} events')

# === STEP 3: Build old→new mapping ===
old_to_new = {}
for i, ev in enumerate(events, 1):
    old_to_new[ev['old_id']] = f'N{i:02d}'

print('Mapping:')
for oid, nid in old_to_new.items():
    if oid != nid:
        print(f'  {oid} → {nid}')

# === STEP 4: Also build mapping for the CORRECT NTRS old IDs ===
# The events currently have IDs from the first renumber (N01-N68, minus N01亚莉莎)
# But the core fields reference OLD old IDs from before any renumber
# We need to figure out what those references mean

# Actually, the broken refs like "N24→N24" are from the v2 renumber mishandling
# The correct approach: scan all core fields, find N## references,
# and map them to new numbers using the same old→new mapping

# === STEP 5: Fix core field cross-references ===
def fix_core_refs(yaml, o2n):
    """Replace N## references in core/核心 field with correct new numbers"""
    lines = yaml.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('核心') or stripped.startswith('排序备注'):
            # Replace old IDs with new, using word boundary protection
            for oid, nid in sorted(o2n.items(), key=lambda x: len(x[0]), reverse=True):
                if oid == nid:
                    continue
                line = re.sub(
                    r'(?<![A-Za-z])' + re.escape(oid) + r'(?=[^.\d]|$)',
                    nid, line
                )
        new_lines.append(line)
    return '\n'.join(new_lines)

# Fix each event's yaml core refs
for ev in events:
    ev['yaml'] = fix_core_refs(ev['yaml'], old_to_new)

# === STEP 6: Detect stage boundaries ===
stage_ranges = []
for m in re.finditer(r'### (A阶段——|B阶段——|B→C阶段——|C阶段——|C→D阶段——|D阶段——|终局——)', block):
    stage_ranges.append((m.start(), m.group(1)))

def get_stage(pos):
    for i in range(len(stage_ranges)-1, -1, -1):
        if stage_ranges[i][0] <= pos:
            s = stage_ranges[i][1]
            if 'B→C' in s: return 'BC'
            if 'C→D' in s: return 'CD'
            if 'A' in s: return 'A'
            if 'B' in s: return 'B'
            if 'C' in s: return 'C'
            if 'D' in s: return 'D'
            if '终局' in s: return 'End'
    return '?'

stage_labels = {
    'A': 'A阶段——探索与试探',
    'B': 'B阶段——挑逗与萌芽',
    'BC': 'B→C阶段——过渡与深入',
    'C': 'C阶段——放开与享受',
    'CD': 'C→D阶段——信任巅峰',
    'D': 'D阶段——极限与反转',
    'End': '终局——确认与抉择',
}

# === STEP 7: Rebuild ===
new_lines = []
new_lines.append(f'## 四、NTRS路线事件（N01-N{len(events):02d}·按叙事顺序）')
new_lines.append('')
new_lines.append(f'> **重编号日期**: 2026-06-25 | **N01-N{len(events):02d}** | 起因补全·艾德里安引入·凯尔两段式·N25拆分·修复版')
new_lines.append('')

# Find position of each event in original block for stage detection
current_stage = None
for idx, ev in enumerate(events, 1):
    new_id = f'N{idx:02d}'
    pos = block.find(f'### 事件{ev["old_id"]}：{ev["title"]}')
    stage = get_stage(pos) if pos != -1 else '?'

    if stage != current_stage and stage in stage_labels:
        current_stage = stage
        new_lines.append(f'### {stage_labels[stage]}')
        new_lines.append('')

    yaml = ev['yaml']
    # Update 事件: line
    yaml = re.sub(r'^(\s*事件:\s*)N\d{2}[.\d]*(\s)', r'\1' + new_id + r'\2', yaml, flags=re.M)
    # Update cross-refs in trigger conditions
    for oid2, nid2 in old_to_new.items():
        if oid2 == nid2: continue
        yaml = re.sub(r'(?<![A-Za-z])' + re.escape(oid2) + r'(?=[^.\d]|$)', nid2, yaml)

    new_lines.append(f'### 事件{new_id}：{ev["title"]}')
    new_lines.append('')
    new_lines.append('```yaml')
    new_lines.append(yaml)
    new_lines.append('```')
    new_lines.append('')
    new_lines.append('---')
    new_lines.append('')

new_block = '\n'.join(new_lines)

# === STEP 8: Update cross-refs in pre and post ===
def update_refs(text):
    for oid, nid in sorted(old_to_new.items(), key=lambda x: len(x[0]), reverse=True):
        if oid == nid: continue
        text = re.sub(r'(?<![A-Za-z])' + re.escape(oid) + r'(?=[^.\d]|$)', nid, text)
    return text

pre = update_refs(pre)
post = update_refs(post)

c = pre + new_block + '\n' + post
while '\n\n\n\n' in c: c = c.replace('\n\n\n\n', '\n\n\n')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

# === STEP 9: Verify ===
ntrs_new = c[c.find('## 四、NTRS'):c.find('\n## 五、', c.find('## 四、NTRS'))]
final_events = re.findall(r'### 事件(N\d+)：', ntrs_new)
expected = [f'N{i:02d}' for i in range(1, len(events)+1)]
missing = [e for e in expected if e not in final_events]
dupes = sorted(set([e for e in final_events if final_events.count(e) > 1]))

print(f'\nNTRS events: {len(final_events)}')
if missing: print(f'MISSING: {missing}')
if dupes: print(f'DUPES: {dupes}')
if not missing and not dupes:
    print(f'✓ All N01-N{len(events):02d} present, no dupes!')

# Check for remaining broken refs
broken = re.findall(r'N\d+→N\d+', ntrs_new)
print(f'Core refs with →: {len(broken)}')
for b in broken[:10]:
    print(f'  {b}')
