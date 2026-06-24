#!/usr/bin/env python3
"""Phase 3 RECOVERY: Fix cascaded threshold reductions.

The first reduce_thresholds.py applied replacements SEQUENTIALLY,
causing values to cascade (e.g., trust 85→70→55→40→30→22→20).
This script uses the KNOWN original values and correct single-pass mapping
to fix all thresholds to their correct reduced values.

Strategy: Map original value → correct reduced value, then find-and-replace
the most likely incorrect cascaded values with the correct ones.
"""

import re

PATH = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# ============================================================
# CORRECT SINGLE-PASS MAPPINGS (original → correct reduced)
# ============================================================

# trust_level correct mappings
TRUST_CORRECT = {
    100: 90, 95: 80, 90: 75, 88: 72, 85: 70,
    80: 65, 75: 60, 70: 55, 65: 50, 60: 45,
    55: 40, 50: 38, 45: 35, 40: 30, 35: 28,
    30: 22, 25: 20,
}

BOND_CORRECT = {
    100: 90, 90: 80, 85: 75, 82: 72, 80: 70,
    75: 65, 70: 58, 65: 55, 60: 50, 55: 48,
    50: 42, 45: 38, 40: 32, 35: 28, 30: 22, 20: 15,
}

ACCEPTANCE_CORRECT = {
    100: 76, 95: 76, 90: 72, 85: 68, 80: 64,
    75: 60, 70: 56, 65: 52, 60: 48, 50: 40,
    45: 32, 40: 32, 30: 25,
}

ABANDON_CORRECT = {
    90: 80, 70: 60, 60: 50, 50: 40, 45: 35,
    40: 30, 35: 25, 30: 20, 20: 15,
}

DESPAIR_CORRECT = {
    85: 75, 80: 70, 70: 60, 60: 50, 50: 40,
    40: 30, 30: 25, 25: 20, 20: 15, 15: 10,
}

SHARED_CORRECT = {
    90: 82, 80: 72, 70: 62, 60: 52, 50: 45,
    45: 38, 40: 35, 35: 28, 30: 25, 25: 20,
    20: 18, 15: 12, 10: 8,
}

EXPLORATION_CORRECT = {
    80: 75, 70: 65, 60: 55, 50: 45, 40: 35,
    30: 25, 25: 20, 10: 8,
}

THALION_CORRECT = {
    95: 85, 90: 80, 85: 75, 80: 70, 70: 60,
    60: 50, 55: 45, 50: 40, 40: 30, 30: 20,
}

POSSESS_CORRECT = {
    90: 82, 85: 75, 80: 70, 75: 60, 70: 58,
}

# Character goodwill
GOODWILL_CORRECT = {
    65: 60, 60: 55, 55: 50, 50: 45, 45: 40,
    40: 35, 35: 30, 30: 25,
}

# Sub-status
SUBSTATUS_CORRECT = {45: 40, 40: 35}

GEORGE_CORRECT = {50: 40, 40: 30, 30: 25}

SERENITY_CORRECT = {70: 60, 30: 25}
COURAGE_CORRECT = {40: 30}
HOPE_CORRECT = {30: 25, 20: 15}

# ============================================================
# For each variable, compute what cascaded values look like
# and map them back to the correct reduced values
# ============================================================

def compute_cascade_chain(mapping, start_val):
    """Compute where a value ends up after cascading through sequential replacements."""
    current = start_val
    while current in mapping:
        current = mapping[current]
    return current

def compute_reverse_map(mapping):
    """For each cascaded final value, list the possible correct values.
    Returns {cascaded_value: [list of (original, correct) pairs]}"""
    reverse = {}
    for orig, correct in mapping.items():
        cascaded = compute_cascade_chain(mapping, orig)
        if cascaded not in reverse:
            reverse[cascaded] = []
        reverse[cascaded].append((orig, correct))
    return reverse

# ============================================================
# Fix strategy: For each variable, find all threshold patterns,
# determine if the value is a cascaded value, and if so,
# we can't uniquely determine the original → mark for manual fix
# ============================================================

