#!/usr/bin/env python3
"""Merge策略：原索引为基础 + 移除确认错误 + 补充被口交区分 + 补充缺失标签"""
import os, re

STORY_DIR = "docs/story"
ORIG_INDEX = "docs/story/_sex_index.txt"
OUTPUT = "docs/story/_sex_index_fixed.txt"

RULES = {
    "本番": [r'(?:插入|抽送|内射|整根.{0,4}(?:没入|进入|推进|顶入))[^。]*(?:小穴|蜜穴|蜜壶)', r'(?:小穴|蜜穴|蜜壶)[^。]*(?:插入|抽送|内射)', r'在(?:她|菲娜|劳拉|艾玛|亚莉莎|亚尔缇娜|奥蕾莉亚|玲|爱丽榭)体内[^。]*(?:射|抽|插)'],
    "肛交": [r'(?:插入|抽送|推进|进入|内射|撑开)[^。]*(?:菊穴|后庭|屁眼|后门)', r'(?:菊穴|后庭|屁眼|后门)[^。]*(?:插入|抽送|推进|进入|内射)'],
    "口交": [r'含[^。]*(?:肉棒|鸡巴|龟头|茎身)', r'(?:吞入|吞吐|吞.{0,3}深)[^。]*(?:肉棒|鸡巴|龟头)', r'(?:嘴唇|嘴)[^。]{0,20}(?:裹|含)[^。]*(?:肉棒|鸡巴|龟头)'],
    "被口交": [r'舔[^。]*(?:蜜穴|阴蒂|花瓣|小穴|阴唇|蜜壶)', r'(?:舌头|舌尖|唇舌)[^。]{0,20}(?:蜜穴|阴蒂|小穴|腿间)', r'(?:嘴唇|嘴)[^。]{0,20}(?:贴上|覆上|含住)[^。]*(?:蜜穴|阴蒂|小穴)'],
    "乳交": [r'(?:乳房|乳沟|双乳|乳肉|奶子)[^。]*(?:夹|裹|包).{0,10}(?:肉棒|鸡巴|茎身|龟头)', r'(?:肉棒|鸡巴)[^。]*(?:乳沟|乳房|双乳|乳肉)[^。]*(?:抽送|夹|裹|进出)'],
    "足交": [r'(?:脚|足|足弓|脚趾|脚心|脚掌)[^。]*(?:套弄|夹住|滑动|裹住|上下).{0,10}(?:肉棒|鸡巴|茎身|龟头)', r'(?:肉棒|鸡巴).{0,20}(?:脚|足|足弓|脚心)[^。]*(?:套弄|夹|滑动)'],
    "手交": [r'(?:手|手指|手掌)[^。]*(?:套弄|打飞机|上下.{0,4}(?:滑动|套弄)|撸).{0,10}(?:肉棒|鸡巴|茎身)', r'(?:握住|握着)[^。]*(?:肉棒|鸡巴)[^。]*(?:套弄|上下|滑动|打飞机|撸)', r'打飞机'],
    "指交": [r'手指[^。]*(?:插入|进入|推进|进出|搅|抽送)[^。]*(?:小穴|蜜穴|蜜壶)', r'(?:小穴|蜜穴)[^。]*手指[^。]*(?:插入|进入|搅|抽送)'],
    "腿交": [r'(?:大腿|腿缝|腿间|腿根)[^。]*(?:夹|抽送|进出|摩擦).{0,10}(?:肉棒|鸡巴|茎身)', r'(?:肉棒|鸡巴)[^。]*(?:腿缝|大腿.{0,4}(?:之间|内侧)|腿间)[^。]*(?:夹|抽送|进出)'],
    "蹭穴": [r'蹭[^。]*(?:穴口|蜜穴口|蜜穴|阴蒂|入口)', r'(?:龟头|肉棒|茎身)[^。]*(?:蹭|磨)[^。]*(?:穴口|蜜穴口|阴蒂)'],
    "接吻": [r'(?:舌吻|接吻|吻[^。]{0,10}唇)', r'嘴唇.*?贴.*?嘴唇'],
    "群交": [r'(?:轮奸|群交|3P|4P|轮流.{0,10}插入|(?:两个|三人|四人).{0,10}(?:同时|轮流).{0,10}(?:插入|干|操))'],
    "暴露": [r'(?:全裸|赤裸|脱.{0,3}(?:光|掉)).{0,20}(?:站|躺|跪|坐|展示)', r'(?:展示|暴露|露).{0,10}(?:乳房|蜜穴|阴部|身体|裸)'],
    "触碰": [r'(?:抚摸|揉|摸|碰|按)[^。]*(?:乳房|乳尖|阴蒂|蜜穴|大腿内侧)', r'(?:乳房|乳尖)[^。]*(?:抚摸|揉|摸)'],
}

def detect_acts(text):
    text = text.replace('\n', '')
    found = set()
    for tag, rule_list in RULES.items():
        for pattern in rule_list:
            if re.search(pattern, text):
                found.add(tag)
                break
    return found

