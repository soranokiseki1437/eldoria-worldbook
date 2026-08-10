#!/usr/bin/env python3
"""sex_index标签审计：扫描情境内容，用动作+部位二元链检测实际性行为，对比索引标签"""

import os, re, sys

STORY_DIR = "docs/story"
INDEX_FILE = "docs/story/_sex_index.txt"

# === 检测规则：动作链 ===
RULES = {
    # 必须严格：动作动词 + 目标身体部位 在一段内同时出现
    "本番": [
        # 插入/抽送/内射 + 小穴/蜜穴/蜜壶
        r'(?:插入|抽送|内射|整根.{0,4}(?:没入|进入|推进|顶入))[^。]*(?:小穴|蜜穴|蜜壶)',
        r'(?:小穴|蜜穴|蜜壶)[^。]*(?:插入|抽送|内射|整根.{0,4}(?:没入|进入))',
        # 她体内 / 在她里面 + 射 / 抽送
        r'在(?:她|菲娜|劳拉|艾玛|亚莉莎|亚尔缇娜|奥蕾莉亚|玲|爱丽榭)体内[^。]*(?:射|抽|插)',
        r'[。]他.{0,30}(?:插入|进入|推进)[^。]*(?:小穴|蜜穴|体内)',
    ],
    "肛交": [
        r'(?:插入|抽送|推进|进入|内射|撑开)[^。]*(?:菊穴|后庭|屁眼|后门)',
        r'(?:菊穴|后庭|屁眼|后门)[^。]*(?:插入|抽送|推进|进入|内射)',
    ],
    "口交": [  # 女给男：含/吞 + 肉棒/鸡巴/龟头
        r'含[^。]*(?:肉棒|鸡巴|龟头|茎身)',
        r'(?:吞入|吞吐|吞.{0,3}深)[^。]*(?:肉棒|鸡巴|龟头)',
        r'(?:嘴唇|嘴)[^。]{0,20}(?:裹|含)[^。]*(?:肉棒|鸡巴|龟头)',
        r'给她?口交|为她?口交',
    ],
    "被口交": [  # 男给女：舔/吸/舌头 + 蜜穴/阴蒂/花瓣/小穴
        r'舔[^。]*(?:蜜穴|阴蒂|花瓣|小穴|阴唇|蜜壶)',
        r'(?:舌头|舌尖|唇舌)[^。]{0,20}(?:蜜穴|阴蒂|小穴|腿间)',
        r'(?:蜜穴|阴蒂)[^。]{0,30}(?:舔|舌头|舌尖)',
        r'(?:嘴唇|嘴)[^。]{0,20}(?:贴上|覆上|含住)[^。]*(?:蜜穴|阴蒂|小穴)',
        r'为她?口交|给他?口交.*?(?:蜜穴|小穴)',
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
    ],
    "群交": [
        r'(?:轮奸|群交|3P|4P|轮流.{0,10}插入|同时.{0,10}(?:插入|干|操)|两个.*?同时.{0,10}(?:插入|干|操|进来))',
    ],
}

def detect_acts(text):
    """扫描一段文本，返回检测到的性行为标签集合"""
    found = set()
    # Normalize text - remove newlines
    text = text.replace('\n', '')

    for tag, rule_list in RULES.items():
        for pattern in rule_list:
            if re.search(pattern, text):
                found.add(tag)
                break
    return found

def parse_index():
    """解析sex_index，返回 {章节号: set(标签)}"""
    index = {}
    current_tag = None
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('##'):
                current_tag = line.lstrip('#').strip()
                # Extract tag name before (
                m = re.match(r'(.+?)（\d+章）', current_tag)
                if m:
                    current_tag = m.group(1).strip()
                elif '章' in current_tag:
                    current_tag = current_tag.split('(')[0].strip()
                continue
            if line.startswith('---'):
                continue
            if ':' not in line:
                continue
            m = re.match(r'(\d+):', line)
            if m:
                ch_num = m.group(1)
                if ch_num not in index:
                    index[ch_num] = set()
                if current_tag:
                    index[ch_num].add(current_tag)
    return index

def parse_chapter(filepath):
    """解析章节TXT，返回 (id, 情境文本)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None, None

    # Extract ID
    m = re.search(r'ID:\s*(\d+)', content)
    if not m:
        return None, None
    ch_id = m.group(1)

    # Extract NSFW
    m_nsfw = re.search(r'NSFW:\s*(\S+)', content)
    if not m_nsfw or m_nsfw.group(1) != '是':
        return ch_id, None  # Non-NSFW, skip

    # Extract 情境 section
    m_situ = re.search(r'情境:\s*\n(.*?)(?=\n(?:核心|占有欲确认|章节任务):)', content, re.DOTALL)
    if not m_situ:
        return ch_id, None

    situ_text = m_situ.group(1)
    return ch_id, situ_text

def main():
    # Parse index
    print("解析 sex_index...")
    index = parse_index()
    print(f"  {len(index)} 个章节在索引中")

    # Scan all chapters
    print("\n扫描章节情境内容...")
    discrepancies = []
    total_nsfw = 0

    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'):
                continue
            filepath = os.path.join(root, f)
            ch_id, situ = parse_chapter(filepath)
            if ch_id is None:
                continue
            if situ is None:
                continue  # Non-NSFW
            total_nsfw += 1

            # Detect acts
            detected = detect_acts(situ)

            # Get index labels
            index_labels = index.get(ch_id, set())

            # Compare
            missing_in_index = detected - index_labels  # detected but not in index
            extra_in_index = index_labels - detected  # in index but not detected
            has_index = ch_id in index

            if missing_in_index or extra_in_index or not has_index:
                title_m = re.search(r'名称:\s*(.+)', open(filepath, encoding='utf-8').read())
                title = title_m.group(1).strip() if title_m else "?"
                discrepancies.append((ch_id, title, detected, index_labels, missing_in_index, extra_in_index, not has_index))

    # Sort by chapter number
    discrepancies.sort(key=lambda x: int(x[0]))

    # Output
    print(f"\n{'='*80}")
    print(f"审计结果: {total_nsfw} NSFW章节扫描完成")
    print(f"差异章节: {len(discrepancies)} 个")
    print(f"{'='*80}\n")

    if not discrepancies:
        print("✓ 无差异，索引完全准确！")
        return

    # Summary by error type
    missing_count = sum(1 for d in discrepancies if d[4])
    extra_count = sum(1 for d in discrepancies if d[5])
    unindexed_count = sum(1 for d in discrepancies if d[6])
    print(f"索引缺失标签: {missing_count} 章")
    print(f"索引多余标签: {extra_count} 章")
    print(f"未收录章节: {unindexed_count} 章")
    print(f"\n{'='*80}")
    print("详细差异列表 (需人工确认):")
    print(f"{'='*80}\n")

    for ch_id, title, detected, idx_labels, missing, extra, unindexed in discrepancies:
        print(f"[Ch{ch_id}] {title}")
        if unindexed:
            print(f"  ⚠ 未收录在sex_index中!")
            print(f"  检测到: {', '.join(sorted(detected)) if detected else '(无)'}")
        else:
            idx_str = ', '.join(sorted(idx_labels)) if idx_labels else '(空)'
            det_str = ', '.join(sorted(detected)) if detected else '(无)'
            print(f"  索引: {idx_str}")
            print(f"  检测: {det_str}")
            if missing:
                print(f"  → 索引缺失: {', '.join(sorted(missing))}")
            if extra:
                print(f"  → 索引多余: {', '.join(sorted(extra))}")
        print()

if __name__ == '__main__':
    main()
