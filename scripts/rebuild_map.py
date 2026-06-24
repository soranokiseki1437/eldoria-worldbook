import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

ntrs_start = c.find('## 四、NTRS路线事件')
ntrs_end = c.find('\n## 五、', ntrs_start)
ntrs_block = c[ntrs_start:ntrs_end]

# Extract events
events = []
for m in re.finditer(r'### 事件(N\d+)：(.+?)\n', ntrs_block):
    events.append((m.group(1), m.group(2)))

# Get stage per event
stage_ranges = []
for m in re.finditer(r'### (A阶段——|B阶段——|B→C阶段——|C阶段——|C→D阶段——|D阶段——|终局——)', ntrs_block):
    stage_ranges.append((m.start(), m.group(1)))

def get_stage(pos):
    for i in range(len(stage_ranges)-1, -1, -1):
        if stage_ranges[i][0] <= pos:
            s = stage_ranges[i][1]
            if 'B→C' in s: return 'BC'
            if 'C→D' in s: return 'CD'
            if 'A' in s: return 'A'
            if 'B' in s: return 'B'
            if 'C' in s: return 'C'
            if 'D' in s: return 'D'
            if '终局' in s: return 'End'
    return '?'

stage_events = {s: [] for s in ['A','B','BC','C','CD','D','End']}
for eid, title in events:
    pos = ntrs_block.find(f'### 事件{eid}：{title}')
    stage_events[get_stage(pos)].append((eid, title))

def get_tp(eid):
    pat = rf'### 事件{re.escape(eid)}：.+?\n\n```yaml\n(.*?)\n```'
    m = re.search(pat, ntrs_block, re.DOTALL)
    if not m: return '—'
    y = m.group(1)
    tp = re.search(r'第三者:\s*(.+?)$', y, re.M)
    if not tp: return '—'
    t = tp.group(1).strip()
    if '低语者' in t:
        if '5' in t or '6' in t: return '低语者×5~6'
        if '三' in t: return '低语者×3'
        return '低语者'
    if '迷路' in t or '陌生' in t: return '陌生人'
    if '同伴' in t or '亚莉莎' in t: return '同伴围观'
    if '独属' in t: return '—'
    return t

cn = {
    'A': 'Ch13-15：探索与试探（A阶段）',
    'B': 'Ch16-18：挑逗与萌芽（B阶段）',
    'BC': 'Ch19-21：过渡与深入（B→C阶段）',
    'C': 'Ch22-24：放开与享受（C阶段）',
    'CD': 'Ch25-26：信任巅峰（C→D阶段）',
    'D': 'Ch27：极限与反转（D阶段）',
    'End': 'Ch28：确认与抉择（终局）',
}

lines = []
# N01 in Ch12
for eid, title in stage_events.get('A', []):
    if '坦白' in title:
        lines.append('### Ch12：坦白之夜·路线分支')
        lines.append('| 事件ID | 事件名称 | 第三者 |')
        lines.append('|--------|---------|--------|')
        lines.append(f'| {eid} | {title} | — |')
        lines.append('')
        break

for stage in ['A', 'B', 'BC', 'C', 'CD', 'D', 'End']:
    evs = stage_events.get(stage, [])
    if not evs: continue
    if stage == 'A':
        evs = [(e, t) for e, t in evs if '坦白' not in t]
    lines.append(f'### {cn[stage]}')
    lines.append('| 事件ID | 事件名称 | 第三者 |')
    lines.append('|--------|---------|--------|')
    for eid, title in evs:
        tp = get_tp(eid)
        lines.append(f'| {eid} | {title} | {tp} |')
    lines.append('')

new_table = '\n'.join(lines)

ots = c.find('## 事件-章节映射表')
ote = c.find('\n## 一、事件系统总览', ots)
assert ots != -1 and ote != -1, f'ots={ots}, ote={ote}'

c = c[:ots] + '## 事件-章节映射表\n\n' + new_table + '\n' + c[ote:]

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

for s in ['A','B','BC','C','CD','D','End']:
    print(f'  {s}: {len(stage_events[s])} events')
print('Mapping rebuilt OK')
