import json

with open('output/Eldoria_V10.31.0.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== 检查世界书中所有常驻/重要条目中关于菲娜的描述 ===")
for k, v in data.get('entries', {}).items():
    comment = v.get('comment', '')
    content = v.get('content', '')
    keys = v.get('key', [])
    constant = v.get('constant', False)
    
    if constant or 'Seraphina' in comment or '菲娜' in comment:
        # print if there is any mention of speech, voice, dialogue, tone, 口癖, 语气
        for line in content.split('\n'):
            for kw in ['语言', '台词', '口吻', '语气', '声线', '说话', '口头禅', '习惯']:
                if kw in line and ('Seraphina' in line or '菲娜' in line or '她' in line):
                    print(f"[{comment}] {line.strip()[:100]}")
