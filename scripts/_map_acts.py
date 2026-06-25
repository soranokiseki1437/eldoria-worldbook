import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.find('## 四、NTRS路线事件')
ntrs = text[start:text.find('## 五、', start)]

acts = {'手交':[], '乳交':[], '足交':[], '插入':[], '本番':[]}
for m in re.finditer(r'### 事件(N\d{2})[：:]([^\n]+)', ntrs):
    eid, title = m.group(1), m.group(2)
    chunk = ntrs[m.start():]
    end_bt = chunk.find('\n```')
    body = chunk[:end_bt]
    sa = re.search(r'性行为等级[：:]\s*(.+?)(?:\n|$)', body)
    act_text = sa.group(1) if sa else ''
    sa2 = re.search(r'性行为[：:]\s*(.+?)(?:\n|$)', body)
    if sa2 and not sa: act_text = sa2.group(1)
    for act in acts:
        if act in act_text or act in title:
            phase_m = re.search(r'情感阶段[：:]\s*(.+?)(?:\n|$)', body)
            phase = phase_m.group(1)[:8] if phase_m else '?'
            acts[act].append((eid, phase, title[:35]))

for act, events in acts.items():
    if events:
        print(f'\n=== {act} ({len(events)}) ===')
        for eid, phase, title in events:
            print(f'  {eid} [{phase}] {title}')
