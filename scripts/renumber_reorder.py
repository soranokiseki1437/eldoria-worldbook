"""
Step 1-2: Fix bugs + Extract all NTRS events + Renumber + Reorder + Write back
"""
import re

with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

# ============================================================
# OLD → NEW NUMBERING MAP
# ============================================================
old_to_new = {
    # A stage (10)
    'N1':  'N01', 'N2':  'N02', 'N5':  'N03', 'N8':  'N04',
    'N9':  'N05', 'N6':  'N06', 'N7':  'N07', 'N10': 'N08',
    'N12': 'N09', 'N3':  'N10',
    # B stage (8)
    'N21': 'N11', 'N11': 'N12', 'N13': 'N13', 'N14': 'N14',
    'N15': 'N15', 'N16': 'N16', 'N17': 'N17', 'N20': 'N18',
    # B→C stage (12)
    'N18': 'N19', 'C1':  'N20', 'N22': 'N21', 'C3':  'N22',
    'N23': 'N23', 'N25': 'N24', 'N26': 'N25', 'N27': 'N26',
    'N28': 'N27', 'N29': 'N28', 'N4':  'N29', 'N30': 'N30',
    # C stage (12)
    'N32': 'N31', 'N33': 'N32', 'C2':  'N33', 'N39': 'N34',
    'C4':  'N35', 'N40': 'N36', 'N41': 'N37', 'N42': 'N38',
    'N43': 'N39', 'N45': 'N40', 'N46': 'N41', 'N57': 'N42',
    # C→D stage (6)
    'N34': 'N43', 'C5':  'N44', 'N47': 'N45', 'C6':  'N46',
    'N48': 'N47', 'N50': 'N48',
    # D stage (8)
    'N51': 'N49', 'N53': 'N50', 'N54': 'N51', 'N55': 'N52',
    'N52': 'N53', 'N19': 'N54', 'N31': 'N55', 'H3':  'N56',
    # Finale (2)
    'N58': 'N57', 'N59': 'N58',
}

# Narrative order (old IDs) for rebuilding
narrative_order = [
    # A
    'N1','N2','N5','N8','N9','N6','N7','N10','N12','N3',
    # B
    'N21','N11','N13','N14','N15','N16','N17','N20',
    # B→C
    'N18','C1','N22','C3','N23','N25','N26','N27','N28','N29','N4','N30',
    # C
    'N32','N33','C2','N39','C4','N40','N41','N42','N43','N45','N46','N57',
    # C→D
    'N34','C5','N47','C6','N48','N50',
    # D
    'N51','N53','N54','N55','N52','N19','N31','H3',
    # Finale
    'N58','N59',
]

# Stage labels for section headers
stage_for_new = {
    'N01':'A','N02':'A','N03':'A','N04':'A','N05':'A','N06':'A','N07':'A','N08':'A','N09':'A','N10':'A',
    'N11':'B','N12':'B','N13':'B','N14':'B','N15':'B','N16':'B','N17':'B','N18':'B',
    'N19':'B→C','N20':'B→C','N21':'B→C','N22':'B→C','N23':'B→C','N24':'B→C','N25':'B→C','N26':'B→C','N27':'B→C','N28':'B→C','N29':'B→C','N30':'B→C',
    'N31':'C','N32':'C','N33':'C','N34':'C','N35':'C','N36':'C','N37':'C','N38':'C','N39':'C','N40':'C','N41':'C','N42':'C',
    'N43':'C→D','N44':'C→D','N45':'C→D','N46':'C→D','N47':'C→D','N48':'C→D',
    'N49':'D','N50':'D','N51':'D','N52':'D','N53':'D','N54':'D','N55':'D','N56':'D',
    'N57':'终局','N58':'终局',
}

print(f"Total events in narrative order: {len(narrative_order)}")

# ============================================================
# STEP 1a: Fix N51 "从P20以来" reference
# ============================================================
c = c.replace('从P20以来积累的熟练', '长久以来积累的熟练')
print('Fixed: N51 P20 reference')

