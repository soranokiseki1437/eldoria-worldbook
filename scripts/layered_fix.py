#!/usr/bin/env python3
"""三层修复：
1. 扫描所有NSFW章节，用宽松检测初步标记
2. 与当前索引对比，分三类：确认错误 / 确认缺失 / 需人工判读
3. 只输出高置信度修复 + 低置信度待审列表
"""
import os, re

STORY_DIR = "docs/story"
INDEX_FILE = "docs/story/_sex_index.txt"

# 检测规则分高低置信度
HI_CONF = {
    # 高置信度：匹配到了基本就是真的
    "被口交": [
        (r'舔[^。]{0,30}(?:蜜穴|阴蒂|花瓣|小穴)', 1.0),
        (r'(?:舌头|舌尖|唇舌)[^。]{0,20}(?:蜜穴|阴蒂|小穴)', 0.95),
        (r'(?:嘴唇|嘴)[^。]{0,20}(?:贴上|覆上|含住)[^。]{0,20}(?:蜜穴|阴蒂)', 0.9),
    ],
    "本番": [
        (r'(?:插入|抽送|内射)[^。]{0,30}(?:小穴|蜜穴|蜜壶)', 1.0),
        (r'在(?:她|菲娜|劳拉|艾玛|亚莉莎|亚尔缇娜|奥蕾莉亚|玲|爱丽榭)体内[^。]{0,20}(?:射|抽|插)', 0.95),
        (r'(?:整根|肉棒)[^。]{0,20}(?:没入|进入|推入|顶入)[^。]{0,20}(?:小穴|蜜穴)', 0.95),
    ],
    "肛交": [
        (r'(?:插入|抽送|推进|进入)[^。]{0,30}(?:菊穴|后庭|屁眼|后门)', 1.0),
        (r'(?:菊穴|后庭|屁眼|后门)[^。]{0,30}(?:插入|抽送|推进|进入)', 1.0),
    ],
    "乳交": [
        (r'(?:乳房|乳沟|双乳|乳肉|奶子)[^。]{0,20}(?:夹|裹|包)[^。]{0,10}(?:肉棒|鸡巴|茎身|龟头)', 1.0),
        (r'(?:肉棒|鸡巴)[^。]{0,20}(?:乳沟|乳房|双乳)[^。]{0,20}(?:抽送|进出)', 0.95),
    ],
}
LO_CONF = {
    "口交": [
        (r'含[^。]{0,30}(?:肉棒|鸡巴|龟头|茎身)', 0.9),
        (r'(?:吞入|吞吐|吞.{0,3}深)[^。]{0,20}(?:肉棒|鸡巴|龟头)', 0.9),
        (r'(?:嘴唇|嘴)[^。]{0,10}(?:裹|含)[^。]{0,20}(?:肉棒|鸡巴|龟头)', 0.85),
    ],
    "足交": [
        (r'(?:脚|足|足弓|脚趾|脚心)[^。]{0,30}(?:套弄|夹住|滑动|裹住)[^。]{0,10}(?:肉棒|鸡巴|茎身)', 0.85),
        (r'足交', 0.95),
    ],
    "手交": [
        (r'(?:手|手指|手掌)[^。]{0,20}(?:套弄|打飞机|撸)[^。]{0,10}(?:肉棒|鸡巴|茎身)', 0.85),
        (r'打飞机', 0.95),
        (r'(?:握住|握着)[^。]{0,20}(?:肉棒|鸡巴)[^。]{0,10}(?:套弄|上下|滑动)', 0.8),
    ],
    "指交": [
        (r'手指[^。]{0,20}(?:插入|进入|推进|进出|搅)[^。]{0,20}(?:小穴|蜜穴|蜜壶)', 0.9),
        (r'指交', 0.95),
    ],
    "腿交": [
        (r'(?:大腿|腿缝|腿间)[^。]{0,20}(?:夹|抽送|进出)[^。]{0,10}(?:肉棒|鸡巴)', 0.85),
        (r'腿交', 0.95),
    ],
    "蹭穴": [
        (r'蹭[^。]{0,20}(?:穴口|蜜穴口|蜜穴|阴蒂|入口)', 0.85),
        (r'(?:龟头|肉棒)[^。]{0,15}(?:蹭|磨)[^。]{0,15}(?:穴口|蜜穴口|阴蒂)', 0.8),
    ],
}

def detect(text):
    """返回 {标签: 最高置信度}"""
    text = text.replace('\n', '')
    result = {}
    for rules in [HI_CONF, LO_CONF]:
        for tag, patterns in rules.items():
            best = 0
            for pat, conf in patterns:
                if re.search(pat, text) and conf > best:
                    best = conf
            if best > 0:
                result[tag] = best
    return result

def main():
    # Scan files
    ch_data = {}
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

    # Parse current index
    idx = {}
    cur = None
    with open(INDEX_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('##'):
                m = re.match(r'##\s*(.+?)\s*\(', line)
                cur = m.group(1).strip() if m else cur
            elif m := re.match(r'(\d+):', line):
                idx.setdefault(m.group(1), set()).add(cur)

    # Categorize actions
    remove = []  # (ch_id, tag, name, reason)
    add = []     # (ch_id, tag, name, conf)
    missing_chs = []  # NSFW chapters not in index at all

    for ch_id, (name, detected) in ch_data.items():
        idx_tags = idx.get(ch_id, set())

        if not idx_tags:
            # Chapter not in index
            hi_tags = {t for t, c in detected.items() if c >= 0.9}
            lo_tags = {t for t, c in detected.items() if 0.7 <= c < 0.9}
            missing_chs.append((ch_id, name, hi_tags, lo_tags))
            continue

        # Check index tags that shouldn't be there
        for tag in idx_tags:
            if tag not in detected:
                # Index says X, detection found nothing
                remove.append((ch_id, tag, name, "未检测到"))
            elif detected[tag] < 0.7:
                # Index says X, detection found low confidence
                remove.append((ch_id, tag, name, f"检测置信度仅{detected[tag]:.0%}"))

        # Check detected tags missing from index
        for tag, conf in detected.items():
            if tag not in idx_tags and conf >= 0.9:
                add.append((ch_id, tag, name, conf))

    # Output
    print(f"扫描 {len(ch_data)} NSFW章节")
    print(f"确认应移除标签: {len(remove)} 条")
    print(f"确认应添加标签: {len(add)} 条")
    print(f"未收录章节: {len(missing_chs)} 个")

    if remove:
        print(f"\n{'='*50}")
        print("【移除】索引有但原文无（高置信度）:")
        for ch_id, tag, name, reason in remove:
            print(f"  Ch{ch_id} [{tag}] {name} — {reason}")

    if add:
        print(f"\n{'='*50}")
        print("【添加】原文有但索引无（高置信度）:")
        for ch_id, tag, name, conf in add:
            print(f"  Ch{ch_id} [{tag}] {name} (置信度{conf:.0%})")

    if missing_chs:
        print(f"\n{'='*50}")
        print("【未收录】NSFW章节完全不在索引中:")
        for ch_id, name, hi, lo in missing_chs[:30]:
            hi_s = ','.join(sorted(hi)) if hi else '-'
            lo_s = ','.join(sorted(lo)) if lo else '-'
            print(f"  Ch{ch_id} {name}")
            print(f"    高置信: {hi_s}  低置信: {lo_s}")
        if len(missing_chs) > 30:
            print(f"  ... 还有 {len(missing_chs)-30} 个")

if __name__ == '__main__':
    main()
