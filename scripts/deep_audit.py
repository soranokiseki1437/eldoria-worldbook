#!/usr/bin/env python3
"""深度审计：逐章对比修正后索引 vs 原文实际性行为，找出混乱规律"""
import os, re

STORY_DIR = "docs/story"
INDEX_FILE = "docs/story/_sex_index.txt"

# 标签检测（宽泛但分层）
RULES = {
    "本番": [r'(?:插入|抽送|内射|整根.{0,4}(?:没入|进入))[^。]*(?:小穴|蜜穴|蜜壶)', r'(?:小穴|蜜穴|蜜壶)[^。]*(?:插入|抽送|内射)'],
    "肛交": [r'(?:插入|抽送|推进|进入)[^。]*(?:菊穴|后庭|屁眼|后门)', r'(?:菊穴|后庭|屁眼|后门)[^。]*(?:插入|抽送|进入)'],
    "口交": [r'含[^。]*(?:肉棒|鸡巴|龟头|茎身)', r'(?:吞入|吞吐)[^。]*(?:肉棒|鸡巴|龟头)', r'(?:嘴唇|嘴)[^。]{0,20}(?:裹|含)[^。]*(?:肉棒|鸡巴|龟头)'],
    "被口交": [r'舔[^。]*(?:蜜穴|阴蒂|花瓣|小穴|阴唇|蜜壶)', r'(?:舌头|舌尖|唇舌)[^。]{0,20}(?:蜜穴|阴蒂|小穴|腿间)'],
    "乳交": [r'(?:乳房|乳沟|双乳|乳肉|奶子)[^。]*(?:夹|裹|包).{0,10}(?:肉棒|鸡巴|茎身|龟头)', r'(?:肉棒|鸡巴)[^。]*(?:乳沟|乳房|双乳|乳肉)[^。]*(?:抽送|夹|裹|进出)'],
    "足交": [r'(?:脚|足|足弓|脚趾|脚心)[^。]*(?:套弄|夹住|滑动|裹住|上下).{0,10}(?:肉棒|鸡巴|茎身|龟头)'],
    "手交": [r'(?:手|手指|手掌)[^。]*(?:套弄|打飞机|上下.{0,4}(?:滑动|套弄)|撸).{0,10}(?:肉棒|鸡巴|茎身)', r'(?:握住|握着)[^。]*(?:肉棒|鸡巴)[^。]*(?:套弄|上下|滑动|打飞机|撸)', r'打飞机'],
    "指交": [r'手指[^。]*(?:插入|进入|推进|进出|搅)[^。]*(?:小穴|蜜穴|蜜壶)'],
    "腿交": [r'(?:大腿|腿缝|腿间|腿根)[^。]*(?:夹|抽送|进出).{0,10}(?:肉棒|鸡巴)'],
    "蹭穴": [r'蹭[^。]*(?:穴口|蜜穴口|蜜穴|阴蒂|入口)'],
}

def detect(text):
    text = text.replace('\n', '')
    return {t for t, rules in RULES.items() if any(re.search(p, text) for p in rules)}

def main():
    # Scan files
    ch_data = {}  # id -> (name, detected_tags)
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'): continue
            fp = os.path.join(root, f)
            try:
                with open(fp, encoding='utf-8') as fh: c = fh.read()
            except: continue
            m = re.search(r'ID:\s*(\d+)', c)
            if not m: continue
            mid = m.group(1)
            mn = re.search(r'NSFW:\s*(\S+)', c)
            if not mn or mn.group(1) != '是': continue
            mn2 = re.search(r'名称:\s*(.+)', c)
            name = mn2.group(1).strip() if mn2 else "?"
            ms = re.search(r'情境:\s*\n(.*?)(?=\n(?:核心|占有欲确认|章节任务):)', c, re.DOTALL)
            situ = ms.group(1) if ms else ""
            ch_data[mid] = (name, detect(situ))

    # Parse index
    idx = {}  # id -> set(tags)
    cur = None
    with open(INDEX_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('##'):
                m = re.match(r'##\s*(.+?)\s*\(', line)
                cur = m.group(1).strip() if m else cur
            elif m := re.match(r'(\d+):', line):
                idx.setdefault(m.group(1), set()).add(cur)

    # Analyze each tag category
    all_tags = list(RULES.keys())
    tag_stats = {t: {"total": 0, "confirmed": 0, "missing_detect": 0, "extra_detect": 0, "no_overlap": 0} for t in all_tags}

    issues = []
    for tag in all_tags:
        chs_in_idx = {k for k, v in idx.items() if tag in v}
        chs_detected = {k for k, v in ch_data.items() if tag in v}

        tag_stats[tag]["total"] = len(chs_in_idx)

        for ch_id in chs_in_idx:
            detected = ch_data.get(ch_id, ("", set()))[1]
            if tag in detected:
                tag_stats[tag]["confirmed"] += 1
            else:
                tag_stats[tag]["missing_detect"] += 1
                name = ch_data.get(ch_id, ("?", set()))[0]
                # Check what IS detected
                what_is = detected & set(all_tags)
                issues.append((tag, ch_id, name, what_is))

    print(f"{'标签':<8} {'总数':>5} {'确认':>5} {'检测漏':>7} {'准确率':>7}")
    print("-" * 40)
    for tag in all_tags:
        s = tag_stats[tag]
        rate = f"{s['confirmed']/s['total']*100:.0f}%" if s['total'] > 0 else "N/A"
        print(f"{tag:<8} {s['total']:>5} {s['confirmed']:>5} {s['missing_detect']:>7} {rate:>7}")

    print(f"\n{'='*60}")
    print("检测漏详情（索引有但原文未检测到）:")
    print(f"{'='*60}")

    by_tag = {}
    for tag, ch_id, name, what_is in issues:
        by_tag.setdefault(tag, []).append((ch_id, name, what_is))

    for tag in all_tags:
        items = by_tag.get(tag, [])
        if not items: continue
        print(f"\n--- {tag} ({len(items)}个检测漏) ---")
        for ch_id, name, what_is in items[:15]:
            detected_str = ', '.join(sorted(what_is)) if what_is else '(无检测)'
            print(f"  Ch{ch_id} {name}")
            print(f"    实际检测到: {detected_str}")
        if len(items) > 15:
            print(f"  ... 还有 {len(items)-15} 个")

if __name__ == '__main__':
    main()