# ============================================================
# STEP 1b: Delete N44 (copy-paste of N8)
# ============================================================
# Find N44 header and its entire block
n44_header = '### 事件N44：温泉夜——水汽中的足交'
i44 = c.find(n44_header)
if i44 >= 0:
    # Find next ### 事件 or ## section after N44
    n44_yaml_start = c.find('```yaml', i44)
    n44_yaml_end = c.find('```', n44_yaml_start + 7)
    # Extend to include trailing --- and whitespace
    n44_end = n44_yaml_end + 4  # after ```
    # Skip trailing newlines and ---
    after = c[n44_end:]
    after_trimmed = after.lstrip('\n\r ')
    if after_trimmed.startswith('---'):
        n44_end += len(after) - len(after_trimmed) + 3
    c = c[:i44] + c[n44_end:]
    print('Deleted: N44 (copy-paste of N8)')
else:
    print('N44 not found (may already be deleted)')

# ============================================================
# STEP 1c: Fix N34 header (currently says N34, YAML says N43)
# N34 old=温泉NTRS版 → becomes new N43 (C→D)
# The N43 old=温泉混浴 becomes new N39 (C)
# These are TWO SEPARATE events. Keep both.
# Just fix N34's header to match its YAML content (温泉晕厥)
# ============================================================
# N34 header: "### 事件N34：温泉NTRS版" → keep as-is, it's fine
# Its YAML content already correctly describes 温泉晕厥·事后告知
print('Checked: N34/N43 — two separate events, both valid')

# ============================================================
# STEP 2a: Extract all NTRS event YAML blocks
# ============================================================
extracted = {}  # old_id → {'yaml': str, 'header': str}

# Helper: find event by old ID
def find_event(content, old_id, is_c=False, is_h=False):
    """Find event block by old ID. Returns (header_text, yaml_content, start_pos, end_pos) or None"""
    if is_h:
        # H3 has header "### 事件H3：..."
        pattern = f'### 事件H3：'
    elif is_c:
        # C1-C6: multiple possible header patterns
        pattern = f'### 事件{old_id}：'
    else:
        pattern = f'### 事件{old_id}：'

    i = content.find(pattern)
    if i < 0:
        return None

    # Find the header line end
    hdr_end = content.find('\n', i)
    header = content[i:hdr_end]

    # Find yaml block
    ys = content.find('```yaml', i)
    if ys < 0: return None
    ye = content.find('```', ys + 7)
    if ye < 0: return None

    yaml_content = content[ys+7:ye].strip()

    # End position: after ``` and optional --- separator
    end = ye + 4  # after ```
    after = content[end:]
    after_trimmed = after.lstrip('\n\r ')
    if after_trimmed.startswith('---'):
        end += len(after) - len(after_trimmed) + 4  # +4 for ---\n

    return (header, yaml_content, i, end)

# Extract all events
all_old = list(old_to_new.keys())
not_found = []

for old_id in all_old:
    is_c = old_id.startswith('C')
    is_h = old_id == 'H3'
    result = find_event(c, old_id, is_c, is_h)
    if result is None:
        not_found.append(old_id)
        continue
    header, yaml, start, end = result
    extracted[old_id] = {
        'header': header,
        'yaml': yaml,
        'start': start,
        'end': end,
        'is_c': is_c,
        'is_h': is_h,
    }

if not_found:
    print(f'WARNING: Events not found: {not_found}')
print(f'Extracted {len(extracted)} events')

# ============================================================
# STEP 2b: Delete old event blocks from file (reverse order to preserve positions)
# ============================================================
# Sort by start position descending
removals = sorted(extracted.values(), key=lambda x: x['start'], reverse=True)
for r in removals:
    c = c[:r['start']] + c[r['end']:]
print(f'Removed {len(removals)} old event blocks')

# ============================================================
# STEP 2c: Build renumbered YAML for each event
# ============================================================
def renumber_yaml(yaml_text, old_id, new_id):
    """Update the 事件: field to new number"""
    # Replace first line "  事件: OLD_ID ..." → "  事件: NEW_ID ..."
    lines = yaml_text.split('\n')
    first_line = lines[0]
    # Replace old ID with new ID in the first line
    # Pattern: "  事件: NXX ..." or "  事件: C1 ..." or "  事件: H3 ..."
    new_first = re.sub(r'^(\s*事件:\s*)' + re.escape(old_id) + r'(\s.*)?$',
                       r'\1' + new_id + r'\2', first_line)
    if new_first == first_line:
        # Try without space prefix
        new_first = re.sub(r'^(事件:\s*)' + re.escape(old_id) + r'(\s.*)?$',
                           r'\1' + new_id + r'\2', first_line)
    lines[0] = new_first
    return '\n'.join(lines)

