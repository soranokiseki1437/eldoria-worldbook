# -*- coding: utf-8 -*-
"""
generate_event_browser.py — 全事件浏览器生成器
================================================
解析 05_事件系统.md 中所有事件，生成自包含的交互式HTML页面。

用法：
    python scripts/generate_event_browser.py

输出：
    visual/全事件浏览器.html
"""

import re
import json
import os
import sys

# ─── 路径配置 ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_MD = os.path.join(BASE_DIR, "docs", "05_事件系统.md")
OUTPUT_HTML = os.path.join(BASE_DIR, "visual", "全事件浏览器.html")

# ─── 前缀元数据 ─────────────────────────────────────────
PREFIX_META = {
    "E":  {"name": "固定事件",   "color": "#4facfe", "route": "共通",     "order": 1},
    "P":  {"name": "纯爱路线",   "color": "#f093fb", "route": "纯爱",     "order": 2},
    "N":  {"name": "NTRS路线",   "color": "#fa709a", "route": "NTRS",     "order": 3},
    "PN": {"name": "被动NTR路线","color": "#30cfd0", "route": "被动NTR",   "order": 4},
    "S":  {"name": "NSFW通用",   "color": "#ff9a9e", "route": "通用/多线", "order": 5},
    "C":  {"name": "角色NSFW",   "color": "#a18cd1", "route": "通用",     "order": 6},
    "G":  {"name": "通用SFW",    "color": "#43e97b", "route": "通用",     "order": 7},
    "W":  {"name": "世界事件",   "color": "#f5576c", "route": "共通",     "order": 8},
    "H":  {"name": "隐藏事件",   "color": "#a8edea", "route": "隐藏",     "order": 9},
    "R":  {"name": "黎恩专属",   "color": "#89f7fe", "route": "黎恩",     "order": 10},
}

# ─── 章节名称 ──────────────────────────────────────────
CHAPTER_NAMES = {
    1: "林间空地的苏醒", 2: "影牙兽的威胁", 3: "心木废墟的秘密",
    4: "VII班的到来", 5: "森林的庆典", 6: "古老先灵的低语",
    7: "各方来客", 8: "路线分化",
    9: "纯爱·守护者契约", 10: "温泉与誓言", 11: "古老的启示",
    12: "边界与试探", 13: "第一次见证", 14: "多人共享之夜",
    15: "圣光之镜",
    16: "被动NTR·第一次缺席", 17: "Thalion的诱惑", 18: "堕落之夜",
    19: "重新争取",
    20: "净化仪式", 21: "与Thalion的决战", 22: "终极抉择",
    23: "终局", 24: "新的开始",
}

# ─── 已知事件清单（从章节映射表+事件标题行提取） ─────────
# 用于识别"仅有摘要"的事件
KNOWN_EVENTS = {
    # E系列 (15个) — 从 事件1-15 标题
    **{f"E{i:02d}": f"事件{i}" for i in range(1, 16)},
    # P系列 (16个)
    **{f"P{i}": f"事件P{i}" for i in range(1, 17)},
    # N系列 (15个)
    **{f"N{i}": f"事件N{i}" for i in range(1, 16)},
    # PN系列 (13个)
    **{f"PN{i}": f"事件PN{i}" for i in range(1, 14)},
    # S系列 (30个)
    **{f"S{i}": f"事件S{i}" for i in range(1, 31)},
    # C系列 (6个)
    **{f"C{i}": f"事件C{i}" for i in range(1, 7)},
    # G系列 (7个)
    **{f"G{i}": f"事件G{i}" for i in range(1, 8)},
    # W系列 (8个) — W1-W8
    **{f"W{i}": f"事件W{i}" for i in range(1, 9)},
    # H系列 (5个)
    **{f"H{i}": f"事件H{i}" for i in range(1, 6)},
    # R系列 (8个)
    **{f"R{i}": f"事件R{i}" for i in range(1, 9)},
}


def parse_chapter_mapping(content):
    """从章节映射表提取事件→章节的分配。
    处理多行：当前章节为空时继承上一章节号。
    """
    event_chapters = {}
    event_names_from_table = {}

    # 找到映射表范围
    table_start = content.find("## 事件-章节映射表")
    table_end = content.find("---", table_start)
    table_text = content[table_start:table_end]

    current_chapter = 0
    for line in table_text.split("\n"):
        # 匹配: | 第X章 ... | E01 | 事件名 |
        # 或: | | W1 | 事件名 | (继承上一章节)
        m = re.match(r'\|\s*(?:第(\d+)章[^|]*)?\|\s*([A-Z]+\d+)\s*(?:\(([^)]*)\))?\s*\|(.+?)\|', line)
        if not m:
            continue

        chap_str = m.group(1)
        event_id = m.group(2).strip()
        event_name = m.group(4).strip() if m.group(4) else ""

        if chap_str:
            current_chapter = int(chap_str)

        if event_id and current_chapter > 0:
            event_chapters[event_id] = current_chapter
            if event_name:
                event_names_from_table[event_id] = event_name

    return event_chapters, event_names_from_table


