"""Analyze NTRS events: third-party distribution and sex act types (fixed)"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    md = f.read()

ntrs_start = md.find('## 四、NTRS路线事件（N01-N58')
ntrs_end = md.find('\n## 五、', ntrs_start)
block = md[ntrs_start:ntrs_end]

events = []

# Split by ### 事件 headers
sections = re.split(r'\n(?=### 事件N\d{2}：)', block)
for sec in sections:
    hdr_match = re.match(r'### 事件(N\d{2})：(.+?)$', sec, re.M)
    if not hdr_match:
        continue
    eid = hdr_match.group(1)
    title = hdr_match.group(2).strip()

    # Extract YAML block
    yaml_match = re.search(r'```yaml\n(.+?)\n```', sec, re.DOTALL)
    if not yaml_match:
        continue
    yaml = yaml_match.group(1)

    # Extract fields
    third = ''
    sex = ''

    m3 = re.search(r'第三者:\s*(.+?)$', yaml, re.M)
    if m3: third = m3.group(1).strip()

    ms = re.search(r'性行为(?:等级)?:\s*(.+?)$', yaml, re.M)
    if ms: sex = ms.group(1).strip()

    events.append({'id': eid, 'title': title, 'third': third, 'sex': sex})

# Manually assign stages based on the known mapping
stage_map = {
    'N01':'A','N02':'A','N03':'A','N04':'A','N05':'A',
    'N06':'A','N07':'A','N08':'A','N09':'A','N10':'A',
    'N11':'B','N12':'B','N13':'B','N14':'B','N15':'B',
    'N16':'B','N17':'B','N18':'B',
    'N19':'B→C','N20':'B→C','N21':'B→C','N22':'B→C',
    'N23':'B→C','N24':'B→C','N25':'B→C','N26':'B→C',
    'N27':'B→C','N28':'B→C','N29':'B→C','N30':'B→C',
    'N31':'C','N32':'C','N33':'C','N34':'C','N35':'C',
    'N36':'C','N37':'C','N38':'C','N39':'C','N40':'C',
    'N41':'C','N42':'C',
    'N43':'C→D','N44':'C→D','N45':'C→D',
    'N46':'C→D','N47':'C→D','N48':'C→D',
    'N49':'D','N50':'D','N51':'D','N52':'D','N53':'D',
    'N54':'D','N55':'D','N56':'D',
    'N57':'终局','N58':'终局',
}

for e in events:
    e['stage'] = stage_map.get(e['id'], '?')

stages_order = ['A', 'B', 'B→C', 'C', 'C→D', 'D', '终局']

print(f'Parsed {len(events)} events')

# ===== TABLE 1 =====
print()
print('=' * 100)
print('表1：第三者（四大常驻+其他）× 阶段 —— NTRS路线事件出现频次')
print('=' * 100)

all_thirds = {}
for e in events:
    t = e['third']
    t = t.replace('——', '—').strip()
    if not t:
        t = '无（纯两人·菲娜视角）'

    # Normalize
    if '无' in t and '独属于' in t:
        t = '无（纯两人）'
    if '低语者' in t and '5' in t:
        t = '低语者×5~6'
    if '低语者' in t and '三' in t:
        t = '低语者×3'
    if '低语者' in t and '非人' in t:
        t = '低语者（单只）'
    if '可选' in t:
        t = '可选（乔治/艾德里安/凯尔）'
    if '亚莉莎劳拉菲乔治' in t:
        t = '同伴围观（不知情）'

    # Split combined thirds
    parts = re.split(r'[+＋×、]', t)
    parts = [p.strip() for p in parts if p.strip()]

    for th in parts:
        if not th: continue
        if th not in all_thirds:
            all_thirds[th] = {}
        sk = e['stage']
        all_thirds[th][sk] = all_thirds[th].get(sk, 0) + 1

# Sort: main 4 + others by total
main4 = ['凯尔', '艾德里安', '乔治', '雷恩']
others = sorted([t for t in all_thirds if t not in main4],
                key=lambda t: -sum(all_thirds[t].values()))
sorted_thirds = main4 + others

hdr = f"{'第三者':<24}"
for s in stages_order:
    hdr += f'{s:>6}'
hdr += f'{"合计":>6}'
print(hdr)
print('-' * len(hdr))

for th in sorted_thirds:
    row = f'{th:<24}'
    total = 0
    for s in stages_order:
        c = all_thirds[th].get(s, 0)
        row += f'{c:>6}'
        total += c
    row += f'{total:>6}'
    print(row)

# Total row
print('-' * len(hdr))
total_row = f'{"阶段事件数":<24}'
for s in stages_order:
    c = sum(1 for e in events if e['stage'] == s)
    total_row += f'{c:>6}'
total_row += f'{len(events):>6}'
print(total_row)

# ===== TABLE 2 =====
print()
print('=' * 100)
print('表2：性行为类型 × 阶段 —— NTRS路线频次分布')
print('=' * 100)

sex_cats = {}
for e in events:
    s = e['sex']
    cats = set()
    s_l = s

    if '轮奸' in s_l: cats.add('轮奸')
    if '群交' in s_l or '多人' in s_l: cats.add('群交/多人')
    if '隐奸' in s_l: cats.add('隐奸')
    if '插入' in s_l or '本番' in s_l or s_l.startswith('9+') or s_l.startswith('9（'):
        cats.add('插入/本番')
    if '口交' in s_l: cats.add('口交')
    if '乳交' in s_l: cats.add('乳交')
    if '手交' in s_l: cats.add('手交')
    if '足交' in s_l: cats.add('足交')
    if '指交' in s_l: cats.add('指交')
    if '摸乳' in s_l: cats.add('摸乳')
    if '舔乳' in s_l: cats.add('舔乳')
    if '蹭触' in s_l or '蹭' in s_l: cats.add('阴茎蹭触')
    if '纯情感' in s_l or s_l.startswith('0（'): cats.add('纯情感(0级)')
    if '暴露' in s_l or '注视' in s_l:
        cats.add('注视/暴露')

    if not cats:
        cats.add('(未分类)')

    sk = e['stage']
    for c in cats:
        if c not in sex_cats:
            sex_cats[c] = {}
        sex_cats[c][sk] = sex_cats[c].get(sk, 0) + 1

# Custom sex order
sex_order = ['纯情感(0级)', '注视/暴露', '摸乳', '舔乳', '阴茎蹭触',
             '足交', '手交', '指交', '口交', '乳交',
             '插入/本番', '隐奸', '群交/多人', '轮奸']
sorted_sex = [s for s in sex_order if s in sex_cats]
sorted_sex += [s for s in sex_cats if s not in sorted_sex]

hdr2 = f"{'性行为类型':<20}"
for s in stages_order:
    hdr2 += f'{s:>6}'
hdr2 += f'{"合计":>6}'
print(hdr2)
print('-' * len(hdr2))

for sx in sorted_sex:
    row = f'{sx:<20}'
    total = 0
    for s in stages_order:
        c = sex_cats[sx].get(s, 0)
        row += f'{c:>6}'
        total += c
    row += f'{total:>6}'
    print(row)

print('-' * len(hdr2))
total_row2 = f'{"事件数":<20}'
for s in stages_order:
    c = sum(1 for e in events if e['stage'] == s)
    total_row2 += f'{c:>6}'
total_row2 += f'{len(events):>6}'
print(total_row2)

# ===== PER-THIRD SEX BREAKDOWN =====
print()
print('=' * 100)
print('表3：四大第三者 × 性行为类型 — 专属事件分布')
print('=' * 100)

# Only events with exactly one of the main 4 third parties
for main in main4:
    main_events = []
    for e in events:
        t = e['third']
        if main in t and not any(m != main and m in t for m in main4):
            main_events.append(e)

    if not main_events:
        continue

    # Count sex types for this third party
    sc = {}
    for e in main_events:
        s = e['sex']
        cats = set()
        if '轮奸' in s: cats.add('轮奸')
        if '群交' in s or '多人' in s: cats.add('群交')
        if '隐奸' in s: cats.add('隐奸')
        if '插入' in s or '本番' in s or s.startswith('9+') or s.startswith('9（'): cats.add('插入')
        if '口交' in s: cats.add('口交')
        if '乳交' in s: cats.add('乳交')
        if '手交' in s: cats.add('手交')
        if '足交' in s: cats.add('足交')
        if '指交' in s: cats.add('指交')
        if '摸乳' in s: cats.add('摸乳')
        if '舔乳' in s: cats.add('舔乳')
        if '蹭触' in s: cats.add('蹭触')
        if '纯情感' in s or s.startswith('0（'): cats.add('纯情感')
        if '暴露' in s or '注视' in s: cats.add('注视')
        for c in cats:
            sc[c] = sc.get(c, 0) + 1

    types = ['注视','纯情感','摸乳','舔乳','蹭触','足交','手交','指交','口交','乳交','插入','隐奸','群交']
    total = len(main_events)
    desc = ' + '.join([f'{t}×{sc[t]}' for t in types if t in sc])
    stages = {}
    for e in main_events:
        sk = e['stage']
        stages[sk] = stages.get(sk, 0) + 1
    stage_desc = ' | '.join([f'{s}:{stages[s]}' for s in stages_order if s in stages])
    print(f'  {main:<8} ({total:>2}事件): {desc}')
    print(f'         阶段分布: {stage_desc}')
    print()
