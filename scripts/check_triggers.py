import re
with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# Search within NTRS block only
ntrs_start = c.find('## 四、NTRS路线事件')
ntrs = c[ntrs_start:]

for kw in ['迷路的旅人', '艾德里安的察觉']:
    pos = ntrs.find(kw)
    ev_start = ntrs.rfind('### 事件N', 0, pos)
    nxt = ntrs.find('### 事件N', ev_start + 10)
    if nxt == -1: nxt = len(ntrs)
    block = ntrs[ev_start:nxt]
    print(f'=== {kw} ===')
    for line in block.split('\n'):
        if '触发条件' in line or 'N26已触发' in line or 'N66已触发' in line:
            print(f'  {line.strip()[:120]}')
    print()
