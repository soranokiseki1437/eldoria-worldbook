# -*- coding: utf-8 -*-
"""
generate_chapter_browser.py — 全章节浏览器生成器
==========================================================
直接读取 docs/story/*.TXT 生成自包含的交互式HTML页面。
网格卡片布局，角色×阶段分类，第三者字段精准匹配。

用法：
    python scripts/generate_chapter_browser.py
输出：
    visual/全章节浏览器.html
"""

import re
import json
import os
import sys

# ─── 路径配置 ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_HTML = os.path.join(BASE_DIR, "visual", "全章节浏览器.html")

# ─── 前缀元数据 ─────────────────────────────────────────
from story_config import PREFIX_META, ALL_PREFIXES

# ─── 章节名称（从 DEFAULT_CHAPTERS 动态加载） ──────────────
def _load_chapter_names():
    """从 assign_chapters.DEFAULT_CHAPTERS 构建章节名称映射"""
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))
    try:
        from assign_chapters import DEFAULT_CHAPTERS
        return {ch_num: ch['title'] for ch_num, ch in DEFAULT_CHAPTERS.items()}
    except ImportError:
        return {}

CHAPTER_NAMES = _load_chapter_names()

# ─── KNOWN_EVENTS: 从章节映射表动态生成（不再硬编码） ──
# parse_chapter_mapping 会将所有事件ID提取到 event_names_from_table
# 此处仅设置空字典，build_events 会从映射表中自动填充缺失事件
KNOWN_EVENTS = {}

# ─── 角色名集合（用于标题匹配） ─────────────────
CHARACTER_NAMES = [
    "Seraphina", "菲娜", "黎恩", "凯尔", "艾玛", "劳拉", "菲", "亚莉莎",
    "玲", "爱丽榭", "亚尔缇娜", "乔治", "艾德里安", "雷恩", "奥蕾莉亚",
    "多尔金", "哈根", "法林", "罗恩", "加尔",
]

# ─── 角色检测：第三者 + 好感影响 + 标题 ─────────────────
def extract_main_characters(raw_yaml, event_name):
    """三层提取主角角色名（OR叠加，满足任意一层即加入）。
    仅当三层均无命中时才兜底为 Seraphina+黎恩。
    """
    chars = []

    if not raw_yaml:
        return ["Seraphina", "黎恩"]

    # 第一层：第三者字段（排除空值/解析artifact）
    m = re.search(r'^第三者:\s*(.+)', raw_yaml, re.MULTILINE)
    if m:
        tp_raw = m.group(1).strip()
        if tp_raw and not re.match(r'(黎恩知情|N/A|情境[:：]|核心[:：])', tp_raw):
            cleaned = re.sub(r'[（(][^)）]*[)）]', '', tp_raw)
            cleaned = cleaned.replace('×', '+')
            for name in re.split(r'[+、]', cleaned):
                name = name.strip()
                if name in CHARACTER_NAMES:
                    chars.append(name)

    # 第二层：好感影响字段（排除解析artifact——空字段后接情境等）
    m2 = re.search(r'^好感影响:\s*(.+)', raw_yaml, re.MULTILINE)
    if m2:
        aff_text = m2.group(1).strip()
        if not re.match(r'(情境[:：]|核心[:：]|章节)', aff_text):
            for cname in CHARACTER_NAMES:
                if cname in aff_text and cname not in chars:
                    chars.append(cname)

    # 第三层：标题中的角色名
    for cname in CHARACTER_NAMES:
        if cname in event_name and cname not in chars:
            chars.append(cname)

    # 三层都没命中 → 兜底为 Seraphina+黎恩 章节
    if not chars:
        chars = ["Seraphina", "黎恩"]

    return chars


def load_chapter_mapping():
    """从 assign_chapters.DEFAULT_CHAPTERS 加载事件→章节映射。"""
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))
    try:
        from assign_chapters import DEFAULT_CHAPTERS
    except ImportError:
        return {}, {}
    event_chapters = {}
    event_names_from_table = {}
    for ch_num, ch_data in DEFAULT_CHAPTERS.items():
        for eid in ch_data.get('events', []):
            event_chapters[eid] = ch_num
    return event_chapters, event_names_from_table


