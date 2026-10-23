import json

with open('output/Eldoria_V10.31.0.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data.get('entries', {})

print("=== 检查非剧情章节（设定卡/规则卡）中是否有'呀' ===")
setting_hits = []
for k, v in entries.items():
    comment = v.get('comment', '')
    content = v.get('content', '')
    # 过滤剧情章节
    if comment.startswith('第') and '章' in comment:
        continue
    for line in content.split('\n'):
        if '呀' in line and '吱呀' not in line:
            setting_hits.append((comment, line.strip()))

print(f"Setting hits count: {len(setting_hits)}")
for comment, l in setting_hits:
    print(f"[{comment}]: {l}")
