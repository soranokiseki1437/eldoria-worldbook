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
    third = ''; sex = ''
    m3 = re.search(r'第三者:\s*(.+?)$', yaml, re.M)
    if m3: third = m3.group(1).strip()
    ms = re.search(r'性行为(?:等级)?:\s*(.+?)$', yaml, re.M)
    if ms: sex = ms.group(1).strip()
    events.append({'id': eid, 'third': third, 'sex': sex})

stage_map = {}
stages = {1:'A',2:'A',3:'A',4:'A',5:'A',6:'A',7:'A',8:'A',9:'A',10:'A',
          11:'B',12:'B',13:'B',14:'B',15:'B',16:'B',17:'B',18:'B',
          19:'BC',20:'BC',21:'BC',22:'BC',23:'BC',24:'BC',25:'BC',26:'BC',27:'BC',28:'BC',29:'BC',30:'BC',
          31:'C',32:'C',33:'C',34:'C',35:'C',36:'C',37:'C',38:'CD',39:'C',40:'C',41:'C',42:'C',
          43:'CD',44:'CD',45:'CD',46:'CD',47:'CD',48:'CD',49:'CD',50:'CD',51:'CD',
          52:'D',53:'D',54:'D',55:'D',56:'D',57:'D',58:'D',59:'D',60:'End',61:'End'}
for n, s in stages.items():
    stage_map[f'N{n:02d}'] = s

stages_order = ['A','B','BC','C','CD','D','End']

# Third party
third_count = {}; third_stage = {}
for e in events:
    t = e['third'].strip()
    if not t: t = '无'
    if '独属于' in t: t = '无(纯两人)'
    if '低语者' in t and '5' in t: t = '低语者x5-6'
    if '低语者' in t and '三' in t: t = '低语者x3'
    if '低语者' in t and '非人' in t: t = '低语者(单)'
    if '可选' in t: t = '可选'
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

main4 = ['凯尔','艾德里安','乔治','雷恩']
sorted_t = main4 + sorted([t for t in third_count if t not in main4], key=lambda t: -third_count[t])

print('=== 第三者 x 阶段 ===')
hdr = '%-20s' % '第三者'
for s in stages_order: hdr += ' %4s' % s
hdr += ' 合计'
print(hdr)
print('-' * 55)
for th in sorted_t:
    total = third_count[th]
    row = '%-20s' % th
    for s in stages_order:
        row += ' %4d' % third_stage[th].get(s, 0)
    row += ' %4d' % total
    print(row)

# Sex types
sex_count = {}; sex_stage = {}
for e in events:
    s = e['sex']
    cats = set()
    if '轮奸' in s: cats.add('轮奸')
    if '群交' in s or '多人' in s: cats.add('群交/多人')
    if '隐奸' in s: cats.add('隐奸')
    if '插入' in s or '本番' in s or s[:2] in ['9+','9(']: cats.add('插入/本番')
    if '口交' in s: cats.add('口交')
    if '乳交' in s: cats.add('乳交')
    if '手交' in s: cats.add('手交')
    if '足交' in s: cats.add('足交')
    if '指交' in s: cats.add('指交')
    if '摸乳' in s: cats.add('摸乳')
    if '舔乳' in s: cats.add('舔乳')
    if '蹭触' in s: cats.add('蹭触')
    if '纯情感' in s or s.startswith('0('): cats.add('纯情感')
    if '暴露' in s or '注视' in s: cats.add('注视/暴露')
    if not cats: cats.add(s[:15])
    sk = stage_map.get(e['id'], '?')
    for c in cats:
        sex_count[c] = sex_count.get(c, 0) + 1
        if c not in sex_stage: sex_stage[c] = {}
        sex_stage[c][sk] = sex_stage[c].get(sk, 0) + 1

order = ['纯情感','注视/暴露','摸乳','舔乳','蹭触','足交','手交','指交','口交','乳交','插入/本番','隐奸','群交/多人','轮奸']
sorted_s = [s for s in order if s in sex_count]

print()
print('=== 性行为类型 x 阶段 ===')
hdr2 = '%-16s' % '类型'
for s in stages_order: hdr2 += ' %4s' % s
hdr2 += ' 合计'
print(hdr2)
print('-' * 50)
for sx in sorted_s:
    total = sex_count[sx]
    row = '%-16s' % sx
    for s in stages_order:
        row += ' %4d' % sex_stage[sx].get(s, 0)
    row += ' %4d' % total
    print(row)

# Per-third
print()
print('=== 四大第三者 x 性行为 ===')
for main in main4:
    sc = {}; stg = {}
    for e in events:
        t = e['third']
        if main in t and not any(m != main and m in t for m in main4):
            s = e['sex']
            if '轮奸' in s: sc['轮奸'] = sc.get('轮奸',0)+1
            if '群交' in s: sc['群交'] = sc.get('群交',0)+1
            if '隐奸' in s: sc['隐奸'] = sc.get('隐奸',0)+1
            if '插入' in s or '本番' in s or s[:2] in ['9+','9(']: sc['插入'] = sc.get('插入',0)+1
            if '口交' in s: sc['口交'] = sc.get('口交',0)+1
            if '乳交' in s: sc['乳交'] = sc.get('乳交',0)+1
            if '手交' in s: sc['手交'] = sc.get('手交',0)+1
            if '足交' in s: sc['足交'] = sc.get('足交',0)+1
            if '指交' in s: sc['指交'] = sc.get('指交',0)+1
            if '摸乳' in s: sc['摸乳'] = sc.get('摸乳',0)+1
            if '舔乳' in s: sc['舔乳'] = sc.get('舔乳',0)+1
            if '纯情感' in s: sc['纯情感'] = sc.get('纯情感',0)+1
            if '暴露' in s: sc['暴露'] = sc.get('暴露',0)+1
            sk = stage_map.get(e['id'], '?')
            stg[sk] = stg.get(sk, 0) + 1

    total = sum(stg.values())
    sex_desc = ' + '.join(['%sx%d' % (k,v) for k, v in sorted(sc.items(), key=lambda x: -x[1])])
    stage_desc = ' '.join(['%s:%d' % (s, stg.get(s,0)) for s in stages_order])
    print('%s (%2d): %s' % (main, total, sex_desc))
    print('      %s' % stage_desc)
    print()
