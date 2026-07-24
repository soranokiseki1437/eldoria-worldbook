#!/usr/bin/env python3
"""生成修正版sex_index：基于审计检测标签，输出新索引文件"""
import os, re

STORY_DIR = "docs/story"
OUTPUT = "docs/story/_sex_index_fixed.txt"

# 精简检测规则（去掉了群交/接吻等辅助标签，只保留核心性行为）
RULES = {
    "本番": [
        r'(?:插入|抽送|内射|整根.{0,4}(?:没入|进入|推进|顶入))[^。]*(?:小穴|蜜穴|蜜壶)',
        r'(?:小穴|蜜穴|蜜壶)[^。]*(?:插入|抽送|内射)',
        r'在(?:她|菲娜|劳拉|艾玛|亚莉莎|亚尔缇娜|奥蕾莉亚|玲|爱丽榭)体内[^。]*(?:射|抽|插)',
    ],
    "肛交": [
        r'(?:插入|抽送|推进|进入|内射|撑开)[^。]*(?:菊穴|后庭|屁眼|后门)',
        r'(?:菊穴|后庭|屁眼|后门)[^。]*(?:插入|抽送|推进|进入|内射)',
    ],
    "口交": [
        r'含[^。]*(?:肉棒|鸡巴|龟头|茎身)',
        r'(?:吞入|吞吐|吞.{0,3}深)[^。]*(?:肉棒|鸡巴|龟头)',
        r'(?:嘴唇|嘴)[^。]{0,20}(?:裹|含)[^。]*(?:肉棒|鸡巴|龟头)',
    ],
    "被口交": [
        r'舔[^。]*(?:蜜穴|阴蒂|花瓣|小穴|阴唇|蜜壶)',
        r'(?:舌头|舌尖|唇舌)[^。]{0,20}(?:蜜穴|阴蒂|小穴|腿间)',
        r'(?:嘴唇|嘴)[^。]{0,20}(?:贴上|覆上|含住)[^。]*(?:蜜穴|阴蒂|小穴)',
    ],
    "乳交": [
        r'(?:乳房|乳沟|双乳|乳肉|奶子)[^。]*(?:夹|裹|包).{0,10}(?:肉棒|鸡巴|茎身|龟头)',
        r'(?:肉棒|鸡巴)[^。]*(?:乳沟|乳房|双乳|乳肉)[^。]*(?:抽送|夹|裹|进出)',
    ],
    "足交": [
        r'(?:脚|足|足弓|脚趾|脚心|脚掌)[^。]*(?:套弄|夹住|滑动|裹住|上下).{0,10}(?:肉棒|鸡巴|茎身|龟头)',
        r'(?:肉棒|鸡巴).{0,20}(?:脚|足|足弓|脚心)[^。]*(?:套弄|夹|滑动)',
    ],
    "手交": [
        r'(?:手|手指|手掌)[^。]*(?:套弄|打飞机|上下.{0,4}(?:滑动|套弄)|撸).{0,10}(?:肉棒|鸡巴|茎身)',
        r'(?:握住|握着)[^。]*(?:肉棒|鸡巴)[^。]*(?:套弄|上下|滑动|打飞机|撸)',
        r'打飞机',
    ],
    "指交": [
        r'手指[^。]*(?:插入|进入|推进|进出|搅|抽送)[^。]*(?:小穴|蜜穴|蜜壶)',
        r'(?:小穴|蜜穴)[^。]*手指[^。]*(?:插入|进入|搅|抽送)',
    ],
    "腿交": [
        r'(?:大腿|腿缝|腿间|腿根)[^。]*(?:夹|抽送|进出|摩擦).{0,10}(?:肉棒|鸡巴|茎身)',
        r'(?:肉棒|鸡巴)[^。]*(?:腿缝|大腿.{0,4}(?:之间|内侧)|腿间)[^。]*(?:夹|抽送|进出)',
    ],
    "蹭穴": [
        r'蹭[^。]*(?:穴口|蜜穴口|蜜穴|阴蒂|入口)',
        r'(?:龟头|肉棒|茎身)[^。]*(?:蹭|磨)[^。]*(?:穴口|蜜穴口|阴蒂)',
    ],
    "接吻": [
        r'(?:舌吻|唇.*?舌|接吻|吻[^。]{0,10}唇)',
        r'嘴唇.*?贴.*?嘴唇',
    ],
    "群交": [
        r'(?:轮奸|群交|3P|4P|轮流.{0,10}插入|(?:两个|三人|四人).{0,10}(?:同时|轮流).{0,10}(?:插入|干|操))',
    ],
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
    except:
        return None, None, None
    m = re.search(r'ID:\s*(\d+)', content)
    if not m: return None, None, None
    ch_id = m.group(1)
    m_nsfw = re.search(r'NSFW:\s*(\S+)', content)
    if not m_nsfw or m_nsfw.group(1) != '是':
        return ch_id, None, None
    m_name = re.search(r'名称:\s*(.+)', content)
    name = m_name.group(1).strip() if m_name else "?"
    m_situ = re.search(r'情境:\s*\n(.*?)(?=\n(?:核心|占有欲确认|章节任务):)', content, re.DOTALL)
    situ = m_situ.group(1) if m_situ else ""
    return ch_id, name, situ

def main():
    # Scan all chapters, build {ch_id: (name, acts)}
    chapters = {}
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'): continue
            ch_id, name, situ = parse_chapter(os.path.join(root, f))
            if ch_id is None or situ is None: continue
            acts = detect_acts(situ)
            chapters[ch_id] = (name, acts)

    # Build by-tag index
    tag_chapters = {}
    for ch_id, (name, acts) in chapters.items():
        for tag in sorted(acts):
            if tag not in tag_chapters:
                tag_chapters[tag] = []
            tag_chapters[tag].append((int(ch_id), name))

    # Sort each tag's chapters numerically
    for tag in tag_chapters:
        tag_chapters[tag].sort(key=lambda x: x[0])

    # Calculate stats
    total = len(chapters)
    tag_order = ["本番","肛交","口交","被口交","乳交","腿交","足交","手交","指交","蹭穴","接吻","群交"]

    print(f"扫描 {total} NSFW章节")
    print(f"检测到 {sum(len(v) for v in tag_chapters.values())} 个标签条目")
    print(f"未检测到标签的章节: {sum(1 for ch_id, (_, acts) in chapters.items() if not acts)}")

    # Write fixed index
    with open(OUTPUT, 'w', encoding='utf-8') as out:
        for tag in tag_order:
            if tag not in tag_chapters: continue
            out.write(f"## {tag} ({len(tag_chapters[tag])}章)\n")
            for ch_id, name in tag_chapters[tag]:
                out.write(f"{ch_id}: {name}\n")
            out.write("\n")
        # Remaining tags
        for tag in sorted(tag_chapters):
            if tag in tag_order: continue
            out.write(f"## {tag} ({len(tag_chapters[tag])}章)\n")
            for ch_id, name in tag_chapters[tag]:
                out.write(f"{ch_id}: {name}\n")
            out.write("\n")

    print(f"\n修正索引已写入: {OUTPUT}")
    print(f"请人工抽查后替换 _sex_index.txt")

if __name__ == '__main__':
    main()
