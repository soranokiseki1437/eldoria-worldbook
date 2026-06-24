import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

ntrs_start = c.find('## 四、NTRS路线事件')
ntrs_end = c.find('\n## 五、', ntrs_start)
pre = c[:ntrs_start]
ntrs = c[ntrs_start:ntrs_end]
post = c[ntrs_end:]

# Extract all YAML blocks from NTRS section
def replace_yaml_nrefs(yaml_text):
    """Replace N## references within YAML body text, preserving structure"""
    lines = yaml_text.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip the 事件: line (keep the event's own ID)
        if stripped.startswith('事件:'):
            new_lines.append(line)
            continue
        # Replace patterns like N06→N07, N15, N26, etc.
        # But NOT when part of other identifiers
        # Pattern: N followed by 2 digits, optionally .digit, not preceded by letter
        # Remove N## references entirely (not replace — delete)
        # N06→N07两段式 → 两段式
        # 和N06雷恩的 → 和雷恩的
        line = re.sub(r'(?<![A-Za-z])N\d{2}[.\d]*→N\d{2}[.\d]*(?![.\d])', '', line)
        line = re.sub(r'(?<![A-Za-z])N\d{2}[.\d]*(?![.\d])', '', line)
        # Clean up double spaces
        line = re.sub(r'  +', ' ', line)
        new_lines.append(line)
    return '\n'.join(new_lines)

# Process each YAML block
count = 0
for m in re.finditer(r'(```yaml\n)(.*?)(\n```)', ntrs, re.DOTALL):
    old_yaml = m.group(2)
    new_yaml = replace_yaml_nrefs(old_yaml)
    if old_yaml != new_yaml:
        count += 1
    ntrs = ntrs.replace(m.group(0), m.group(1) + new_yaml + m.group(3), 1)

c = pre + ntrs + post

# Also clean up in the mapping table description line and section intro
# (but keep the table itself)

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

print(f'Stripped N## from {count} YAML blocks in NTRS section')
print('All narrative N## references replaced with …')
