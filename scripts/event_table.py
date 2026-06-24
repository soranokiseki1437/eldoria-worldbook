import re
with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()
ntrs = c[c.find('## 四、NTRS'):c.find('\n## 五、', c.find('## 四、NTRS'))]

events = []
for m in re.finditer(r'### 事件(N\d+)：(.+?)$', ntrs, re.MULTILINE):
    events.append((m.group(1), m.group(2)))

# Extract third parties
third_map = {}
for m in re.finditer(r'### 事件(N\d+)：.+?\n\n```yaml\n(.*?)\n```', ntrs, re.DOTALL):
    eid = m.group(1)
    y = m.group(2)
    tp = re.search(r'第三者:\s*(.+?)$', y, re.M)
    t = tp.group(1).strip()[:14] if tp else '—'
    if '低语者' in t:
        if '5' in t or '6' in t: t = '低语者x5-6'
        elif '三' in t: t = '低语者x3'
        else: t = '低语者'
    if '迷路' in t or '陌生' in t: t = '陌生人'
    if '同伴' in t or '亚莉莎' in t: t = '同伴围观'
    third_map[eid] = t

stage_names = {1:'A', 2:'A', 3:'A', 4:'A', 5:'A', 6:'A', 7:'A', 8:'A', 9:'A', 10:'A', 11:'A',
               12:'B', 23:'B',
               24:'BC', 35:'BC',
               36:'C', 47:'C',
               48:'CD', 55:'CD',
               56:'D', 65:'D',
               66:'终局', 67:'终局'}

new_set = {'艾德里安的察觉——从容的入局者',
           '凯尔的第一次——黑丝与滚烫的手心',
           '凯尔的臣服——从闻到舔到足交',
           '艾德里安的扑克——两局即止',
           '酒后扑克——黎恩的请求'}

print(f'{"#":4s} {"事件":38s} {"第三者":14s} {"阶段":6s} {"状态":10s}')
print('-' * 78)

for eid, title in events:
    n = int(eid[1:])
    # Stage
    if n <= 11: stage = 'A'
    elif n <= 23: stage = 'B'
    elif n <= 35: stage = 'B→C'
    elif n <= 47: stage = 'C'
    elif n <= 55: stage = 'C→D'
    elif n <= 65: stage = 'D'
    else: stage = '终局'

    # Status
    if n <= 29: status = '✅已审查'
    elif n <= 34: status = '🔶桥接'
    else: status = '⬜未动'

    new_mark = ' 🆕' if title in new_set else ''
    tp = third_map.get(eid, '—')

    print(f'{eid:4s} {title[:36]:36s} {tp:14s} {stage:6s} {status}{new_mark}')
