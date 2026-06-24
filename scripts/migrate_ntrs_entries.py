"""
将build_eldoria.py中所有硬编码NTRS条目替换为add_ntrs_entry()调用。
内容自动从05_事件系统.md读取。可复用。

用法：python migrate_ntrs_entries.py [--dry-run]
"""
import re, sys, os, shutil, time

PROJECT = r'C:\Users\lx\Desktop\世界书'
BUILD_PY = os.path.join(PROJECT, 'scripts', 'build_eldoria.py')
MD_PATH = os.path.join(PROJECT, 'docs', '05_事件系统.md')
BACKUP_DIR = os.path.join(PROJECT, 'backups')
DRY_RUN = '--dry-run' in sys.argv

# ── 从md读事件标题 ──
with open(MD_PATH, 'r', encoding='utf-8') as f:
    md = f.read()
MD_EVENTS = {}
for m in re.finditer(r'### 事件(N\d{2})[：:]([^\n]+)', md):
    MD_EVENTS[m.group(1)] = m.group(2).strip()
print(f'[MD] {len(MD_EVENTS)} NTRS事件')

# ── 解析build.py中的硬编码NTRS块 ──
with open(BUILD_PY, 'r', encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')

blocks = []  # [{start_line, end_line, uid, keys, order, prob, old_comment, old_n}]
i = 0
while i < len(lines):
    if 'entries.append(make_entry(' in lines[i]:
        depth = 0
        j = i
        block_lines = []
        while j < len(lines):
            l = lines[j]
            block_lines.append(l)
            depth += l.count('(') - l.count(')')
            if depth <= 0 and j > i:
                break
            j += 1
        block_text = '\n'.join(block_lines)
        if '【NTRS' in block_text:
            uid_m = re.search(r'uid\s*=\s*(\d+)', block_text)
            keys_m = re.search(r'keys\s*=\s*(\[[^\]]*\])', block_text, re.DOTALL)
            order_m = re.search(r'order\s*=\s*(\d+)', block_text)
            prob_m = re.search(r'probability\s*=\s*(\d+)', block_text)
            comment_m = re.search(r'comment="([^"]*)"', block_text)
            if uid_m:
                old_comment = comment_m.group(1) if comment_m else ''
                old_n = None
                nm = re.search(r'N(\d{1,2})', old_comment)
                if nm:
                    old_n = int(nm.group(1))
                blocks.append({
                    'start': i, 'end': j,
                    'uid': int(uid_m.group(1)),
                    'keys': keys_m.group(1) if keys_m else '[]',
                    'order': int(order_m.group(1)) if order_m else 0,
                    'prob': int(prob_m.group(1)) if prob_m else 80,
                    'old_comment': old_comment,
                    'old_n': old_n,
                })
        i = j
    i += 1

print(f'[build.py] {len(blocks)} 硬编码NTRS条目')

# ── 手动映射表：old_N# → new_N## ──
# 基于概念相似性。只覆盖关键差异，其余走自动匹配。
MANUAL_MAP = {
    # 旧框架条目 → 对应新事件
    1: 'N01', 2: 'N02', 3: 'N11', 4: 'N03', 5: 'N06', 6: 'N36',
    7: 'N09', 8: 'N13', 9: 'N10', 10: 'N12', 11: 'N14',
    12: 'N14', 13: 'N15', 14: 'N17', 16: 'N37', 17: 'N32',
    18: 'N34', 19: 'N42', 20: 'N27', 21: 'N21',
    22: 'N41', 23: 'N38', 24: 'N46', 25: 'N47',
    26: 'N38', 27: 'N35', 28: 'N20', 29: 'N25',
    30: 'N23', 31: 'N66', 32: 'N66', 33: 'N43',
    34: 'N43', 35: 'N43', 36: 'N53', 37: 'N54',
    38: 'N45', 39: 'N39', 40: 'N40', 41: 'N41',
    42: 'N48', 43: 'N52', 44: 'N44', 45: 'N66',
    46: 'N45', 47: 'N47', 48: 'N48', 49: 'N49',
    51: 'N46', 52: 'N67', 53: 'N72', 54: 'N73',
    55: 'N74', 56: 'N75', 57: 'N49', 58: 'N51',
    59: 'N60', 60: 'N61', 61: 'N64', 62: 'N60',
    63: 'N61', 64: 'N67', 65: 'N68', 66: 'N69',
    67: 'N70',
}

# ── UID回退映射：处理无N编号的旧框架条目 ──
UID_FALLBACK = {
    27: 'N01',   # 【NTRS路线】坦白之夜 → N01
    28: 'N11',   # 【NTRS路线】三种一对一见证 → N11 第一次共享
    29: 'N43',   # 【NTRS路线】三种多人共享 → N43 她的游戏
}

def find_new_id(old_comment, old_n, uid):
    """手动映射优先 → UID回退 → 关键词匹配"""
    if old_n and old_n in MANUAL_MAP:
        return MANUAL_MAP[old_n]
    if uid in UID_FALLBACK:
        return UID_FALLBACK[uid]

    # 关键词匹配
    rest = re.sub(r'【NTRS[^】]*】\s*', '', old_comment)
    rest = re.sub(r'N\d+\s*', '', rest)
    keywords = [kw for kw in re.split(r'[——：:、，/\-—\s]+', rest) if len(kw) >= 2]
    best_id, best_score = None, 0
    for eid, etitle in MD_EVENTS.items():
        score = sum(1 for kw in keywords if kw in etitle)
        if score > best_score:
            best_score = score
            best_id = eid
    return best_id if best_score >= 1 else None

# ── 展示映射 ──
print('\n映射预览：')
mapped = unmapped = 0
for b in blocks:
    new_id = find_new_id(b['old_comment'], b['old_n'], b['uid'])
    status = '✅' if new_id else '❌'
    if new_id: mapped += 1
    else: unmapped += 1
    print(f"  {status} uid={b['uid']:>4} order={b['order']:>4} old_N{b['old_n'] or '??':>2} → {new_id or '???'}  {b['old_comment'][:70]}")

print(f'\n映射: {mapped} / 未映射: {unmapped}')

if DRY_RUN:
    print('\n[Dry-run] 未修改文件。')
    sys.exit(0)

if unmapped > 0:
    print(f'\n⚠️  {unmapped} 个未映射，跳过。继续？(y/n)')
    if input().strip().lower() != 'y':
        sys.exit(1)

# ── 备份 ──
ts = time.strftime('%Y%m%d_%H%M%S')
bak_path = os.path.join(BACKUP_DIR, f'build_eldoria.py.{ts}.bak')
shutil.copy2(BUILD_PY, bak_path)
print(f'\n[备份] {bak_path}')

# ── 从后往前替换 ──
new_lines = list(lines)
replaced = 0
for b in reversed(blocks):
    new_id = find_new_id(b['old_comment'], b['old_n'], b['uid'])
    if not new_id:
        continue
    title = MD_EVENTS.get(new_id, '')
    # 从原始第一行提取缩进
    orig_indent = len(lines[b['start']]) - len(lines[b['start']].lstrip())
    indent = ' ' * orig_indent
    replacement = [
        f'{indent}# MD驱动: {new_id} {title}',
        f'{indent}add_ntrs_entry(entries, \'{new_id}\', uid={b["uid"]}, keys={b["keys"]}, order={b["order"]}, probability={b["prob"]})',
    ]
    new_lines[b['start']:b['end']+1] = replacement
    replaced += 1

new_text = '\n'.join(new_lines)
with open(BUILD_PY, 'w', encoding='utf-8') as f:
    f.write(new_text)

print(f'[替换] {replaced} 个条目 → add_ntrs_entry()')
print('运行 python scripts/build_eldoria.py --validate 验证')
