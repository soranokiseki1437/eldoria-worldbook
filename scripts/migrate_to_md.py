"""
一次性迁移：将build_eldoria.py中所有硬编码NTRS条目替换为add_ntrs_entry()调用。
内容自动从05_事件系统.md读取。
"""
import re, sys, os

PROJECT = r'C:\Users\lx\Desktop\世界书'
build_py = os.path.join(PROJECT, 'scripts', 'build_eldoria.py')
md_path = os.path.join(PROJECT, 'docs', '05_事件系统.md')

# Step 1: 从md读取所有NTRS事件 → {N##: title}
with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

md_events = {}
for m in re.finditer(r'### 事件(N\d{2})[：:]([^\n]+)', md_text):
    md_events[m.group(1)] = m.group(2).strip()
print(f'MD中找到 {len(md_events)} 个NTRS事件')

# Step 2: 读取build_eldoria.py
with open(build_py, 'r', encoding='utf-8') as f:
    build_text = f.read()

# Step 3: 找到所有硬编码NTRS条目
# 模式：从 comment="【NTRS... 开始到 content="...", 结束的 make_entry 块
pattern = r'''
(?P<indent>[ \t]*)
entries\.append\(make_entry\(
(?P<body>.*?)
\)\)
'''.replace('\n', '')

# 更简单的模式：匹配完整的 entries.append(make_entry(...))
# 使用括号计数来匹配
blocks = []
lines = build_text.split('\n')
i = 0
while i < len(lines):
    line = lines[i]
    # 检测硬编码NTRS条目开始
    if 'entries.append(make_entry(' in line and i > 0:
        # 检查前一行是否包含【NTRS
        prev = lines[i-1]
        if '【NTRS' in prev:
            # 找到块开始
            start = i - 1  # comment line
            # 收集直到匹配的 ))
            depth = 0
            j = i
            block_lines = [prev]
            while j < len(lines):
                l = lines[j]
                block_lines.append(l)
                depth += l.count('(') - l.count(')')
                if 'make_entry(' in l:
                    pass  # already counted
                if depth == 0 and '))' in l:
                    break
                if depth <= 0 and j > i:
                    break
                j += 1
            if depth <= 0:
                blocks.append((start, j, '\n'.join(block_lines)))
    i += 1

print(f'找到 {len(blocks)} 个硬编码NTRS条目')

# Step 4: 为每个旧条目找到最匹配的新N##
# 策略：从comment中提取旧编号/标题，匹配md事件
import difflib

def find_best_match(old_comment, old_content_title):
    """根据旧条目的comment和content标题找到最匹配的新事件"""
    # 提取旧编号
    old_num = None
    m = re.search(r'N(\d{1,2})', old_comment)
    if m:
        old_num = m.group(1)

    # 提取旧标题
    old_title = old_comment.split('——', 1)[-1] if '——' in old_comment else old_comment.split('】', 1)[-1]
    old_title = old_title.strip()

    # 也从content中提取标题
    if old_content_title:
        old_title2 = old_content_title.replace('【NTRS事件——', '').split('：')[0]

    # 尝试用标题匹配
    best_id = None
    best_score = 0

    for eid, etitle in md_events.items():
        # 简单包含匹配
        score = 0
        # 关键词匹配
        keywords = old_title.replace('——', ' ').replace('：', ' ').split()
        for kw in keywords:
            if len(kw) >= 2 and kw in etitle:
                score += 1

        if score > best_score:
            best_score = score
            best_id = eid

    return best_id

# Step 5: 生成替换
# 由于自动匹配不完美，采用手动映射表覆盖关键条目
# 读取所有旧comment中的概念，手动映射到新N##

# 先收集所有旧条目的comment
old_comments = []
for start, end, block in blocks:
    m = re.search(r'comment="([^"]+)"', block)
    if m:
        old_comments.append(m.group(1))

print('\n旧条目列表:')
for i, c in enumerate(old_comments):
    print(f'  {i}: {c[:100]}')

print('\n新MD事件:')
for eid, title in sorted(md_events.items()):
    print(f'  {eid}: {title}')