renumbered = {}
for old_id in narrative_order:
    if old_id not in extracted:
        print(f'MISSING from extracted: {old_id}')
        continue
    new_id = old_to_new[old_id]
    new_yaml = renumber_yaml(extracted[old_id]['yaml'], old_id, new_id)
    renumbered[new_id] = new_yaml

# ============================================================
# STEP 2d: Build the new ordered event block
# ============================================================
stage_labels = {
    'A': 'A阶段——探索与试探',
    'B': 'B阶段——挑逗与萌芽',
    'B→C': 'B→C阶段——过渡与深入',
    'C': 'C阶段——放开与享受',
    'C→D': 'C→D阶段——信任巅峰',
    'D': 'D阶段——极限与反转',
    '终局': '终局——确认与抉择',
}

new_block = []
new_block.append('')
new_block.append('## 四、NTRS路线事件（N01-N58·全部重编号·按叙事顺序）')
new_block.append('')
new_block.append('> **重编号日期**: 2026-06-24 | **旧编号范围**: N1-N59 + C1-C6 + H3 → **新编号**: N01-N58')
new_block.append('> **叙事顺序**: A → B → B→C → C → C→D → D → 终局')
new_block.append('')

current_stage = None
for new_id in [old_to_new[oid] for oid in narrative_order]:
    stage = stage_for_new.get(new_id, '?')
    if stage != current_stage:
        current_stage = stage
        label = stage_labels.get(stage, f'{stage}阶段')
        new_block.append(f'### {label}')
        new_block.append('')

    yaml_content = renumbered[new_id]
    new_block.append(f'### 事件{new_id}：{yaml_content.split(chr(10))[0].replace("事件: " + new_id, "").strip()}')
    new_block.append('')
    new_block.append('```yaml')
    new_block.append(yaml_content)
    new_block.append('```')
    new_block.append('')
    new_block.append('---')
    new_block.append('')

new_block_text = '\n'.join(new_block)

# ============================================================
# STEP 2e: Find insertion point & insert
# ============================================================
# Insert after the chapter mapping table, before section 五 (passive NTR)
# Find "## 五、被动NTR路线事件" or similar
insert_marker = '## 五、被动NTR路线事件'
insert_pos = c.find(insert_marker)
if insert_pos < 0:
    # Fallback: find after mapping table
    insert_pos = c.find('## 五、')

if insert_pos < 0:
    print('ERROR: Cannot find insertion point')
else:
    # Insert new block before section 五
    c = c[:insert_pos] + new_block_text + '\n\n' + c[insert_pos:]
    print(f'Inserted renumbered events at position {insert_pos}')

# ============================================================
# STEP 2f: Clean up empty section headers
# ============================================================
# Remove empty section headers from old NTRS sections
# These sections are now empty shells
empty_sections = [
    '## 十三、NTRS路线扩展事件',
    '## 十四、NTRS路线NSFW事件',
    '## 十五、NTRS路线足交事件',
    '## 十六、其他角色NSFW事件（C1-C6）',
]

for sect in empty_sections:
    i = c.find(sect)
    if i >= 0:
        # Find next ## section or the --- before it
        # Remove from the ## header to the next ##
        next_sect = c.find('\n## ', i + len(sect))
        if next_sect < 0:
            next_sect = c.find('\n---\n', i + len(sect))
        if next_sect > 0:
            # Include leading newline
            start = i
            while start > 0 and c[start-1] in '\n\r':
                start -= 1
            c = c[:start] + c[next_sect:]
            print(f'Cleaned empty section: {sect[:40]}...')

# Clean up any triple blank lines
while '\n\n\n\n' in c:
    c = c.replace('\n\n\n\n', '\n\n\n')

# ============================================================
# WRITE
# ============================================================
with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'\nDone! File: {len(c)} chars, {c.count(chr(10))} lines')
print(f'New events: N01-N58 in narrative order')