def parse_event_headers(content):
    """解析所有 ### 事件XXX 标题及其后的内容块。
    返回: {event_id: {name, raw_block, has_yaml}}
    """
    events_raw = {}

    # 匹配所有 ### 事件 标题行
    # 格式1: ### 事件{NUMBER}：{NAME}  (E系列)
    # 格式2: ### 事件{PREFIX}{NUMBER}：{NAME}  (其他系列)
    header_pattern = re.compile(
        r'^###\s+事件([A-Z]*\d+)[：:]\s*(.+?)$',
        re.MULTILINE
    )

    matches = list(header_pattern.finditer(content))
    for i, match in enumerate(matches):
        num_part = match.group(1).strip()
        raw_name = match.group(2).strip()

        # E系列：事件1-15的ID加上"E"前缀
        if re.match(r'^\d+$', num_part):
            event_id = f"E{int(num_part):02d}"
        else:
            event_id = num_part

        # 提取名称本体（去除括号中的路线/类型标注）
        name = re.sub(r'\s*[（(][^)）]*[)）]\s*', '', raw_name).strip()

        # 提取该事件的内容块（到下一个 ### 事件 或 ## 或文件尾）
        block_start = match.end()
        next_header = re.search(r'^###\s+|^##\s', content[block_start:], re.MULTILINE)
        if next_header:
            block_end = block_start + next_header.start()
        else:
            block_end = len(content)
        block = content[block_start:block_end].strip()

        # 检查是否有YAML块
        yaml_match = re.search(r'```yaml\s*\n(.*?)```', block, re.DOTALL)
        has_yaml = yaml_match is not None
        raw_yaml = yaml_match.group(1).strip() if has_yaml else ""

        events_raw[event_id] = {
            "name": name,
            "raw_name": raw_name,
            "raw_block": block,
            "has_yaml": has_yaml,
            "raw_yaml": raw_yaml,
        }

    return events_raw


def infer_tags(event_id, name, raw_yaml):
    """推断类型标签"""
    prefix = re.match(r'^([A-Z]+)', event_id).group(1)
    content_lower = (name + " " + raw_yaml).lower()
    tags = []

    # 路线标记
    route_map = {"P": "纯爱", "N": "NTRS", "PN": "被动NTR", "E": "共通",
                 "G": "共通", "W": "共通", "H": "隐藏", "R": "黎恩"}
    route = route_map.get(prefix, "")
    if route:
        tags.append(route)

    # NSFW关键词检测
    nsfw_kws = ["足交", "本番", "手交", "口交", "乳交", "腿交", "nsfw",
                "隐奸", "群交", "夜袭", "暴露", "足下的", "足部", "裸足",
                "丝袜", "玷污", "堕落之夜", "足控", "含入", "契约之夜",
                "鬼之圣光", "温泉的清晨", "晨露", "桌下之", "即兴", "倒影"]
    sfw_kws = ["训练", "狩猎", "篝火故事", "对话", "约会", "净化仪式",
               "战斗准备", "启示", "修炼", "守护夜", "正式介绍", "宣誓"]

    is_nsfw = any(kw in content_lower for kw in nsfw_kws)
    is_sfw = any(kw in name for kw in sfw_kws)

    if is_nsfw:
        tags.append("NSFW")
        # 细分
        type_map = {
            "足交": ["足交", "裸足", "足部", "丝袜", "足下", "足控", "晨露", "玉足"],
            "本番": ["本番", "契约之夜", "交融", "清晨", "即兴", "倒影", "直接本番", "傲娇本番", "游戏本番", "骑士本番"],
            "手交": ["手交"],
            "口交": ["口交", "含入", "唇"],
            "乳交": ["乳交", "圣光之谷", "胸怀"],
            "腿交": ["腿交", "大腿之间"],
            "隐奸": ["隐奸", "桌下之"],
            "群交": ["群交", "赌局", "共享之夜"],
        }
        for tag, keywords in type_map.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(tag)
    elif is_sfw or prefix in ("E", "G", "W"):
        tags.append("SFW")
    else:
        tags.append("SFW")

    return tags


def get_nsfw_level(tags):
    """返回最高NSFW等级"""
    levels = ["本番", "口交", "乳交", "腿交", "足交", "手交", "隐奸", "群交", "NSFW"]
    for lv in levels:
        if lv in tags:
            return lv
    return ""


