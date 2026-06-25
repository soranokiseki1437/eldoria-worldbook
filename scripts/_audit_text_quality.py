import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()
start = text.find('## 四、NTRS路线事件')
ntrs = text[start:text.find('## 五、', start)]

print(f'NTRS section: {len(ntrs)} chars')
print()

# 1. Dashes in bullet narrative
dashes = re.findall(r'——', ntrs)
print(f'1. 破折号(——): {len(dashes)}处')

# 2. "不是...而是" pattern
not_but = re.findall(r'不是.{1,30}而是', ntrs)
print(f'2. "不是X而是Y": {len(not_but)}处')
for m in not_but[:8]:
    print(f'   → {m}')

# 3. Meta-references (number counts, progression terms)
meta = re.findall(r'\d+次选择|\d+个事件|\d+次共享|递进|弧线|N\d{2}', ntrs)
print(f'3. 元引用(数字/递进/弧线/事件ID): {len(meta)}处')
for m in meta[:10]:
    print(f'   → {m}')

# 4. "然后笑了/笑了笑" in sex context (potentially inappropriate)
laugh_during = re.findall(r'然后笑[了笑]|笑了$|笑出声|笑得更', ntrs)
print(f'4. 笑(可能不合时宜): {len(laugh_during)}处')

# 5. Check for specific problematic phrases
bad_phrases = ['全副精力', '77次', '78个事件', 'N11的恐惧', 'N75的接受', '不是堕落']
for bp in bad_phrases:
    count = len(re.findall(bp, ntrs))
    if count:
        print(f'5. 问题短语"{bp}": {count}处')
