import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

ntrs = c[c.find('## 四、NTRS'):c.find('\n## 五、', c.find('## 四、NTRS'))]

# === Fix 1: YAML 事件: field mismatches ===
events = []
for m in re.finditer(r'### 事件(N\d+)：(.+?)\n\n```yaml\n(.*?)\n```', ntrs, re.DOTALL):
    hdr_id = m.group(1)
    title = m.group(2)
    yaml = m.group(3)
    yaml_id_m = re.search(r'^(\s*事件:\s*)N(\d+)', yaml, re.M)
    if yaml_id_m and yaml_id_m.group(2) != hdr_id[1:]:
        old_line = yaml_id_m.group(0)
        new_line = yaml_id_m.group(1) + hdr_id
        print(f'  YAML fix: {yaml_id_m.group(2)} → {hdr_id[1:]} for {title[:40]}')
        # Replace in full text
        full_ev = m.group(0)
        full_ev_fixed = full_ev.replace(old_line, new_line, 1)
        c = c.replace(full_ev, full_ev_fixed, 1)

# === Fix 2: Known broken trigger refs ===
# N08 should ref N07 (雷恩同意), not N26
fixes = [
    # (event_title_kw, old_ref, new_ref)
    ('艾德里安的察觉——从容的入局者', 'N26已触发', 'N07已触发'),
    ('乔治的回礼——从按摩到足交', 'N66已触发', 'N16已触发'),
]
for kw, old, new in fixes:
    pos = c.find(kw)
    if pos != -1:
        ev_start = c.rfind('### 事件N', 0, pos)
        ev_end = c.find('### 事件N', ev_start + 10)
        if ev_end == -1:
            ev_end = len(c)
        block = c[ev_start:ev_end]
        if old in block:
            block_fixed = block.replace(old, new)
            c = c[:ev_start] + block_fixed + c[ev_end:]
            print(f'  Trigger fix: {old} → {new} in {kw[:30]}')

# === Fix 3: Scan all trigger条件 for impossible refs ===
# N01-N11 (A) should only ref N01-N11
# N12-N22 (B) should ref N01-N22
# etc.
print('\nScanning trigger条件 for stage-mismatch refs...')
for m in re.finditer(r'### 事件(N\d+)：(.+?)\n\n```yaml\n(.*?)\n```', ntrs, re.DOTALL):
    eid = int(m.group(1)[1:])
    title = m.group(2)[:40]
    yaml = m.group(3)
    refs = re.findall(r'N(\d+)已触发', yaml)
    for ref in refs:
        ref_n = int(ref)
        if ref_n > eid:
            print(f'  FUTURE REF: {m.group(1)} → N{ref} (event #{ref_n} triggers after #{eid})')
        if ref_n == eid:
            print(f'  SELF REF: {m.group(1)} → N{ref}')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)
print('\nFixes applied.')
