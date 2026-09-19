# -*- coding: utf-8 -*-
import re

files = [
    '方案/第一批次_故事1-3章节正文.md',
    '方案/第二批次_故事4-7章节正文.md',
    '方案/第三批次_故事8-10章节正文.md'
]

# Pattern to find dates at the beginning of bullet 1
date_patterns = [
    r'  - \d+月\d+日下午，',
    r'  - \d+月\d+日傍晚，',
    r'  - \d+月\d+日清晨，',
    r'  - \d+月下旬清晨，',
    r'  - \d+月下旬傍晚，',
    r'  - \d+月下旬午后，',
    r'  - \d+月中旬午后，',
    r'  - \d+月中旬清晨，',
    r'  - \d+月中旬傍晚，',
    r'  - \d+月上旬黄昏，',
    r'  - \d+月上旬午后，',
    r'  - \d+月上旬清晨，',
]

for f in files:
    content = open(f, 'r', encoding='utf-8').read()
    orig = content
    
    # Replace dates at bullet 1 starts
    content = re.sub(r'  - \d+月\d+日下午，', '  - 午后，', content)
    content = re.sub(r'  - \d+月\d+日傍晚，', '  - 傍晚，', content)
    content = re.sub(r'  - \d+月\d+日清晨，', '  - 清晨，', content)
    content = re.sub(r'  - \d+月下旬清晨，', '  - 清晨，', content)
    content = re.sub(r'  - \d+月下旬傍晚，', '  - 傍晚，', content)
    content = re.sub(r'  - \d+月下旬午后，', '  - 午后，', content)
    content = re.sub(r'  - \d+月中旬午后，', '  - 午后，', content)
    content = re.sub(r'  - \d+月中旬清晨，', '  - 清晨，', content)
    content = re.sub(r'  - \d+月中旬傍晚，', '  - 傍晚，', content)
    content = re.sub(r'  - \d+月上旬黄昏，', '  - 黄昏，', content)
    content = re.sub(r'  - \d+月上旬午后，', '  - 午后，', content)
    content = re.sub(r'  - \d+月上旬清晨，', '  - 清晨，', content)
    
    if content != orig:
        print(f"Updated dates in {f}")
        with open(f, 'w', encoding='utf-8') as out:
            out.write(content)
    else:
        print(f"No dates found to replace in {f}")

