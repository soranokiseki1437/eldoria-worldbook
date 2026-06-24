"""Simple NTRS scarcity analysis"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    md = f.read()

ntrs_start = md.find('## 四、NTRS路线事件（N01-N61')
ntrs_end = md.find('\n## 五、', ntrs_start)
block = md[ntrs_start:ntrs_end]

events = []
for m in re.finditer(r'### 事件(N\d{2})：(.+?)\n\n```yaml\n(.+?)\n```', block, re.DOTALL):
    eid = m.group(1)
    yaml = m.group(3)
    third = ''
    sex = ''
    m3 = re.search(r'第三者:\s*(.+?)$', yaml, re.M)
    if m3: third = m3.group(1).strip()
    ms = re.search(r'性行为(?:等级)?:\s*(.+?)$', yaml, re.M)
    if ms: sex = ms.group(1).strip()
    events.append({'id': eid, 'third': third, 'sex': sex})

# Simplified stage map
stage_map = {
    'N01':'A','N02':'A','N03':'A','N04':'A','N05':'A','N06':'A','N07':'A','N08':'A','N09':'A','N10':'A',
    'N11':'B','N12':'B','N13':'B','N14':'B','N15':'B','N16':'B','N17':'B','N18':'B',
    'N19':'BC','N20':'BC','N21':'BC','N22':'BC','N23':'BC','N24':'BC','N25':'BC','N26':'BC','N27':'BC','N28':'BC','N29':'BC','N30':'BC',
    'N31':'C','N32':'C','N33':'C','N34':'C','N35':'C','N36':'C','N37':'C','N38':'CD','N39':'C','N40':'C','N41':'C','N42':'C',
    'N43':'CD','N44':'CD','N45':'CD','N46':'CD','N47':'CD','N48':'CD','N49':'CD','N50':'CD','N51':'CD',
    'N52':'D','N53':'D','N54':'D','N55':'D','N56':'D','N57':'D','N58':'D','N59':'D',
    'N60':'终','N61':'终',
}

stages_order = ['A','B','BC','C','CD','D','终']

# ===== TABLE 1: Third party =====
print('=' * 80)
print('表1：第三者分布')
print('=' * 80)

third_count = {}
third_stage = {}
for e in events:
    t = e['third'].strip()
    if not t: t = '无'
    # normalize
    t = t.replace('——','—')
    if '无——独属于' in t: t = '无(纯两人)'
    if '低语者' in t and '5' in t: t = '低语者×5~6'
    if '低语者' in t and '三' in t: t = '低语者×3'
    if '低语者' in t and '非人' in t: t = '低语者(单)'
    if '可选' in t: t = '可选(三选一)'
    if '亚莉莎劳拉' in t: t = '同伴围观'
    if '迷路旅人' in t: t = '陌生人'

    parts = re.split(r'[+＋×]', t)
    for th in parts:
        th = th.strip()
        if not th: continue
        third_count[th] = third_count.get(th, 0) + 1
        if th not in third_stage: third_stage[th] = {}
        sk = stage_map.get(e['id'], '?')
        third_stage[th][sk] = third_stage[th].get(sk, 0) + 1

# Main 4 + others
main4 = ['凯尔','艾德里安','乔治','雷恩']
sorted_t = main4 + sorted([t for t in third_count if t not in main4], key=lambda t: -third_count[t])

print(f'{\"第三者\":<20} {\"合计\":>4}  A  B BC  C CD  D 终')
print('-' * 45)
for th in sorted_t:
    total = third_count[th]
    row = f'{th:<20} {total:>4}'
    for s in stages_order:
        row += f'{third_stage[th].get(s,0):>3}'
    print(row)

# ===== TABLE 2: Sex types =====
print()
print('=' * 80)
print('表2：性行为类型分布')
print('=' * 80)

sex_count = {}
sex_stage = {}
for e in events:
    s = e['sex']
    cats = set()
    if '轮奸' in s: cats.add('轮奸')
    if '群交' in s or '多人' in s: cats.add('群交/多人')
    if '隐奸' in s: cats.add('隐奸')
    if '插入' in s or '本番' in s or s.startswith('9+') or s.startswith('9（'):
        cats.add('插入/本番')
    if '口交' in s: cats.add('口交')
    if '乳交' in s: cats.add('乳交')
    if '手交' in s: cats.add('手交')
    if '足交' in s: cats.add('足交')
    if '指交' in s: cats.add('指交')
    if '摸乳' in s: cats.add('摸乳')
    if '舔乳' in s: cats.add('舔乳')
    if '蹭触' in s or '蹭' in s: cats.add('蹭触')
    if '纯情感' in s or s.startswith('0（'): cats.add('纯情感')
    if '暴露' in s or '注视' in s: cats.add('注视/暴露')
    if not cats: cats.add(s[:20])

    sk = stage_map.get(e['id'], '?')
    for c in cats:
        sex_count[c] = sex_count.get(c, 0) + 1
        if c not in sex_stage: sex_stage[c] = {}
        sex_stage[c][sk] = sex_stage[c].get(sk, 0) + 1

order = ['纯情感','注视/暴露','摸乳','舔乳','蹭触','足交','手交','指交','口交','乳交','插入/本番','隐奸','群交/多人','轮奸']
sorted_s = [s for s in order if s in sex_count]

print(f'{\"性行为\":<16} {\"合计\":>4}  A  B BC  C CD  D 终')
print('-' * 45)
for sx in sorted_s:
    total = sex_count[sx]
    row = f'{sx:<16} {total:>4}'
    for s in stages_order:
        row += f'{sex_stage[sx].get(s,0):>3}'
    print(row)

# ===== TABLE 3: Per-third sex breakdown =====
print()
print('=' * 80)
print('表3：四大第三者 × 性行为类型')
print('=' * 80)

for main in main4:
    sc = {}
    stages = {}
    for e in events:
        t = e['third']
        if main in t and not any(m != main and m in t for m in main4):
            s = e['sex']
            cats = set()
            if '轮奸' in s: cats.add('轮奸')
            if '群交' in s: cats.add('群交')
            if '隐奸' in s: cats.add('隐奸')
            if '插入' in s or '本番' in s or s.startswith('9+'): cats.add('插入')
            if '口交' in s: cats.add('口交')
            if '乳交' in s: cats.add('乳交')
            if '手交' in s: cats.add('手交')
            if '足交' in s: cats.add('足交')
            if '指交' in s: cats.add('指交')
            if '摸乳' in s: cats.add('摸乳')
            if '舔乳' in s: cats.add('舔乳')
            if '蹭触' in s: cats.add('蹭触')
            if '纯情感' in s or s.startswith('0（'): cats.add('纯情感')
            if '暴露' in s: cats.add('暴露')
            for c in cats: sc[c] = sc.get(c, 0) + 1
            sk = stage_map.get(e['id'], '?')
            stages[sk] = stages.get(sk, 0) + 1

    total = sum(stages.values())
    sex_desc = ' + '.join([f'{k}×{v}' for k, v in sorted(sc.items(), key=lambda x: -x[1])])
    stage_desc = ' '.join([f'{s}:{stages.get(s,0)}' for s in stages_order])
    print(f'{main:<8} ({total:>2}次): {sex_desc}')
    print(f'         {stage_desc}')
    print()
