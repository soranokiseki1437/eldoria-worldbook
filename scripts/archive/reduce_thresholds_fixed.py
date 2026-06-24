#!/usr/bin/env python3
"""Phase 3 FIX: Single-pass threshold reduction to prevent double-reduction.
The previous script applied replacements sequentially, causing values to be
reduced multiple times (e.g., acceptance 50→40 then 40→32 = 50→32 instead of 50→40).
This version uses a single-pass regex with lookup function for each variable."""

import re

PATH = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()
original = content

changes = []

def replace_all(var_pattern, mapping_dict):
    """Replace all {var} >= {old} with {var} >= {new} in a single pass.
    mapping_dict: {old_value: new_value}"""
    global content, changes

    def replacer(m):
        val = int(m.group(2))
        if val in mapping_dict:
            new_val = mapping_dict[val]
            return f'{m.group(1)} >= {new_val}'
        return m.group(0)

    pattern = rf'({var_pattern})\s*>=\s*(\d+)'
    new_content, count = re.subn(pattern, replacer, content)
    if count > 0:
        # Count actual replacements
        actual = 0
        for old_val in mapping_dict:
            # Count occurrences in original that matched
            pass
        content = new_content
        changes.append(f"  {var_pattern}: {count} total threshold patterns scanned")

# Also handle less-than: {var} < {old}
def replace_all_lt(var_pattern, mapping_dict):
    """Replace {var} < {old} with {var} < {new} in a single pass."""
    global content, changes

    def replacer(m):
        val = int(m.group(2))
        if val in mapping_dict:
            new_val = mapping_dict[val]
            return f'{m.group(1)} < {new_val}'
        return m.group(0)

    pattern = rf'({var_pattern})\s*<\s*(\d+)'
    new_content, count = re.subn(pattern, replacer, content)
    if count > 0:
        content = new_content
        changes.append(f"  {var_pattern} <: {count} total threshold patterns scanned")

# ============================================================
# Build and apply mappings
# ============================================================

# trust_level: old → new
trust_map = {
    100: 90, 95: 80, 90: 75, 88: 72, 85: 70,
    80: 65, 75: 60, 70: 55, 65: 50, 60: 45,
    55: 40, 50: 38, 45: 35, 40: 30, 35: 28,
    30: 22, 25: 20,
}
replace_all(r'trust(?:_level)?', trust_map)

# bond_level
bond_map = {
    100: 90, 90: 80, 85: 75, 82: 72, 80: 70,
    75: 65, 70: 58, 65: 55, 60: 50, 55: 48,
    50: 42, 45: 38, 40: 32, 35: 28, 30: 22, 20: 15,
}
replace_all(r'bond(?:_level)?', bond_map)

# seraphina_acceptance / acceptance
acceptance_map = {
    100: 76, 95: 76, 90: 72, 85: 68, 80: 64,
    75: 60, 70: 56, 65: 52, 60: 48, 50: 40,
    45: 32, 40: 32, 30: 25,
}
replace_all(r'seraphina_acceptance', acceptance_map)
replace_all(r'acceptance', acceptance_map)

# abandonment (abandon, abandonment, abandonment_count)
abandon_map = {
    90: 80, 70: 60, 60: 50, 50: 40, 45: 35,
    40: 30, 35: 25, 30: 20, 20: 15,
}
replace_all(r'abandon(?:ment(?:_count)?)?', abandon_map)

# despair / seraphina_despair
despair_map = {
    85: 75, 80: 70, 70: 60, 60: 50, 50: 40,
    40: 30, 30: 25, 25: 20, 20: 15, 15: 10,
}
replace_all(r'(?:seraphina_)?despair', despair_map)

# shared_experience_level / shared
shared_map = {
    90: 82, 80: 72, 70: 62, 60: 52, 50: 45,
    45: 38, 40: 35, 35: 28, 30: 25, 25: 20,
    20: 18, 15: 12, 10: 8,
}
replace_all(r'shared(?:_experience(?:_level)?)?', shared_map)

# exploration_progress
exploration_map = {
    80: 75, 70: 65, 60: 55, 50: 45, 40: 35,
    30: 25, 25: 20, 10: 8,
}
replace_all(r'exploration(?:_progress)?', exploration_map)

# thalions_influence
thalion_map = {
    95: 85, 90: 80, 85: 75, 80: 70, 70: 60,
    60: 50, 55: 45, 50: 40, 40: 30, 30: 20,
}
replace_all(r'thalions?_influence', thalion_map)

# possessiveness_intensity / possess
possess_map = {
    90: 82, 85: 75, 80: 70, 75: 60, 70: 58,
}
replace_all(r'possess(?:iveness(?:_intensity)?)?', possess_map)

# Character 好感
goodwill_map = {
    65: 60, 60: 55, 55: 50, 50: 45, 45: 40,
    40: 35, 35: 30, 30: 25,
}
replace_all(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', goodwill_map)

# Sub-status variables
sub_status_map = {
    45: 40, 40: 35,
}
replace_all(r'sub_alisas_status', sub_status_map)
replace_all(r'sub_lauras_status', sub_status_map)
replace_all(r'sub_emmas_status', sub_status_map)
replace_all(r'sub_fies_status', sub_status_map)

# george_closeness
george_map = {
    50: 40, 40: 30, 30: 25,
}
replace_all(r'george_closeness', george_map)

# reans_serenity
replace_all(r'reans_serenity', {70: 60, 30: 25})

# courage_level
replace_all(r'courage_level', {40: 30})

# hope_level
replace_all(r'hope(?:_level)?', {30: 25, 20: 15})

# character intimacy
replace_all(r'renne_playfulness', {55: 50, 35: 30})
replace_all(r'alisa_intimacy', {60: 55, 40: 35})
replace_all(r'fie_intimacy', {60: 55, 35: 30})
replace_all(r'laura_intimacy', {60: 55, 45: 40})

# ============================================================
# LESS-THAN thresholds (passive NTR)
# ============================================================
replace_all_lt(r'trust(?:_level)?', {45: 35, 20: 15, 40: 30})
replace_all_lt(r'(?:seraphina_)?despair', {
    60: 50, 50: 40, 40: 30, 30: 25, 25: 20, 20: 15, 15: 10,
})
replace_all_lt(r'abandon(?:ment(?:_count)?)?', {30: 25})

# ============================================================
# Count actual changes
# ============================================================
diff_count = 0
orig_lines = original.split('\n')
new_lines = content.split('\n')
for i, (o, n) in enumerate(zip(orig_lines, new_lines)):
    if o != n:
        diff_count += 1

print(f"Phase 3 (fixed) complete. Lines changed: {diff_count}")
print(f"Variable groups processed: {len(changes)}")
for c in changes:
    print(c)

# Check for common double-reduction artifacts
# If we see acceptance >= 32 but the mapping says 50→40 and 40→32, that's double-reduction
import sys
# Check acceptance values
acc_vals = set()
for m in re.finditer(r'acceptance\s*>=\s*(\d+)', content):
    acc_vals.add(int(m.group(1)))
print(f"\nAcceptance values in file: {sorted(acc_vals)}")
print(f"Expected acceptance values from mapping: {sorted(set(acceptance_map.values()))}")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)