print("=== Cascade Analysis ===")
for var_name, mapping in [
    ("trust", TRUST_CORRECT),
    ("bond", BOND_CORRECT),
    ("acceptance", ACCEPTANCE_CORRECT),
    ("abandon", ABANDON_CORRECT),
    ("despair", DESPAIR_CORRECT),
    ("shared", SHARED_CORRECT),
]:
    reverse = compute_reverse_map(mapping)
    ambiguous = {k: v for k, v in reverse.items() if len(v) > 1}
    unambiguous = {k: v for k, v in reverse.items() if len(v) == 1}

    print(f"\n{var_name}: {len(unambiguous)} unambiguous, {len(ambiguous)} ambiguous cascaded values")

    if ambiguous:
        for cascaded, pairs in sorted(ambiguous.items())[:5]:
            print(f"  Cascaded value {cascaded}: could be {[(o, c) for o, c in pairs[:5]]}")

# ============================================================
# STRATEGY: Use event CONTEXT to determine correct values
# We'll match specific event names and fix their thresholds
# ============================================================

# Event → (variable, correct_reduced_value) mappings
# Based on the original threshold analysis from the transcript

# Pure Love events: trust thresholds
pure_love_fixes = {
    # Event header → (old pattern in file, replacement)
    # We'll use the event name as context and fix the trigger line

    # P1: trust 30→22 ✅ (no cascade, already correct)
    # P2: trust 50→38 ❌ cascaded: 50→38→28→22→20. Should be 38.
    '事件: 鬼之力失控后的安抚': ('trust(?:_level)? >= 22', 'trust_level >= 38'),
    # P3: trust 60→45 ❌ cascaded: 60→45→35→28→22→20. Should be 45.
    '事件: 第一次约会': ('trust(?:_level)? >= 22', 'trust_level >= 45'),
    # P4: trust 85→70 ❌ cascaded heavily. Should be 70.
    '事件: 守护者的契约': ('trust(?:_level)? >= 22', 'trust_level >= 70'),
    # P5: trust 80→65 ❌ cascaded. Should be 65.
    '事件: VII班的"正式介绍"': ('trust(?:_level)? >= 22', 'trust_level >= 65'),
    # P6: trust 80→65 ❌ Should be 65.
    '事件: 心木废墟的净化仪式前置准备': ('trust(?:_level)? >= 20', 'trust_level >= 65'),
    # P7: trust 75→60 ❌ Should be 60.
    '事件: 与Thalion的第一次正面战斗': ('trust(?:_level)? >= 22', 'trust_level >= 60'),
    # P8: trust 75→60 ❌ Should be 60.
    '事件: 温泉事件（纯爱版本）': ('trust(?:_level)? >= 22', 'trust_level >= 60'),
    # P9: trust 80→65 ❌ Should be 65.
    '事件: 守护夜——并肩作战到黎明': ('trust(?:_level)? >= 22', 'trust_level >= 65'),
    # P10: trust 85→70 ❌ Should be 70.
    '事件: 古老先灵的启示——森林意志与黎恩的作用': ('trust(?:_level)? >= 22', 'trust_level >= 70'),
    # P11: trust 90→75 ❌ Should be 75.
    '事件: 终极战斗准备——与Thalion的最终对质前夕': ('trust(?:_level)? >= 22', 'trust_level >= 75'),
    # P12: trust 90→75 ❌ Should be 75.
    '事件: 终局抉择（纯爱版本）': ('trust(?:_level)? >= 22', 'trust_level >= 75'),
    # P13: trust 85→70 ❌ Should be 70.
    '事件: P13 契约之夜（纯爱NSFW）': ('trust(?:_level)? >= 22', 'trust_level >= 70'),
    # P14: trust 80→65 ❌ Should be 65.
    '事件: P14 温泉的清晨（纯爱NSFW）': ('trust(?:_level)? >= 22', 'trust_level >= 65'),
    # P15: trust 88→72 ❌ Should be 72.
    '事件: P15 鬼之圣光交融（纯爱NSFW）': ('trust(?:_level)? >= 22', 'trust_level >= 72'),
    # P16: trust 90→75 ❌ Should be 75.
    '事件: P16 足下的誓言（纯爱NSFW）': ('trust(?:_level)? >= 22', 'trust_level >= 75'),
}

