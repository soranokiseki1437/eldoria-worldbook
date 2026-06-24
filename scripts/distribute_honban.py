"""
将"本番性交事件"章节的4个事件(N72-N75)均匀分布插入N49之后，重编号N50+。

插入点：N49后 → N50菲 / N53后 → N54亚莉莎 / N56后 → N58玲 / N59后 → N62劳拉
安全措施：单次pass regex + 词边界保护 + 自动备份

用法：python distribute_honban.py [--dry-run]
"""
import re, sys, os, shutil, time

PROJECT = r'C:\Users\lx\Desktop\世界书'
MD = os.path.join(PROJECT, 'docs', '05_事件系统.md')
BACKUP_DIR = os.path.join(PROJECT, 'backups')
DRY_RUN = '--dry-run' in sys.argv

# ── 读取文件 ──
with open(MD, 'r', encoding='utf-8') as f:
    text = f.read()
orig = text

# ── Step 1: 从"本番性交事件"章节提取4个事件 ──
section_start = text.find('## 本番性交事件')
section_end = text.find('\n## ', section_start + 10) if text.find('\n## ', section_start + 10) > 0 else len(text)
honban_section = text[section_start:section_end]

# 提取每个事件块
events = {}
for m in re.finditer(r'### 事件(N7[2-5])[：:]([^\n]+)\n\n```yaml\n(.*?)\n```', honban_section, re.DOTALL):
    eid = m.group(1)
    title = m.group(2).strip()
    yaml_body = m.group(3)
    events[eid] = {
        'title': title,
        'yaml': yaml_body,
        'block': f'### 事件{eid}：{title}\n\n```yaml\n{yaml_body}\n```\n\n---\n',
    }
    print(f'[提取] {eid}：{title}')

if len(events) != 4:
    print(f'ERROR: 期望4个事件，找到{len(events)}个')
    sys.exit(1)

# 按字符位置排序（N72, N73, N74, N75）
ordered = sorted(events.items(), key=lambda x: honban_section.find(f'### 事件{x[0]}：'))

# ── Step 2: 分配插入位置 ──
# 用临时ID（NX1-NX4）插入，避免和现有N50+冲突，最后统一重编号
insert_plan = [
    # (after_event, temp_id, source_event_key, final_id)
    ('N49', 'NX1', ordered[0][0], 'N50'),   # 菲
    ('N53', 'NX2', ordered[1][0], 'N54'),   # 亚莉莎
    ('N56', 'NX3', ordered[2][0], 'N58'),   # 玲
    ('N59', 'NX4', ordered[3][0], 'N62'),   # 劳拉
]

# ── Step 3: 从后往前插入（避免行号偏移） ──
for after_eid, temp_id, src_id, final_id in reversed(insert_plan):
    # 在after_eid后面找到插入点
    pattern = rf'### 事件{after_eid}[：:][^\n]*\n'
    m = re.search(pattern, text)
    if not m:
        print(f'ERROR: 找不到 {after_eid}')
        sys.exit(1)

    # 找到该事件块的结束位置（下一个### 事件 或 --- 分隔符）
    after_block_start = m.start()
    # 找到这个事件块的结束
    next_event = re.search(r'\n### 事件N\d{2}[：:]', text[after_block_start + len(m.group()):])
    if next_event:
        insert_pos = after_block_start + len(m.group()) + next_event.start()
    else:
        insert_pos = after_block_start + len(m.group())

    # 生成新的事件块（使用临时ID）
    evt = events[src_id]
    new_block = f'\n### 事件{temp_id}：{evt["title"]}\n\n```yaml\n{evt["yaml"]}\n```\n\n---\n'

    # 插入
    text = text[:insert_pos] + new_block + text[insert_pos:]
    print(f'[插入] {temp_id}→{final_id} ← {src_id}（{evt["title"]}） after {after_eid}')

# ── Step 4: 删除"本番性交事件"章节 ──
# 重新计算（文本已变）
new_section_start = text.find('## 本番性交事件')
new_section_end = text.find('\n## ', new_section_start + 10)
if new_section_end < 0:
    new_section_end = len(text)
# 保留章节标题前的空行
while new_section_end < len(text) and text[new_section_end] == '\n':
    new_section_end += 1
text = text[:new_section_start].rstrip('\n') + '\n' + text[new_section_end:]
print('[删除] 本番性交事件章节')

# ── Step 5: 从N49起统一连续重编号 ──
# 收集N49之后所有事件，按出现顺序重新分配连续编号
all_events = []
for m in re.finditer(r'### 事件(N[A-Z\d]{2,3})[：:]([^\n]+)', text):
    all_events.append((m.start(), m.group(1), m.group(2)))

# 找N49位置
n49_idx = None
for i, (pos, eid, title) in enumerate(all_events):
    if eid == 'N49':
        n49_idx = i
        break

if n49_idx is None:
    print('ERROR: 找不到N49')
    sys.exit(1)

# N49之后：从50开始重新分配
renumber_map = {}
expected = 50
for i in range(n49_idx + 1, len(all_events)):
    old_id = all_events[i][1]
    new_id = f'N{expected:02d}'
    if old_id != new_id:
        renumber_map[old_id] = new_id
    expected += 1

print(f'\n重编号: {len(renumber_map)} 个 (N50→N{expected-1:02d})')
for old, new in sorted(renumber_map.items()):
    print(f'  {old} → {new}')

# 单次pass替换：从N49之后开始
n49_pos = all_events[n49_idx][0]
before = text[:n49_pos]
after = text[n49_pos:]

def replace_id(match):
    eid = match.group(1)
    return f'### 事件{renumber_map.get(eid, eid)}：'

after = re.sub(r'### 事件(N[A-Z\d]{2,3})[：:]', replace_id, after)
after = re.sub(r'事件:\s*(N[A-Z\d]{2,3})\b',
               lambda m: f'事件: {renumber_map.get(m.group(1), m.group(1))}', after)

text = before + after

# ── Step 6: 验证无重复编号 ──
final_ids = []
for m in re.finditer(r'### 事件(N\d{2})[：:]', text):
    final_ids.append(m.group(1))

from collections import Counter
dupes = {k: v for k, v in Counter(final_ids).items() if v > 1}
if dupes:
    print(f'\n❌ 仍有重复编号: {dupes}')
    sys.exit(1)

print(f'\n✅ 无重复编号，最终事件数: {len(final_ids)}')

if DRY_RUN:
    print('[Dry-run] 未修改文件')
    sys.exit(0)

# ── Step 7: 备份并写入 ──
ts = time.strftime('%Y%m%d_%H%M%S')
bak = os.path.join(BACKUP_DIR, f'05_事件系统.md.{ts}.bak')
shutil.copy2(MD, bak)
print(f'[备份] {bak}')

with open(MD, 'w', encoding='utf-8') as f:
    f.write(text)

print('[完成] 运行 python scripts/event_tool.py validate docs/05_事件系统.md 验证')
