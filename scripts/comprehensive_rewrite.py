"""
Comprehensive rewrite: all user changes in one pass, then renumber.
Finds events by title keywords, not by number, to avoid cross-ref issues.
"""
import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

def find_event_block(text, title_keyword):
    """Find event by title keyword, return (start_idx, end_idx, full_block_text)"""
    # Find the header
    pattern = r'### 事件(N\d+)：.*?' + re.escape(title_keyword) + r'.*'
    m = re.search(pattern, text)
    if not m:
        print(f'  NOT FOUND: {title_keyword}')
        return None, None, None

    start = m.start()
    eid = m.group(1)

    # Find end: next ### 事件 or next stage header or --- followed by non-event
    rest = text[start+5:]  # skip past '### 事'
    next_event = re.search(r'\n### 事件N\d+：', rest)
    next_section = re.search(r'\n### [A-ZB→C终D].*?阶段——', rest)

    end_offset = len(rest)
    if next_event:
        end_offset = min(end_offset, next_event.start())
    if next_section:
        end_offset = min(end_offset, next_section.start())

    end = start + 5 + end_offset
    block = text[start:end]
    return start, end, block, eid

def replace_event_block(text, title_keyword, new_block):
    """Replace an event found by title keyword with new block"""
    pattern = r'### 事件(N\d+)：.*?' + re.escape(title_keyword) + r'.*'
    m = re.search(pattern, text)
    if not m:
        print(f'  REPLACE FAILED: {title_keyword}')
        return text

    start = m.start()
    eid = m.group(1)

    # Find end
    rest = text[start+5:]
    next_event = re.search(r'\n### 事件N\d+：', rest)
    next_section = re.search(r'\n### [A-ZB→C终D].*?阶段——', rest)

    end_offset = len(rest)
    if next_event:
        end_offset = min(end_offset, next_event.start())
    if next_section:
        end_offset = min(end_offset, next_section.start())

    end = start + 5 + end_offset

    return text[:start] + new_block + text[end:]

# ============================================================
# CHANGE 1: N08 — Add艾德里安 hearing
# ============================================================
kw = '艾德里安的察觉'
s, e, block, eid = find_event_block(c, kw)
if s:
    block = block.replace(
        '艾德里安请黎恩和菲娜到府邸用茶。三杯茶斟好后他把门关上——',
        '艾德里安请黎恩和菲娜到府邸用茶。三杯茶斟好后他把门关上——\n'
        '      - 他能察觉不止因为雷恩修了四天外墙。前日经过木屋时他的听力捕捉到了两人的低语——"找谁合适"。\n'
        '        结合雷恩的眼神——答案已经浮出水面。他把门关上——'
    )
    block = block.replace(
        '"雷恩最近状态很奇怪。修了四天外墙还没修好。和他平时不像——他看菲娜的眼神变了。"\n'
        '        菲娜手指收紧——但艾德里安下一句话让她愣住了',
        '"开门见山。"\n'
        '        菲娜手指收紧——但艾德里安下一句话让她愣住了'
    )
    c = c[:s] + block + c[e:]
    print('1. N08: Added hearing detail')

