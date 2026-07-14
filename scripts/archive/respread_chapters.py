#!/usr/bin/env python
"""Respread chapters with new IDs and update proposal"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp = os.path.join(BASE, '方案', '艾玛×矮人兄弟NSFW新增方案.md')

with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()

# Mapping: old_id → new_id (using full 230.X pattern to avoid partial matches)
id_map = [
    ('230.6', '244.3'),
    ('230.7', '254.3'),
    ('230.8', '264.3'),
    ('230.9', '297.3'),
]

for old, new in id_map:
    c = c.replace(old, new)
    print(f'{old} → {new}')

# Update the insertion diagram with new placement justification
old_diagram = '''227: 书房之秘——符文室的馈赠 (艾玛×法林口交，Dolkin门外险些发现)
230: 紫色丝袜——魔女的足 (艾玛×法林紫色丝袜足交，Hagan门外险些发现)
    ↓  ← 艾玛的性经验已建立，"紫色丝袜"成为情欲标记
【NEW】230.3: 紫丝与弯腰——二哥的目击 (Level 2)
    ↓
【NEW】244.3: 大哥的手——锻造室的不打扰 (Level 6)
    ↓
【NEW】254.3: 二哥的约定——足下的善意 (Level 3)
    ↓
【NEW】264.3: 兄弟的争夺——左右开弓 (Level 8)
    ↓
【NEW】297.3: 紫色丝袜的轮番——蹭蹭就进去 (Level 10)
    ↓
231: 劳拉的白袜——鬼之力的释放
... → 239: 桌下之口——祖厅的晚餐 (艾玛×法林桌下口交，三兄弟同桌)
... → 263: 通讯那头——双矮人的口 (Seraphina×Hagan+Dolkin)'''

new_diagram = '''227: 书房之秘——符文室的馈赠 (艾玛×法林口交，Dolkin门外险些发现)
230: 紫色丝袜——魔女的足 (艾玛×法林紫色丝袜足交，Hagan门外险些发现)
    ↓  ← 艾玛的性经验已建立，"紫色丝袜"成为情欲标记
【NEW】230.3: 紫丝与弯腰——二哥的目击 (Level 2 · Stage 5)
    ↓  间隔14章（日常频率，性欲不需要每天解决）
【NEW】244.3: 大哥的手——锻造室的不打扰 (Level 6 · Stage 5)
    ↓  间隔10章
【NEW】254.3: 二哥的约定——足下的善意 (Level 3 · Stage 5)
    ↓  间隔10章
【NEW】264.3: 兄弟的争夺——左右开弓 (Level 8 · Stage 5 · 在263双矮人口交之后形成对照)
    ↓  间隔33章（跨阶段跳跃）
【NEW】297.3: 紫色丝袜的轮番——蹭蹭就进去 (Level 10 · Stage 6 · 艾玛×法林本番297之后)
    ↓
231: 劳拉的白袜——鬼之力的释放
... → 239: 桌下之口——祖厅的晚餐 (艾玛×法林桌下口交，三兄弟同桌)
... → 263: 通讯那头——双矮人的口 (Seraphina×Hagan+Dolkin)
... → 297: 甜蜜顶点——矮人的第一次 (艾玛×法林首次插入)'''

# Update "为什么放在230之后" section
old_why = '''**为什么放在230之后**：艾玛与法林的性关系已深化（227口交、230足交），她对性行为的认知和自信已经建立。紫色丝袜（230）成为情欲标记——哈根在230已瞥见艾玛的袜子颜色"变了"。新三章从同一视觉符号（紫色丝袜）出发，让艾玛注意到：这双袜子不仅对法林有效。

**为什么在239之前**：239是艾玛在祖厅晚餐桌下给法林口交，多尔金和哈根同桌而坐。此时艾玛与兄弟之间仍是"弟妹与哥哥"的正常关系。新三章先建立艾玛与兄弟的私下"帮助"动态，239的正常共餐因此有了更复杂的弦外之音。

**与263（Seraphina×双矮人）的关系**：新三章是艾玛×兄弟的"初次意外"，263是后来Seraphina以更熟练的方式帮双矮人。时间线上：230→230.x(艾玛首次帮兄弟)→239(桌下隐奸)→...→263(Seraphina接力)。'''

new_why = '''**为什么从230起步**：艾玛与法林的性关系已深化（227口交、230足交），紫色丝袜成为情欲标记。230.3从同一视觉符号出发，让艾玛注意到这双袜子不仅对法林有效。

**为什么拉开间距**：五个事件从230跨越到297，间隔10-33章不等。性欲是偶发需求，不是每日任务。每次"帮忙"都是独立事件——某天意外发生，艾玛善意见机行事。密集排列会让善意弧线变成日程表。

**为什么297.3放在Stage 6**：紫色丝袜的轮番（Level 10，兄弟轮奸）必须在艾玛×法林首次本番（297甜蜜顶点）之后。她的身体先完整交付给法林，然后才有兄弟得寸进尺的意外。法林是底线，"告诉法林"才能成为有效威胁。

**与263（Seraphina×双矮人）的关系**：264.3（艾玛×兄弟口交手交）在263之后，形成对照——Seraphina的熟练双人口交在前，艾玛用温柔声音管理兄弟争夺在后。两种风格，同一个矮人兄弟。'''

c = c.replace(old_diagram, new_diagram)
c = c.replace(old_why, new_why)

# Update Q2 about stage placement
old_q2 = '''### Q2: 阶段归属
297.3(紫色丝袜的轮番/Level 10)目前放在Stage 5。也可考虑放在Stage 6(放纵)的开头(276.3)。建议：
- **放在Stage 5(当前方案)**：艾玛全程主导，善意内核，非"失控"——更接近"享受和掌控"
- **放在Stage 6**：Level 10按惯例归入放纵阶段，且已有类似章节(269野外失控花田轮奸)'''

new_q2 = '''### Q2: 阶段归属
297.3(紫色丝袜的轮番/Level 10)已确定放在Stage 6(放纵)，在297甜蜜顶点(艾玛×法林首次插入)之后。理由：
- 艾玛的身体先完整交付法林，然后才有兄弟意外轮奸
- Level 10按惯例归入放纵阶段
- "告诉法林"的威胁在法林已成为她真正的男人之后才有分量'''

c = c.replace(old_q2, new_q2)

# Update Q1
old_q1 = '''### Q1: 章节数量
已确定5章方案：230.3(视觉暴露) + 244.3(大哥手交) + 254.3(二哥足交+约定) + 264.3(兄弟争夺/口交手交) + 297.3(兄弟轮番/插入)。呈完整递进弧线：看→手→足→口+手→插入。'''

new_q1 = '''### Q1: 章节数量与分布
已确定5章方案，从Stage 5跨越到Stage 6：
- 230.3(视觉暴露 · Stage 5)
- 244.3(大哥手交 · Stage 5，间隔14章)
- 254.3(二哥足交+约定 · Stage 5，间隔10章)
- 264.3(兄弟口交手交 · Stage 5，间隔10章)
- 297.3(兄弟轮奸 · Stage 6，间隔33章，在艾玛×法林本番之后)
递进弧线：看→手→足→口+手→插入，总跨度67章。'''

c = c.replace(old_q1, new_q1)

# Update Step files
old_files = '''# 五个新文件
docs/story/5：享受和掌控/_NEW_230.3_紫丝与弯腰——二哥的目击.TXT
docs/story/5：享受和掌控/_NEW_244.3_大哥的手——锻造室的不打扰.TXT
docs/story/5：享受和掌控/_NEW_254.3_二哥的约定——足下的善意.TXT
docs/story/5：享受和掌控/_NEW_264.3_兄弟的争夺——左右开弓.TXT
docs/story/5：享受和掌控/_NEW_297.3_紫色丝袜的轮番——蹭蹭就进去.TXT'''

new_files = '''# 五个新文件（跨Stage 5和Stage 6）
docs/story/5：享受和掌控/_NEW_230.3_紫丝与弯腰——二哥的目击.TXT
docs/story/5：享受和掌控/_NEW_244.3_大哥的手——锻造室的不打扰.TXT
docs/story/5：享受和掌控/_NEW_254.3_二哥的约定——足下的善意.TXT
docs/story/5：享受和掌控/_NEW_264.3_兄弟的争夺——左右开弓.TXT
docs/story/6：放纵/_NEW_297.3_紫色丝袜的轮番——蹭蹭就进去.TXT'''

c = c.replace(old_files, new_files)

# Update sex index note
old_si = '''- 230.3 → 暴露/触碰 分类
- 244.3 → 手交 分类
- 254.3 → 足交 分类
- 264.3 → 口交/手交 分类
- 297.3 → 本番/群交/口交/暴露 分类'''

# Actually the IDs changed, so the sex index lines also need updating
# They were already partially updated by the id_map replacements above
# Let me just ensure the note is correct
old_note = '保留230.6(大哥的手)、230.7(二哥的约定)、230.8(兄弟的争夺)，共5章。'
new_note = '五个文件分布在Stage 5(4个)和Stage 6(1个)，共5章。'
c = c.replace(old_note, new_note)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)

print('Done. All IDs rerouted and text updated.')
