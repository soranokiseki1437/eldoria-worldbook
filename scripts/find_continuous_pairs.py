#!/usr/bin/env python3
"""识别连续叙事章节对/组。
判断标准：两章共享同一场景+同一角色组+动作直接接续，无法插入时间间隔。
"""
import os, re

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
                    if m and not line.lstrip().startswith(('-','A.','B.','C.')):
                        if current_key:
                            data[current_key] = '\n'.join(current_val).strip()
                        current_key = m.group(1).strip()
                        current_val = [m.group(2).strip()] if m.group(2).strip() else []
                    else:
                        current_val.append(line.rstrip('\n'))
                if current_key:
                    data[current_key] = '\n'.join(current_val).strip()
            ch_id = data.get('ID','')
            if not ch_id: continue
            chapters.append({
                'id': int(ch_id), 'name': data.get('名称',''),
                'stage': data.get('阶段',''),
                'third': data.get('第三者','').strip(),
                'situation': data.get('情境',''),
                'core': data.get('核心',''),
                'end_cond': data.get('章节终止条件',''),
            })
    return sorted(chapters, key=lambda c: c['id'])

def get_group(ch):
    """返回主角组标识"""
    if ch['third']:
        return f"菲娜+黎恩+{ch['third']}"
    return "菲娜+黎恩"

def first_situation_line(ch):
    """返回情境第一句（用于判断场景连续性）"""
    sit = ch['situation']
    if not sit: return ''
    # 取第一行非空内容
    for line in sit.split('\n'):
        line = line.strip().lstrip('-').strip()
        if line:
            return line[:120]
    return ''

def extract_location(text):
    """从文本中提取场景关键词"""
    locations = []
    keywords = ['山洞','石壁','洞穴','洞','木屋','河畔','银流河','心木树','锻造室','工坊',
                '书房','符文室','图书室','营地','林间空地','篝火','温泉','商队','商路',
                '岩丘','石殿','沼泽','密林','花田','雾帷','银塔','走廊','训练场',
                '床','桌上','桌下','长桌','厨房','浴室','帐篷','窗边','门口',
                '艾德里安府邸','矮人小屋','凯尔房间','雷恩房间']
    for kw in keywords:
        if kw in text:
            locations.append(kw)
    return locations

def main():
    chapters = parse_all()

    print("=== 连续叙事候选 (ID>=25) ===\n")
    print("判断标准：同场景 + 同角色组 + 动作紧接着，中间无法插入时间间隔\n")

    candidates = []
    for i in range(len(chapters)-1):
        a = chapters[i]
        b = chapters[i+1]

        if a['id'] < 25 or b['id'] < 25:
            continue

        # 条件1：同一主角组
        same_group = (get_group(a) == get_group(b))
        if not same_group:
            continue

        # 条件2：情境第一句有场景重叠
        sit_a = first_situation_line(a)
        sit_b = first_situation_line(b)
        loc_a = extract_location(sit_a)
        loc_b = extract_location(sit_b)
        shared_locs = set(loc_a) & set(loc_b)

        # 条件3：检查条件3是否已经是"待填写"（说明已处理过）或已有暂停写法
        cond3_empty = '（待填写）' in a.get('end_cond', '')

        if shared_locs:
            candidates.append((a, b, shared_locs))

    # 合并连续组
    groups = []
    used = set()
    for a, b, locs in candidates:
        if a['id'] in used:
            continue
        # 向前追溯
        group = [a]
        used.add(a['id'])
        cur = b
        while True:
            group.append(cur)
            used.add(cur['id'])
            # 查找下一个
            found_next = False
            for a2, b2, _ in candidates:
                if a2['id'] == cur['id'] and b2['id'] not in used:
                    cur = b2
                    found_next = True
                    break
            if not found_next:
                break
        if len(group) >= 2:
            groups.append(group)

    for g in groups:
        ids = '→'.join([f'Ch{c["id"]}' for c in g])
        locs = set()
        for c in g:
            locs.update(extract_location(first_situation_line(c)))
        print(f'{ids} ({len(g)}章) [{", ".join(sorted(locs))}]')
        for c in g:
            cond3_line = ''
            ec = c['end_cond']
            for line in ec.split('\n'):
                if line.strip().startswith('3.'):
                    cond3_line = line.strip()
            print(f'  Ch{c["id"]}: {c["name"][:50]}')
            print(f'         条件3: {cond3_line[:80] if cond3_line else "(无/待填写)"}')
        print()

    print(f'共 {len(groups)} 组连续叙事')

if __name__ == '__main__':
    main()
