#!/usr/bin/env python3
"""Phase 3: Comprehensive trigger threshold reduction in 05_事件系统.md.

Applies systematic reductions to all variable thresholds per the plan.
Uses regex to find variable>=value patterns and replace with new values.
"""

import re

PATH = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

def replace_threshold(var_pattern, old_val, new_val):
    """Replace 'var_pattern >= old_val' with 'var_pattern >= new_val'.
    var_pattern matches variable name variants (trust, trust_level, etc.)"""
    global content, changes
    # Pattern: variable_name >= old_val (possibly with spaces, maybe followed by comma/space/newline)
    pattern = rf'({var_pattern})\s*>=\s*{old_val}(?=\s*[,/\n]|$)'
    replacement = rf'\1 >= {new_val}'
    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        content = new_content
        changes.append(f"  {var_pattern} >= {old_val} → >= {new_val}: {count} occurrences")

def replace_threshold_lt(var_pattern, old_val, new_val):
    """Replace '< old_val' patterns (used in passive NTR)."""
    global content, changes
    pattern = rf'({var_pattern})\s*<\s*{old_val}(?=\s*[,/\n]|$)'
    replacement = rf'\1 < {new_val}'
    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        content = content
        changes.append(f"  {var_pattern} < {old_val} → < {new_val}: {count} occurrences")

# ============================================================
# TRUST_LEVEL (and trust, trust_level variants)
# ============================================================
trust_map = [
    (100, 90), (95, 80), (90, 75), (88, 72), (85, 70),
    (80, 65), (75, 60), (70, 55), (65, 50), (60, 45),
    (55, 40), (50, 38), (45, 35), (40, 30), (35, 28),
    (30, 22), (25, 20),
]
for old, new in trust_map:
    replace_threshold(r'trust(?:_level)?', old, new)

# ============================================================
# BOND_LEVEL (bond, bond_level)
# ============================================================
bond_map = [
    (100, 90), (85, 75), (82, 72), (80, 70), (75, 65),
    (70, 58), (65, 55), (60, 50), (55, 48), (50, 42),
    (40, 32), (35, 28), (30, 22), (20, 15),
]
for old, new in bond_map:
    replace_threshold(r'bond(?:_level)?', old, new)

# ============================================================
# SERAPHINA_ACCEPTANCE
# ============================================================
acceptance_map = [
    (100, 76), (95, 76), (90, 72), (85, 68), (80, 64),
    (75, 60), (70, 56), (65, 52), (60, 48), (50, 40),
    (45, 32), (40, 32), (30, 25),
]
for old, new in acceptance_map:
    replace_threshold(r'seraphina_acceptance', old, new)
    replace_threshold(r'acceptance', old, new)  # shorthand used in some YAML

# ============================================================
# ABANDONMENT_COUNT (abandonment, abandonment_count, abandon)
# ============================================================
abandon_map = [
    (90, 80), (70, 60), (60, 50), (50, 40), (45, 35),
    (40, 30), (35, 25), (30, 20), (20, 15),
]
for old, new in abandon_map:
    replace_threshold(r'abandon(?:ment(?:_count)?)?', old, new)

# ============================================================
# SERAPHINA_DESPAIR (despair, seraphina_despair)
# ============================================================
despair_map = [
    (85, 75), (80, 70), (70, 60), (60, 50), (50, 40),
    (40, 30), (30, 25), (25, 20), (20, 15), (15, 10),
]
for old, new in despair_map:
    replace_threshold(r'(?:seraphina_)?despair', old, new)

# ============================================================
# SHARED_EXPERIENCE_LEVEL (shared, shared_experience_level)
# Note: NOT reducing band thresholds (0-20/20-50/50-80/80-100 stay)
# Only reducing granular thresholds within events
# ============================================================
shared_map = [
    # Only reduce the granular event-level thresholds, not the band boundaries
    # 35 → 28, 45 → 38, etc. (minor adjustments)
    (90, 82),  # N14 from 90→82 (slight reduction)
    (80, 72),  # N7, N13 from 80→72
    (70, 62),  # N12 from 70→62
    (60, 52),  # S36 from 60→52
    # Keep 50 as boundary
    (45, 38),  # S14 variant
    (40, 35),  # S10
    (35, 28),  # N5.5, S15
    (30, 25),  # S11, S13
    (25, 20),  # N4.5
    (15, 12),  # N3.5
    (10, 8),   # N3
]
for old, new in shared_map:
    replace_threshold(r'shared(?:_experience(?:_level)?)?', old, new)

