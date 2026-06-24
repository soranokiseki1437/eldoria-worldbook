#!/usr/bin/env python3
"""
重写 generate_event_browser.py 的 generate_html 函数，
将侧边栏纵向列表改为网格布局，紧凑按钮式卡片。
"""
import re

SCRIPT = r"C:\Users\lx\Desktop\世界书\scripts\generate_event_browser.py"

with open(SCRIPT, "r", encoding="utf-8") as f:
    content = f.read()

# Find the generate_html function boundaries
func_start = content.find("def generate_html(events):")
if func_start == -1:
    print("ERROR: generate_html not found")
    exit(1)

# Find the return html line
return_line = content.rfind("    return html")
if return_line == -1:
    print("ERROR: return html not found")
    exit(1)

# Build the new function
new_func = r'''def generate_html(events):
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
<title>Eldoria 全事件浏览器 — V4.7.0</title>
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
  }}

  /* ═══ 顶部栏 ═══ */
  .topbar {{
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .topbar h1 {{
    font-size: 20px;
    margin-bottom: 6px;
    display: inline-block;
    margin-right: 16px;
  }}
  .topbar .stats-inline {{
    display: inline;
    font-size: 13px;
    color: var(--text2);
  }}
  .topbar .stats-inline em {{ color: #667eea; font-style: normal; }}

  .topbar-row {{
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    margin-top: 6px;
  }}

  .search-input {{
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    width: 220px;
    outline: none;
  }}
  .search-input:focus {{ border-color: #667eea; }}
  .search-input::placeholder {{ color: #444; }}

  /* 折叠式筛选区 */
  .filter-section {{
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    margin-bottom: 4px;
  }}
  .filter-section h3 {{
    font-size: 12px;
    color: var(--text3);
    padding: 4px 10px;
    cursor: pointer;
    user-select: none;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .filter-section h3:hover {{ color: var(--text2); }}
  .filter-section .filter-btns {{
    padding: 4px 8px 6px;
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    border-top: 1px solid var(--border);
  }}
  .filter-section.collapsed .filter-btns {{ display: none; }}

  .filter-btn {{
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text2);
    padding: 3px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    white-space: nowrap;
    transition: all 0.15s;
  }}
  .filter-btn:hover {{ border-color: #667eea; color: #fff; }}
  .filter-btn.active {{ background: #667eea22; border-color: #667eea; color: #fff; }}
  .prefix-btn.active {{ border-color: var(--accent); background: color-mix(in srgb, var(--accent) 15%, transparent); }}
  .filter-btn span {{ font-size: 10px; opacity: 0.6; margin-left: 2px; }}

  /* ═══ 网格容器 ═══ */
  .grid-container {{
    padding: 10px 16px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 6px;
  }}

  /* 事件卡片 */
  .event-card {{
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 4px solid #667eea;
    border-radius: 6px;
    padding: 8px 10px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 7px;
    min-height: 44px;
  }}
  .event-card:hover {{
    background: #222240;
    transform: translateY(-1px);
  }}
  .event-card.active {{
    background: rgba(102, 126, 234, 0.12);
    border-color: #667eea;
  }}
  .event-card .card-id {{
    font-size: 13px;
    font-weight: bold;
    color: #fff;
    white-space: nowrap;
    min-width: 28px;
  }}
  .event-card .card-name {{
    font-size: 13px;
    color: #bbb;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
  }}
  .event-card .card-badges {{
    display: flex;
    gap: 2px;
    flex-shrink: 0;
  }}
  .event-card .card-badge {{
    font-size: 9px;
    padding: 0px 4px;
    border-radius: 3px;
    white-space: nowrap;
  }}
  .badge-nsfw {{ background: #fa709a33; color: #fa709a; }}
  .badge-sfw {{ background: #43e97b33; color: #43e97b; }}
  .badge-sum {{ background: #fecf6f22; color: #fecf6f; }}

  /* ═══ 详情面板 ═══ */
  .detail-panel {{
    position: fixed;
    top: 0;
    right: 0;
    width: 560px;
    max-width: 95vw;
    height: 100vh;
    background: var(--bg2);
    border-left: 1px solid var(--border);
    z-index: 200;
    overflow-y: auto;
    padding: 24px 28px;
    transform: translateX(100%);
    transition: transform 0.25s;
    box-shadow: -4px 0 30px rgba(0,0,0,0.4);
  }}
  .detail-panel.open {{
    transform: translateX(0);
  }}
  .detail-panel::-webkit-scrollbar {{ width: 5px; }}
  .detail-panel::-webkit-scrollbar-thumb {{ background: #333; border-radius: 3px; }}

  .detail-close {{
    position: absolute;
    top: 12px;
    right: 16px;
    background: none;
    border: none;
    color: #888;
    font-size: 24px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
  }}
  .detail-close:hover {{ color: #fff; background: #333; }}

  .detail-header {{
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
  }}
  .detail-header h2 {{ font-size: 22px; margin-bottom: 4px; }}
  .detail-header .meta-row {{
    font-size: 14px;
    color: var(--text3);
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .detail-header .meta-row span {{ display: flex; align-items: center; gap: 3px; }}

  .detail-tags {{
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin: 8px 0;
  }}
  .detail-tags .tag {{
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #222;
    color: #aaa;
  }}
  .detail-tags .tag.nsfw {{ background: #fa709a22; color: #fa709a; }}
  .detail-tags .tag.sfw {{ background: #43e97b22; color: #43e97b; }}

  .detail-yaml {{
    background: #0a0a16;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
    overflow-x: auto;
  }}
  .detail-yaml .hl-key {{ color: #f093fb; }}
  .detail-yaml .hl-str {{ color: #43e97b; }}
  .detail-yaml .hl-num {{ color: #fecf6f; }}
  .detail-yaml .hl-com {{ color: #555; }}

  .copy-btn {{
    background: #222;
    border: 1px solid #444;
    color: #aaa;
    padding: 5px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    margin-top: 8px;
  }}
  .copy-btn:hover {{ background: #333; color: #fff; }}

  /* 遮罩 */
  .overlay {{
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 199;
    display: none;
  }}
  .overlay.show {{ display: block; }}

  /* 前缀分组标题 */
  .group-header {{
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    margin-top: 4px;
    cursor: pointer;
    user-select: none;
    font-size: 14px;
    font-weight: bold;
    border-radius: 4px;
  }}
  .group-header:hover {{ background: rgba(255,255,255,0.02); }}
  .group-header .arrow {{ font-size: 10px; transition: transform 0.2s; opacity: 0.4; }}
  .group-header.collapsed .arrow {{ transform: rotate(-90deg); }}

  .kbd-hint {{
    position: fixed;
    bottom: 8px;
    left: 12px;
    font-size: 11px;
    color: #333;
  }}

  @media (max-width: 768px) {{
    .grid-container {{ grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 4px; }}
    .event-card {{ padding: 6px 8px; min-height: 36px; }}
    .detail-panel {{ width: 100vw; }}
  }}
</style>
</head>
<body>

<!-- ═══ 顶部栏 ═══ -->
<div class="topbar">
  <h1>Eldoria 全事件浏览器</h1>
  <span class="stats-inline">
    共 <em>{total}</em> 事件 · 已完善 <em>{has_yaml_count}</em> · NSFW <em>{nsfw_count}</em> · SFW <em>{sfw_count}</em> · <em>V4.7.0</em>
  </span>
  <div class="topbar-row">
    <input type="text" class="search-input" id="searchInput"
           placeholder="🔍 搜索事件 (Ctrl+K) — ID / 名称 / 关键词">
    <div class="filter-section" id="filterPrefix">
      <h3 onclick="toggleFilter(this)">📂 前缀</h3>
      <div class="filter-btns" id="prefixFilters">
        <button class="filter-btn prefix-btn active" data-filter="prefix" data-value="all" style="--accent:#667eea">全部</button>
        {"".join(prefix_btns)}
      </div>
    </div>
    <div class="filter-section" id="filterTag">
      <h3 onclick="toggleFilter(this)">🏷️ 类型</h3>
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
  </div>
</div>

<!-- ═══ 网格容器 ═══ -->
<div class="grid-container" id="eventGrid">
  <!-- JS动态填充 -->
</div>

<!-- ═══ 详情面板 ═══ -->
<div class="overlay" id="overlay" onclick="closeDetail()"></div>
<div class="detail-panel" id="detailPanel">
  <button class="detail-close" onclick="closeDetail()">&times;</button>
  <div id="detailContent"></div>
</div>

<div class="kbd-hint">Ctrl+K 搜索 · Esc 关闭详情</div>

<script>
const EVENTS = {events_json};

let activeFilters = {{ prefix: 'all', tag: 'all', chapter: 'all', search: '' }};
let selectedEventId = null;

const $grid = document.getElementById('eventGrid');
const $detail = document.getElementById('detailPanel');
const $detailContent = document.getElementById('detailContent');
const $overlay = document.getElementById('overlay');
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

// ═══ 渲染网格 ═══
const PREFIX_ORDER = ['E','P','N','PN','S','C','G','W','H','R'];
const PREFIX_NAMES = {{E:'固定事件',P:'纯爱路线',N:'NTRS路线',PN:'被动NTR',S:'NSFW通用',C:'角色NSFW',G:'通用SFW',W:'世界事件',H:'隐藏事件',R:'黎恩专属'}};
const PREFIX_COLORS = {{E:'#4facfe',P:'#f093fb',N:'#fa709a',PN:'#30cfd0',S:'#ff9a9e',C:'#a18cd1',G:'#43e97b',W:'#f5576c',H:'#a8edea',R:'#89f7fe'}};

function renderGrid() {{
  const filtered = getFiltered();

  if (!filtered.length) {{
    $grid.innerHTML = '<div style="grid-column:1/-1;padding:40px;color:#555;text-align:center;font-size:16px;">无匹配事件</div>';
    return;
  }}

  // 按前缀分组
  const groups = {{}};
  for (const e of filtered) {{
    if (!groups[e.prefix]) groups[e.prefix] = [];
    groups[e.prefix].push(e);
  }}

  let html = '';
  for (const p of PREFIX_ORDER) {{
    const items = groups[p];
    if (!items || !items.length) continue;
    const color = PREFIX_COLORS[p] || '#888';
    const pname = PREFIX_NAMES[p] || p;
    const collapseKey = 'group_' + p;
    const collapsed = localStorage.getItem(collapseKey) === '1';

    html += '<div class="group-header' + (collapsed ? ' collapsed' : '') + '" style="color:' + color + '" onclick="toggleGroup(\\'' + p + '\\')">'
      + '<span class="arrow">&#9662;</span>'
      + p + ' · ' + pname
      + '<span style="font-size:11px;opacity:0.5;font-weight:normal">(' + items.length + ')</span>'
      + '</div>';

    for (const e of items) {{
      const active = e.id === selectedEventId ? ' active' : '';
      const nsfwClass = e.tags.includes('NSFW') ? 'badge-nsfw' : 'badge-sfw';
      const nsfwLabel = e.tags.includes('NSFW') ? (e.nsfw_level || 'NSFW') : 'SFW';
      const sumBadge = e.is_summary ? '<span class="card-badge badge-sum">摘要</span>' : '';

      html += '<div class="event-card' + active + (collapsed ? ' hidden' : '') + '" data-eid="' + e.id + '" data-group="' + p + '"'
        + ' style="border-left-color:' + e.prefix_color + '"'
        + ' onclick="selectEvent(\\'' + e.id + '\\')"'
        + ' title="' + e.id + ': ' + e.name + ' | ' + e.prefix_name + ' | Ch.' + e.chapter + ' ' + (e.chapter_name || '') + '">'
        + '<span class="card-id">' + e.id + '</span>'
        + '<span class="card-name">' + e.name + '</span>'
        + '<span class="card-badges">'
        + '<span class="card-badge ' + nsfwClass + '">' + nsfwLabel + '</span>'
        + sumBadge
        + '</span>'
        + '</div>';
    }}
  }}

  $grid.innerHTML = html;
}}

// ═══ 折叠/展开分组 ═══
function toggleGroup(prefix) {{
  const header = document.querySelector('.group-header[style*="' + PREFIX_COLORS[prefix] + '"]');
  // Can't match style easily, find by onclick
  const allHeaders = document.querySelectorAll('.group-header');
  let targetHeader = null;
  for (const h of allHeaders) {{
    if (h.onclick && h.onclick.toString().includes("'" + prefix + "'")) {{
      targetHeader = h; break;
    }}
  }}
  // Fallback: toggle by data
  const cards = document.querySelectorAll('.event-card[data-group="' + prefix + '"]');
  const isCollapsed = cards.length > 0 && cards[0].classList.contains('hidden');

  if (isCollapsed) {{
    cards.forEach(c => c.classList.remove('hidden'));
    if (targetHeader) targetHeader.classList.remove('collapsed');
    localStorage.setItem('group_' + prefix, '0');
  }} else {{
    cards.forEach(c => c.classList.add('hidden'));
    if (targetHeader) targetHeader.classList.add('collapsed');
    localStorage.setItem('group_' + prefix, '1');
  }}
}}

// ═══ 选择事件 ═══
function selectEvent(eventId) {{
  selectedEventId = eventId;
  const event = EVENTS.find(e => e.id === eventId);
  if (!event) return;

  // Update active state in grid
  document.querySelectorAll('.event-card.active').forEach(c => c.classList.remove('active'));
  const card = document.querySelector('.event-card[data-eid="' + eventId + '"]');
  if (card) card.classList.add('active');

  // Highlight YAML
  const yamlHighlighted = event.raw_yaml
    ? event.raw_yaml.split('\\n').map(line => {{
        const m = line.match(/^([ \\t]*)([^:]+)(:)(.*)/);
        if (m) return m[1] + '<span class="hl-key">' + m[2] + '</span>' + m[3] + '<span class="hl-str">' + m[4] + '</span>';
        if (/^\\s*#/.test(line)) return '<span class="hl-com">' + line + '</span>';
        return line;
      }}).join('\\n')
    : '';

  // Build detail HTML
  const tagsHtml = event.tags.map(t => {{
    const cls = t === 'NSFW' ? 'nsfw' : (t === 'SFW' ? 'sfw' : '');
    return '<span class="tag' + (cls ? ' ' + cls : '') + '">' + t + '</span>';
  }}).join('');

  $detailContent.innerHTML =
    '<div class="detail-header">'
    + '<h2 style="display:flex;align-items:center;gap:8px;"><span style="color:' + event.prefix_color + '">' + event.id + '</span> ' + event.name + '</h2>'
    + '<div class="meta-row">'
    + '<span>📂 ' + event.prefix_name + '</span>'
    + (event.chapter > 0 ? '<span>📖 第' + event.chapter + '章 ' + (event.chapter_name || '') + '</span>' : '')
    + '<span>' + (event.has_yaml ? '✅ YAML' : '⚠️ 摘要') + '</span>'
    + (event.trigger ? '<span>🔔 ' + event.trigger.substr(0, 50) + '</span>' : '')
    + '</div>'
    + '<div class="detail-tags">' + tagsHtml + '</div>'
    + '</div>'
    + (event.scene_preview ? '<div style="margin-bottom:14px;color:#aaa;font-size:15px;line-height:1.6;">' + event.scene_preview + '</div>' : '')
    + (event.raw_yaml
      ? '<div class="detail-yaml">' + yamlHighlighted + '</div>'
      + '<button class="copy-btn" onclick="copyYAML()">📋 复制YAML</button>'
      : '<div style="padding:20px;color:#666;">⚠️ 此事件只有章节映射中的摘要信息，尚无详细 YAML 定义</div>');

  // Open panel
  $detail.classList.add('open');
  $overlay.classList.add('show');
  document.body.style.overflow = 'hidden';
}}

// ═══ 关闭详情 ═══
function closeDetail() {{
  $detail.classList.remove('open');
  $overlay.classList.remove('show');
  document.body.style.overflow = '';
  selectedEventId = null;
  document.querySelectorAll('.event-card.active').forEach(c => c.classList.remove('active'));
}}

// ═══ 复制YAML ═══
function copyYAML() {{
  const event = EVENTS.find(e => e.id === selectedEventId);
  if (!event || !event.raw_yaml) return;
  navigator.clipboard.writeText(event.raw_yaml).then(() => {{
    const btn = document.querySelector('.copy-btn');
    if (btn) {{ btn.textContent = '✅ 已复制!'; setTimeout(() => {{ btn.textContent = '📋 复制YAML'; }}, 2000); }}
  }});
}}

// ═══ 筛选按钮事件 ═══
document.addEventListener('click', function(e) {{
  const btn = e.target.closest('.filter-btn');
  if (!btn) return;
  const filterType = btn.dataset.filter;
  const filterValue = btn.dataset.value;

  // Toggle active
  const siblings = btn.parentElement.querySelectorAll('.filter-btn');
  siblings.forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  activeFilters[filterType] = filterValue;
  renderGrid();
}});

// ═══ 搜索 ═══
let searchTimer;
$search.addEventListener('input', function() {{
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {{
    activeFilters.search = $search.value.trim();
    renderGrid();
  }}, 150);
}});

// ═══ 键盘快捷键 ═══
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    closeDetail();
    $search.blur();
  }}
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
    e.preventDefault();
    $search.focus();
  }}
}});

// ═══ 初始渲染 ═══
renderGrid();
</script>
</body>
</html>'''

    return html'''  # noqa (close the return string properly)

# Now replace the old function
old_func = content[func_start:return_line + len("    return html")]
content = content.replace(old_func, new_func)

# Update version reference in title
content = content.replace('V4.6.2', 'V4.7.0')

with open(SCRIPT, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ generate_event_browser.py 已重写为网格布局")
print(f"   总字符: {len(content)}")