def build_events(content):
    """主解析函数：整合章节映射、事件标题、YAML内容"""
    # 1. 解析章节映射
    event_chapters, event_names_from_table = parse_chapter_mapping(content)

    # 2. 解析所有事件标题和YAML块
    events_raw = parse_event_headers(content)

    # 3. 构建完整事件列表
    events = []
    seen_ids = set()

    for event_id, raw in events_raw.items():
        seen_ids.add(event_id)
        prefix = re.match(r'^([A-Z]+)', event_id).group(1)
        meta = PREFIX_META.get(prefix, {"name": prefix, "color": "#888", "order": 99})
        chapter = event_chapters.get(event_id, 0)

        raw_yaml = raw["raw_yaml"]
        name = raw["name"]

        # 提取触发条件
        trigger = ""
        if raw_yaml:
            m = re.search(r'触发条件[：:]\s*(.+?)(?:\n|$)', raw_yaml)
            if m:
                trigger = m.group(1).strip()

        # 提取情境预览
        scene_preview = ""
        if raw_yaml:
            for kw in ["情境：", "情境:", "场景描述：", "场景描述:"]:
                m = re.search(rf'{kw}\s*\n?\s*(.+?)(?=\n\s{{4,}}[A-Z一-鿿])', raw_yaml, re.DOTALL)
                if m:
                    scene_preview = m.group(1).strip()[:200]
                    break

        tags = infer_tags(event_id, name, raw_yaml)
        nsfw_level = get_nsfw_level(tags)
        has_branches = "纯爱" in raw_yaml and ("NTRS" in raw_yaml or "被动NTR" in raw_yaml)

        events.append({
            "id": event_id,
            "prefix": prefix,
            "name": name,
            "chapter": chapter,
            "chapter_name": CHAPTER_NAMES.get(chapter, ""),
            "trigger": trigger,
            "scene_preview": scene_preview,
            "tags": tags,
            "nsfw_level": nsfw_level,
            "has_branches": has_branches,
            "has_yaml": raw["has_yaml"],
            "is_summary": False,
            "raw_yaml": raw_yaml,
            "prefix_name": meta["name"],
            "prefix_color": meta["color"],
        })

    # 4. 补充"仅有摘要"的事件（在章节映射中但无 ### 事件 标题）
    for event_id, default_name in KNOWN_EVENTS.items():
        if event_id not in seen_ids:
            prefix = re.match(r'^([A-Z]+)', event_id).group(1)
            meta = PREFIX_META.get(prefix, {"name": prefix, "color": "#888", "order": 99})
            chapter = event_chapters.get(event_id, 0)
            table_name = event_names_from_table.get(event_id, "")
            name = table_name or default_name

            tags = [meta.get("route", "")]
            tags.append("SFW")
            tags = [t for t in tags if t]

            events.append({
                "id": event_id,
                "prefix": prefix,
                "name": name,
                "chapter": chapter,
                "chapter_name": CHAPTER_NAMES.get(chapter, ""),
                "trigger": "",
                "scene_preview": "",
                "tags": tags,
                "nsfw_level": "",
                "has_branches": False,
                "has_yaml": False,
                "is_summary": True,
                "raw_yaml": f"# ⚠️ 摘要事件 — 当前仅有章节映射，无详细内容\n"
                           f"# 事件ID: {event_id}\n"
                           f"# 事件名称: {name}\n"
                           f"# 所属章节: 第{chapter}章{' ' + CHAPTER_NAMES.get(chapter, '') if chapter else '未分配'}\n"
                           f"# 前缀系列: {meta['name']}\n"
                           f"#\n"
                           f"# 待补全：触发条件、场景描述、玩家选择、变量更新",
                "prefix_name": meta["name"],
                "prefix_color": meta["color"],
            })
            seen_ids.add(event_id)

    # 按前缀+编号排序
    def sort_key(e):
        prefix = e["prefix"]
        order = PREFIX_META.get(prefix, {}).get("order", 99)
        num_match = re.search(r'(\d+)', e["id"])
        num = int(num_match.group(1)) if num_match else 0
        return (order, num)

    events.sort(key=sort_key)
    return events


# ══════════════════════════════════════════════════════════
# HTML 生成
# ══════════════════════════════════════════════════════════