# ============================================================
# CHANGE 2: N12 (丝袜) — Fix cause
# ============================================================
kw = '丝袜与内衣'
s, e, block, eid = find_event_block(c, kw)
if s:
    old_bullet = (
        '- N23低语者失控后菲娜想通了一件事：不要失控。不要非人。凯尔——他在河对岸看了那么久也没靠近、\n'
        '        在书房告白也没越线。不会失控。菲娜和黎恩商量后决定试试主动勾引——\n'
        '        先拿最安全的试。换上黑色蕾丝内衣和吊带丝袜——精灵族从不穿这种东西是亚莉莎留给她的'
    )
    new_bullet = (
        '- N11低语者失控后菲娜对黎恩说：要可控。要熟人。黎恩问——凯尔？她犹豫了一下然后点头。\n'
        '        黎恩提出让她穿黑丝勾引——菲娜听完脸红了：我做不来。黎恩握着她的手——为我。\n'
        '        她看着他的眼睛很久——然后低头：只穿给你看。他说：穿给他看——让我看他的反应。\n'
        '        菲娜深吸一口气——好。但你要在场。全程。黎恩点头。\n'
        '        她从箱底翻出亚莉莎给的黑色蕾丝内衣和吊带丝袜——精灵族从不穿这种东西。穿的时候手指在抖'
    )
    if old_bullet in block:
        block = block.replace(old_bullet, new_bullet)
    else:
        # Try to find just the start
        for line in block.split('\n'):
            if '低语者失控后菲娜想通' in line:
                print(f'  Found N12 line: {line[:80]}')
        # Broader replacement
        idx_start = block.find('N23低语者失控后')
        if idx_start != -1:
            idx_end = block.find('\n', block.find('亚莉莎留给她的', idx_start))
            block = block[:idx_start] + new_bullet.split('N11低语者失控后', 1)[1] + block[idx_end:]

    # Fix the 核心 to emphasize 菲娜害羞
    block = block.replace(
        '核心: B阶段开端——从被看到到主动展示。目的不是勾引凯尔——是给黎恩看他想要的画面。',
        '核心: B阶段开端——黎恩教菲娜主动勾引。菲娜从震惊害羞到勉强接受，全程需要黎恩在场。\n'
        '      目的不是勾引凯尔——是给黎恩看他想要的画面。但迈出这一步的不是她自己的意愿——是他的。'
    )
    c = c[:s] + block + c[e:]
    print('2. N12: Fixed cause (黎恩教, 菲娜害羞勉强)')

# ============================================================
# CHANGE 3: N19 (按摩回礼) — Fix cause
# ============================================================
kw = '乔治的回礼'
s, e, block, eid = find_event_block(c, kw)
if s:
    old_start = '- N66手交教学之后乔治不像之前那样躲着她了。黎恩和菲娜邀请他来做客——'
    new_start = (
        '- 黎恩几天前就和菲娜说了这个计划：请他来做客、让他按摩、你用脚回礼。\n'
        '        菲娜听完脸红了很久——你做全套设计。他点头。她咬着嘴唇——好。听你的。\n'
        '        N16手交教学之后乔治不像之前那样躲着她了。两人邀请他来做客——'
    )
    if old_start in block:
        block = block.replace(old_start, new_start)
    else:
        # find by keyword
        idx = block.find('手交教学之后乔治')
        if idx != -1:
            line_start = block.rfind('\n', 0, idx) + 1
            line_end = block.find('\n', block.find('来做客——', idx)) + 1
            block = block[:line_start] + new_start + block[line_end:]

    # Update核心 to emphasize害羞
    block = block.replace(
        '核心: "对等交换"框架——先接受按摩（被动）再用脚回礼（主动）。',
        '核心: 黎恩提前设计好的"对等交换"——菲娜全程害羞但照做。先接受按摩（被动）再用脚回礼（主动）。\n'
        '      每一步都是黎恩设计的——她执行是因为信任。'
    )
    c = c[:s] + block + c[e:]
    print('3. N19: Fixed cause (黎恩设计, 菲娜害羞执行)')

