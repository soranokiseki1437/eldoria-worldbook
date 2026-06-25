import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.find('## 四、NTRS路线事件')
ntrs = text[start:text.find('## 五、', start)]

issues = []

for m in re.finditer(r'### 事件(N\d{2})[：:]', ntrs):
    eid = m.group(1)
    chunk = ntrs[m.start():]
    end_bt = chunk.find('\n```')
    body = chunk[:end_bt]

    # Find 情境 section bullets (lines starting with ' - ')
    qj_start = body.find('情境:')
    if qj_start < 0: continue
    qj_end = body.find('占有欲确认:', qj_start)
    if qj_end < 0: qj_end = body.find('变量:', qj_start)
    if qj_end < 0: qj_end = body.find('玩家选择:', qj_start)
    qj = body[qj_start:qj_end] if qj_end > 0 else body[qj_start:]

    bullets = re.findall(r'^ - (.+)$', qj, re.MULTILINE)

    for b in bullets:
        b = b.strip()
        # Check for: very long (>180 chars), excessive dashes, filler words
        probs = []
        if len(b) > 180: probs.append(f'{len(b)}chars')
        if b.count('——') > 2: probs.append(f'{b.count("——")}dashes')
        if '然后' in b and b.count('然后') > 1: probs.append('multi-然后')

        if probs:
            issues.append((eid, ', '.join(probs), b[:80]))

if issues:
    print(f'{len(issues)} issues found:')
    for eid, prob, preview in issues:
        print(f'  {eid} [{prob}]: {preview}...')
else:
    print('No bloat issues found.')
