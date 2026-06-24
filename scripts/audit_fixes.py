"""Fix version numbers, event counts, JSON filenames across all docs."""
import re

# =============================================
# 05_事件系统.md
# =============================================
f = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

c = c.replace('> **版本**: v4.7.1 | **阅读顺序**: 第6/8篇',
              '> **版本**: v5.0 | **阅读顺序**: 第6/8篇')
c = c.replace('（155事件全覆盖）', '（全事件覆盖）')
c = c.replace('NTRS路线事件（N1-N63）: 59个', 'NTRS路线事件（N1-N67）: 67个')

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('✅ 05_事件系统.md updated')

# =============================================
# 00_方案总览.md
# =============================================
f = 'C:/Users/lx/Desktop/世界书/docs/00_方案总览.md'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

c = c.replace('> **版本**：v4.7.1（N/PN系列编号整数化——消除所有小数后缀）',
              '> **版本**：v5.0（NTRS全事件起因补全+编号清理+银发→粉发修复）')
c = c.replace('> **目标文件**：`Eldoria_V4.8.0.json`',
              '> **目标文件**：`Eldoria_V5.0.0.json`')
c = c.replace('Eldoria_V4.8.0.json', 'Eldoria_V5.0.0.json')

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('✅ 00_方案总览.md updated')

# =============================================
# 06_条目规划与格式.md
# =============================================
f = 'C:/Users/lx/Desktop/世界书/docs/06_条目规划与格式.md'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

c = c.replace('> **版本**：v4.7.0', '> **版本**：v5.0')
c = c.replace('**目标条目数**：214条（uid 0-213）', '**目标条目数**：249条（uid 0-240）')
c = c.replace('Eldoria_V4.6.2.json', 'Eldoria_V5.0.0.json')
c = c.replace('完整条目列表（uid 0-141，共 145 条）', '完整条目列表（uid 0-240，共 249 条）')
# Fix entry classification count
# "当前总计 214/214 条" or similar
c = re.sub(r'当前总计.*?214.*?条', '当前总计 249/249 条', c)

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('✅ 06_条目规划与格式.md updated')

# =============================================
# 07_最终执行指令.md
# =============================================
f = 'C:/Users/lx/Desktop/世界书/docs/07_最终执行指令.md'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

c = c.replace('> **版本**：v4.6.2', '> **版本**：v5.0')
c = c.replace('Eldoria_V4.8.0.json', 'Eldoria_V5.0.0.json')

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('✅ 07_最终执行指令.md updated')

# =============================================
# build_eldoria.py comment fixes (N15→N21 in comments)
# =============================================
f = 'C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

# Fix comment references
c = c.replace('# Stage B→C: 足交+口交过渡 (N15/N17', '# Stage B→C: 足交+口交过渡 (N21/N17')
c = c.replace('# === uid 226: N15 书桌下的脚 ===', '# === uid 222: N21 凯尔的臣服 ===')
# The uid was already changed from 226 to 222 in earlier sync

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('✅ build_eldoria.py comments updated')

# =============================================
# _table_output.txt
# =============================================
f = 'C:/Users/lx/Desktop/世界书/scripts/_table_output.txt'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()
c = c.replace('树后的银发', '树后的粉发')
with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('✅ _table_output.txt updated')

print('\nAll done.')