# ============================================================
# EXPLORATION_PROGRESS
# ============================================================
exploration_map = [
    (80, 75), (70, 65), (60, 55), (50, 45), (40, 35),
    (30, 25), (25, 20), (10, 8),
]
for old, new in exploration_map:
    replace_threshold(r'exploration(?:_progress)?', old, new)

# ============================================================
# CORRUPTION_LEVEL — UNCHANGED (world balance)
# ============================================================

# ============================================================
# THALIONS_INFLUENCE
# ============================================================
thalion_map = [
    (95, 85), (90, 80), (85, 75), (80, 70), (70, 60),
    (60, 50), (55, 45), (50, 40), (40, 30), (30, 20),
]
for old, new in thalion_map:
    replace_threshold(r'thalions?_influence', old, new)

# ============================================================
# POSSESSIVENESS_INTENSITY
# ============================================================
possess_map = [
    (90, 80), (85, 75), (80, 70), (70, 60),
]
for old, new in possess_map:
    replace_threshold(r'possess(?:iveness(?:_intensity)?)?', old, new)

# ============================================================
# CHARACTER-SPECIFIC THRESHOLDS (好感度)
# ============================================================
# Renne
replace_threshold(r'renne_playfulness', 55, 50)
replace_threshold(r'renne_playfulness', 35, 30)
# Alisa
replace_threshold(r'alisa_intimacy', 60, 55)
replace_threshold(r'alisa_intimacy', 40, 35)
# Fie
replace_threshold(r'fie_intimacy', 60, 55)
replace_threshold(r'fie_intimacy', 35, 30)
# Laura
replace_threshold(r'laura_intimacy', 60, 55)
replace_threshold(r'laura_intimacy', 45, 40)
# Emma
replace_threshold(r'(?:emma|sub_emmas)', 45, 40)
# 好感 (general affection)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 65, 60)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 60, 55)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 55, 50)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 50, 45)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 45, 40)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 40, 35)
replace_threshold(r'(?:玲|亚莉莎|菲|劳拉|艾玛|亚尔缇娜)好感', 35, 30)

# ============================================================
# SUB-STATUS THRESHOLDS
# ============================================================
replace_threshold(r'sub_alisas_status', 40, 35)
replace_threshold(r'sub_lauras_status', 40, 35)
replace_threshold(r'sub_emmas_status', 45, 40)
replace_threshold(r'sub_fies_status', 40, 35)
replace_threshold(r'george_closeness', 50, 40)
replace_threshold(r'george_closeness', 40, 30)
replace_threshold(r'george_closeness', 30, 25)

# ============================================================
# COURAGE_LEVEL
# ============================================================
replace_threshold(r'courage_level', 40, 30)

# ============================================================
# REANS_SERENITY
# ============================================================
replace_threshold(r'reans_serenity', 70, 60)
replace_threshold(r'reans_serenity', 30, 25)

# ============================================================
# HOPE_LEVEL
# ============================================================
# Only minor reductions; hope is a secondary indicator
replace_threshold(r'hope(?:_level)?', 30, 25)
replace_threshold(r'hope(?:_level)?', 20, 15)

# ============================================================
# PASSIVE NTR INVERTED THRESHOLDS (trust < X)
# ============================================================
# PN1: trust < 45 → trust < 35
replace_threshold_lt(r'trust(?:_level)?', 45, 35)
# PN5: trust < 20 → trust < 15
replace_threshold_lt(r'trust(?:_level)?', 20, 15)
# Various despair thresholds that use < (inverted)
replace_threshold_lt(r'(?:seraphina_)?despair', 60, 50)
replace_threshold_lt(r'(?:seraphina_)?despair', 50, 40)
replace_threshold_lt(r'(?:seraphina_)?despair', 40, 30)
replace_threshold_lt(r'(?:seraphina_)?despair', 30, 25)
replace_threshold_lt(r'(?:seraphina_)?despair', 25, 20)
replace_threshold_lt(r'(?:seraphina_)?despair', 20, 15)
replace_threshold_lt(r'(?:seraphina_)?despair', 15, 10)

# ============================================================
# CORRUPTION LEVEL — Unchanged
# ============================================================

# Write
with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Phase 3 complete. Total change categories: {len(changes)}")
for c in changes[:30]:
    print(c)
if len(changes) > 30:
    print(f"... and {len(changes)-30} more change categories")
