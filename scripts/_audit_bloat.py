import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.find('## 四、NTRS路线事件')
ntrs = text[start:text.find('## 五、', start)]

bloated = []
for m in re.finditer(r'### 事件(N\d{2})[：:]', ntrs):
    eid = m.group(1)
    chunk = ntrs[m.start():]
    end_bt = chunk.find('\n```')
    body = chunk[:end_bt]
    bullets = re.findall(r'^ - ', body, re.MULTILINE)
    qj_bullets = re.findall(r'^\s{4,}- ', body, re.MULTILINE)
    total = len(bullets) + len(qj_bullets)
    # Count chars
    chars = len(body)
    if total > 12:
        print(f'{eid}: {total} bullets, {chars} chars — BLOATED')
        bloated.append(eid)
    elif total > 9:
        print(f'{eid}: {total} bullets, {chars} chars — HEAVY')

# Also check for long individual bullets
long_bullets = []
for eid in bloated[:5]:
    m = re.search(r'### 事件' + eid + r'[：:]', ntrs)
    chunk = ntrs[m.start():]
    end_bt = chunk.find('\n```')
    body = chunk[:end_bt]
    for b in re.finditer(r'^ - (.+)$', body, re.MULTILINE):
        if len(b.group(1)) > 200:
            long_bullets.append((eid, len(b.group(1)), b.group(1)[:60]))

if long_bullets:
    print(f'\n=== 过长bullet ({len(long_bullets)}处) ===')
    for eid, length, preview in long_bullets[:10]:
        print(f'  {eid} ({length}chars): {preview}...')