# ============================================================
# CHANGE 4: N22 (树后) — Rewrite as打飞机 only
# ============================================================
kw = '树后的秘密'
s, e, block, eid = find_event_block(c, kw)
if s:
    new_n22 = '''### 事件N22：树后的秘密——第一次给别人打飞机

```yaml
事件: N22 树后的秘密——第一次给别人打飞机
    触发条件: ntrs_awakened=100, acceptance>=60, kael_closeness>=40, N17已触发
    性行为等级: 4（打飞机·第一次给黎恩以外的人手交）
    情感阶段: B→C（第一次给别人打飞机——不是口交是手、不是偷情是给黎恩看）
    黎恩知情: 是——黎恩在远处知道一切约定好的
    第三者: 凯尔
    情境:
      - N21足崇拜之后凯尔看菲娜脚的眼神变了——像在看一本还想继续翻的书。菲娜和黎恩商量——
        下一步：手。不是口——口是给黎恩的。先用手。凯尔被叫到指定树下——不知道黎恩在远处看着
      - 菲娜让他靠在树干上。他解开裤子时手指在抖——偏修长、偏细、白净偏粉。
        和温泉见过的乔治完全不同。握上去时她心里闪过一个念头——比黎恩小。不是更好不是更差——就是不一样。
        她放慢节奏——第一次给黎恩之外的人打飞机。手心贴着他感受脉搏跳动——
        和黎恩的节奏不同，和黎恩的温度不同。但她的眼睛始终往黎恩藏身的方向看
      - 凯尔在她手里释放——他手指插进自己头发里呼吸全乱。她擦手时发现自己在想黎恩——
        不是求救是分享。你看——我在为别人做。你看到了吗
      - 站起来擦干净手指对凯尔说不要告诉黎恩——她知道黎恩知道。这是游戏的一部分
    占有欲确认:
      - 凯尔踉跄离开。菲娜走向黎恩藏身处——你看到了吗。我第一次。给别人。黎恩把她拉过来——
        我看到了。她靠在黎恩胸口——他的手和你的不一样。比你的...她没说完。黎恩收紧手臂——比我的什么。
        她抬头——比你的小。声音很轻但不是贬低。黎恩低头吻她——那是自然。
        她笑了一下——但你的手。我只想握你的手。
    玩家选择:
      A. 让她继续演到底 → shared+25, possess+30
      B. 中途走出来让凯尔知道 → possess+35, bond+10
    变量: shared+25, possess+30~35, acceptance+12, kael_closeness+15, bond+10
    核心: ★第一次给黎恩外的人打飞机——B→C阶段。手交而不是口交（口留给黎恩）。
      她全程比较——比黎恩小、和黎恩节奏不同——但比较之后确认的是：你的手我只想握你的。
      第一次"为别人做但全程在想黎恩"的心理体验。
```'''
    c = c[:s] + new_n22 + c[e:]
    print('4. N22: Rewrote as打飞机 only')

# ============================================================
# CHANGE 5: Move N22 after N26
# ============================================================
# Find current N22 and extract it
n22_pos = c.find('### 事件N22：树后的秘密——第一次给别人打飞机')
n22_next = c.find('\n### 事件N23：', n22_pos)
n22_block = c[n22_pos:n22_next]

# Remove from current position
c = c[:n22_pos] + c[n22_next:]

# Find N26
n26_pos = c.find('### 事件N26：桌下之口——隐奸口交')
# Find end of N26
n26_end = c.find('\n### ', n26_pos + 10)  # next ### marker
if n26_end == -1:
    n26_end = c.find('\n---\n', n26_pos + 10)

# Insert N22 after N26
c = c[:n26_end] + '\n\n' + n22_block + c[n26_end:]
print('5. Moved N22 after N26')