def parse_chapter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except: return None, None, None
    m = re.search(r'ID:\s*(\d+)', content)
    if not m: return None, None, None
    ch_id = m.group(1)
    m_nsfw = re.search(r'NSFW:\s*(\S+)', content)
    if not m_nsfw or m_nsfw.group(1) != '是': return ch_id, None, None
    m_name = re.search(r'名称:\s*(.+)', content)
    name = m_name.group(1).strip() if m_name else "?"
    m_situ = re.search(r'情境:\s*\n(.*?)(?=\n(?:核心|占有欲确认|章节任务):)', content, re.DOTALL)
    situ = m_situ.group(1) if m_situ else ""
    return ch_id, name, situ

def parse_orig_index():
    """返回 {章节号: set(标签)} """
    idx = {}
    current_tag = None
    with open(ORIG_INDEX, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('##'):
                tag = line.lstrip('#').strip()
                m = re.match(r'(.+?)\s*（?\d', tag)
                if m: tag = m.group(1).strip()
                current_tag = tag
                continue
            m = re.match(r'(\d+):', line)
            if m and current_tag:
                ch = m.group(1)
                if ch not in idx: idx[ch] = set()
                idx[ch].add(current_tag)
    return idx

def main():
    print("扫描章节...")
    # Build {ch_id: (name, detected_acts)}
    ch_data = {}
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'): continue
            ch_id, name, situ = parse_chapter(os.path.join(root, f))
            if ch_id is None or situ is None: continue
            ch_data[ch_id] = (name, detect_acts(situ))

    print("解析原索引...")
    orig = parse_orig_index()
    all_tags_in_orig = set()
    for tags in orig.values(): all_tags_in_orig.update(tags)

    # Merge: orig为基础, 移除确认多余, 添加确认缺失
    merged = {}  # {ch_id: set(tags)}
    stats = {"kept": 0, "removed": 0, "added": 0}

    for ch_id in set(list(orig.keys()) + list(ch_data.keys())):
        name = ch_data.get(ch_id, ("?", set()))[0]
        detected = ch_data.get(ch_id, (name, set()))[1]
        orig_tags = orig.get(ch_id, set())

        final = set(orig_tags)  # start with original

        # Remove: 索引有但检测无 (原口交→拆分为口交+被口交)
        for tag in list(final):
            # 口交特殊处理：如果检测到被口交但没检测到口交，且原文没有含肉棒动作
            if tag == "口交":
                has_fellatio = "口交" in detected
                has_cunnilingus = "被口交" in detected
                if not has_fellatio and has_cunnilingus:
                    final.discard("口交")
                    final.add("被口交")
                    stats["removed"] += 1
                    stats["added"] += 1
                elif has_fellatio and not has_cunnilingus:
                    pass  # keep 口交
                elif has_fellatio and has_cunnilingus:
                    final.add("被口交")
                    stats["added"] += 1
            # 其他标签：检测不到就移除
            elif tag not in detected and tag not in ("未分类", "隐奸"):
                final.discard(tag)
                stats["removed"] += 1

        # Add: 检测有但索引无
        for tag in detected:
            if tag not in final and tag != "接吻":  # 接吻太泛，不自动加
                # Only add if it's a clear detection AND not already covered by existing
                if tag == "被口交" and "口交" in final:
                    final.add(tag)  # add distinction
                    stats["added"] += 1
                elif tag not in ("口交", "被口交"):  # non-oral: add if detected
                    if tag not in ("接吻",):  # skip noisy tags
                        final.add(tag)
                        stats["added"] += 1

        merged[ch_id] = (name, final)

    print(f"保留标签: {stats['kept']}, 移除错误: {stats['removed']}, 新增: {stats['added']}")

    # Build output by tag
    tag_order = ["本番","肛交","口交","被口交","乳交","腿交","足交","手交","指交","蹭穴","接吻","暴露","触碰","隐奸","群交","未分类"]
    tag_chs = {t: [] for t in tag_order}
    for ch_id, (name, tags) in merged.items():
        for tag in tags:
            if tag not in tag_chs: tag_chs[tag] = []
            tag_chs[tag].append((int(ch_id), name))

    for tag in tag_chs:
        tag_chs[tag].sort(key=lambda x: x[0])

    with open(OUTPUT, 'w', encoding='utf-8') as out:
        for tag in tag_order:
            if not tag_chs[tag]: continue
            out.write(f"## {tag} ({len(tag_chs[tag])}章)\n")
            for ch_id, name in tag_chs[tag]:
                out.write(f"{ch_id}: {name}\n")
            out.write("\n")

    print(f"\n修正索引: {OUTPUT}")
    for tag in tag_order:
        if tag_chs[tag]:
            print(f"  {tag}: {len(tag_chs[tag])}章")

if __name__ == '__main__':
    main()
