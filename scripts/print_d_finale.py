"""Print all polished D+Finale+C1-C6 events"""
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

headers = [
    # D阶段
    ('### 事件N51：主动口交——NTRS阶段D（Seraphina为第三者口交）', 'N51 ★D阶段'),
    ('### 事件N52：主动隐奸——NTRS阶段D（她设计的游戏）', 'N52 ★D阶段'),
    ('### 事件N53：桌下之手（给第三者）——NTRS隐奸手交', 'N53 ★D阶段'),
    ('### 事件N54：桌下之口（给第三者）——NTRS隐奸口交', 'N54 ★D阶段'),
    ('### 事件N55：隐乳交（给第三者）——NTRS隐蔽乳交', 'N55 ★D阶段'),
    # 移入D的事件
    ('### 事件N19：隐奸——黎恩的窥视（Hidden Affair）', 'N19 ★D阶段（从B移入）'),
    ('### 事件N31：夜袭——黑暗中的访客（Night Raid）', 'N31 ★D阶段（从B移入）'),
    # 终局
    ('### 事件N58：终极确认之夜（NTRS情感阶段D——庆祝式情书）', 'N58 ★终局'),
    ('### 事件N59：终局抉择（NTRS版本）', 'N59 ★终局'),
    # C1-C6
    ('### 事件C1：玲的裸足——小恶魔的秘密（Renne\'s Bare Feet）', 'C1 ★其他角色足交'),
    ('### 事件C2：亚莉莎的蕾丝——傲娇千金的告白（Alisa\'s Lace）', 'C2 ★其他角色足交'),
    ('### 事件C3：菲的裸足——猎兵的诚意（Fie\'s Bare Feet）', 'C3 ★其他角色足交'),
    ('### 事件C4：劳拉的白袜——骑士的荣誉（Laura\'s White Stockings）', 'C4 ★其他角色足交'),
    ('### 事件C5：艾玛的吊带袜——魔女的私授课程（Emma\'s Garter）', 'C5 ★其他角色足交'),
    ('### 事件C6：亚尔缇娜的任务——黑兔的"逻辑性服务"（Altina\'s Mission）', 'C6 ★其他角色足交'),
]

for hdr, label in headers:
    i = c.find(hdr)
    if i < 0:
        # try partial match
        partial = hdr.split('（')[0]
        i = c.find(partial)
    if i < 0:
        print(f'\n{"="*60}')
        print(f'  {label}: NOT FOUND')
        continue
    ys = c.find('```yaml', i)
    ye = c.find('```', ys+7)
    block = c[i:ye+3]
    print(f'\n{"="*60}')
    print(f'  {label}')
    print(f'{"="*60}')
    # Print header line
    hdr_end = block.find('\n')
    print(block[hdr_end+1:])
