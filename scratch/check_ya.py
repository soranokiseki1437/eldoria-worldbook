import json

with open('output/Eldoria_V10.31.0.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data.get('entries', {})
print(f"Total entries: {len(entries)}")

hits = []
for k, v in entries.items():
    comment = v.get('comment', '')
    content = v.get('content', '')
    lines = content.split('\n')
    for line in lines:
        if '呀' in line and '吱呀' not in line:
            hits.append((comment, line.strip()))

print(f"Total non-creak hits: {len(hits)}")
for comment, line in hits:
    print(f"[{comment}]: {line[:100]}")
