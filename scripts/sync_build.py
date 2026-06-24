"""
Sync build_eldoria.py: replace old NTRS N-numbers in content/comment/key strings
with new N-numbers using the old→new mapping from the md renumbering.
Only replaces exact matches — if build.py uses different N-numbers than old md,
those won't match and will be left alone (safe).
"""
import re

with open('scripts/build_eldoria.py', 'r', encoding='utf-8') as f:
    build = f.read()

# Old md → New md mapping (from renumber_reorder.py)
# build.py N-numbers sometimes match old md, sometimes don't.
# Replace only where they match.
old_to_new = {
    'N1':'N01','N2':'N02','N3':'N10','N4':'N29','N5':'N03',
    'N6':'N06','N7':'N07','N8':'N04','N9':'N05','N10':'N08',
    'N11':'N12','N12':'N09','N13':'N13','N14':'N14','N15':'N15',
    'N16':'N16','N17':'N17','N18':'N19','N19':'N54','N20':'N18',
    'N21':'N11','N22':'N21','N23':'N23','N25':'N24','N26':'N25',
    'N27':'N26','N28':'N27','N29':'N28','N30':'N30','N31':'N55',
    'N32':'N31','N33':'N32','N34':'N43','N39':'N34','N40':'N36',
    'N41':'N37','N42':'N38','N43':'N39','N45':'N40','N46':'N41',
    'N47':'N45','N48':'N47','N50':'N48','N51':'N49','N52':'N53',
    'N53':'N50','N54':'N51','N55':'N52','N57':'N42','N58':'N57',
    'N59':'N58',
    'C1':'N20','C2':'N33','C3':'N22','C4':'N35','C5':'N44','C6':'N46',
    'H3':'N56',
}

changes = 0

for old_id, new_id in old_to_new.items():
    if old_id == new_id:
        continue

    # Find old_id in content strings with word-boundary-like context
    # Pattern: "【NTRS事件——OLD_ID：" or "事件: OLD_ID " or "n<old_id_lower>"

    # 1. Chinese bracket pattern
    pat1 = f'【NTRS事件——{old_id}：'
    repl1 = f'【NTRS事件——{new_id}：'
    n1 = build.count(pat1)
    if n1:
        build = build.replace(pat1, repl1)
        changes += n1
        print(f'  {pat1} → {repl1} ({n1})')

    # 2. 事件: pattern
    pat2 = f'事件: {old_id} '
    repl2 = f'事件: {new_id} '
    n2 = build.count(pat2)
    if n2:
        build = build.replace(pat2, repl2)
        changes += n2
        print(f'  {pat2} → {repl2} ({n2})')

    # 3. Comment pattern: "# === uid NNN: OLD_ID ..."
    pat3 = re.compile(r'(# === uid \d+: )' + re.escape(old_id) + r'(\s)')
    n3 = len(pat3.findall(build))
    if n3:
        build = pat3.sub(r'\1' + new_id + r'\2', build)
        changes += n3
        print(f'  comment uid: {old_id} → {new_id} ({n3})')

    # 4. keys pattern: "n01" style
    old_key = f'"{old_id.lower()}"'
    new_key = f'"{new_id.lower()}"'
    n4 = build.count(old_key)
    if n4:
        build = build.replace(old_key, new_key)
        changes += n4
        print(f'  keys {old_key} → {new_key} ({n4})')

print(f'\nTotal changes: {changes}')

with open('scripts/build_eldoria.py', 'w', encoding='utf-8') as f:
    f.write(build)

print('Build script updated (safe mode: only exact matches)')