def parse_txt_file(filepath):
    """解析单个 .TXT 事件文件，返回 dict"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    data = {}
    current_key = None
    current_value = []
    for line in lines:
        if not line.strip():
            continue
        m = re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', line)
        if m and not line.lstrip().startswith(('-', 'A.', 'B.', 'C.')):
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_value = [val] if val else []
        else:
            current_value.append(line.rstrip('\n'))
    if current_key:
        data[current_key] = '\n'.join(current_value).strip()
    return data


def load_events_from_txt():
    """从 docs/story/{prefix}/*.TXT 读取所有章节数据。
    返回 {event_id: {name, raw_yaml, has_yaml, prefix, ...}}"""
    event_dir = os.path.join(BASE_DIR, 'docs', 'story')
    events_raw = {}
    for pfx in os.listdir(event_dir):
        pfx_path = os.path.join(event_dir, pfx)
        if not os.path.isdir(pfx_path):
            continue
        for fname in sorted(os.listdir(pfx_path)):
            if not fname.upper().endswith('.TXT'):
                continue
            fp = os.path.join(pfx_path, fname)
            data = parse_txt_file(fp)
            eid = data.get('ID', '')
            name = data.get('名称', '')
            if not eid:
                continue
            # Build yaml-like text from key-value pairs for tag inference
            raw_yaml = '\n'.join(f'{k}: {v}' for k, v in data.items())
            # Extract numeric 性行为等级 (TXT field, e.g. "9" or "8（腿交——...）")
            sex_lv_raw = data.get('性行为等级', '').strip()
            sex_lv_m = re.match(r'(\d+)', sex_lv_raw)
            sex_level = int(sex_lv_m.group(1)) if sex_lv_m else None
            events_raw[eid] = {
                'name': name,
                'raw_name': name,
                'raw_yaml': raw_yaml,
                'has_yaml': True,
                'is_nsfw': data.get('NSFW', '').strip() == '是',
                'sex_level': sex_level,
                'prefix': pfx,
            }
    return events_raw


def load_sex_index():
    """读取 docs/story/_sex_index.txt → {章节ID: [标签列表]}
    非整数编号（如 615.5）无法匹配任何章节，打印警告。"""
    index_path = os.path.join(BASE_DIR, 'docs', 'story', '_sex_index.txt')
    index = {}
    non_int = []
    if not os.path.exists(index_path):
        return index, non_int
    with open(index_path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    current_tag = None
    for raw in text.split('\n'):
        line = raw.strip()
        if not line:
            continue
        if line.startswith('##'):
            # '## 本番 (65章)' → '本番'
            parts = line.split()
            current_tag = re.sub(r'[\s(（].*', '', parts[1]) if len(parts) > 1 else ''
            continue
        if line.startswith('#'):
            continue
        m = re.match(r'^([\d.]+):', line)
        if m and current_tag:
            num = m.group(1)
            if '.' in num:
                non_int.append((num, line.split(':', 1)[1].strip()))
                continue
            sid = str(int(num))  # strip leading zeros (020→20) to match TXT ID format
            index.setdefault(sid, []).append(current_tag)
    return index, non_int


def infer_tags(event_id, name, raw_yaml, is_nsfw_explicit=None, prefix="", sex_level=None, sex_index=None):
    """从 _sex_index.txt 读取章节类型标签（手工维护，无自动推断）。"""
    tags = []
    if is_nsfw_explicit is True:
        tags.append("NSFW")
    elif is_nsfw_explicit is False:
        tags.append("SFW")
    else:
        tags.append("SFW")
    # 从手工索引读取类型标签
    if sex_index:
        for t in sex_index.get(event_id, []):
            if t not in tags:
                tags.append(t)
    return tags


def get_nsfw_level(tags):
    levels = ["肛交", "本番", "口交", "乳交", "腿交", "足交", "手交", "指交", "蹭穴", "接吻", "暴露", "触碰", "隐奸", "群交", "未分类", "NSFW"]
    for lv in levels:
        if lv in tags:
            return lv
    return ""


def build_events():
    event_chapters, event_names_from_table = load_chapter_mapping()
    events_raw = load_events_from_txt()
    sex_index, non_int = load_sex_index()
    events = []
    seen_ids = set()
    for event_id, raw in events_raw.items():
        seen_ids.add(event_id)
        prefix = raw.get('prefix', '')  # 从文件来源目录获取
        meta = PREFIX_META.get(prefix, {"name": prefix, "color": "#888", "order": 99})
        chapter = event_chapters.get(event_id, 0)
        raw_yaml = raw["raw_yaml"]
        name = raw["name"]
        trigger = ""
        if raw_yaml:
            m = re.search(r'trigger[：:]\s*(.+?)(?:\n|$)', raw_yaml)
            if m:
                trigger = m.group(1).strip()
        scene_preview = ""
        if raw_yaml:
            for kw in ["情境：", "情境:", "场景描述：", "场景描述:"]:
                m = re.search(rf'{kw}\s*\n?\s*(.+?)(?=\n\s{{4,}}[A-Z一-鿿])', raw_yaml, re.DOTALL)
                if m:
                    scene_preview = m.group(1).strip()[:200]
                    break
        is_nsfw_flag = raw.get('is_nsfw', None)
        tags = infer_tags(event_id, name, raw_yaml, is_nsfw_flag, prefix=prefix, sex_level=raw.get('sex_level'), sex_index=sex_index)
        nsfw_level = get_nsfw_level(tags)
        has_branches = "纯爱" in raw_yaml and ("NTRS" in raw_yaml or "被动NTR" in raw_yaml)
        characters = extract_main_characters(raw_yaml, name)
        events.append({
            "id": event_id, "prefix": prefix, "name": name,
            "chapter": chapter, "chapter_name": CHAPTER_NAMES.get(chapter, ""),
            "trigger": trigger, "scene_preview": scene_preview,
            "tags": tags, "nsfw_level": nsfw_level, "has_branches": has_branches,
            "has_yaml": raw["has_yaml"], "is_summary": False, "raw_yaml": raw_yaml,
            "prefix_name": meta["name"], "prefix_color": meta["color"],
            "characters": characters,
        })
    # sex索引漂移检测 — 索引中的编号找不到对应章节时打印警告
    if non_int:
        print(f"  ⚠ sex索引含 {len(non_int)} 条非整数编号（无法匹配章节，浏览器将忽略）:")
        for num, title in non_int:
            print(f"    {num}: {title}")
    unknown = [sid for sid in sex_index if sid not in seen_ids]
    if unknown:
        print(f"  ⚠ sex索引 {len(unknown)} 条编号在章节文件中不存在（索引脱节，需同步）:")
        for sid in sorted(unknown, key=int)[:20]:
            print(f"    {sid}: {sex_index[sid]}")
        if len(unknown) > 20:
            print(f"    ... 还有 {len(unknown)-20} 条")

    for event_id, default_name in KNOWN_EVENTS.items():
        if event_id not in seen_ids:
            prefix = re.match(r'^([A-Z]+)', event_id)
            prefix = prefix.group(1) if prefix else ''
            meta = PREFIX_META.get(prefix, {"name": prefix, "color": "#888", "order": 99})
            chapter = event_chapters.get(event_id, 0)
            table_name = event_names_from_table.get(event_id, "")
            name = table_name or default_name
            tags = [meta.get("route", ""), "SFW"]
            tags = [t for t in tags if t]
            events.append({
                "id": event_id, "prefix": prefix, "name": name,
                "chapter": chapter, "chapter_name": CHAPTER_NAMES.get(chapter, ""),
                "trigger": "", "scene_preview": "", "tags": tags, "nsfw_level": "",
                "has_branches": False, "has_yaml": False, "is_summary": True,
                "raw_yaml": "",
                "prefix_name": meta["name"], "prefix_color": meta["color"],
                "characters": [],
            })
            seen_ids.add(event_id)

    def sort_key(e):
        prefix = e["prefix"]
        order = PREFIX_META.get(prefix, {}).get("order", 99)
        num_match = re.search(r'(\d+)', e["id"])
        num = int(num_match.group(1)) if num_match else 0
        return (order, num)
    events.sort(key=sort_key)
    return events, event_chapters, event_names_from_table


# ══════════════════════════════════════════════════════════
# event_data.js 生成 — 剧情时间线可视化数据
# ══════════════════════════════════════════════════════════

ROUTE_MAP = {
    '0：序章': 'prologue', '1：试探和暧昧': 'ntrs', '2：挑逗和接受': 'ntrs',
    '3：渐进接触': 'ntrs', '4：跨线': 'ntrs', '5：享受和掌控': 'ntrs',
    '6：放纵': 'ntrs', '7：终局': 'ntrs', '8：后日谈': 'epilogue',
}

def generate_event_data_js(events, event_chapters):
    """从解析结果生成 event_data.js"""
    lines = []
    lines.append("// 自动生成于: " + __import__('datetime').datetime.now().isoformat())
    lines.append("// 数据源: docs/story/*.TXT")
    lines.append("// 生成器: scripts/generate_chapter_browser.py")
    lines.append("")
    lines.append("const EVENTS = [")

    for e in events:
        eid = e["id"]
        title = e["name"]
        route = ROUTE_MAP.get(e["prefix"], "general")
        chapter = e.get("chapter_name", "") or f"第{e['chapter']}章"
        summary = (e.get("scene_preview", "") or e.get("trigger", ""))[:120]
        etype = "nsfw" if e.get("nsfw_level") else "main"

        lines.append("  {")
        lines.append(f'    "id": "{eid}",')
        lines.append(f'    "title": {json.dumps(title, ensure_ascii=False)},')
        lines.append(f'    "route": "{route}",')
        lines.append(f'    "chapter": {json.dumps(chapter, ensure_ascii=False)},')
        lines.append(f'    "summary": {json.dumps(summary, ensure_ascii=False)},')
        lines.append(f'    "type": "{etype}"')
        lines.append("  },")

    lines.append("];")
    lines.append("")

    # CHAPTERS — from chapter mapping (deduplicated)
    lines.append("const CHAPTERS = [")
    seen_chapters = set()
    for ch_num in sorted(set(e.get("chapter", 0) for e in events if e.get("chapter", 0) >= 0)):
        ch_name = CHAPTER_NAMES.get(ch_num, "")
        if not ch_name:
            continue
        count = sum(1 for e in events if e["chapter"] == ch_num)
        phase = "intro" if ch_num == 0 else "ntrs" if ch_num <= 7 else "finale"
        lines.append("  {")
        lines.append(f'    "num": {ch_num},')
        lines.append(f'    "name": {json.dumps(ch_name, ensure_ascii=False)},')
        lines.append(f'    "phase": "{phase}",')
        lines.append(f'    "count": {count}')
        lines.append("  },")
    lines.append("];")
    lines.append("")

    # DEBUTS — auto-generated from first-appearance logic (basic)
    lines.append("// 自动生成的登场顺序（按事件ID首次出现推断）")
    lines.append("const DEBUTS = [")
    seen_chars = set()
    debut_chars = [
        ("黎恩", "E01", "#4facfe", "黎"),
        ("Seraphina", "E01", "#f093fb", "S"),
        ("亚莉莎", "5", "#fa709a", "亚"),
        ("爱丽榭", "5", "#ff9a9e", "爱"),
        ("劳拉", "6", "#89f7fe", "劳"),
        ("乔治", "6", "#43e97b", "乔"),
        ("艾玛", "7", "#f5576c", "艾"),
        ("菲", "7", "#30cfd0", "菲"),
        ("玲", "36", "#c4a0ff", "玲"),
        ("Thalion", "38", "#a18cd1", "T"),
        ("矮人三兄弟", "41", "#fecf6f", "矮"),
        ("亚尔缇娜", "42", "#f093fb", "缇"),
        ("奥蕾莉亚", "46", "#fa709a", "奥"),
        ("古老先灵", "47", "#a18cd1", "灵"),
        ("艾德里安", "49", "#f5576c", "德"),
        ("雷恩", "52", "#89f7fe", "雷"),
        ("凯尔", "53", "#30cfd0", "凯"),
    ]
    for name, event_id, color, avatar in debut_chars:
        lines.append("  {")
        lines.append(f'    "name": "{name}",')
        lines.append(f'    "event": "{event_id}",')
        lines.append(f'    "color": "{color}",')
        lines.append(f'    "avatar": "{avatar}"')
        lines.append("  },")
    lines.append("];")

    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════
# HTML 生成 (V2 — 网格卡片布局)
# ══════════════════════════════════════════════════════════

CSS = """
  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg: #0f0f1a; --bg2: #1a1a2e; --text: #e0e0e0;
    --text2: #999; --text3: #666; --border: #2a2a4a;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: var(--bg); color: var(--text); min-height: 100vh;
  }

  /* ═══ 顶部栏 ═══ */
  .topbar {
    background: var(--bg2); border-bottom: 1px solid var(--border);
    padding: 10px 16px; position: sticky; top: 0; z-index: 100;
  }
  .topbar h1 { font-size: 20px; display: inline; margin-right: 14px; }
  .topbar .stats-inline { font-size: 12px; color: var(--text2); }
  .topbar .stats-inline em { color: #667eea; font-style: normal; }

  .topbar-row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-top: 6px; }

  .search-input {
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    padding: 5px 10px; border-radius: 5px; font-size: 13px; width: 200px; outline: none;
  }
  .search-input:focus { border-color: #667eea; }
  .search-input::placeholder { color: #444; }

  /* 折叠式筛选区 */
  .filter-section { border: 1px solid var(--border); border-radius: 6px; background: var(--bg); }
  .filter-section h3 {
    font-size: 11px; color: var(--text3); padding: 3px 8px; cursor: pointer;
    user-select: none; display: flex; align-items: center; gap: 3px;
  }
  .filter-section h3:hover { color: var(--text2); }
  .filter-section .filter-btns {
    padding: 3px 6px 5px; display: flex; gap: 3px; flex-wrap: wrap; border-top: 1px solid var(--border);
  }
  .filter-section.collapsed .filter-btns { display: none; }

  .filter-btn {
    background: transparent; border: 1px solid var(--border); color: var(--text2);
    padding: 2px 7px; border-radius: 3px; cursor: pointer; font-size: 11px;
    white-space: nowrap; transition: all 0.15s;
  }
  .filter-btn:hover { border-color: #667eea; color: #fff; }
  .filter-btn.active { background: #667eea22; border-color: #667eea; color: #fff; }
  .prefix-btn.active { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 15%, transparent); }
  .filter-btn span { font-size: 9px; opacity: 0.5; margin-left: 2px; }

  /* ═══ 网格容器 ═══ */
  .grid-container {
    padding: 8px 12px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(188px, 1fr));
    gap: 5px;
  }

  /* 事件卡片 */
  .event-card {
    background: var(--bg2); border: 1px solid var(--border);
    border-left: 3px solid #667eea; border-radius: 5px;
    padding: 6px 8px; cursor: pointer; transition: all 0.15s;
    display: flex; align-items: center; gap: 5px; min-height: 38px;
    text-decoration: none;
  }
  .event-card:hover { background: #222240; transform: translateY(-1px); }
  .event-card.active { background: rgba(102, 126, 234, 0.12); border-color: #667eea; }
  .event-card.hidden { display: none; }
  .event-card .card-id { font-size: 12px; font-weight: bold; color: #fff; white-space: nowrap; min-width: 24px; }
  .event-card .card-name {
    font-size: 12px; color: #bbb; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1;
  }
  .event-card .card-badges { display: flex; gap: 1px; flex-shrink: 0; }
  .card-badge { font-size: 8px; padding: 0px 3px; border-radius: 2px; white-space: nowrap; }
  .badge-nsfw { background: #fa709a33; color: #fa709a; }
  .badge-sfw { background: #43e97b33; color: #43e97b; }

  /* 分组标题 */
  .group-header {
    grid-column: 1 / -1;
    display: flex; align-items: center; gap: 6px; padding: 5px 6px;
    margin-top: 3px; cursor: pointer; user-select: none;
    font-size: 13px; font-weight: bold; border-radius: 4px;
  }
  .group-header:hover { background: rgba(255,255,255,0.02); }
  .group-header .arrow { font-size: 9px; transition: transform 0.2s; opacity: 0.4; }
  .group-header.collapsed .arrow { transform: rotate(-90deg); }

  /* ═══ 详情面板 ═══ */
  .detail-panel {
    position: fixed; top: 0; right: 0; width: 540px; max-width: 94vw; height: 100vh;
    background: var(--bg2); border-left: 1px solid var(--border); z-index: 200;
    overflow-y: auto; padding: 20px 24px;
    transform: translateX(100%); transition: transform 0.25s;
    box-shadow: -4px 0 30px rgba(0,0,0,0.4);
  }
  .detail-panel.open { transform: translateX(0); }
  .detail-panel::-webkit-scrollbar { width: 5px; }
  .detail-panel::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }

  .detail-close {
    position: sticky; top: 8px; float: right;
    background: none; border: none; color: #888; font-size: 26px;
    cursor: pointer; padding: 2px 8px; border-radius: 4px; z-index: 10;
  }
  .detail-close:hover { color: #fff; background: #333; }

  .detail-header { margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
  .detail-header h2 { font-size: 20px; margin-bottom: 3px; }
  .detail-header .meta-row {
    font-size: 13px; color: var(--text3); display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
  }

  .detail-tags { display: flex; gap: 3px; flex-wrap: wrap; margin: 6px 0; }
  .detail-tags .tag {
    font-size: 11px; padding: 1px 7px; border-radius: 3px; background: #222; color: #aaa;
  }
  .detail-tags .tag.nsfw { background: #fa709a22; color: #fa709a; }
  .detail-tags .tag.sfw { background: #43e97b22; color: #43e97b; }

  .detail-yaml {
    background: #0a0a16; border: 1px solid var(--border); border-radius: 6px;
    padding: 14px; font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px; line-height: 1.55; white-space: pre-wrap; word-break: break-all;
    overflow-x: auto; max-height: 65vh; overflow-y: auto;
  }
  .detail-yaml .hl-key { color: #f093fb; }
  .detail-yaml .hl-str { color: #43e97b; }
  .detail-yaml .hl-num { color: #fecf6f; }
  .detail-yaml .hl-com { color: #555; }

  .copy-btn {
    background: #222; border: 1px solid #444; color: #aaa;
    padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; margin-top: 6px;
  }
  .copy-btn:hover { background: #333; color: #fff; }

  .overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 199; display: none;
  }
  .overlay.show { display: block; }

  .kbd-hint { position: fixed; bottom: 6px; left: 10px; font-size: 10px; color: #333; }

  .empty-state {
    grid-column: 1 / -1; padding: 60px 20px; text-align: center; color: #555; font-size: 16px;
  }

  @media (max-width: 768px) {
    .grid-container { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 3px; }
    .event-card { padding: 4px 6px; min-height: 32px; }
    .event-card .card-id { font-size: 10px; }
    .event-card .card-name { font-size: 10px; }
    .detail-panel { width: 100vw; }
    .topbar h1 { font-size: 16px; }
  }
"""


def generate_html(events):
    events_json = json.dumps(events, ensure_ascii=False, indent=2)
    total = len(events)
    has_yaml_count = sum(1 for e in events if e["has_yaml"])
    summary_count = sum(1 for e in events if e["is_summary"])
    nsfw_count = sum(1 for e in events if "NSFW" in e["tags"])
    sfw_count = total - nsfw_count

    # 前缀按钮
    all_prefixes = sorted(set(e["prefix"] for e in events),
                          key=lambda x: PREFIX_META.get(x, {}).get("order", 99))
    prefix_btns = []
    for p in all_prefixes:
        meta = PREFIX_META.get(p, {"name": p, "color": "#888"})
        count = sum(1 for e in events if e["prefix"] == p)
        prefix_btns.append(
            '<button class="filter-btn prefix-btn active" data-filter="prefix" data-value="{}" '
            'style="--accent:{}">{}<span>{}({})</span></button>'.format(
                p, meta["color"], p, meta["name"], count)
        )

    # 类型按钮
    all_tags = set()
    for e in events:
        for t in e["tags"]:
            all_tags.add(t)
    tag_order = ["SFW", "NSFW", "肛交", "本番", "口交", "乳交", "腿交", "足交", "手交", "指交", "蹭穴", "接吻", "暴露", "触碰", "隐奸", "群交", "未分类"]
    tag_btns = ['<button class="filter-btn type-btn active" data-filter="tag" data-value="all">全部</button>']
    for t in tag_order:
        if t in all_tags or t == "未分类":
            count = sum(1 for e in events if t in e["tags"])
            tag_btns.append('<button class="filter-btn type-btn" data-filter="tag" data-value="{}">{}({})</button>'.format(t, t, count))

    # 章节按钮
    all_chapters = set(e["chapter"] for e in events)
    chapter_btns = ['<button class="filter-btn chapter-btn active" data-filter="chapter" data-value="all">全部</button>']
    for ch in sorted(all_chapters):
        if ch > 0:
            ch_name = CHAPTER_NAMES.get(ch, "")
            short = ch_name[:6] if ch_name else ""
            count = sum(1 for e in events if e["chapter"] == ch)
            chapter_btns.append(
                '<button class="filter-btn chapter-btn" data-filter="chapter" data-value="{}" '
                'title="第{}章 {}">Ch.{}<span>{}({})</span></button>'.format(ch, ch, ch_name, ch, short, count)
            )

    # 角色按钮（按CHARACTER_NAMES顺序，只显示有出场的）
    all_characters = set()
    for e in events:
        for c in e.get("characters", []):
            all_characters.add(c)
    # 过滤掉Seraphina和黎恩（每章都有，无筛选意义），按标准顺序排
    char_order = [c for c in CHARACTER_NAMES if c in all_characters
                  and c not in ('Seraphina', '菲娜', '黎恩')]
    char_btns = ['<button class="filter-btn char-btn active" data-filter="character" data-value="all">全部</button>']
    for c in char_order:
        count = sum(1 for e in events if c in e.get("characters", []))
        char_btns.append(
            '<button class="filter-btn char-btn" data-filter="character" data-value="{}">{}({})</button>'.format(c, c, count)
        )

    html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
    html += '<meta charset="UTF-8">\n'
    html += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    html += '<title>Eldoria 全章节浏览器</title>\n'
    html += '<style>\n' + CSS + '\n</style>\n</head>\n<body>\n'

    # 顶部栏
    html += '<div class="topbar">\n'
    html += '<h1>Eldoria 全章节浏览器</h1>\n'
    html += '<span class="stats-inline">共 <em>{}</em> 章节 &middot; 已完善 <em>{}</em> &middot; NSFW <em>{}</em> &middot; SFW <em>{}</em></span>\n'.format(
        total, has_yaml_count, nsfw_count, sfw_count)
    html += '<div class="topbar-row">\n'
    html += '<input type="text" class="search-input" id="searchInput" placeholder="🔍 搜索章节 (Ctrl+K) - ID / 名称 / 关键词">\n'

    html += '<div class="filter-section" id="filterPrefix">\n'
    html += '<h3 onclick="toggleFilter(this)">📂 前缀</h3>\n'
    html += '<div class="filter-btns" id="prefixFilters">\n'
    html += '<button class="filter-btn prefix-btn active" data-filter="prefix" data-value="all" style="--accent:#667eea">全部</button>\n'
    html += '\n'.join(prefix_btns) + '\n</div>\n</div>\n'

    html += '<div class="filter-section" id="filterTag">\n'
    html += '<h3 onclick="toggleFilter(this)">🏷️ 类型</h3>\n'
    html += '<div class="filter-btns" id="tagFilters">\n'
    html += '\n'.join(tag_btns) + '\n</div>\n</div>\n'

    html += '<div class="filter-section" id="filterChapter">\n'
    html += '<h3 onclick="toggleFilter(this)">📖 章节</h3>\n'
    html += '<div class="filter-btns" id="chapterFilters">\n'
    html += '\n'.join(chapter_btns) + '\n</div>\n</div>\n'

    html += '<div class="filter-section" id="filterCharacter">\n'
    html += '<h3 onclick="toggleFilter(this)">👤 角色</h3>\n'
    html += '<div class="filter-btns" id="characterFilters">\n'
    html += '\n'.join(char_btns) + '\n</div>\n</div>\n'

    html += '</div></div>\n'  # close topbar-row, topbar

    # 网格容器
    html += '<div class="grid-container" id="eventGrid"></div>\n'

    # 详情面板
    html += '<div class="overlay" id="overlay" onclick="closeDetail()"></div>\n'
    html += '<div class="detail-panel" id="detailPanel">\n'
    html += '<button class="detail-close" onclick="closeDetail()">&times;</button>\n'
    html += '<div id="detailContent"></div>\n</div>\n'

    html += '<div class="kbd-hint">Ctrl+K 搜索 · Esc 关闭详情</div>\n'

    # JavaScript
    html += '<script>\n'
    html += 'const EVENTS = {};\n'.format(events_json)
    html += '''
let activeFilters = { prefix: 'all', tag: 'all', chapter: 'all', character: 'all', search: '' };
let selectedEventId = null;

const $grid = document.getElementById('eventGrid');
const $detail = document.getElementById('detailPanel');
const $detailContent = document.getElementById('detailContent');
const $overlay = document.getElementById('overlay');
const $search = document.getElementById('searchInput');

function getFiltered() {
  return EVENTS.filter(function(e) {
    if (activeFilters.prefix !== 'all' && e.prefix !== activeFilters.prefix) return false;
    if (activeFilters.tag !== 'all' && e.tags.indexOf(activeFilters.tag) === -1) return false;
    if (activeFilters.chapter !== 'all' && e.chapter !== parseInt(activeFilters.chapter)) return false;
    if (activeFilters.character !== 'all' && (e.characters || []).indexOf(activeFilters.character) === -1) return false;
    if (activeFilters.search) {
      var q = activeFilters.search.toLowerCase();
      var hay = (e.id + ' ' + e.name + ' ' + e.tags.join(' ') + ' ' +
                 e.trigger + ' ' + e.scene_preview + ' ' + e.raw_yaml).toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    return true;
  });
}

'''

    # Generate prefix metadata from story_config
    prefix_order = list(ALL_PREFIXES)
    prefix_names = {p: PREFIX_META[p]['name'] for p in ALL_PREFIXES}
    prefix_colors = {p: PREFIX_META[p]['color'] for p in ALL_PREFIXES}

    html += 'var PREFIX_ORDER = ' + json.dumps(prefix_order) + ';\n'
    html += 'var PREFIX_NAMES = ' + json.dumps(prefix_names) + ';\n'
    html += 'var PREFIX_COLORS = ' + json.dumps(prefix_colors) + ';\n'

    html += '''

function renderGrid() {
  var filtered = getFiltered();

  if (!filtered.length) {
    $grid.innerHTML = '<div class="empty-state">无匹配章节</div>';
    return;
  }

  var groups = {};
  for (var i = 0; i < filtered.length; i++) {
    var e = filtered[i];
    if (!groups[e.prefix]) groups[e.prefix] = [];
    groups[e.prefix].push(e);
  }

  var html = '';
  for (var pi = 0; pi < PREFIX_ORDER.length; pi++) {
    var p = PREFIX_ORDER[pi];
    var items = groups[p];
    if (!items || !items.length) continue;
    var color = PREFIX_COLORS[p] || '#888';
    var pname = PREFIX_NAMES[p] || p;
    var collapseKey = 'group_' + p;
    var collapsed = localStorage.getItem(collapseKey) === '1';

    html += '<div class="group-header' + (collapsed ? ' collapsed' : '') + '" style="color:' + color + '" data-group="' + p + '" onclick="toggleGroup(\\'' + p + '\\')">'
      + '<span class="arrow">&#9662;</span>'
      + p + ' &middot; ' + pname
      + '<span style="font-size:11px;opacity:0.5;font-weight:normal">(' + items.length + ')</span>'
      + '</div>';

    for (var j = 0; j < items.length; j++) {
      var e = items[j];
      var active = e.id === selectedEventId ? ' active' : '';
      var hidden = collapsed ? ' hidden' : '';
      var nsfwClass = e.tags.indexOf('NSFW') !== -1 ? 'badge-nsfw' : 'badge-sfw';
      var nsfwLabel = e.tags.indexOf('NSFW') !== -1 ? (e.nsfw_level || 'NSFW') : 'SFW';

      html += '<div class="event-card' + active + hidden + '" data-eid="' + e.id + '" data-group="' + p + '"'
        + ' style="border-left-color:' + e.prefix_color + '"'
        + ' onclick="selectEvent(\\'' + e.id + '\\')"'
        + ' title="' + e.id + ': ' + e.name + ' | ' + e.prefix_name + ' | Ch.' + e.chapter + '">'
        + '<span class="card-id">' + e.id + '</span>'
        + '<span class="card-name">' + e.name + '</span>'
        + '<span class="card-badges"><span class="card-badge ' + nsfwClass + '">' + nsfwLabel + '</span></span>'
        + '</div>';
    }
  }
  $grid.innerHTML = html;
}

function toggleGroup(prefix) {
  var cards = document.querySelectorAll('.event-card[data-group="' + prefix + '"]');
  var header = document.querySelector('.group-header[data-group="' + prefix + '"]');
  if (!cards.length) return;
  var isCollapsed = cards[0].classList.contains('hidden');
  var i;
  if (isCollapsed) {
    for (i = 0; i < cards.length; i++) cards[i].classList.remove('hidden');
    if (header) header.classList.remove('collapsed');
    localStorage.setItem('group_' + prefix, '0');
  } else {
    for (i = 0; i < cards.length; i++) cards[i].classList.add('hidden');
    if (header) header.classList.add('collapsed');
    localStorage.setItem('group_' + prefix, '1');
  }
}

function selectEvent(eventId) {
  selectedEventId = eventId;
  var event = null;
  for (var i = 0; i < EVENTS.length; i++) { if (EVENTS[i].id === eventId) { event = EVENTS[i]; break; } }
  if (!event) return;

  // Update active
  var cards = document.querySelectorAll('.event-card.active');
  for (var i = 0; i < cards.length; i++) cards[i].classList.remove('active');
  var card = document.querySelector('.event-card[data-eid="' + eventId + '"]');
  if (card) card.classList.add('active');

  // Highlight YAML
  var yamlHighlighted = '';
  if (event.raw_yaml) {
    var lines = event.raw_yaml.split('\\n');
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var m = line.match(/^([ \\t]*)([^:]+)(:)(.*)/);
      if (m) {
        yamlHighlighted += m[1] + '<span class="hl-key">' + m[2] + '</span>' + m[3] + '<span class="hl-str">' + m[4] + '</span>\\n';
      } else if (/^\\s*#/.test(line)) {
        yamlHighlighted += '<span class="hl-com">' + line + '</span>\\n';
      } else {
        yamlHighlighted += line + '\\n';
      }
    }
  }

  // Build tags
  var tagsHtml = '';
  for (var i = 0; i < event.tags.length; i++) {
    var t = event.tags[i];
    var cls = t === 'NSFW' ? 'nsfw' : (t === 'SFW' ? 'sfw' : '');
    tagsHtml += '<span class="tag' + (cls ? ' ' + cls : '') + '">' + t + '</span>';
  }

  $detailContent.innerHTML =
    '<div class="detail-header">'
    + '<h2 style="display:flex;align-items:center;gap:6px;"><span style="color:' + event.prefix_color + '">' + event.id + '</span> ' + event.name + '</h2>'
    + '<div class="meta-row">'
    + '<span>📂 ' + event.prefix_name + '</span>'
    + (event.chapter > 0 ? '<span>📖 第' + event.chapter + '章 ' + (event.chapter_name || '') + '</span>' : '')
    + (event.characters && event.characters.length ? '<span>👤 ' + event.characters.join(', ') + '</span>' : '')
    + '<span>' + (event.has_yaml ? '✅ YAML' : '⚠️ 摘要') + '</span>'
    + (event.trigger ? '<span>🔔 ' + event.trigger.substring(0, 50) + '</span>' : '')
    + '</div>'
    + '<div class="detail-tags">' + tagsHtml + '</div>'
    + '</div>'
    + (event.scene_preview ? '<div style="margin-bottom:12px;color:#aaa;font-size:14px;line-height:1.6;">' + event.scene_preview + '</div>' : '')
    + (event.raw_yaml
      ? '<div class="detail-yaml">' + yamlHighlighted + '</div>'
      + '<button class="copy-btn" onclick="copyYAML()">📋 复制YAML</button>'
      : '<div style="padding:20px;color:#666;">⚠️ 此章节无详细 YAML 定义</div>');

  $detail.classList.add('open');
  $overlay.classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeDetail() {
  $detail.classList.remove('open');
  $overlay.classList.remove('show');
  document.body.style.overflow = '';
  selectedEventId = null;
  var cards = document.querySelectorAll('.event-card.active');
  for (var i = 0; i < cards.length; i++) cards[i].classList.remove('active');
}

function copyYAML() {
  var event = null;
  for (var i = 0; i < EVENTS.length; i++) { if (EVENTS[i].id === selectedEventId) { event = EVENTS[i]; break; } }
  if (!event || !event.raw_yaml) return;
  navigator.clipboard.writeText(event.raw_yaml).then(function() {
    var btn = document.querySelector('.copy-btn');
    if (btn) { btn.textContent = '✅ 已复制!'; setTimeout(function() { btn.textContent = '📋 复制YAML'; }, 2000); }
  });
}

// Filter button clicks
document.addEventListener('click', function(e) {
  var btn = e.target.closest('.filter-btn');
  if (!btn) return;
  var filterType = btn.dataset.filter;
  var filterValue = btn.dataset.value;
  var siblings = btn.parentElement.querySelectorAll('.filter-btn');
  for (var i = 0; i < siblings.length; i++) siblings[i].classList.remove('active');
  btn.classList.add('active');
  activeFilters[filterType] = filterValue;
  renderGrid();
});

// Search
var searchTimer;
$search.addEventListener('input', function() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(function() {
    activeFilters.search = $search.value.trim();
    renderGrid();
  }, 150);
});

// Keyboard
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeDetail(); $search.blur(); }
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); $search.focus(); }
});

// Collapse filter sections
function toggleFilter(h3) {
  var section = h3.parentElement;
  section.classList.toggle('collapsed');
  localStorage.setItem('filter_' + section.id, section.classList.contains('collapsed') ? '1' : '0');
}

// Restore filter collapse state
(function() {
  var sections = document.querySelectorAll('.filter-section');
  for (var i = 0; i < sections.length; i++) {
    if (localStorage.getItem('filter_' + sections[i].id) === '1') {
      sections[i].classList.add('collapsed');
    }
  }
})();

// Initial render
renderGrid();
</script>
</body>
</html>'''

    return html


# ─── 入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    print(f"扫描: {os.path.join(BASE_DIR, 'docs', 'story')}")
    events, event_chapters, event_names = build_events()

    prefixes = {}
    for e in events:
        prefixes[e["prefix"]] = prefixes.get(e["prefix"], 0) + 1
    print(f"  解析完成: {len(events)} 个章节")
    print(f"  前缀分布: {prefixes}")
    print(f"  含YAML: {sum(1 for e in events if e['has_yaml'])}")
    print(f"  摘要: {sum(1 for e in events if e['is_summary'])}")

    print(f"生成HTML: {OUTPUT_HTML}")
    html = generate_html(events)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  完成! 文件大小: {len(html):,} 字符")

    # ─── 同步生成 event_data.js（剧情时间线数据） ──────────
    data_js = generate_event_data_js(events, event_chapters)
    data_js_path = os.path.join(BASE_DIR, "visual", "chapter_data.js")
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write(data_js)
    print(f"生成数据: {data_js_path}")
    print(f"  完成! 文件大小: {len(data_js):,} 字符")