# Bond thresholds for pure love events
bond_fixes = {
    # P1: bond 20→15 ✅
    # P2: bond 30→22 ✅ (no cascade since 22 not in map)
    # P3: bond 40→32 ❌ cascaded. Should be 32.
    '事件: 第一次约会': ('bond(?:_level)? >= 15', 'bond_level >= 32'),
    # P4: bond 70→58 ❌ cascaded. Should be 58.
    '事件: 守护者的契约': ('bond(?:_level)? >= 20', 'bond_level >= 58'),
    # P5: bond 60→50 ❌ Should be 50.
    '事件: VII班的"正式介绍"': ('bond(?:_level)? >= 20', 'bond_level >= 50'),
    # P6: bond 70→58 ❌ Should be 58.
    '事件: 心木废墟的净化仪式前置准备': ('bond(?:_level)? >= 20', 'bond_level >= 58'),
    # P10: bond 70→58 ❌ Should be 58.
    '事件: 古老先灵的启示——森林意志与黎恩的作用': ('bond(?:_level)? >= 20', 'bond_level >= 58'),
    # P11: bond 85→75 ❌ Should be 75.
    '事件: 终极战斗准备——与Thalion的最终对质前夕': ('bond(?:_level)? >= 22', 'bond_level >= 75'),
    # P13: bond 75→65 ❌ cascaded: 75→65→55→48→42→?... Should be 65.
    '事件: P13 契约之夜（纯爱NSFW）': ('bond(?:_level)? >= 42', 'bond_level >= 65'),
    # P14: bond 75→65 ❌ Should be 65.
    '事件: P14 温泉的清晨（纯爱NSFW）': ('bond(?:_level)? >= 42', 'bond_level >= 65'),
    # P15: bond 82→72 ❌ Should be 72.
    '事件: P15 鬼之圣光交融（纯爱NSFW）': ('bond(?:_level)? >= 42', 'bond_level >= 72'),
    # P16: bond 85→75 ❌ Should be 75.
    '事件: P16 足下的誓言（纯爱NSFW）': ('bond(?:_level)? >= 42', 'bond_level >= 75'),
}

print("\n=== Applying Event-Specific Fixes ===")

# Apply trust fixes
for event_name, (old_pattern, replacement) in pure_love_fixes.items():
    pos = content.find(event_name)
    if pos == -1:
        print(f"  NOT FOUND: {event_name[:60]}")
        continue

    # Find the trigger condition within 500 chars after event name
    search_region = content[pos:pos+800]
    match = re.search(old_pattern, search_region)
    if match:
        # Replace only within this event's trigger
        old_text = match.group(0)
        start = pos + match.start()
        end = pos + match.end()
        content = content[:start] + replacement + content[end:]
        changes.append(f"  Trust fix: {event_name[:50]} — {old_text} → {replacement}")
    else:
        # Try finding the cascaded value
        # Look for trust >= {cascaded_value}
        trust_match = re.search(r'trust(?:_level)?\s*>=\s*(\d+)', search_region)
        if trust_match:
            current_val = trust_match.group(0)
            print(f"  TRUST MISMATCH: {event_name[:50]} — found {current_val}, expected pattern {old_pattern}")

# Apply bond fixes
for event_name, (old_pattern, replacement) in bond_fixes.items():
    pos = content.find(event_name)
    if pos == -1:
        continue

    search_region = content[pos:pos+800]
    match = re.search(old_pattern, search_region)
    if match:
        old_text = match.group(0)
        start = pos + match.start()
        end = pos + match.end()
        content = content[:start] + replacement + content[end:]
        changes.append(f"  Bond fix: {event_name[:50]} — {old_text} → {replacement}")

