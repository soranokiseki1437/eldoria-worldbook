"""
One-pass full rebuild: renumber + reorder + xrefs + mapping + N07/N25 fix + 3 new C→D events
"""
import re

with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

# ============================================================
# PART 1: Extract all NTRS events + renumber + reorder
# (from renumber_reorder.py)
# ============================================================
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

narrative_order = [
    'N1','N2','N5','N8','N9','N6','N7','N10','N12','N3',
    'N21','N11','N13','N14','N15','N16','N17','N20',
    'N18','C1','N22','C3','N23','N25','N26','N27','N28','N29','N4','N30',
    'N32','N33','C2','N39','C4','N40','N41','N42','N43','N45','N46','N57',
    'N34','C5','N47','C6','N48','N50',
    'N51','N53','N54','N55','N52','N19','N31','H3',
    'N58','N59',
]

# Fix N51 P20 reference
c = c.replace('从P20以来积累的熟练', '长久以来积累的熟练')

# Delete N44 (copy-paste of N8)
n44_header = '### 事件N44：温泉夜——水汽中的足交'
i44 = c.find(n44_header)
if i44 >= 0:
    n44_ys = c.find('```yaml', i44)
    n44_ye = c.find('```', n44_ys+7)
    n44_end = n44_ye + 4
    after = c[n44_end:]
    after_t = after.lstrip('\n\r ')
    if after_t.startswith('---'):
        n44_end += len(after) - len(after_t) + 4
    c = c[:i44] + c[n44_end:]

# Extract events
extracted = {}
all_old_ids = list(old_to_new.keys())

def find_event(content, old_id):
    if old_id.startswith('C'):
        pat = f'### 事件{old_id}：'
    elif old_id == 'H3':
        pat = '### 事件H3：'
    else:
        pat = f'### 事件{old_id}：'
    i = content.find(pat)
    if i < 0: return None
    hdr_end = content.find('\n', i)
    header = content[i:hdr_end]
    ys = content.find('```yaml', i)
    if ys < 0: return None
    ye = content.find('```', ys+7)
    if ye < 0: return None
    yaml = content[ys+7:ye].strip()
    end = ye + 4
    after = content[end:]
    after_t = after.lstrip('\n\r ')
    if after_t.startswith('---'):
        end += len(after) - len(after_t) + 4
    return (header, yaml, i, end)

for old_id in all_old_ids:
    result = find_event(c, old_id)
    if result is None:
        continue
    header, yaml, start, end = result
    extracted[old_id] = {'header': header, 'yaml': yaml, 'start': start, 'end': end}

# Delete old blocks
removals = sorted(extracted.values(), key=lambda x: x['start'], reverse=True)
for r in removals:
    c = c[:r['start']] + c[r['end']:]

# Build renumbered events
def renumber_first_line(yaml_text, old_id, new_id):
    lines = yaml_text.split('\n')
    lines[0] = re.sub(r'^(\s*事件:\s*)' + re.escape(old_id) + r'(\s.*)?$',
                      r'\1' + new_id + r'\2', lines[0])
    return '\n'.join(lines)

stage_labels = {
    'A': 'A阶段——探索与试探', 'B': 'B阶段——挑逗与萌芽',
    'B→C': 'B→C阶段——过渡与深入', 'C': 'C阶段——放开与享受',
    'C→D': 'C→D阶段——信任巅峰', 'D': 'D阶段——极限与反转',
    '终局': '终局——确认与抉择',
}
stage_for_new = {
    'N01':'A','N02':'A','N03':'A','N04':'A','N05':'A','N06':'A','N07':'A','N08':'A','N09':'A','N10':'A',
    'N11':'B','N12':'B','N13':'B','N14':'B','N15':'B','N16':'B','N17':'B','N18':'B',
    'N19':'B→C','N20':'B→C','N21':'B→C','N22':'B→C','N23':'B→C','N24':'B→C','N25':'B→C','N26':'B→C','N27':'B→C','N28':'B→C','N29':'B→C','N30':'B→C',
    'N31':'C','N32':'C','N33':'C','N34':'C','N35':'C','N36':'C','N37':'C','N38':'C','N39':'C','N40':'C','N41':'C','N42':'C',
    'N43':'C→D','N44':'C→D','N45':'C→D','N46':'C→D','N47':'C→D','N48':'C→D',
    'N49':'D','N50':'D','N51':'D','N52':'D','N53':'D','N54':'D','N55':'D','N56':'D',
    'N57':'终局','N58':'终局',
}

