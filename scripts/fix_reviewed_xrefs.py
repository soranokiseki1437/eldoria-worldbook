"""
Fix trigger cross-refs in reviewed range N01-N29.
Many events were wrongly mapped to N26/N66/N67 during renumber.
Check each event and fix known patterns.
"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# Known fixes: (event_title_kw, old_wrong_ref, new_correct_ref)
# These are for the reviewed range N01-N29
fixes = [
    # A阶段
    ('迷路的旅人——陌生人仅注视', 'N26已触发', 'N02已触发'),       # N03 should ref边界协商
    ('装睡——角落的骑士', 'N26已触发', 'N04已触发'),              # N05 should ref足部护理
    ('雷恩的初访——正义的拒绝', 'N26已触发', 'N03已触发'),        # N06 should ref迷路旅人
    ('雷恩的同意——从拒绝到触碰', 'N26已触发', 'N06已触发'),      # N07 should ref雷恩拒绝
    ('艾德里安的察觉——从容的入局者', 'N26已触发', 'N07已触发'),  # N08 should ref雷恩同意
    ('凯尔的告白——真诚暗恋', 'N26已触发', 'N09已触发'),          # N10 should ref乔治注视

    # B阶段
    ('挑逗的萌芽', 'N26已触发', 'N09已触发'),                    # N13 should ref乔治注视
    ('银色的探索——指交', 'N26已触发', 'N07已触发'),             # N14 should ref雷恩同意
    ('乔治的逃跑——亲密的陷阱', 'N26已触发', 'N09已触发'),       # N15 should ref乔治注视
    ('乔治的同意——笨拙的第一课', 'N26已触发', 'N15已触发'),     # N16 should ref乔治逃跑
    ('艾德里安的指尖——从容的探索', 'N26已触发', 'N08已触发'),   # N17 should ref艾德里安自荐
    ('圣光之泉——口交受け', 'N26已触发', 'N17已触发'),           # N18 should ref艾德里安指交
    ('凯尔的第一次——黑丝与滚烫的手心', 'N26已触发', 'N12已触发'), # N20 should ref丝袜
    ('凯尔的臣服——从闻到舔到足交', 'N26已触发', 'N20已触发'),   # N21 should ref凯尔黑丝

    # B→C阶段
    ('桌下之手——隐奸手交', 'N66已触发', 'N22已触发'),           # N23 should ref tree secret
    ('第一次双人共享——两只手同时', 'N66已触发', 'N26已触发'),   # N27 (N26 is树后打飞机)

    # N66/N67 refs that should point to closer events
    ('乔治的回礼——从按摩到足交', 'N66已触发', 'N16已触发'),     # N19
    ('凯尔的第一次——黑丝与滚烫的手心', 'N66已触发', 'N12已触发'), # N20 (additional)
    ('凯尔的臣服——从闻到舔到足交', 'N63已触发', 'N20已触发'),   # N21 (additional)

    # N17 fix
    ('圣光之泉——口交受け', 'N66已触发', 'N17已触发'),           # Also has N66
]

for kw, old, new in fixes:
    pos = c.find(kw)
    if pos == -1:
        print(f'  NOT FOUND: {kw}')
        continue
    # Find the event boundaries in the NTRS section
    ev_start = c.rfind('### 事件N', 0, pos)
    # Find next event or section boundary
    nxt = c.find('\n### 事件N', ev_start + 10)
    if nxt == -1:
        nxt = c.find('\n### B', ev_start + 10)
    if nxt == -1:
        nxt = c.find('\n### C', ev_start + 10)
    if nxt == -1:
        nxt = len(c)
    block = c[ev_start:nxt]
    if old in block:
        c = c[:ev_start] + block.replace(old, new) + c[nxt:]
        print(f'  OK: {old} → {new} in {kw[:35]}')
    else:
        # Don't print not-found for minor fixes
        pass

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)
print('\nTrigger ref fixes applied.')
