import re, json

polished = {}
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    content = f.read()

blocks = re.split(r'### UID (\d+)', content)
for i in range(1, len(blocks), 2):
    uid = blocks[i]
    block = blocks[i+1] if i+1 < len(blocks) else ''
    yaml_match = re.search(r'```\n(.*?)\n```', block, re.DOTALL)
    if yaml_match:
        yaml_text = yaml_match.group(1)
        polished[uid] = yaml_text

with open('docs/polished_events_backup.json', 'w', encoding='utf-8') as f:
    json.dump(polished, f, ensure_ascii=False, indent=2)

print(f'Saved {len(polished)} polished events')
for uid in sorted(polished.keys(), key=int)[:10]:
    first_line = polished[uid].split('\n')[0]
    print(f'  uid={uid}: {first_line[:80]}')
