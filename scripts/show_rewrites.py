import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

keywords = [
    '艾德里安的察觉——从容的入局者',
    '丝袜与内衣——故意的展示',
    '乔治的回礼——从按摩到足交',
    '树后的秘密——第一次给别人打飞机',
    '第一次双人共享——两只手同时',
    '艾德里安的扑克——手与乳的初次',
    '酒后扑克——第一次给别人口交',
]

for kw in keywords:
    # Find the event
    pos = c.find(kw)
    if pos == -1:
        print(f'\n=== NOT FOUND: {kw} ===\n')
        continue

    # Find event header start
    ev_start = c.rfind('### 事件N', 0, pos)
    # Find event end (next ### 事件N or next ### stage header)
    rest = c[ev_start+5:]
    m = re.search(r'\n### 事件N\d+：', rest)
    if not m:
        m = re.search(r'\n### [A-ZB→C终D].*?阶段——', rest)
    ev_end = ev_start + 5 + (m.start() if m else len(rest))

    print(c[ev_start:ev_end])
    print()
