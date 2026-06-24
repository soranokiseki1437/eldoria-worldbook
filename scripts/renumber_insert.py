"""
Renumber: N48.5/N48.6/N48.7 → N49/N50/N51
Shift all subsequent N49-N58 → N52-N61
Update cross-references.
"""
import re

with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Step 1: Rename the inserted events
replacements = [
    ('N48.5', 'N49'),
    ('N48.6', 'N50'),
    ('N48.7', 'N51'),
]
for old, new in replacements:
    c = c.replace(old, new)
    print(f'{old} → {new}')

# Step 2: Shift existing N49-N58 to N52-N61
# N49→N52, N50→N53, ..., N58→N61
# Do this in reverse order (highest first) to avoid cascade
shift_map = {}
for old_num in range(58, 48, -1):  # 58 down to 49
    new_num = old_num + 3
    shift_map[f'N{old_num:02d}'] = f'N{new_num:02d}'
    shift_map[f'N{old_num}'] = f'N{new_num}'

# Build single-pass regex (reverse sorted by key length)
sorted_keys = sorted(shift_map.keys(), key=lambda x: (len(x), x), reverse=True)
pattern = r'(?<![A-Za-z0-9])(' + '|'.join(re.escape(k) for k in sorted_keys) + r')(?![0-9])'

def replace_shift(m):
    old = m.group(1)
    return shift_map.get(old, old)

# Only apply within NTRS section
ntrs_start = c.find('## 四、NTRS路线事件（N01-N58')
ntrs_end = c.find('\n## 五、', ntrs_start)
block = c[ntrs_start:ntrs_end]

new_block, n = re.subn(pattern, replace_shift, block)
c = c[:ntrs_start] + new_block + c[ntrs_end:]

print(f'Shift replacements: {n}')

# Update section header
c = c.replace(
    '## 四、NTRS路线事件（N01-N58·全部重编号·按叙事顺序）',
    '## 四、NTRS路线事件（N01-N61·全部重编号·按叙事顺序）')
c = c.replace(
    '> **重编号日期**: 2026-06-24 | **旧编号范围**: N1-N59 + C1-C6 + H3 → **新编号**: N01-N58',
    '> **重编号日期**: 2026-06-24 | **旧编号范围**: N1-N59 + C1-C6 + H3 → **新编号**: N01-N61')
c = c.replace(
    '> **叙事顺序**: A → B → B→C → C → C→D → D → 终局',
    '> **叙事顺序**: A(10) → B(8) → B→C(12) → C(12) → C→D(9) → D(8) → 终局(2)')

# Update C→D header
c = c.replace('### C→D阶段——信任巅峰（9事件·N43-N51）', '### C→D阶段——信任巅峰（9事件）')

# Update D header count
c = c.replace('### D阶段——极限与反转\n', '### D阶段——极限与反转（8事件·N52-N59）\n')

# Update 终局 header
c = c.replace('### 终局——确认与抉择\n', '### 终局——确认与抉择（2事件·N60-N61）\n')

with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'\nFinal file: {len(c)} chars, {c.count(chr(10))} lines')
print('Renumbering complete: N01-N61')

# Verify
for new_id in [f'N{n:02d}' for n in range(1, 62)]:
    if f'### 事件{new_id}：' not in c and f'事件: {new_id} ' not in c:
        print(f'  MISSING: {new_id}')
