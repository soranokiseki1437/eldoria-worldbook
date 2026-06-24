"""Step 3: Update NTRS cross-references — single-pass atomic replacement"""
import re

with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Find NTRS section boundaries
ntrs_start = c.find('## 四、NTRS路线事件（N01-N58')
ntrs_next = c.find('\n## 五、', ntrs_start)
if ntrs_next < 0:
    ntrs_next = len(c)

ntrs_block = c[ntrs_start:ntrs_next]

# Old→New mapping (sorted by old ID length descending for regex building)
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
}

# Build regex: match any old N-ID with word-boundary protection
# Sort keys longest-first so N10 matches before N1
sorted_old = sorted(old_to_new.keys(), key=len, reverse=True)
pattern = r'(?<![A-Za-z0-9])(' + '|'.join(re.escape(k) for k in sorted_old) + r')(已触发|已完成|已(?!触|完成))'

def replace_ref(m):
    old_id = m.group(1)
    suffix = m.group(2)
    new_id = old_to_new.get(old_id, old_id)
    return new_id + suffix

new_block, changes = re.subn(pattern, replace_ref, ntrs_block)

c = c[:ntrs_start] + new_block + c[ntrs_next:]

print(f'Total replacements: {changes}')

# Verify no cascade issues
for old_id, new_id in old_to_new.items():
    if old_id == new_id:
        continue
    remaining = re.findall(r'(?<![A-Za-z0-9])' + re.escape(old_id) + r'(?:已触发|已完成|已(?!触|完成))', new_block)
    if remaining:
        print(f'  REMAINING: {old_id} in {remaining}')

with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(c)

print('Cross-references updated — single-pass atomic, PN series untouched')
