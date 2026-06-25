import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'### 事件N04[：:]', text)
end_m = re.search(r'\n```', text[m.start():])
print(f'end_m found: {end_m is not None}')
if end_m:
    body = text[m.start():m.start()+end_m.start()]
    print(f'Body length: {len(body)}')
    for p in ['蜷', '耳尖', '耳朵', '笑了', '害羞', '不好意思', '抿嘴']:
        print(f'  {p}: {p in body}')
else:
    chunk = text[m.start():m.start()+2000]
    bt = chunk.find('```')
    print(f'First backtick at offset: {bt}')
