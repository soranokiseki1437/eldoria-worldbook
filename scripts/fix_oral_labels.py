#!/usr/bin/env python3
"""保守修复：仅拆分口交→口交+被口交，其余标签保持原样不动"""
import os, re

STORY_DIR = "docs/story"
ORIG_INDEX = "docs/story/_sex_index.txt"
OUTPUT = "docs/story/_sex_index_fixed.txt"

# 仅用于区分口交方向的检测
FELLATIO = [  # 女给男口交
    r'含[^。]*(?:肉棒|鸡巴|龟头|茎身)',
    r'(?:吞入|吞吐|吞.{0,3}深)[^。]*(?:肉棒|鸡巴|龟头)',
    r'(?:嘴|口)[^。]{0,20}(?:裹|含|吞)[^。]*(?:肉棒|鸡巴|龟头)',
]
CUNNILINGUS = [  # 男给女口交
    r'舔[^。]*(?:蜜穴|阴蒂|花瓣|小穴|阴唇|蜜壶|腿间)',
    r'(?:舌头|舌尖|唇舌)[^。]{0,20}(?:蜜穴|阴蒂|小穴|腿间)',
    r'(?:嘴唇|嘴)[^。]{0,20}(?:贴上|覆上|含住)[^。]*(?:蜜穴|阴蒂|小穴)',
]

def detect_fellatio(text): return any(re.search(p, text) for p in FELLATIO)
def detect_cunnilingus(text): return any(re.search(p, text) for p in CUNNILINGUS)

def parse_chapter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
    except: return None, None, None
    m = re.search(r'ID:\s*(\d+)', content)
    if not m: return None, None, None
    ch_id = m.group(1)
    m_nsfw = re.search(r'NSFW:\s*(\S+)', content)
    if not m_nsfw or m_nsfw.group(1) != '是': return ch_id, None, None
    m_situ = re.search(r'情境:\s*\n(.*?)(?=\n(?:核心|占有欲确认|章节任务):)', content, re.DOTALL)
    situ = m_situ.group(1) if m_situ else ""
    return ch_id, None, situ

def main():
    # 1. 扫描所有章节，建立 章号→(有fellatio, 有cunnilingus)
    print("扫描口交方向...")
    oral_map = {}  # ch_id -> (has_f, has_c)
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'): continue
            ch_id, _, situ = parse_chapter(os.path.join(root, f))
            if ch_id is None or situ is None: continue
            oral_map[ch_id] = (detect_fellatio(situ), detect_cunnilingus(situ))

    # 2. 读取原索引，修正口交标签
    print("修正索引...")
    current_tag = None
    changes = []

    with open(OUTPUT, 'w', encoding='utf-8') as out:
        with open(ORIG_INDEX, 'r', encoding='utf-8') as f:
            for line in f:
                raw = line.rstrip('\n')

                if raw.startswith('##'):
                    current_tag = raw.lstrip('#').strip()
                    m = re.match(r'(.+?)\s*（?\d', current_tag)
                    if m: current_tag = m.group(1).strip()
                    out.write(raw + '\n')
                    continue

                if not raw.strip():
                    out.write('\n')
                    continue

                m = re.match(r'(\d+):(.+)', raw)
                if not m:
                    out.write(raw + '\n')
                    continue

                ch_id = m.group(1)
                rest = m.group(2)

                # 只在口交分类下处理
                if current_tag == "口交":
                    has_f, has_c = oral_map.get(ch_id, (False, False))

                    if has_f and has_c:
                        # 两者都有：保持口交，另外在"被口交"中记录
                        out.write(raw + '\n')
                        changes.append((ch_id, "both"))
                    elif has_c and not has_f:
                        # 只有被口交：改为被口交
                        out.write(f"{ch_id}:{rest}\n")
                        changes.append((ch_id, "口交→被口交"))
                    elif has_f and not has_c:
                        # 只有口交：保持口交
                        out.write(raw + '\n')
                        changes.append((ch_id, "口交"))
                    else:
                        # 都没有：保留原样（可能是auto-detect漏了）
                        out.write(raw + '\n')
                        changes.append((ch_id, "未检测到,保留"))
                else:
                    out.write(raw + '\n')

    # 3. 补充被口交分类
    # 收集所有需要加到被口交的章节
    cunnilingus_chs = []
    for ch_id in oral_map:
        has_f, has_c = oral_map[ch_id]
        if has_c:
            cunnilingus_chs.append(ch_id)

    # 从原索引读取章节名称
    ch_names = {}
    with open(ORIG_INDEX, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = re.match(r'(\d+):(.+)', line)
            if m: ch_names[m.group(1)] = m.group(2).strip()

    # Append被口交 section
    with open(OUTPUT, 'a', encoding='utf-8') as out:
        out.write(f"\n## 被口交 ({len(cunnilingus_chs)}章)\n")
        for ch_id in sorted(cunnilingus_chs, key=int):
            name = ch_names.get(ch_id, "?")
            out.write(f"{ch_id}: {name}\n")

    # Report
    changes_by_type = {}
    for ch_id, typ in changes:
        changes_by_type[typ] = changes_by_type.get(typ, 0) + 1

    print(f"\n口交标签修正完成:")
    for typ, count in sorted(changes_by_type.items()):
        print(f"  {typ}: {count}章")
    print(f"\n被口交(男给女): {len(cunnilingus_chs)}章")
    print(f"修正索引: {OUTPUT}")

if __name__ == '__main__':
    main()
