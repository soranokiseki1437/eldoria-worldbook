import re
with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    md = f.read()

start = md.find('### C到D阶段——信任巅峰')
if start < 0:
    start = md.find('### C→D阶段——信任巅峰')
end = md.find('### D阶段——极限与反转')
block = md[start:end]

for m in re.finditer(r'### 事件(N\d{2})：(.+?)\n\n```yaml\n(.+?)\n```', block, re.DOTALL):
    eid = m.group(1)
    title = m.group(2)
    yaml = m.group(3)
    print(f'{"="*60}')
    print(f'  {eid}：{title}')
    print(f'{"="*60}')

    for field in ['事件:', '触发', '性行为', '情感', '黎恩知情', '第三者']:
        pat = field + r'\s*(.+)'
        ms = re.search(pat, yaml)
        if ms:
            print(f'  {field} {ms.group(1).strip()[:120]}')

    # Situation
    ms = re.search(r'情境:\s*\n(.+?)(?:\n    占有|\n    玩家|\n    变量|\n    核心|\n    禁令)', yaml, re.DOTALL)
    if ms:
        print(f'  情境:')
        for line in ms.group(1).strip().split('\n'):
            print(f'    {line.strip()}')

    # 占有欲确认
    ms = re.search(r'占有欲确认:\s*\n(.+?)(?:\n    玩家|\n    变量|\n    核心|\n    禁令)', yaml, re.DOTALL)
    if ms:
        print(f'  占有欲确认:')
        for line in ms.group(1).strip().split('\n'):
            print(f'    {line.strip()}')

    # Core
    ms = re.search(r'核心:\s*(.+?)$', yaml, re.M)
    if ms:
        print(f'  核心: {ms.group(1).strip()[:150]}')

    print()