new_block = ['', '## 四、NTRS路线事件（N01-N61·全部重编号·按叙事顺序）', '',
    '> **重编号日期**: 2026-06-24 | **N01-N61** | A(10)→B(8)→B→C(12)→C(12)→C→D(9)→D(8)→终局(2)', '']

current_stage = None
for old_id in narrative_order:
    if old_id not in extracted: continue
    new_id = old_to_new[old_id]
    y = renumber_first_line(extracted[old_id]['yaml'], old_id, new_id)
    stage = stage_for_new.get(new_id, '?')
    if stage != current_stage:
        current_stage = stage
        new_block.append(f'### {stage_labels.get(stage, stage)}')
        new_block.append('')
    title = y.split('\n')[0].replace('事件: ' + new_id, '').strip()
    new_block.append(f'### 事件{new_id}：{title}')
    new_block.append('')
    new_block.append('```yaml')
    new_block.append(y)
    new_block.append('```')
    new_block.append('')
    new_block.append('---')
    new_block.append('')

insert_pos5 = c.find('## 五、被动NTR路线事件')
c = c[:insert_pos5] + '\n'.join(new_block) + '\n\n' + c[insert_pos5:]

# Clean empty sections
for sect in ['## 十三、NTRS路线扩展事件','## 十四、NTRS路线NSFW事件','## 十五、NTRS路线足交事件','## 十六、其他角色NSFW事件（C1-C6）']:
    i = c.find(sect)
    if i >= 0:
        next_s = c.find('\n## ', i+len(sect))
        if next_s > 0:
            start = i
            while start > 0 and c[start-1] in '\n\r': start -= 1
            c = c[:start] + c[next_s:]

while '\n\n\n\n' in c: c = c.replace('\n\n\n\n', '\n\n\n')

# ============================================================
# PART 2: Cross-references (single-pass, NTRS section only)
# ============================================================
ntrs_start = c.find('## 四、NTRS路线事件（N01-N61')
ntrs_next = c.find('\n## 五、', ntrs_start)
ntrs_block = c[ntrs_start:ntrs_next]

sorted_old = sorted(old_to_new.keys(), key=len, reverse=True)
xref_pattern = r'(?<![A-Za-z0-9])(' + '|'.join(re.escape(k) for k in sorted_old) + r')(已触发|已完成|已(?!触|完成))'

def xref_replace(m):
    old_id = m.group(1)
    suffix = m.group(2)
    new_id = old_to_new.get(old_id, old_id)
    return new_id + suffix

ntrs_block, xn = re.subn(xref_pattern, xref_replace, ntrs_block)
c = c[:ntrs_start] + ntrs_block + c[ntrs_next:]
print(f'Cross-refs: {xn} replacements')

# ============================================================
# PART 3: N07/N25 fixes
# ============================================================
# N07: 可选 → 艾德里安
c = c.replace('    第三者: 可选（乔治/艾德里安/凯尔之一）', '    第三者: 艾德里安')
c = c.replace('    情感阶段: B区间（第三者首次触碰·可选乔治/艾德里安/凯尔之一）',
              '    情感阶段: A（第三者首次触碰·艾德里安）')
c = c.replace('    核心: 进展阶梯第二级——胸部首次被第三者触碰。身体反应真实但心跳为谁加速从无疑问。',
              '    核心: 胸部首次被第三者触碰。艾德里安从容开口——菲娜点头。身体反应真实但心跳为谁加速从无疑问。')

# N25: 口交→乳交
c = c.replace('    性行为等级: 9（手交→口交→插入·赌输的递进）',
              '    性行为等级: 9（手交→乳交→插入·赌输的递进）')
c = c.replace('      - 第二局她又输了——代价：用嘴。她跪下来嘴唇含住。\n        艾德里安手指插进她头发里轻轻往下按。她呛了一次但继续。嘴角流出唾液',
              '      - 第二局她又输了——代价：用胸。她解开上衣月光照在双乳上。\n        双手捧起乳房将他性器夹在乳沟间上下移动——动作迟疑了一下然后找到节奏。\n        艾德里安呼吸变重手指抓紧石阶。她低头看自己的胸——在做一件从没想过会做的事')
