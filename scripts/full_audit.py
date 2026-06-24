#!/usr/bin/env python3
"""全面审计 05_事件系统.md 和 build_eldoria.py 的一致性"""
import re, json, os

BASE = r"C:\Users\lx\Desktop\世界书"

# ============================================================
# 1. JSON 检查
# ============================================================
with open(os.path.join(BASE, "output", "Eldoria_V4.7.0.json"), "r", encoding="utf-8") as f:
    data = json.load(f)
entries = data["entries"]

print("=" * 60)
print("1. JSON 条目检查")
print("=" * 60)
print(f"总条目: {len(entries)}")
print(f"UID范围: {min(int(u) for u in entries)} - {max(int(u) for u in entries)}")

# UID连续性
all_uids = sorted(int(u) for u in entries)
missing = sorted(set(range(0, 183)) - set(all_uids))
print(f"UID连续性: {'✅ 0-182无缺失' if not missing else f'❌ 缺失{missing}'}")

# 内容过短
short = [(u, len(str(e.get('content',''))), str(e.get('comment',''))[:80])
         for u, e in entries.items() if len(str(e.get('content',''))) < 50]
print(f"内容过短(<50字符): {len(short)}条")
for u, clen, c in short:
    print(f"  uid={u}: {clen}字符 — {c}")

# ============================================================
# 2. 05_事件系统.md 检查
# ============================================================
with open(os.path.join(BASE, "docs", "05_事件系统.md"), "r", encoding="utf-8") as f:
    md = f.read()

print(f"\n{'=' * 60}")
print("2. 05_事件系统.md 事件标题检查")
print("=" * 60)
print(f"文件: {len(md)}字符, {len(md.splitlines())}行")

headers = re.findall(r'^### 事件(\w+)：(.+)$', md, re.MULTILINE)
print(f"事件标题总数: {len(headers)}")

# 前缀统计
prefixes = {}
for eid, name in headers:
    if eid.startswith('PN'): p = 'PN'
    elif eid[0].isdigit(): p = 'E'
    else: p = eid[0]
    prefixes.setdefault(p, []).append(eid)

expected = {'E':15,'P':16,'N':15,'PN':13,'S':30,'C':6,'G':7,'W':8,'H':5,'R':8}
print("\n前缀分布:")
all_match = True
for p in sorted(prefixes.keys()):
    actual = len(prefixes[p])
    exp = expected.get(p, '?')
    ok = actual == exp
    if not ok: all_match = False
    print(f"  {p}: {actual}/{exp} {'✅' if ok else '❌ 缺失!'}")

# ============================================================
# 3. 每个事件的YAML内容长度
# ============================================================
print(f"\n{'=' * 60}")
print("3. 各事件YAML内容长度")
print("=" * 60)

short_yaml = []
for eid, name in headers:
    # Find the YAML block after this header
    idx = md.find(f"### 事件{eid}：{name}")
    if idx == -1:
        short_yaml.append((eid, name, -1, "NOT FOUND"))
        continue
    # Find ```yaml after header
    yaml_start = md.find("```yaml", idx)
    if yaml_start == -1:
        short_yaml.append((eid, name, 0, "NO YAML BLOCK"))
        continue
    yaml_content_start = md.find("\n", yaml_start) + 1
    yaml_end = md.find("```", yaml_content_start)
    if yaml_end == -1:
        short_yaml.append((eid, name, 0, "UNCLOSED YAML"))
        continue
    yaml_text = md[yaml_content_start:yaml_end].strip()
    ylen = len(yaml_text)
    if ylen < 100:
        short_yaml.append((eid, name, ylen, "TOO SHORT"))

if short_yaml:
    print(f"❌ YAML不足(<100字符): {len(short_yaml)}个")
    for eid, name, ylen, reason in short_yaml:
        print(f"  {eid} ({name}): {ylen}字符 — {reason}")
    all_match = False
else:
    print(f"✅ 全部{len(headers)}个事件YAML ≥ 100字符")

# ============================================================
# 4. 检查build_eldoria.py中是否有对应条目
# ============================================================
with open(os.path.join(BASE, "scripts", "build_eldoria.py"), "r", encoding="utf-8") as f:
    build = f.read()

print(f"\n{'=' * 60}")
print("4. build_eldoria.py 条目覆盖")
print("=" * 60)

# 提取所有 make_entry uid=xxx 调用
build_uids = set()
for m in re.finditer(r'uid\s*=\s*(\d+)', build):
    build_uids.add(int(m.group(1)))

print(f"build中定义的UID数: {len(build_uids)}")
json_uids = set(int(u) for u in entries.keys())
missing_in_build = json_uids - build_uids
missing_in_json = build_uids - json_uids - {999}  # 999 might be test
if missing_in_build:
    print(f"❌ JSON中有但build中无: {sorted(missing_in_build)}")
    all_match = False
else:
    print(f"✅ JSON中所有UID在build中都有定义")

if missing_in_json:
    print(f"⚠️ build中有但JSON中无: {sorted(missing_in_json)}")

# ============================================================
# 5. 事件浏览器检查
# ============================================================
print(f"\n{'=' * 60}")
print("5. 事件浏览器检查")
print("=" * 60)

with open(os.path.join(BASE, "visual", "全事件浏览器.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Extract EVENTS array
events_match = re.search(r'const EVENTS = (\[.*?\]);', html, re.DOTALL)
if events_match:
    browser_events = json.loads(events_match.group(1))
    print(f"浏览器事件数: {len(browser_events)}")
    yaml_yes = sum(1 for e in browser_events if e.get('has_yaml'))
    summary_yes = sum(1 for e in browser_events if e.get('is_summary'))
    print(f"含YAML: {yaml_yes}, 摘要: {summary_yes}")
    if summary_yes > 0:
        print(f"❌ 仍有{summary_yes}个摘要事件!")
        all_match = False
    else:
        print(f"✅ 0个摘要事件")

# Check for JS errors
has_balanced_braces = html.count('{') == html.count('}')
print(f"JS花括号平衡: {'✅' if has_balanced_braces else '❌'} ({html.count('{')} vs {html.count('}')})")

# ============================================================
# 总结
# ============================================================
print(f"\n{'=' * 60}")
if all_match:
    print("🎉 全面审计通过！无问题发现。")
else:
    print("⚠️ 发现问题，详见上述报告。")
print("=" * 60)
