import yaml, re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    md = f.read()
start = md.find('## 四、NTRS路线事件')
end = md.find('\n## 五、', start)
section = md[start:end]
m = re.search(r'### 事件N21[：:][^\n]+\n\n\`\`\`yaml\n(.*?)\n\`\`\`', section, re.DOTALL)
if m:
    yt = m.group(1)
    print('YAML text (first 600 chars):')
    print(yt[:600])
    print('\n---')
    try:
        d = yaml.safe_load(yt)
        print('Parsed keys:', list(d.keys()) if d else 'None')
        for k in ['触发条件','性行为等级','情感阶段','情境','占有欲确认','变量','核心']:
            print(f'{k}: {"FOUND" if d and k in d else "MISSING"}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('NO MATCH for N21')
    # Show what's around N21
    idx = section.find('事件N21')
    print(section[idx:idx+200])