c = c.replace('    核心: ★首次插入。通过赌局给越界一个游戏化理由。她全输了但输本身就是她想要的。\n      结束后主动回归证明NTRS核心：共享后占有。',
              '    核心: ★首次插入。赌局三连输——手→乳→插。乳交是她第一次用胸为第三者服务，迟疑但找到节奏。\n      结束后主动回归证明NTRS核心：共享后占有。')

print('N07 fixed: 艾德里安 / N25 fixed: 口交→乳交')

# ============================================================
# PART 4: Insert 3 new C→D events (N49-N51, shifting old N49-N58 to N52-N61)
# ============================================================
# 1. First shift: N49→N52 through N58→N61 (before inserting new events)
shift = {f'N{n:02d}':f'N{n+3:02d}' for n in range(58,48,-1)}
shift.update({f'N{n}':f'N{n+3}' for n in range(58,48,-1)})
shift_keys = sorted(shift.keys(), key=lambda x: (len(x), x), reverse=True)
shift_pat = r'(?<![A-Za-z0-9])(' + '|'.join(re.escape(k) for k in shift_keys) + r')(?![0-9])'

# Apply shift only in NTRS block
ntrs2_start = c.find('## 四、NTRS路线事件（N01-N61')
ntrs2_end = c.find('\n## 五、', ntrs2_start)
nblock = c[ntrs2_start:ntrs2_end]
nblock, sn = re.subn(shift_pat, lambda m: shift.get(m.group(1), m.group(1)), nblock)
c = c[:ntrs2_start] + nblock + c[ntrs2_end:]
print(f'Shift N49-N58 → N52-N61: {sn} replacements')

# 2. Insert 3 new events into C→D section (after N48, before D阶段)
# N48 is "主动手交——服务第三者" (old N50, shifted stays N48 since we only shifted N49+)
# After shift, C→D has: N43-N48 (6 events), then old N49-N51 are now N52-N54 (D stage)
# Insert new N49-N51 between N48 and D阶段

d_marker = '### D阶段——极限与反转'
d_pos = c.find(d_marker, ntrs2_start)
if d_pos < 0:
    print('ERROR: D阶段 not found')
