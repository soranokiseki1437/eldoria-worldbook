#!/usr/bin/env python3
"""分析章节密集度，识别需要插入过渡章节的位置"""
import os, re, json

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'story')

def parse_all():
    chapters = []
    for root, dirs, files in os.walk(STORY_DIR):
        for f in sorted(files):
            if f.startswith('_') or not f.endswith('.TXT'): continue
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as ff:
                data = {}
                current_key = None
                current_val = []
                for line in ff:
                    m = re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', line)
                    if m and not line.lstrip().startswith(('-', 'A.', 'B.', 'C.')):
                        if current_key:
                            data[current_key] = '\n'.join(current_val).strip()
                        current_key = m.group(1).strip()
                        current_val = [m.group(2).strip()] if m.group(2).strip() else []
                    else:
                        current_val.append(line.rstrip('\n'))
                if current_key:
                    data[current_key] = '\n'.join(current_val).strip()
            ch_id = data.get('ID', '')
            if not ch_id: continue
            chapters.append({
                'id': int(ch_id), 'name': data.get('名称', ''),
                'nsfw': data.get('NSFW', '') == '是',
                'stage': data.get('阶段', ''), 'third': data.get('第三者', ''),
                'sex_lv': data.get('性行为等级', ''),
            })
    return sorted(chapters, key=lambda c: c['id'])

def main():
    chapters = parse_all()
    print(f'Total: {len(chapters)} chapters\n')

    # 1. NSFW密集区间
    print('=== NSFW密集区间 (连续3+章NSFW无SFW缓冲, ID>=25) ===')
    clusters = []
    i = 0
    while i < len(chapters):
        ch = chapters[i]
        if ch['nsfw'] and ch['id'] >= 25:
            start_idx = i
            cluster = []
            while i < len(chapters) and chapters[i]['nsfw'] and chapters[i]['id'] >= 25:
                cluster.append(chapters[i])
                i += 1
            if len(cluster) >= 3:
                thirds = set(c['third'] for c in cluster if c['third'])
                ts = '/'.join(sorted(thirds)[:3]) if thirds else '纯爱'
                rng = f'{cluster[0]["id"]}-{cluster[-1]["id"]}'
                clusters.append({'range': rng, 'count': len(cluster), 'thirds': ts, 'chapters': cluster})
                print(f'  Ch{cluster[0]["id"]}-{cluster[-1]["id"]} ({len(cluster)}章) [{ts}]')
                for c in cluster:
                    print(f'    {c["id"]}: {c["name"][:50]} | 第三者={c["third"] or "无"} | Lv{c["sex_lv"]}')
        else:
            i += 1

    # 2. 推荐插入点
    print('\n=== 推荐过渡章节插入点 (4+章密集区间中间) ===')
    for cl in clusters:
        if cl['count'] >= 4:
            mid = cl['chapters'][len(cl['chapters'])//2]['id']
            print(f'  {cl["range"]} ({cl["count"]}章 {cl["thirds"]}) → 建议在Ch{mid}前后插入过渡章')

    # 3. 第三者弧线总览
    print('\n=== 第三者弧线总览 ===')
    from collections import defaultdict
    arcs = defaultdict(list)
    for ch in chapters:
        if ch['third'] and ch['id'] >= 25:
            arcs[ch['third']].append(ch['id'])
    for name, ids in sorted(arcs.items()):
        print(f'  {name}: Ch{min(ids)}-{max(ids)} ({len(ids)}章)')

    # 4. 现有SFW章
    print('\n=== 现有SFW缓冲章 (ID>=25) ===')
    sfw = [c for c in chapters if not c['nsfw'] and c['id'] >= 25]
    for c in sfw:
        print(f'  Ch{c["id"]}: {c["name"][:50]}')

if __name__ == '__main__':
    main()
