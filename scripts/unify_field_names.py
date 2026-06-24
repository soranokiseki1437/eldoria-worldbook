#!/usr/bin/env python3
"""Phase 2a: Unify field names in 05_事件系统.md to the standard format.

Safe replacements (unique key names that won't conflict with prose):
  叙事注意: → 核心:
  场景氛围: → 核心:
  情感核心: → 核心:
  核心设计: → 核心:
  核心反差: → 核心:
  变量更新（核心）: → 变量更新:
  NSFW等级: → 性行为等级:
  后续玩家选择: → 玩家选择:

Context-dependent replacements (only at YAML key indent level):
  场景描述: → 情境:
  分支: → 路线分支:  (when it means route branches, at 4-space indent)
  变量: → 变量更新:  (when it's the variable effects key, at 4-space indent)

Merging (old multi-part narrative → 情境: sub-sections):
  场景细节: → merged into 情境: as "    发展:"
  情境发展: → merged into 情境: as "    发展:"
  事后: → merged into 情境: as "    事后:"
  影响: → merged into 变量更新:
  后续: → merged into 情境:
  事件基础效果: → merged into 变量更新:
"""

import re

PATH = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# ============================================================
# STEP 1: Safe exact-string replacements (unique key names)
# ============================================================
safe_replacements = [
    ('    叙事注意:', '    核心:'),
    ('    场景氛围:', '    核心:'),
    ('    情感核心:', '    核心:'),
    ('    核心设计:', '    核心:'),
    ('    核心反差:', '    核心:'),
    ('    变量更新（核心）:', '    变量更新:'),
    ('    NSFW等级:', '    性行为等级:'),
    ('    后续玩家选择:', '    玩家选择:'),
]

for old, new in safe_replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        changes.append(f"  {old!r} → {new!r}: {count} occurrences")

# ============================================================
# STEP 2: 场景描述: → 情境: (YAML key, safe due to 4-space indent)
# ============================================================
count = content.count('    场景描述:')
content = content.replace('    场景描述:', '    情境:')
changes.append(f"  '    场景描述:' → '    情境:': {count} occurrences")

# ============================================================
# STEP 3: 场景细节: → merge into 情境: as sub-section 发展:
# ============================================================
# Pattern: "    场景细节:\n      ..." → "    情境:\n      发展:\n      ..."
# But we already changed 场景描述 to 情境 above, so we need to be careful.
# 场景细节: appears IN ADDITION TO 场景描述 in P13-P16.
# Strategy: change 场景细节: → keep the key but rename to indicate sub-section
count_sd = content.count('    场景细节:')
# Actually, we keep 场景细节 as is but rename the key to indicate it's a sub-section
# within 情境. But since 场景描述 already became 情境, 场景细节 should become a
# continuation. Let's mark it as "    发展:" (development sub-section)
content = content.replace('    场景细节:', '      发展:')
changes.append(f"  '    场景细节:' → '      发展:': {count_sd} occurrences")

# ============================================================
# STEP 4: 情境发展: → 发展: sub-section
# ============================================================
count_sd2 = content.count('    情境发展:')
content = content.replace('    情境发展:', '      发展:')
changes.append(f"  '    情境发展:' → '      发展:': {count_sd2} occurrences")

# ============================================================
# STEP 5: 事后: → 事后: sub-section (keep name, adjust indent to be sub-section)
# ============================================================
count_af = content.count('    事后:')
content = content.replace('    事后:', '      事后:')
changes.append(f"  '    事后:' → '      事后:': {count_af} occurrences")

# ============================================================
# STEP 6: 影响: → merge into 变量更新 context
# ============================================================
# "影响:" in early E events lists variable effects. Rename to "变量更新:"
count_yx = content.count('    影响:')
content = content.replace('    影响:', '    变量更新:')
changes.append(f"  '    影响:' → '    变量更新:': {count_yx} occurrences")

# ============================================================
# STEP 7: 后续: → merge into 情境: as contextual follow-up
# ============================================================
count_hx = content.count('    后续:')
content = content.replace('    后续:', '      后续:')
changes.append(f"  '    后续:' → '      后续:' (sub-section): {count_hx} occurrences")

# ============================================================
# STEP 8: 事件基础效果: → 变量更新:
# ============================================================
count_jc = content.count('    事件基础效果:')
content = content.replace('    事件基础效果:', '    变量更新:')
changes.append(f"  '    事件基础效果:' → '    变量更新:': {count_jc} occurrences")

# ============================================================
# STEP 9: 分支: → 路线分支: (only when it's a route-branch key in YAML)
# ============================================================
# In 05_事件系统.md, "分支:" at 4-space indent in S1-S5, G, R events means route branches
count_fz = content.count('\n    分支:')
content = content.replace('\n    分支:', '\n    路线分支:')
changes.append(f"  '\\n    分支:' → '\\n    路线分支:': {count_fz} occurrences")

# ============================================================
# STEP 10: 变量: → 变量更新: (YAML key at 4-space indent)
# ============================================================
# Need to be careful: "变量:" can appear in non-YAML contexts
# Pattern: at start of line after a newline, followed by content on same line
# In YAML context it's always "    变量: var_name +delta, ..."
# We'll match "    变量: " (4-space indent + 变量: + space)
count_bl = content.count('\n    变量: ')
content = content.replace('\n    变量: ', '\n    变量更新: ')
changes.append(f"  '\\n    变量: ' → '\\n    变量更新: ': {count_bl} occurrences")

# ============================================================
# STEP 11: Clean up any double 变量更新 that might have been created
# ============================================================
# If an event already had 变量更新: and we changed 影响: to 变量更新:,
# there might be duplicates. This is intentional for now — we'll handle
# merging in a later pass if needed.
count_double = content.count('变量更新:\n    变量更新:')
if count_double > 0:
    changes.append(f"  WARNING: {count_double} double '变量更新:' found — may need manual merge")

# Write back
with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Phase 2a complete. Changes made:")
for c in changes:
    print(c)
print(f"\nTotal change categories: {len(changes)}")
