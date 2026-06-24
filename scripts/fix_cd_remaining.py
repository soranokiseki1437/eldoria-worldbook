with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# N48: fix the merged "第三者 触发:" line
old = '    第三者 触发: ntrs_awakened=100, acceptance>=60, shared>=52'
new = '    第三者: 乔治\n    触发: ntrs_awakened=100, acceptance>=60, shared>=52'
if old in c:
    c = c.replace(old, new)
    print('N48: format fixed')
else:
    print('N48: pattern not found — checking...')
    # find context
    i = c.find('### 事件N48：主动手交')
    ctx = c[i:i+300]
    if '第三者' in ctx:
        idx = ctx.find('第三者')
        print(f'  Found: {ctx[idx:idx+80]}')

# N49: remove event reference "和N04"
c = c.replace(
    '脚心覆上。和N04凯尔那次完全不同——那时她紧张呼吸不稳。现在脚趾灵活脚弓有力——',
    '脚心覆上。和最初那次完全不同——那时她紧张呼吸不稳。现在脚趾灵活脚弓有力——')
c = c.replace(
    '核心: 与N04凯尔足交对照。A阶段凯尔远观·她紧张——C→D她为雷恩足交·她从容。',
    '核心: 与最初凯尔足交对照。A阶段远观·她紧张——C→D她为雷恩足交·她从容。')
print('N49: event ref removed')

# Check N38 position
n38_pos = c.find('### 事件N38：醉诱')
n43_pos = c.find('### 事件N43：温泉晕厥')
d_pos = c.find('### D阶段——极限与反转')
print(f'N38 at {n38_pos}, N43 at {n43_pos}, D阶段 at {d_pos}')
if n38_pos > n43_pos and n38_pos < d_pos:
    print('N38: in C→D section ✅')
else:
    print('N38: NOT in C→D section — needs move')

# N43: fix stage label C → C→D
c = c.replace(
    '    情感: C（信任极限——不在场也做了但第一时间告知）',
    '    情感: C→D（信任极限——不在场也做了但第一时间告知）')
print('N43: stage C→D')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)
print('All remaining fixes done')
