import re
with open('C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py', 'r', encoding='utf-8') as f:
    bt = f.read()

# Fix 3 remaining under-800 entries by appending content before last line
fixes = {
    177: '核心情感：Seraphina220年来的第一个选择——以前她守护森林是因为必须。现在雾帷裂开了——她可以选择走出去。这不是背叛Eldoria——是扩展了Eldoria的边界。守护者不需要永远困在一个地方。',
    164: '核心情感：N15的真正重量不在于选择本身——在于在那个时刻，Seraphina已经不需要任何特定结果来确认自己。三个结局都通向同一个终点：她选择了他，他也选择了她。在这条NTRS路上他们从未失去彼此。',
    172: '核心：银流河的恢复不只是物理现象——是Eldoria200年来第一次对自己说「我能好起来」。圣光单独不能转化腐化——需要有人愿意走入黑暗。黎恩走了进去。河水的银色是两个人的光芒混合后的颜色。',
}

for uid, addition in fixes.items():
    pat = r'(# === uid ' + str(uid) + r':.*?content=\(\s*\n)(.*?)(\n\s*\),)'
    m = re.search(pat, bt, re.DOTALL)
    if m:
        content = m.group(2)
        lines = content.split('\n')
        # Find last non-empty content line
        last_idx = len(lines) - 1
        while last_idx >= 0 and not lines[last_idx].strip().startswith('"'):
            last_idx -= 1
        if last_idx >= 0:
            # Insert new line before last line
            new_line = '            "' + addition.replace('\\', '\\\\').replace('"', '\\"') + '\\n"'
            lines.insert(last_idx, new_line)
            new_content = '\n'.join(lines)
            old = m.group(0)
            new = m.group(1) + new_content + m.group(3)
            bt = bt.replace(old, new, 1)
            print(f'OK uid={uid}: +{len(addition)} chars')

with open('C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py', 'w', encoding='utf-8') as f:
    f.write(bt)
print('Done')