# ============================================================
# CHANGE 6: N27 (双人共享) — Rewrite as两人打飞机
# ============================================================
kw = '第一次双人共享'
s, e, block, eid = find_event_block(c, kw)
if s:
    new_n27 = '''### 事件N27：第一次双人共享——两只手同时

```yaml
事件: N27 第一次双人共享——两只手同时
    触发条件: ntrs_awakened=100, acceptance>=44, shared>=22, george_closeness>=30, kael_closeness>=30, N22已触发
    性行为等级: 4+4（打飞机×2·第一次同时给两个男人手交）
    情感阶段: B→C（一对一到二对一桥接——左右手不同节奏）
    黎恩知情: 是——黎恩在场注视
    第三者: 乔治+凯尔
    情境:
      - N22给了凯尔第一次打飞机、N16给了乔治第一课——两个人都被她碰过了。菲娜想试同时。
        篝火暗红余烬。她坐中间——左边乔治右边凯尔。两人都紧张——乔治膝上握拳凯尔推眼镜
      - 右手握乔治——偏粗、白净、龟头圆钝，写字的手在腿间无处安放。左手握凯尔——偏修长、偏细、白净偏粉，
        学者的手插进自己头发里。两种不同的硬度和脉搏在左右手同时跳动——她低头看了一眼自己的手，
        一只握着粗的、一只握着长的——脸一下子红了
      - 身体微旋双手保持不同节奏——乔治这边慢因为他还容易紧张，凯尔那边快因为他忍得比她想的更难受。
        琥珀色眼睛在两个目标间切换——左边笨拙的工程师还问力度对不对，右边学者已经在数天花板裂缝。
        不是从容是专心——她在做一件从没做过的事而且做得很认真
      - 两人先后在她手里释放——时间差大概四十秒。菲娜活动了一下酸胀的手指——
        比想象的累。但是——她看着黎恩——好玩。同时两个。左右手不同的人。
        下次——还可以更多吗？不是挑逗是认真尝试
    占有欲确认:
      - 两人离开后菲娜靠在黎恩胸口——手腕还在酸。两只手都在抖——握了两个人也握了两个不同的形状。
        但你的——她把黎恩的手按在自己手心——你的手掌。我只想留在你手掌里。
    玩家选择:
      A. 让她继续到两人都释放 → shared+20, possess+15
      B. 中途接手取代两人 → possess+25, bond+15
    变量: shared+20, possess+20, acceptance+10, george_closeness+5, kael_closeness+5, trust+10
    核心: 第一次同时给两个人打飞机——左右手不同人不不同节奏不同形状。
      发现同时两个并不比一个难——迈向多人的信心基础。但最终回归黎恩手掌的归属。
```'''
    c = c[:s] + new_n27 + c[e:]
    print('6. N27: Rewrote as两人打飞机')

# ============================================================
# CHANGE 7: N28 (扑克两局) — Rewrite as打飞机+乳交
# ============================================================
kw = '艾德里安的扑克'
s, e, block, eid = find_event_block(c, kw)
if s:
    new_n28 = '''### 事件N28：艾德里安的扑克——手与乳的初次

```yaml
事件: N28 艾德里安的扑克——手与乳的初次
    触发条件: ntrs_awakened=100, acceptance>=60, adrian_closeness>=45, N22已触发
    性行为等级: 4+7（打飞机+乳交·第一次给别人打飞机和第一次乳交）
    情感阶段: B→C（首次手+乳——借赌局尝试两种新方式）
    黎恩知情: 是——黎恩全程在场
    第三者: 艾德里安
    情境:
      - 银流河畔午后。艾德里安提议扑克——不赌钱。两局。菲娜看了黎恩一眼然后点头。
        艾德里安洗牌——手指修长和指交时用的是同一种从容
      - 第一局她输了——代价：用手。菲娜深吸一口气——她是第一次给黎恩和凯尔之外的人打飞机。
        他解开裤子——偏长、偏粗、麦色，龟头饱满圆润。和凯尔的修长白净完全不同、和乔治的偏粗圆钝也不同——
        他的阴茎和他的人一样好看。她握住——触感比视觉更诚实。手法已经熟练但对象是新的。
        他呼吸变重但她保持节奏——黎恩在看。她手上在为别人做眼睛在分享
      - 第二局她又输了——代价：用胸。菲娜犹豫了一下——这也是第一次：第一次给别人乳交。她解开上衣时手指比刚才慢——
        月光下双乳泛淡金。双手捧起乳房将他性器夹在乳沟间——不是黎恩的是别人的。她低头看着自己的胸在做一件从没想过会做的事。
        乳沟间的触感陌生——和手完全不同。她抬头看黎恩——不是求助是分享。你看——我在为别人做了。用胸
      - 两局结束。艾德里安没有要求更多——站起来倒了杯水递给她。"今天到此为止。你的第一次——不是我的。"
        不是轻佻是郑重。菲娜接过水杯——手还在微微颤抖但不是害怕
    占有欲确认:
      - 艾德里安走后菲娜靠在黎恩肩上——两次。手和胸。都是第一次。给你之外的人。
        黎恩收紧手臂——感觉怎么样。她想了想——手比胸更...习惯。胸——低头看到的是他的不是你的。不一样。
        黎恩低头吻她额头——谢谢你。她抬头——谢什么。告诉我。每一个第一次都告诉我。
    玩家选择:
      A. 全程沉默注视 → possess+35, shared+20
      B. 每局结束后确认她的状态 → trust+20, bond+15
    变量: shared+25, possess+30, acceptance+12, adrian_closeness+20, trust+15
    核心: ★两个第一次——第一次给黎恩外人打飞机+第一次乳交。两局即止不是累了——
      艾德里安自己叫停因为他知道两局已经够了。不是体力不够是尊重她的第一次。
```'''
    c = c[:s] + new_n28 + c[e:]
    print('7. N28: Rewrote as打飞机+乳交')

