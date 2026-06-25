import re

with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()

phases = {
    'A': (1, 12), 'B': (12, 35), 'C': (35, 53),
    'C→D': (53, 67), 'D': (67, 76), '终局': (76, 78),
}

emotions = {
    '天真/可爱/娇羞': ['脸红', '耳尖', '害羞', '不好意思', '抿嘴', '低头.*笑', '被自己', '蜷.*脚', '幼鸟', '初学者', '自己先笑', '轻声笑', '耳朵.*粉', '脸.*红', '被.*逗笑', '扑哧', '噗嗤'],
    '慌乱/震惊': ['慌乱', '震惊', '僵住', '没反应', '猛地', '弹了一下', '不知措', '手忙脚', '吓.*跳', '吸.*气'],
    '生气/委屈': ['生气', '委屈', '愤怒', '咬牙', '攥紧', '下颌', '怨恨', '恨'],
    '害怕/恐惧': ['害怕', '恐惧', '战栗', '发抖', '颤抖'],
    '放荡/大胆/淫乱': ['咽下去', '咽下了', '吞下', '从容', '老手', '不再犹豫', '没有退', '放肆', '大胆', '淫'],
}

for phase_name, (start, end) in phases.items():
    print(f'\n## {phase_name}阶段 (N{start:02d}-N{end-1:02d})')
    for emo_name, patterns in emotions.items():
        count = 0
        for n in range(start, end):
            eid = f'N{n:02d}'
            m = re.search(r'### 事件' + eid + '[：:]', text)
            if not m: continue
            # Find CLOSING ``` (skip opening ```yaml)
            chunk = text[m.start():]
            first_bt = chunk.find('```')
            second_bt = chunk.find('```', first_bt + 3)
            body = chunk[:second_bt] if second_bt > 0 else ''
            for p in patterns:
                if re.search(p, body):
                    count += 1
                    break
        total = end - start
        pct = count/total*100 if total else 0
        bar = '#' * int(pct/10) + '-' * (10-int(pct/10))
        print(f'  {emo_name}: {bar} {count}/{total}')
