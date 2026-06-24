"""
Final rebuild: apply scarcity fixes + renumber everything properly
"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# Find NTRS block
i0 = c.find('## 四、NTRS路线事件（N01-N61')
i1 = c.find('\n## 五、', i0)
pre = c[:i0]
post = c[i1:]
block = c[i0:i1]

# Extract all NTRS events in order
events = []
for m in re.finditer(r'(### 事件N\d{2}[.\d]*[：:].+?\n\n```yaml\n.+?\n```)', block, re.DOTALL):
    events.append(m.group(1))

print(f'Extracted {len(events)} events')

# Build a mapping from old header to YAML content
event_data = []  # (old_header, yaml_content)
for ev in events:
    hdr_match = re.match(r'### (事件N\d{2}[.\d]*)[：:](.+)', ev)
    if hdr_match:
        old_id = hdr_match.group(1).replace('事件','')
        title = hdr_match.group(2).strip()
        yaml_match = re.search(r'```yaml\n(.+?)\n```', ev, re.DOTALL)
        yaml = yaml_match.group(1) if yaml_match else ''
        event_data.append({'old_id': old_id, 'title': title, 'yaml': yaml})

# ===== APPLY CHANGES =====
# 1. N52/N53/N54: 雷恩→艾德里安 in YAML
for ed in event_data:
    oid = ed['old_id']
    if oid in ['N52','N53','N54']:
        ed['yaml'] = ed['yaml'].replace('第三者: 雷恩', '第三者: 艾德里安')
        # Update situation text for N52
        if oid == 'N52':
            ed['yaml'] = ed['yaml'].replace('雷恩坐椅上背挺直——如在圣殿。菲娜跪他双腿间', '艾德里安坐椅上——双腿敞开从容得像在自己家。菲娜跪他双腿间')
            ed['yaml'] = ed['yaml'].replace('尝过了。骑士的味道——和学者不一样', '尝过了。浪子的味道——没有想象中那么花哨')
        if oid == 'N53':
            ed['yaml'] = ed['yaml'].replace('坐雷恩旁', '坐艾德里安旁')
            ed['yaml'] = ed['yaml'].replace('解开雷恩腰带', '解开艾德里安腰带')
            ed['yaml'] = ed['yaml'].replace('雷恩表情快绷不住——圣殿骑士的庄严在瓦解', '艾德里安表情快绷不住——浪子第一次失控')
            ed['yaml'] = ed['yaml'].replace('雷恩指节攥紧桌沿', '艾德里安指节攥紧桌沿')
        if oid == 'N54':
            ed['yaml'] = ed['yaml'].replace('银发在雷恩膝间晃动', '银发在艾德里安膝间晃动')
            ed['yaml'] = ed['yaml'].replace('雷恩手在桌上假装写字——笔迹越来越潦草。圣殿骑士的字已经不成形', '艾德里安手在桌上假装写字——笔迹越来越潦草。浪子第一次写字手抖')

print('Applied: N52/N53/N54 → 艾德里安')

# 2. Insert new events into the ordered list
# 乔治指交: after N28 (old numbering) in B→C
# 艾德里安舔乳: after N48 (old numbering) in C→D

new_finger = {
    'old_id': 'NEW_FINGER',
    'title': '乔治的手指——笨拙的探索',
    'yaml': '''  事件: NEW_FINGER 乔治的手指——笨拙的探索
    阶段: B→C
    触发: ntrs_awakened=100, acceptance>=56, george_closeness>=38, N24已触发
    性行为: 指交（男→女·笨拙的探索）
    情感: B→C（反差——最不擅长手指的人用手指探索她）
    黎恩知情: 是——黎恩坐房间角落
    第三者: 乔治
    情境:
      - 木屋。乔治站在床边推了三次眼镜——我研究了一下...手指的结构。菲娜没忍住笑出声。乔治脸更红了——不是嘲笑是觉得可爱
      - 他的手指比雷恩的粗糙——不是因为剑茧是因为拧螺丝。进入时角度偏了——不是那里。往左。再往上一点。她不得不全程指导——但他每找到正确位置就停下来问这样可以吗。第三次问的时候她抓住他手腕——可以。不要再问了。自己感受
      - 他的笨拙在手指碰到那一点时消失了——她的腰突然弓起。他瞪大眼睛——就是这里？她说不出话只能点头。他接下来像修导力装置一样专注——反复验证同一位置直到她在他手里抖成一团
    占有欲确认:
      - 结束后乔治看着自己湿透的手指——学术式惊讶。菲娜靠进黎恩怀里还在喘——他问我三次可以吗...第四次的时候我已经到了。黎恩收紧手臂——你指导得很好。她抬头——教他比被服务更有意思
    变量: shared+18, possess+20, george_closeness+18, trust+10
    核心: 指交x2——雷恩的指交是成熟温柔(B阶段)，乔治的指交是笨拙专注(B→C)。全程需要指导但一旦找到位置就像修导力装置一样反复验证。反差萌。'''
}

new_lick = {
    'old_id': 'NEW_LICK',
    'title': '艾德里安的舌——反向服务',
    'yaml': '''  事件: NEW_LICK 艾德里安的舌——反向服务
    阶段: C→D
    触发: ntrs_awakened=100, acceptance>=62, adrian_closeness>=40, N48已触发
    性行为: 舔乳（男→女·艾德里安用舌）
    情感: C→D（反向——浪子的嘴不只是用来调侃的）
    黎恩知情: 是——黎恩在场
    第三者: 艾德里安
    情境:
      - 木屋。艾德里安把她按坐在床沿——平时是他躺着她跪。今天——换。她还没反应过来他已经俯身——嘴唇覆上乳尖
      - 他的舌头比手指更灵活——画圈、轻咬、吸吮、松开再含住。她手指插进他银灰色长发——你练过。他抬头——不是练过，是天生。然后换另一边
      - 乳尖在他嘴里硬成石子——她腰不自觉往上挺。他按住她小腹——别急。还没完。舌尖从乳缘滑到乳沟再从另一侧滑回来——像在写她的身体地图
      - 结束时她胸口全是他嘴唇留下的淡红印子。他直起身——需要我写一份报告吗。她抓起枕头砸他——不需要。下次——继续
    占有欲确认:
      - 黎恩走过来拇指擦过她乳尖——这里。我的。她点头——你的。但刚才...是他的舌头。黎恩低头含住同一处——她倒吸一口气。你也在证明什么。不是证明——是覆盖
    变量: shared+15, possess+20, adrian_closeness+15, trust+8
    核心: 舔乳x2——低语者的舔乳是恐惧(A)，艾德里安的舔乳是享受(C→D)。浪子的舌头不只是用来调侃的——天生就会。黎恩事后覆盖同一个位置。'''
}

# Insert finger after N28, lick after N48
new_order = []
for ed in event_data:
    new_order.append(ed)
    if ed['old_id'] == 'N28':
        new_order.append(new_finger)
    if ed['old_id'] == 'N48':
        new_order.append(new_lick)

print(f'New order: {len(new_order)} events (was {len(event_data)})')

# ===== RENUMBER: N01-N63 =====
stage_labels = {
    'A': 'A阶段——探索与试探', 'B': 'B阶段——挑逗与萌芽',
    'BC': 'B→C阶段——过渡与深入', 'C': 'C阶段——放开与享受',
    'CD': 'C→D阶段——信任巅峰', 'D': 'D阶段——极限与反转',
    'End': '终局——确认与抉择',
}

def get_stage(idx):
    if idx <= 10: return 'A'
    if idx <= 18: return 'B'
    if idx <= 30: return 'BC'
    if idx <= 42: return 'C'
    if idx <= 51: return 'CD'
    if idx <= 59: return 'D'
    return 'End'

new_block = []
new_block.append('## 四、NTRS路线事件（N01-N63·全部重编号·按叙事顺序）')
new_block.append('')
new_block.append('> **重编号日期**: 2026-06-24 | **N01-N63** | A(10)→B(8)→B→C(12)→C(12)→C→D(11)→D(8)→终局(2)')
new_block.append('')
new_block.append('> **补强**: N52/N53/N54雷恩→艾德里安 | +N29乔治指交 | +N49艾德里安舔乳')
new_block.append('')

current_stage = None
for idx, ed in enumerate(new_order, 1):
    new_id = f'N{idx:02d}'
    stage = get_stage(idx)

    if stage != current_stage:
        current_stage = stage
        new_block.append(f'### {stage_labels[stage]}')
        new_block.append('')

    # Update YAML first line to new ID
    yaml = ed['yaml']
    yaml = re.sub(r'^(\s*事件:\s*)\S+(\s.*)?$', r'\1' + new_id + r'\2', yaml, flags=re.M)

    # Update trigger cross-references in YAML
    # Build old→new map
    old_to_new_map = {}
    for j, e2 in enumerate(new_order, 1):
        old_to_new_map[e2['old_id']] = f'N{j:02d}'

    # Replace old IDs in trigger conditions
    for old, new in old_to_new_map.items():
        if old == new or old.startswith('NEW'):
            continue
        yaml = re.sub(r'(?<![A-Za-z0-9])' + re.escape(old) + r'(已触发|已完成|已(?!触|完成))',
                      new + r'\1', yaml)

    title = ed['title']
    new_block.append(f'### 事件{new_id}：{title}')
    new_block.append('')
    new_block.append('```yaml')
    new_block.append(yaml)
    new_block.append('```')
    new_block.append('')
    new_block.append('---')
    new_block.append('')

# Reassemble
c = pre + '\n'.join(new_block) + '\n\n' + post

# Clean up old duplicate headers and _TMP residue
c = c.replace('## 四、NTRS路线事件（N1-N61）', '')  # remove old header
c = re.sub(r'N\d+_TMP', lambda m: m.group(0).replace('_TMP',''), c)

# Remove triple+ blank lines
while '\n\n\n\n' in c:
    c = c.replace('\n\n\n\n', '\n\n\n')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

print(f'Written: {len(c)} chars, {c.count(chr(10))} lines')

# Verify
final_events = re.findall(r'### 事件(N\d+)：', c)
print(f'Final events in file order: {len(final_events)}')
expected = [f'N{i:02d}' for i in range(1, 64)]
missing = [e for e in expected if e not in final_events]
dupes = [e for e in final_events if final_events.count(e) > 1]
if missing: print(f'MISSING: {missing}')
if dupes: print(f'DUPES: {set(dupes)}')
if not missing and not dupes:
    print('All N01-N63 present, no dupes!')