# ============================================================
# CHANGE 8: N29 (酒后扑克) — Rewrite as口交
# ============================================================
kw = '酒后扑克'
s, e, block, eid = find_event_block(c, kw)
if s:
    new_n29 = '''### 事件N29：酒后扑克——第一次给别人口交

```yaml
事件: N29 酒后扑克——第一次给别人口交
    触发条件: ntrs_awakened=100, acceptance>=62, adrian_closeness>=50, N28已触发
    性行为等级: 6（口交·第一次给黎恩以外的人口交——黎恩赢的请求）
    情感阶段: B→C（首次口交——黎恩赢的、黎恩请求的、黎恩握着她手）
    黎恩知情: 是——黎恩赢的、黎恩请求的
    第三者: 艾德里安
    情境:
      - N28之后几周——几次正经扑克让三人熟了。艾德里安这个人嘴贱但守规矩、从容但不越界。
        某个晚上又是扑克——喝着酒打着牌不赌东西
      - 酒过几巡——赢的人可以提一个条件。不赌别的。黎恩洗牌。三局——黎恩全赢。
        菲娜看着他——黎恩喝酒脸不红但她的手被他攥住了。他声音平稳——"我的条件。
        我想看你给他口交。"
      - 菲娜手指在他手里僵了一下。给别人口交——这是她的第一次。口曾经是给黎恩的。
        慌乱——看黎恩又看艾德里安。黎恩没有松手——手指穿过她指缝扣紧。不是推她过去是陪她。
        "是你的嘴——永远是你的。但我想看。"她在他指间慢慢松开——然后她跪到艾德里安面前。
        他解开裤子——偏长、偏粗、麦色，龟头饱满圆润，和手交时一样好看。她含住——第一次给黎恩之外的人。
        嘴里的形状不一样。温度一样。脉搏不一样。她闭上眼睛——脑海里不是艾德里安是黎恩的手在她手心里
      - 释放时她吞下去了——因为是第一次因为是黎恩看着因为是他说想要。擦嘴角时黎恩把她拉起来——
        吻住她——嘴里还有别人的味道——但他不在意。他在意的是她做到了——而且告诉了他每一个第一次
    占有欲确认:
      - 事后她靠在黎恩胸口——嘴里还是别人的味道——第一次给别人。但我是闭着眼睛的。
        想的是你的手。黎恩收紧手臂——我知道。她抬头——这是我最后的第一次了。手、胸、嘴——都给出去了。
        只剩——她没说完。黎恩低头——剩下的全部。留给我。她点头——全部。只给你。
    变量: shared+25, possess+35, acceptance+15, adrian_closeness+20, trust+15, bond+15
    核心: ★最后一个"第一次"——口交给别人。和N28手交+乳交形成艾德里安三第一次弧线。
      黎恩赢的、黎恩请求的——不是她输了是他选的人。结束后她确认：手胸嘴都给过了，剩下的全部只给黎恩。
```'''
    c = c[:s] + new_n29 + c[e:]
    print('8. N29: Rewrote as口交')

# ============================================================
# SAVE
# ============================================================
with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

print('\nAll 8 changes applied! Ready for renumber.')