def generate_html(events):
    events_json = json.dumps(events, ensure_ascii=False, indent=2)

    # 收集元数据
    all_prefixes = sorted(set(e["prefix"] for e in events),
                          key=lambda x: PREFIX_META.get(x, {}).get("order", 99))
    all_tags = set()
    all_chapters = set()
    for e in events:
        all_chapters.add(e["chapter"])
        for t in e["tags"]:
            all_tags.add(t)

    # 前缀按钮
    prefix_btns = []
    for p in all_prefixes:
        meta = PREFIX_META.get(p, {"name": p, "color": "#888"})
        count = sum(1 for e in events if e["prefix"] == p)
        prefix_btns.append(
            f'<button class="filter-btn prefix-btn active" data-filter="prefix" data-value="{p}" '
            f'style="--accent:{meta["color"]}">{p}<span>{meta["name"]}({count})</span></button>'
        )

    # 类型按钮
    tag_order = ["SFW", "NSFW", "足交", "本番", "手交", "口交", "乳交", "腿交", "隐奸", "群交",
                 "纯爱", "NTRS", "被动NTR", "共通", "隐藏", "黎恩"]
    tag_btns = ['<button class="filter-btn type-btn active" data-filter="tag" data-value="all">全部</button>']
    for t in tag_order:
        if t in all_tags:
            count = sum(1 for e in events if t in e["tags"])
            tag_btns.append(f'<button class="filter-btn type-btn" data-filter="tag" data-value="{t}">{t}({count})</button>')

    # 章节按钮
    chapter_btns = ['<button class="filter-btn chapter-btn active" data-filter="chapter" data-value="all">全部</button>']
    for ch in sorted(all_chapters):
        if ch > 0:
            ch_name = CHAPTER_NAMES.get(ch, "")
            short = ch_name[:6] if ch_name else ""
            count = sum(1 for e in events if e["chapter"] == ch)
            chapter_btns.append(
                f'<button class="filter-btn chapter-btn" data-filter="chapter" data-value="{ch}" '
                f'title="第{ch}章 {ch_name}">Ch.{ch}<span>{short}({count})</span></button>'
            )

    # 统计信息
    total = len(events)
    has_yaml_count = sum(1 for e in events if e["has_yaml"])
    summary_count = sum(1 for e in events if e["is_summary"])
    nsfw_count = sum(1 for e in events if "NSFW" in e["tags"])
    sfw_count = total - nsfw_count

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Eldoria 全事件浏览器 — V4.6.2</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  :root {{
    --bg: #0f0f1a;
    --bg2: #1a1a2e;
    --text: #e0e0e0;
    --text2: #999;
    --text3: #666;
    --border: #2a2a4a;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
  }}

  // ═══ 侧边栏 ═══ */
  .sidebar {{
    width: 380px;
    min-width: 380px;
    background: var(--bg2);
    border-right: 1px solid var(--border);
    height: 100vh;
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 10;
  }}
  .sidebar-header {{
    padding: 16px 18px 10px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }}
  .sidebar-header h2 {{
    font-size: 18px;
    background: linear-gradient(90deg, #f0a0c0, #c0a0f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2px;
  }}
  .sidebar-header .stats {{
    font-size: 14px;
    color: var(--text2);
    line-height: 1.6;
  }}
  .sidebar-header .stats em {{
    font-style: normal;
    color: #c0a0f0;
    font-weight: bold;
  }}

  /* 搜索框 */
  .search-wrap {{
    padding: 10px 18px;
    border-bottom: 1px solid var(--border);
  }}
  .search-input {{
    width: 100%;
    padding: 10px 14px;
    border-radius: 18px;
    border: 1px solid var(--border);
    background: rgba(30, 30, 50, 0.6);
    color: var(--text);
    font-size: 16px;
    outline: none;
    transition: all 0.3s;
  }}
  .search-input:focus {{
    border-color: #667eea;
    background: rgba(40, 40, 70, 0.8);
  }}
  .search-input::placeholder {{ color: #555; }}

  /* 筛选区域 */
  .filter-section {{
    padding: 8px 18px;
    border-bottom: 1px solid var(--border);
  }}
  .filter-section h3 {{
    font-size: 14px;
    color: var(--text2);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: pointer;
    user-select: none;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .filter-section h3::after {{
    content: '▾';
    font-size: 10px;
    transition: transform 0.2s;
    opacity: 0.4;
  }}
  .filter-section.collapsed h3::after {{
    transform: rotate(-90deg);
  }}
  .filter-section.collapsed .filter-btns {{
    display: none;
  }}
  .filter-btns {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }}
  .filter-btn {{
    padding: 3px 8px;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    border: 1px solid var(--border);
    background: rgba(30, 30, 50, 0.5);
    color: #aaa;
    transition: all 0.2s;
    user-select: none;
    white-space: nowrap;
  }}
  .filter-btn:hover {{
    background: rgba(60, 60, 100, 0.5);
    color: #fff;
  }}
  .filter-btn.active {{ color: #fff; border-color: transparent; }}

  /* 前缀按钮 */
  .prefix-btn.active {{ background: var(--accent); }}
  .prefix-btn span {{ font-size: 14px; opacity: 0.65; margin-left: 1px; }}

  /* 章节按钮 */
  .chapter-btn.active {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
  .chapter-btn span {{ font-size: 14px; opacity: 0.55; margin-left: 1px; }}

  /* 类型按钮 */
  .type-btn[data-value="NSFW"] {{ border-color: #fa709a44; }}
  .type-btn[data-value="NSFW"].active {{ background: linear-gradient(135deg, #fa709a, #f5576c); }}
  .type-btn[data-value="SFW"] {{ border-color: #43e97b44; }}
  .type-btn[data-value="SFW"].active {{ background: linear-gradient(135deg, #43e97b, #38f9d7); color: #000; }}
  .type-btn[data-value="足交"].active {{ background: linear-gradient(135deg, #ff9a9e, #fecfef); color: #000; }}
  .type-btn[data-value="本番"].active {{ background: linear-gradient(135deg, #fa709a, #fee140); color: #000; }}
  .type-btn[data-value="手交"].active {{ background: linear-gradient(135deg, #a18cd1, #fbc2eb); color: #000; }}
  .type-btn[data-value="口交"].active {{ background: linear-gradient(135deg, #ffecd2, #fcb69f); color: #000; }}
  .type-btn[data-value="乳交"].active {{ background: linear-gradient(135deg, #89f7fe, #66a6ff); color: #000; }}
  .type-btn[data-value="腿交"].active {{ background: linear-gradient(135deg, #d4a5a5, #9b8ea8); }}
  .type-btn[data-value="隐奸"].active {{ background: linear-gradient(135deg, #a8edea, #fed6e3); color: #000; }}
  .type-btn[data-value="群交"].active {{ background: linear-gradient(135deg, #f5576c, #ff9a9e); }}
  .type-btn[data-value="纯爱"].active {{ background: linear-gradient(135deg, #f093fb, #f5576c); }}
  .type-btn[data-value="NTRS"].active {{ background: linear-gradient(135deg, #fa709a, #fee140); color: #000; }}
  .type-btn[data-value="被动NTR"].active {{ background: linear-gradient(135deg, #30cfd0, #330867); }}
  .type-btn[data-value="隐藏"].active {{ background: linear-gradient(135deg, #a8edea, #fed6e3); color: #000; }}
  .type-btn[data-value="共通"].active {{ background: linear-gradient(135deg, #4facfe, #00f2fe); color: #000; }}

  /* 滚动事件列表 */
  .sidebar-events {{
    flex: 1;
    overflow-y: auto;
    padding: 6px 8px;
  }}
  .sidebar-events::-webkit-scrollbar {{ width: 4px; }}
  .sidebar-events::-webkit-scrollbar-thumb {{ background: #333; border-radius: 2px; }}

  .event-list-item {{
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 2px;
    transition: all 0.15s;
    border-left: 3px solid transparent;
  }}
  .event-list-item:hover {{ background: rgba(255,255,255,0.04); }}
  .event-list-item.active {{
    background: rgba(102, 126, 234, 0.15);
    border-left-color: #667eea;
  }}
  .event-list-item .eid {{
    font-size: 14px;
    font-weight: bold;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .event-list-item .ename {{
    font-size: 16px;
    color: #aaa;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .event-list-item .emeta {{
    font-size: 14px;
    color: #555;
    margin-top: 1px;
    display: flex;
    gap: 5px;
    align-items: center;
  }}
  .event-list-item .dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
  }}
  .event-list-item .badge {{
    font-size: 13px;
    padding: 1px 4px;
    border-radius: 4px;
  }}

  /* 前缀分组标题 */
  .event-group-header {{
    padding: 5px 10px;
    margin: 4px 0 2px;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
    user-select: none;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: background 0.15s;
  }}
  .event-group-header:hover {{
    background: rgba(255,255,255,0.03);
  }}
  .event-group-header .arrow {{
    font-size: 9px;
    transition: transform 0.2s;
    opacity: 0.4;
  }}
  .event-group-header.collapsed .arrow {{
    transform: rotate(-90deg);
  }}
  .event-group-header .gname {{
    flex: 1;
  }}
  .event-group-header .gcount {{
    font-size: 10px;
    opacity: 0.5;
    font-weight: normal;
  }}
  .event-group-items {{
    /* items under a group */
  }}
  .event-group-items.hidden {{
    display: none;
  }}
  .badge-nsfw {{ background: #fa709a33; color: #fa709a; }}
  .badge-sfw {{ background: #43e97b33; color: #43e97b; }}
  .badge-sum {{ background: #fecf6f22; color: #fecf6f; }}
  .badge-yaml {{ background: #667eea22; color: #8899dd; }}

  // ═══ 主内容区 ═══ */
  .main {{
    flex: 1;
    height: 100vh;
    overflow-y: auto;
    padding: 28px 36px;
  }}
  .main::-webkit-scrollbar {{ width: 6px; }}
  .main::-webkit-scrollbar-thumb {{ background: #333; border-radius: 3px; }}

  .empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text3);
  }}
  .empty-state .icon {{ font-size: 60px; margin-bottom: 14px; opacity: 0.25; }}
  .empty-state h3 {{ font-size: 18px; margin-bottom: 6px; color: var(--text2); }}

  /* 事件详情 */
  .detail-header {{
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
  }}
  .detail-header .eid-large {{
    font-size: 28px;
    font-weight: bold;
    background: linear-gradient(90deg, #c0a0f0, #f0a0c0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline-block;
    margin-right: 10px;
  }}
  .detail-header .ename-large {{
    font-size: 22px;
    color: #fff;
    display: inline;
  }}
  .detail-header .meta-row {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 8px;
  }}
  .meta-chip {{
    padding: 3px 9px;
    border-radius: 10px;
    font-size: 16px;
    border: 1px solid var(--border);
  }}

  .detail-section {{ margin-bottom: 16px; }}
  .detail-section h3 {{
    font-size: 15px;
    color: #888;
    margin-bottom: 6px;
    padding-bottom: 3px;
    border-bottom: 1px dashed rgba(255,255,255,0.05);
  }}

  .yaml-block {{
    background: #0a0a14;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    font-family: 'SF Mono', 'Cascadia Code', 'Consolas', 'Microsoft YaHei', monospace;
    font-size: 15px;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #c8d6e5;
    position: relative;
  }}
  .summary-block {{
    background: #1a1a10;
    border: 1px dashed #fecf6f44;
  }}

  .copy-btn {{
    position: absolute;
    top: 8px;
    right: 12px;
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    border: 1px solid var(--border);
    background: rgba(30, 30, 50, 0.8);
    color: #888;
    transition: all 0.2s;
    z-index: 1;
  }}
  .copy-btn:hover {{ background: #667eea33; border-color: #667eea; color: #fff; }}
  .copy-btn.copied {{ background: #43e97b33; border-color: #43e97b; color: #43e97b; }}

  /* 分支标记 */
  .tag-chip {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 7px;
    font-size: 15px;
    margin: 2px;
  }}

  /* 响应式 */
  @media (max-width: 800px) {{
    body {{ flex-direction: column; }}
    .sidebar {{ width: 100%; min-width: auto; height: auto; max-height: 42vh; position: relative; }}
    .main {{ height: auto; padding: 16px; }}
  }}

  /* 快捷键提示 */
  .kbd-hint {{
    position: fixed;
    bottom: 12px;
    right: 16px;
    font-size: 15px;
    color: #444;
    pointer-events: none;
  }}
</style>
</head>
<body>

<!-- ═══ 侧边栏 ═══ -->
<div class="sidebar">
  <div class="sidebar-header">
    <h2>Eldoria 全事件浏览器</h2>
    <div class="stats">
      共 <em>{total}</em> 事件 ·
      已完善 <em>{has_yaml_count}</em> ·
      摘要 <em>{summary_count}</em><br>
      NSFW <em>{nsfw_count}</em> · SFW <em>{sfw_count}</em> · V4.6.2
    </div>
  </div>

  <div class="search-wrap">
    <input type="text" class="search-input" id="searchInput"
           placeholder="🔍 搜索 (Ctrl+K) — 名称、ID、关键词...">
  </div>

  <div class="filter-section" id="filterPrefix">
    <h3 onclick="toggleFilter(this)">📂 事件前缀</h3>
    <div class="filter-btns" id="prefixFilters">
      <button class="filter-btn prefix-btn active" data-filter="prefix" data-value="all" style="--accent:#667eea">全部</button>
      {"".join(prefix_btns)}
    </div>
  </div>

  <div class="filter-section" id="filterTag">
    <h3 onclick="toggleFilter(this)">🏷️ 类型标签</h3>
    <div class="filter-btns" id="tagFilters">
      {"".join(tag_btns)}
    </div>
  </div>

  <div class="filter-section" id="filterChapter">
    <h3 onclick="toggleFilter(this)">📖 章节</h3>
    <div class="filter-btns" id="chapterFilters">
      {"".join(chapter_btns)}
    </div>
  </div>

  <div class="sidebar-events" id="eventList">
    <!-- JS动态填充 -->
  </div>
</div>

<!-- ═══ 主内容区 ═══ -->
<div class="main" id="mainContent">
  <div class="empty-state">
    <div class="icon">📋</div>
    <h3>选择事件查看详情</h3>
    <p>从左侧列表点击任意事件，此处将展示完整事件定义</p>
  </div>
</div>

<div class="kbd-hint">Ctrl+K 搜索 · Esc 清空</div>

<script>
const EVENTS = {events_json};

let activeFilters = {{ prefix: 'all', tag: 'all', chapter: 'all', search: '' }};
let selectedEventId = null;

const $list = document.getElementById('eventList');
const $main = document.getElementById('mainContent');
const $search = document.getElementById('searchInput');

// ═══ 筛选 ═══
function getFiltered() {{
  return EVENTS.filter(e => {{
    if (activeFilters.prefix !== 'all' && e.prefix !== activeFilters.prefix) return false;
    if (activeFilters.tag !== 'all' && !e.tags.includes(activeFilters.tag)) return false;
    if (activeFilters.chapter !== 'all' && e.chapter !== parseInt(activeFilters.chapter)) return false;
    if (activeFilters.search) {{
      const q = activeFilters.search.toLowerCase();
      const hay = (e.id + ' ' + e.name + ' ' + e.tags.join(' ') + ' ' +
                   e.trigger + ' ' + e.scene_preview + ' ' + e.raw_yaml).toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});
}}

// ═══ 渲染列表（按前缀分组） ═══
const PREFIX_ORDER = ['E','P','N','PN','S','C','G','W','H','R'];
const PREFIX_NAMES = {{E:'固定事件',P:'纯爱路线',N:'NTRS路线',PN:'被动NTR',S:'NSFW通用',C:'角色NSFW',G:'通用SFW',W:'世界事件',H:'隐藏事件',R:'黎恩专属'}};
const PREFIX_COLORS = {{E:'#4facfe',P:'#f093fb',N:'#fa709a',PN:'#30cfd0',S:'#ff9a9e',C:'#a18cd1',G:'#43e97b',W:'#f5576c',H:'#a8edea',R:'#89f7fe'}};

function renderList() {{
  const filtered = getFiltered();

  if (!filtered.length) {{
    $list.innerHTML = '<div style="padding:20px;color:#555;text-align:center;">无匹配事件</div>';
    return;
  }}

  // 按前缀分组
  const groups = {{}};
  for (const e of filtered) {{
    if (!groups[e.prefix]) groups[e.prefix] = [];
    groups[e.prefix].push(e);
  }}

  // 渲染分组
  let html = '';
  for (const p of PREFIX_ORDER) {{
    const items = groups[p];
    if (!items || !items.length) continue;
    const color = PREFIX_COLORS[p] || '#888';
    const pname = PREFIX_NAMES[p] || p;
    const yamlCount = items.filter(e => e.has_yaml).length;
    const sumCount = items.filter(e => e.is_summary).length;
    const collapseKey = 'group_' + p;
    const collapsed = localStorage.getItem(collapseKey) === '1';

    html += `<div class="event-group-header${{collapsed ? ' collapsed' : ''}}" data-group="${{p}}" style="color:${{color}}" onclick="toggleGroup('${{p}}')">
      <span class="arrow">▾</span>
      <span class="dot" style="background:${{color}};width:8px;height:8px;border-radius:50%;flex-shrink:0;"></span>
      <span class="gname">${{p}} · ${{pname}}</span>
      <span class="gcount">${{items.length}}事件 ${{yamlCount > 0 ? '✓'+yamlCount : ''}}${{sumCount > 0 ? ' ✎'+sumCount : ''}}</span>
    </div>`;

    html += `<div class="event-group-items${{collapsed ? ' hidden' : ''}}" id="group-${{p}}">`;
    for (const e of items) {{
      const active = e.id === selectedEventId ? ' active' : '';
      const nsfwBadge = e.tags.includes('NSFW')
        ? '<span class="badge badge-nsfw">' + (e.nsfw_level || 'NSFW') + '</span>'
        : '<span class="badge badge-sfw">SFW</span>';
      const sumBadge = e.is_summary ? '<span class="badge badge-sum">摘要</span>' : '';
      const ch = e.chapter > 0 ? 'Ch.' + e.chapter : '';
      html += '<div class="event-list-item' + active + '" data-eid="' + e.id + '" onclick="selectEvent(\\'' + e.id + '\\')">'
        + '<div class="eid"><span class="dot" style="background:' + e.prefix_color + '"></span>'
        + e.id + ' ' + nsfwBadge + sumBadge + '</div>'
        + '<div class="ename">' + e.name + '</div>'
        + '<div class="emeta"><span>' + e.prefix_name + '</span>'
        + (ch ? '<span>' + ch + '</span>' : '')
        + (e.chapter_name ? '<span>' + e.chapter_name.substr(0,8) + '</span>' : '')
        + '</div></div>';
    }}
    html += '</div>';
  }}

  $list.innerHTML = html;
}}

// ═══ 折叠/展开分组 ═══
function toggleGroup(prefix) {{
  const header = document.querySelector('.event-group-header[data-group=\"' + prefix + '\"]');
  const items = document.getElementById('group-' + prefix);
  if (!header || !items) return;
  const collapsed = items.classList.toggle('hidden');
  header.classList.toggle('collapsed', collapsed);
  localStorage.setItem('group_' + prefix, collapsed ? '1' : '0');
}}

// ═══ 折叠/展开筛选区 ═══
function toggleFilter(h3) {{
  const section = h3.parentElement;
  section.classList.toggle('collapsed');
  localStorage.setItem('filter_' + section.id, section.classList.contains('collapsed') ? '1' : '0');
}}

// ═══ 选择事件 ═══
function selectEvent(eventId) {{
  selectedEventId = eventId;
  const e = EVENTS.find(ev => ev.id === eventId);
  if (!e) return;

  const tagsHtml = e.tags.map(t => {{
    const colors = {{
      '纯爱':'#f093fb', 'NTRS':'#fa709a', '被动NTR':'#30cfd0', '共通':'#4facfe',
      'NSFW':'#fa709a', 'SFW':'#43e97b', '足交':'#ff9a9e', '本番':'#fee140',
      '手交':'#a18cd1', '口交':'#fcb69f', '乳交':'#66a6ff', '腿交':'#9b8ea8',
      '隐奸':'#a8edea', '群交':'#f5576c', '黎恩':'#89f7fe', '隐藏':'#a8edea'
    }};
    const c = colors[t] || '#888';
    return `<span class="tag-chip" style="background:${{c}}22;color:${{c}};border:1px solid ${{c}}44">${{t}}</span>`;
  }}).join('');

  const prefixColor = e.prefix_color;
  const yamlContent = e.raw_yaml
    ? e.raw_yaml
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    : '';
  // YAML syntax highlighting - use split/join to avoid f-string escape issues
  const yamlHighlighted = yamlContent.split('\\n').map(function(line) {{
    var m = line.match(/^([ \\t]*)([^:]+)(:)(.*)/);
    if (m) {{
      return m[1] + '<span style="color:#f0a0c0">' + m[2] + '</span>' + m[3] + '<span style="color:#a0c0f0">' + m[4] + '</span>';
    }}
    return line;
  }}).join('\\n');

  $main.innerHTML = `
    <div class="detail-header">
      <span class="eid-large">${{e.id}}</span>
      <span class="ename-large">${{escapeHtml(e.name)}}</span>
      ${{e.is_summary ? '<span class="badge badge-sum" style="font-size:15px;vertical-align:middle;margin-left:8px;">⚠️ 摘要事件</span>' : ''}}
      <div class="meta-row">
        <span class="meta-chip" style="border-color:${{prefixColor}}88;color:${{prefixColor}}">
          ${{e.prefix}} · ${{e.prefix_name}}
        </span>
        ${{e.chapter > 0 ? `<span class="meta-chip" style="border-color:#43e97b88;color:#43e97b">
          第${{e.chapter}}章 · ${{e.chapter_name}}</span>` : ''}}
        ${{e.tags.includes('NSFW')
          ? `<span class="meta-chip" style="border-color:#fa709a88;color:#fa709a;background:#fa709a11">NSFW · ${{e.nsfw_level || 'NSFW'}}</span>`
          : `<span class="meta-chip" style="border-color:#43e97b88;color:#43e97b;background:#43e97b11">SFW</span>`}}
        ${{e.has_branches ? '<span class="meta-chip" style="border-color:#fecf6f88;color:#fecf6f">三线分支</span>' : ''}}
        ${{e.is_summary ? '<span class="meta-chip" style="border-color:#fecf6f88;color:#fecf6f">待补全</span>' : ''}}
      </div>
      <div style="margin-top:6px">${{tagsHtml}}</div>
      ${{e.trigger ? `<div style="margin-top:6px;font-size:14px;color:#888;">触发: ${{escapeHtml(e.trigger)}}</div>` : ''}}
    </div>

    <div class="detail-section">
      <h3>📄 完整事件定义 ${{e.is_summary ? '(摘要 — 05_事件系统.md中无详细内容)' : '(来自 05_事件系统.md)'}}</h3>
      <div class="yaml-block ${{e.is_summary ? 'summary-block' : ''}}" id="yamlBlock">
        <button class="copy-btn" onclick="copyYaml()" id="copyBtn">📋 复制</button>
        <div id="yamlContent">${{yamlHighlighted || '<span style="color:#666;">无内容</span>'}}</div>
      </div>
    </div>

    ${{e.scene_preview ? `
    <div class="detail-section">
      <h3>📝 情境预览</h3>
      <div style="font-size:16px;color:#bbb;line-height:1.7;padding:12px 16px;background:#0a0a14;border-radius:8px;border:1px solid var(--border);">
        ${{escapeHtml(e.scene_preview)}}...
      </div>
    </div>` : ''}}
  `;

  // 滚动列表到选中项
  const item = document.querySelector(`.event-list-item[data-eid="${{eventId}}"]`);
  if (item) item.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});

  renderList();
}}

// ═══ 复制 ═══
function copyYaml() {{
  const e = EVENTS.find(ev => ev.id === selectedEventId);
  if (!e || !e.raw_yaml) return;
  navigator.clipboard.writeText(e.raw_yaml).then(() => {{
    const btn = document.getElementById('copyBtn');
    if (btn) {{ btn.textContent = '✅ 已复制'; btn.classList.add('copied');
      setTimeout(() => {{ btn.textContent = '📋 复制'; btn.classList.remove('copied'); }}, 1500); }}
  }});
}}

function escapeHtml(str) {{
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}}

// ═══ 筛选按钮 ═══
document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const type = btn.dataset.filter;
    const val = btn.dataset.value;
    btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilters[type] = val;
    selectedEventId = null;
    renderList();
    $main.innerHTML = `<div class="empty-state"><div class="icon">📋</div>
      <h3>选择事件查看详情</h3><p>当前匹配: ${{getFiltered().length}} 个事件</p></div>`;
  }});
}});

// ═══ 搜索 ═══
$search.addEventListener('input', () => {{
  activeFilters.search = $search.value.trim();
  renderList();
}});

// ═══ 快捷键 ═══
document.addEventListener('keydown', e => {{
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{ e.preventDefault(); $search.focus(); }}
  if (e.key === 'Escape') {{ $search.blur(); $search.value = ''; activeFilters.search = ''; renderList(); }}
}});

// ═══ 恢复折叠状态 ═══
(function() {{
  // 恢复筛选区折叠
  ['filterPrefix','filterTag','filterChapter'].forEach(function(id) {{
    var el = document.getElementById(id);
    if (el && localStorage.getItem('filter_' + id) === '1') {{
      el.classList.add('collapsed');
    }}
  }});
  // 默认折叠：类型标签和章节（减少初次加载高度）
  if (!localStorage.getItem('filter_tag')) {{
    var tagSec = document.getElementById('filterTag');
    if (tagSec) tagSec.classList.add('collapsed');
  }}
  if (!localStorage.getItem('filter_chapter')) {{
    var chSec = document.getElementById('filterChapter');
    if (chSec) chSec.classList.add('collapsed');
  }}
}})();

// ═══ 初始化 ═══
renderList();
console.log('Eldoria 全事件浏览器就绪 · ' + EVENTS.length + ' 个事件');
</script>

</body>
</html>'''

    return html


# ─── 入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    print(f"解析文件: {EVENT_MD}")
    with open(EVENT_MD, "r", encoding="utf-8") as f:
        content = f.read()

    events = build_events(content)

    # 统计
    prefixes = {}
    for e in events:
        prefixes[e["prefix"]] = prefixes.get(e["prefix"], 0) + 1
    print(f"  解析完成: {len(events)} 个事件")
    print(f"  前缀分布: {prefixes}")
    print(f"  含YAML: {sum(1 for e in events if e['has_yaml'])}")
    print(f"  摘要: {sum(1 for e in events if e['is_summary'])}")

    print(f"生成HTML: {OUTPUT_HTML}")
    html = generate_html(events)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"完成! 文件大小: {len(html):,} 字符")
