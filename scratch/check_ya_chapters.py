import json

with open('output/Eldoria_V10.31.0.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data.get('entries', {})

chapter_hits = []
for k, v in entries.items():
    comment = v.get('comment', '')
    content = v.get('content', '')
    if comment.startswith('第') and '章' in comment:
        for line in content.split('\n'):
            if '呀' in line and '吱呀' not in line:
                chapter_hits.append((comment, v.get('key', []), line.strip()))

print(f"Chapter hits count: {len(chapter_hits)}")
for comment, keys, l in chapter_hits:
    print(f"[{comment}] (Keys: {keys}): {l}")