# Now fix acceptance cascade: acceptance >= 32 should be >= 40
# (50→40 was correct, but cascaded to 32 via 40→32)
# Only fix where original was 50 (C1-C6, N4, S11)
# These events use "acceptance >= 32" (without seraphina_ prefix)
acceptance_fixes = [
    ('事件: 玲的裸足——小恶魔的秘密', 'acceptance >= 40'),   # was 50→40
    ('事件: 亚莉莎的蕾丝——傲娇千金的告白', 'acceptance >= 40'),
    ('事件: 菲的裸足——猎兵的诚意', 'acceptance >= 40'),
    ('事件: 劳拉的白袜——骑士的荣誉', 'acceptance >= 40'),
    ('事件: 艾玛的吊带袜——魔女的私授课程', 'acceptance >= 40'),
    ('事件: 亚尔缇娜的任务——黑兔的"逻辑性服务"', 'acceptance >= 40'),
    ('事件: 丝袜之诱——角色各自的足部魅力', 'seraphina_acceptance >= 40'),
]

for event_name, correct_pattern in acceptance_fixes:
    pos = content.find(event_name)
    if pos == -1:
        print(f"  NOT FOUND: {event_name[:60]}")
        continue

    search_region = content[pos:pos+800]
    # Find acceptance >= 32 (cascaded wrong value)
    match = re.search(r'(?:seraphina_)?acceptance\s*>=\s*32', search_region)
    if match:
        old_text = match.group(0)
        start = pos + match.start()
        end = pos + match.end()
        content = content[:start] + correct_pattern + content[end:]
        changes.append(f"  Acceptance fix: {event_name[:50]} — {old_text} → {correct_pattern}")

# N4: acceptance >= 50→40, but cascaded to 32
pos = content.find('事件: 乔治的注视——NTRS情感阶段B')
if pos > 0:
    search = content[pos:pos+800]
    match = re.search(r'seraphina_acceptance\s*>=\s*32', search)
    if match:
        start = pos + match.start()
        end = pos + match.end()
        content = content[:start] + 'seraphina_acceptance >= 40' + content[end:]
        changes.append("  Acceptance fix: N4 — 32→40")

# N2: acceptance 30→25 ✅ (no cascade, 25 not in map)

# Fix despair cascades in PN series
# PN11: despair 85→75 → cascaded: 75→60→50→40→30→25→20→15→10. Final: 10!
# Should be 75
despair_fixes = [
    ('事件: PN11 堕落之夜的细节', r'(?:seraphina_)?despair\s*>=\s*\d+', 'despair >= 75'),
    ('事件: PN5 堕落之夜', r'(?:seraphina_)?despair\s*>=\s*\d+', 'despair >= 70'),  # was 80→70
    ('事件: PN13 耳边的低语', r'(?:seraphina_)?despair\s*>=\s*\d+', 'despair >= 60'),  # was 70→60
    ('事件: PN14 再次找上门', r'(?:seraphina_)?despair\s*>=\s*\d+', 'despair >= 70'),  # was 80→70
    ('事件: PN15 趁他睡着', r'(?:seraphina_)?despair\s*>=\s*\d+', 'despair >= 50'),  # was 60→50
]

for event_name, pattern, correct in despair_fixes:
    pos = content.find(event_name)
    if pos == -1:
        continue
    search = content[pos:pos+800]
    match = re.search(pattern, search)
    if match:
        old = match.group(0)
        start = pos + match.start()
        end = pos + match.end()
        content = content[:start] + correct + content[end:]
        changes.append(f"  Despair fix: {event_name[:50]} — {old} → {correct}")

# Fix abandonment cascades
abandon_fixes = [
    ('事件: PN11 堕落之夜的细节', r'abandon(?:ment(?:_count)?)?\s*>=\s*\d+', 'abandonment >= 80'),  # was 90→80
]

for event_name, pattern, correct in abandon_fixes:
    pos = content.find(event_name)
    if pos == -1:
        continue
    search = content[pos:pos+800]
    match = re.search(pattern, search)
    if match:
        old = match.group(0)
        start = pos + match.start()
        end = pos + match.end()
        content = content[:start] + correct + content[end:]
        changes.append(f"  Abandon fix: {event_name[:50]} — {old} → {correct}")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal fixes applied: {len(changes)}")
for c in changes:
    print(c)
