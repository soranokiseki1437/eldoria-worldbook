"""Print D-stage + Finale + H3 events in full"""
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

headers = [
    ('### 事件N51：主动口交', 'N51 主动口交——老手的从容'),
    ('### 事件N52：主动隐奸', 'N52 主动隐奸——她设计的游戏'),
    ('### 事件N53：桌下之手', 'N53 桌下之手——隐奸手交'),
    ('### 事件N54：桌下之口', 'N54 桌下之口——隐奸口交'),
    ('### 事件N55：隐乳交', 'N55 隐乳交——月光下的视觉盛宴'),
    ('### 事件N19：隐奸——黎恩的窥视', 'N19 隐奸——黑暗中的窥视（从B移入D）'),
    ('### 事件N31：夜袭——黑暗中的访客', 'N31 夜袭——她开的门（从B移入D）'),
    ('### 事件H3：腐化低语者的', 'H3 低语者的轮奸——D阶段极限（从世界移入D）'),
    ('### 事件N58：终极确认之夜', 'N58 终极确认——她的情书'),
    ('### 事件N59：终局抉择', 'N59 终局抉择'),
]

for hdr, label in headers:
    i = c.find(hdr)
    if i < 0:
        print(f'\n{"="*70}')
        print(f'  {label}: NOT FOUND')
        continue
    ys = c.find('```yaml', i)
    ye = c.find('```', ys+7)
    block = c[i:ye+3]
    hdr_end = block.find('\n')
    yaml_content = block[hdr_end+1:]
    print(f'\n{"="*70}')
    print(f'  {label}')
    print(f'{"="*70}')
    print(yaml_content)
