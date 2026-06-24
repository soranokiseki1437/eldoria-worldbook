#!/usr/bin/env python3
"""Insert N61 into the sequence: N61→N17, shift N17-N58 → N18-N59.
Uses placeholder approach to avoid conflicts."""
import re

TARGET = r'C:\Users\lx\Desktop\世界书\docs\05_事件系统.md'

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Replace old N17-N58 with placeholders (descending to avoid conflicts)
# N61 also gets a placeholder
shifts = list(range(17, 59))  # N17-N58 → N18-N59
special = 61  # N61 → N17

# Phase 1: Old→placeholder
for old in sorted(shifts + [special], reverse=True):
    if old == special:
        new = 17
    else:
        new = old + 1
    placeholder = f'N__SHIFT_{old}_TO_{new}__'
    pattern = rf'(?<![0-9A-Z])N{old}(?![0-9])'
    content = re.sub(pattern, placeholder, content)

# Phase 2: Placeholder→new
for old in shifts + [special]:
    if old == special:
        new = 17
    else:
        new = old + 1
    placeholder = f'N__SHIFT_{old}_TO_{new}__'
    content = content.replace(placeholder, f'N{new}')

with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

found = sorted(set(int(m.group(1)) for m in re.finditer(r'### 事件N(\d+)：', content)))
print(f"Headers: {found}")
print(f"Count: {len(found)}")

# Check for N61 residue
n61 = len(re.findall(r'(?<![0-9A-Z])N61(?![0-9])', content))
print(f"N61 residues: {n61}")

# Check for N17
n17_headers = re.findall(r'### 事件N17：.*', content)
print(f"N17 headers: {n17_headers}")
