#!/usr/bin/env python3
"""分析同一主角组的连续章节——找出需要时间间隔但挤在一起的章节对"""
import os, re
from collections import defaultdict

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

            # 确定主角组
            third = data.get('第三者', '').strip()
            if third:
                protagonist_group = f'菲娜+黎恩+{third}'
            else:
                protagonist_group = '菲娜+黎恩'

            chapters.append({
                'id': int(ch_id), 'name': data.get('名称', ''),
                'nsfw': data.get('NSFW', '') == '是',
                'stage': data.get('阶段', ''),
                'third': third,
                'group': protagonist_group,
                'core': data.get('核心', ''),
            })
    return sorted(chapters, key=lambda c: c['id'])

def main():
    chapters = parse_all()

    # 找出同一主角组的连续章节对（ID>=25）
    print('=== 同一主角组连续2+章（ID>=25）===\n')

    clusters = []
    i = 0
    while i < len(chapters):
        ch = chapters[i]
        if ch['id'] < 25:
            i += 1
            continue

        # 找连续同组章节
        cluster = [ch]
        j = i + 1
        while j < len(chapters):
            next_ch = chapters[j]
            if next_ch['group'] == ch['group']:
                cluster.append(next_ch)
                j += 1
            else:
                break

        if len(cluster) >= 2:
            clusters.append(cluster)
            group_label = cluster[0]['group'][:60]
            ids = f'Ch{cluster[0]["id"]}-{cluster[-1]["id"]}'
            print(f'{ids} ({len(cluster)}章) [{group_label}]')
            for c in cluster:
                nsfw_mark = '🔞' if c['nsfw'] else '🌿'
                print(f'  {nsfw_mark} Ch{c["id"]}: {c["name"][:50]}')
            print()

        i = j

    # 统计需要过渡章的位置
    print('=== 建议插入过渡章的位置 ===')
    print('（同一主角组连续2+章，且核心事件无时间连续性要求）\n')

    count = 0
    for cluster in clusters:
        if len(cluster) >= 2:
            # 在cluster中间或每2章后插入
            for k in range(len(cluster) - 1):
                ch_a = cluster[k]
                ch_b = cluster[k + 1]
                # 检查：两个都是NSFW，且没有明确的时间连续性
                # 简化判断：同一主角组连续NSFW章
                if ch_a['nsfw'] and ch_b['nsfw']:
                    count += 1
                    print(f'  #{count}: Ch{ch_a["id"]}→Ch{ch_b["id"]} 之间')
                    print(f'      {ch_a["name"][:45]}')
                    print(f'      {ch_b["name"][:45]}')
                    print(f'      主角组: {ch_a["group"][:50]}')
                    print()

    print(f'共 {count} 个建议插入点')

if __name__ == '__main__':
    main()