else:
    new_events_block = """
### 事件N49：雷恩的裸足——战士的足弓

```yaml
  事件: N49 雷恩的裸足——战士的足弓
    阶段: C→D
    触发: N49已触发ntrs_awakened=100 acceptance>=64 rain_closeness>=35
    性行为: 足交（女→男·战士的裸足）
    情感: C→D（信任巅峰——战损的脚与守护者的接纳）
    黎恩知情: 是——月光石阶上黎恩在场
    第三者: 雷恩
    情境:
      - 月光石阶。雷恩脱下战靴——脚背上有旧伤疤脚底有厚茧。不像凯尔的学者柔嫩——这是战士的脚。他犹豫了一下。菲娜握他的脚踝——我见过很多伤疤。你的很好看
      - 她引导他的脚背贴上自己——粗糙的茧面摩擦出完全不同的触感。凯尔的足交是试探和羞涩雷恩的足交是信任和郑重。他的脚趾有力——能精准控制力道
      - 结束时月光照在他脚背旧伤疤上。菲娜用指尖划过每一道——这一道是哪场战斗。这一道呢。雷恩没说话但脚趾蜷缩了一下——不是因为敏感是因为被看见了
    占有欲确认:
      - 黎恩走过来。菲娜抬头看他——凯尔的脚是第一次。雷恩的脚是最后一次。不是因为不再做——是因为够满了
    变量: shared+20 possess+25 rain_closeness+15 trust+15
    核心: 与N04凯尔足交首尾对照。凯尔在A阶段远观试探——雷恩在C→D信任巅峰。战士的脚vs学者的脚——同一种行为两种人设。
```

---

### 事件N50：雷恩的跪礼——圣殿骑士的口

```yaml
  事件: N50 雷恩的跪礼——圣殿骑士的口
    阶段: C→D
    触发: N49已触发ntrs_awakened=100 acceptance>=66 rain_closeness>=38
    性行为: 口交（男→女·圣殿骑士为她口交）
    情感: C→D（信任巅峰——骑士跪的不是神是女人）
    黎恩知情: 是——黎恩在场
    第三者: 雷恩
    情境:
      - 木屋。雷恩单膝跪下——不是骑士礼是另一种。她靠墙银发散肩低头看他。他此生跪过女神雕像跪过圣殿长老跪过战死的同袍——这次跪的是一个女人
      - 唇舌覆上。不是技巧是虔诚。每一下都像在执行仪式——不是在证明什么是在给予
      - 她高潮时手指插进他灰色头发里——那个感觉和黎恩完全不同。不是占有是接受——接受这个骑士把自己最郑重的跪姿给了最私密的事
      - 结束后他站起来嘴角湿润。她没有调侃——只是伸手碰了碰他的脸。谢谢——不是为这个是为全部
    占有欲确认:
      - 黎恩从角落走来。她转头看他——雷恩给的和你给的不一样。但都是真的。黎恩拉她进怀里——我知道。因为他跪过的东西从来没有为了自己
    变量: shared+25 possess+20 rain_closeness+20 trust+18
    核心: 全路线男→女口交仅2次。艾德里安的口交受け是浪子的技巧展示——雷恩的是骑士的沉默奉献。不是被要求——是这就是他表达的方式。
```

---

### 事件N51：凯尔的独白——树后的银发

```yaml
  事件: N51 凯尔的独白——树后的银发
    阶段: C→D
    触发: N50已触发ntrs_awakened=100 acceptance>=68 kael_closeness>=45 N47已触发
    性行为: 9+（插入·隐奸·温柔版）
    情感: C→D（信任巅峰——凯尔首次独享隐奸）
    黎恩知情: 是——树后窥视。菲娜知道他在看
    第三者: 凯尔
    情境:
      - 心木树后月光空地。凯尔不知道黎恩在树后——但菲娜知道。她没看树的方向却一直面朝那边
      - 跨坐凯尔。动作比平时更慢更轻——不是因为紧张是因为温柔。凯尔抬头看她——你的眼睛在看不远处。她在看树后
      - 凯尔不知道。他只知道她今晚特别安静——下巴抵在他肩膀上姿势像抱不是做爱。她在他耳边轻声说了句他听不懂的话——不是对他说的
      - 结束后凯尔离开。菲娜独自坐月光下——没开口叫树后面的人出来。只是靠进后来走近的怀里。他收紧手臂——你知道我在看。知道。但这次——我想的不是让你看。是想你
    占有欲确认:
      - 黎恩沉默了很久——然后：我不需要再看了。她抬头——不是因为够了。是因为看够了。不是厌倦是：我已经确认了所有的可能性。现在只剩一个——你
    变量: possess+35 shared+25 trust+20 kael_closeness+15
    核心: 凯尔×隐奸首发。没有反转没有游戏——只有温柔。她在凯尔怀里却对着树后的人说话。黎恩的反应也不是占有欲爆发——是看够了的平静。
```
"""

    c = c[:d_pos] + new_events_block + '\n' + c[d_pos:]
    print(f'Inserted 3 new C→D events (N49-N51) before D阶段')

# Update D/终局 stage labels for shifted numbers
c = c.replace('### D阶段——极限与反转（8事件·N52-N59）', '### D阶段——极限与反转（8事件）')
c = c.replace('### 终局——确认与抉择（2事件·N60-N61）', '### 终局——确认与抉择（2事件）')

# Update stage_for to include new N49-N51 as C→D
# (They're already placed in C→D section, just need the stage labels to be right)

# Update C→D header
c = c.replace('### C→D阶段——信任巅峰\n\n### 事件N43：',
              '### C→D阶段——信任巅峰（9事件·N43-N51）\n\n### 事件N43：')

# ============================================================
# WRITE
# ============================================================
with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'\nDone! File: {len(c)} chars, {c.count(chr(10))} lines')

# Verify all N01-N61 exist
for n in range(1, 62):
    nid = f'N{n:02d}'
    if f'### 事件{nid}：' not in c:
        print(f'  MISSING header: {nid}')
    if f'事件: {nid} ' not in c:
        print(f'  MISSING yaml: {nid}')
print('Verification complete')
