"""Audit all NTRS events for sex act direction errors"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    md = f.read()

ntrs_start = md.find('## 四、NTRS路线事件（N01-N61')
ntrs_end = md.find('\n## 五、', ntrs_start)
block = md[ntrs_start:ntrs_end]

events = []
for m in re.finditer(r'### 事件(N\d{2})：(.+?)\n\n```yaml\n(.+?)\n```', block, re.DOTALL):
    eid = m.group(1)
    yaml = m.group(3)
    third = ''
    sex = ''
    m3 = re.search(r'第三者:\s*(.+?)$', yaml, re.M)
    if m3: third = m3.group(1).strip()
    ms = re.search(r'性行为(?:等级)?:\s*(.+?)$', yaml, re.M)
    if ms: sex = ms.group(1).strip()
    msi = re.search(r'情境:\s*\n(.+?)(?:\n    占有|\n    玩家|\n    变量|\n    核心)', yaml, re.DOTALL)
    sit = msi.group(1)[:300] if msi else ''
    events.append({'id': eid, 'third': third, 'sex': sex, 'sit': sit})

print('=== 足交事件（应为女→男，菲娜的脚服务第三者） ===')
for e in events:
    if '足交' in e['sex']:
        issues = []
        # Check for "his foot/her guiding his foot" patterns (wrong direction)
        if re.search(r'(他|雷恩|凯尔|乔治|艾德里安).{0,15}(脚背|脚趾|脚心|脚底|裸足|脱下|战靴|足弓).{0,15}(贴上|摩擦|覆|夹|触|按|压)', e['sit']):
            issues.append('第三者用脚')
        if re.search(r'引导他.{0,10}脚', e['sit']):
            issues.append('她引导他的脚')
        if re.search(r'他的.{0,10}脚.{0,10}(在|贴|覆|夹|触)', e['sit']):
            issues.append('他的脚主动')
        status = '⚠️ ' + ' | '.join(issues) if issues else '✅'
        print(f'  {e["id"]} {status}')
        print(f'     第三者: {e["third"][:30]}')
        print(f'     性行为: {e["sex"][:60]}')
        if issues:
            print(f'     情境片段: {e["sit"][:120]}...')
        print()

print('=== 口交事件 ===')
for e in events:
    if '口交' in e['sex']:
        d = '?'
        if '女→男' in e['sex'] or '女→第三' in e['sex']: d = '♀→♂(菲娜口男)'
        elif '男→女' in e['sex'] or '男对女' in e['sex'] or '受け' in e['sex']: d = '♂→♀(男口菲娜)'
        print(f'  {e["id"]} | {d:20} | {e["third"][:20]:20} | {e["sex"][:50]}')

print()
print('=== 指交事件（应为♂→♀，第三者手指服务菲娜） ===')
for e in events:
    if '指交' in e['sex']:
        print(f'  {e["id"]} | {e["third"][:20]:20} | {e["sex"][:50]}')

print()
print('=== 乳交事件（应为♀→♂，菲娜用胸夹第三者） ===')
for e in events:
    if '乳交' in e['sex']:
        print(f'  {e["id"]} | {e["third"][:20]:20} | {e["sex"][:50]}')

print()
print('=== 手交事件 ===')
for e in events:
    if '手交' in e['sex']:
        d = '♀→♂' if '女→男' in e['sex'] else ('♂→♀' if '男→女' in e['sex'] else '?')
        print(f'  {e["id"]} | {d:6} | {e["third"][:20]:20} | {e["sex"][:50]}')
