"""Sync N21, N28, N29 from md → build.py + 06_条目规划"""
import re

# ============================================================
# PART 1: Update build_eldoria.py
# ============================================================
with open('C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py', 'r', encoding='utf-8') as f:
    bp = f.read()

# --- Update uid 222 (N15 书桌下的脚) → match md N21 凯尔的臣服 ---
old_uid222 = '''        content=(
            "【NTRS事件——N15：书桌下的脚】\\\\n\\\\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 56, N14已触发, kael_closeness >= 25, 书房场景\\\\n"
            "性行为等级：4（足交——菲娜→男。桌下隐奸）\\\\n"
            "情感阶段：B→C过渡（动机：用脚是最远的触碰——她用最远的距离测试最近的反应）\\\\n"
            "黎恩知情：是——黎恩在窗台上看书，不知道桌下的事\\\\n\\\\n"
            "场景描述：\\\\n"
            "书房。凯尔在对面的书桌上写精灵文献综述——第十七页。\\\\n"
            "Seraphina坐在他对面，赤足。她在桌面上翻文献——脚在桌下。\\\\n"
            "她的脚趾先碰到他的鞋面。凯尔的手顿了一下——继续写。\\\\n"
            "然后脚趾滑进了他的裤脚——沿着脚踝向上，停在小腿。\\\\n"
            "凯尔打错了一个精灵文单词。\\\\n"
            "「继续写——」她说，声音平稳得像在说午后的天气。\\\\n"
            "脚趾沿着小腿内侧向上——到膝盖，到膝盖内侧。\\\\n"
            "他推了下眼镜——指尖在颤。又一整段精灵文乱了。\\\\n"
            "黎恩在窗台上翻了一页。\\\\n\\\\n"
            "占有欲确认场景：\\\\n"
            "凯尔走后，她的脚还光着。黎恩走过来——握住她的脚踝。\\\\n"
            "「你在桌下——」\\\\n"
            "「我在桌下。」她把脚心贴在他脸上——刚刚碰过凯尔小腿的脚心。\\\\n"
            "「他打错了一段。」\\\\n"
            "「我看到的是你。」\\\\n\\\\n"
            "变量更新：shared_experience_level +15, possessiveness_intensity +18, seraphina_acceptance +8, kael_closeness +10\\\\n"
            "核心：用脚触碰——最远也最隐秘。她在练习掌控距离和反应。\\\\n"
            "桌下和桌上是两个世界：上面的她在翻文献，下面的脚在画地图。"
        ),'''

new_uid222 = '''        content=(
            "【NTRS事件——N21：凯尔的臣服——从闻到舔到足交】\\\\n\\\\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 60, kael_closeness >= 40\\\\n"
            "性行为等级：6（闻脚+舔脚+足交——凯尔足崇拜）\\\\n"
            "情感阶段：B→C（菲娜第一次被舔脚——学者的足崇拜从害羞到沉迷）\\\\n"
            "黎恩知情：是——黎恩在窗外看\\\\n\\\\n"
            "场景描述：\\\\n"
            "黎恩对菲娜耳语了几句——她脸一下子红了。在他书房？黎恩点头。她咬着嘴唇站起来——\\\\n"
            "走到凯尔书房门口回头看了黎恩一眼。黎恩在窗外站定。她推门。\\\\n"
            "凯尔在整理文献——看到她进来又推了推眼镜。她走到他桌前脸还红着但话被黎恩练过。\\\\n"
            "她在他书桌对面坐下——脱下一只丝袜，赤脚搭在他桌沿。凯尔摘下眼镜又戴上——手不知道放哪里。\\\\n"
            "菲娜伸脚——脚趾碰到他嘴唇时他呼吸停了。他没说话——先闻。鼻尖沿脚弓从足跟到趾尖，\\\\n"
            "像在读一本精灵语古籍。然后嘴唇落下——干燥、轻、精确如文献检索。\\\\n"
            "舌头出来——从脚踝滑到脚心——她差点从椅子上滑下去因为痒。\\\\n"
            "他停了一下确认她的表情——没问题——继续。舔完了一整只脚的每一根脚趾。\\\\n"
            "然后是另一只脚。两脚夹住他脸时他弓背往她脚心蹭。她将脚从脸滑下——赤脚覆上他腿间。\\\\n"
            "偏修长、偏细、白净偏粉——和温泉见过的乔治完全不同。脚弓下的触感温热、搏动。\\\\n"
            "她用脚趾环住茎身——趾腹贴紧——缓慢上下滑动。脚心能感觉到每一根血管的走向。\\\\n"
            "凯尔手指在桌面上抓了三道印子——呼吸变成断续的喘息。\\\\n"
            "她调整角度——脚趾夹住龟头边缘，脚心裹住茎身——节奏从慢到快。\\\\n"
            "释放时他把脸埋在她脚心——眼镜压歪了——精液从她脚趾间渗出，沿着脚背往下淌。\\\\n"
            "她伸出另一只脚趾碰了碰他的额头——下次脚也可以。\\\\n\\\\n"
            "占有欲确认：\\\\n"
            "菲娜走出书房腿是软的。黎恩从窗外绕到她身边。她靠在墙上——他舔了一整只脚、每一根脚趾。\\\\n"
            "不是色情的——开始不是。像在读书。我的脚是那本书。黎恩低头——那你喜欢吗。她点头——\\\\n"
            "他认真的样子让我忘了害羞。\\\\n\\\\n"
            "变量更新：shared_experience_level +22, possessiveness_intensity +25, seraphina_acceptance +12, kael_closeness +18\\\\n"
            "核心：凯尔从丝袜远观到闻脚舔脚足交三连跳——但在他的感受里不是跳，\\\\n"
            "是「终于能近距离研究」。菲娜第一次被舔脚——从害羞到接受再到「下次也可以」。\\\\n"
            "足交成分为主导：脚趾环住茎身上下、趾腹贴紧、脚心裹茎、精液从趾间渗出淌下脚背。"
        ),'''

if old_uid222 in bp:
    bp = bp.replace(old_uid222, new_uid222)
    print('✅ build.py uid 222 (N15→N21) updated')
else:
    print('❌ build.py uid 222 NOT FOUND')

# --- Update uid 222 comment/keywords ---
bp = bp.replace(
    'keys=["书桌下的脚", "ntrs", "n15", "凯尔", "足交", "书桌", "隐奸"]',
    'keys=["凯尔的臣服", "ntrs", "n21", "凯尔", "足交", "闻脚", "舔脚", "足崇拜"]')
bp = bp.replace(
    'comment="【NTRS事件】 N15 书桌下的脚——书房里菲娜用赤足在桌下碰凯尔，隐奸足交，黎恩在窗台看书"',
    'comment="【NTRS事件】 N21 凯尔的臣服——从闻到舔到足交，足崇拜三连跳"')
print('✅ build.py uid 222 keys/comment updated')

# --- N28 & N29: Add new entries for 艾德里安扑克 events ---
# Find insertion point: after the last NTRS event in get_uid224_240_entries
# Let's find the end of that function
func_end_marker = '''    # === uid 240: N37 镜前的游戏 ===
    entries.append(make_entry(
        uid=236,'''

# Find position of the end of get_uid224_240_entries
pos = bp.find('''    return entries


def get_uid_pn_erosion_entries''')
if pos == -1:
    pos = bp.find('''    return entries


# ═══════════════════════════════════════════════════════════''')

if pos > 0:
    # Insert N28+N29 before the return statement of the function containing uid 224-240
    # Actually let me find get_uid224_240_entries's return
    pass

print(f'Searching for insertion point...')

# Find get_uid224_240_entries function and its return statement
func_start = bp.find('def get_uid224_240_entries():')
func_return = bp.find('\n    return entries\n', func_start)
if func_return > 0:
    insert_pos = func_return  # Insert before return
    print(f'Found get_uid224_240_entries return at position {func_return}')
else:
    print('❌ Could not find insertion point for N28/N29')
    insert_pos = -1

# N28 + N29 insertion
n28_n29_entries = '''
    # === uid 237: N28 艾德里安的扑克——乳的初次 ===
    entries.append(make_entry(
        uid=237,
        keys=["艾德里安的扑克", "ntrs", "n28", "艾德里安", "扑克", "乳交", "打飞机", "赌局"],
        comment="【NTRS事件】 N28 艾德里安的扑克——乳的初次，手交非初次（树后凯尔为首），乳交才是第一次",
        order=440,
        probability=80,
        content=(
            "【NTRS事件——N28：艾德里安的扑克——乳的初次】\\\\n\\\\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 60, adrian_closeness >= 45\\\\n"
            "性行为等级：4+7（打飞机+乳交·手交非初次——树后凯尔为首·乳交为初次）\\\\n"
            "情感阶段：B→C（手交再演+乳交初体验——借赌局尝试新方式）\\\\n"
            "黎恩知情：是——黎恩全程在场\\\\n\\\\n"
            "场景描述：\\\\n"
            "银流河畔午后。艾德里安提议扑克——不赌钱。两局。菲娜看了黎恩一眼然后点头。\\\\n"
            "艾德里安洗牌——手指修长和指交时用的是同一种从容。\\\\n"
            "第一局她输了——代价：用手。菲娜深吸一口气——她给凯尔打过、给乔治打过，手交不是第一次了。\\\\n"
            "但艾德里安是新的。他解开裤子——偏长、偏粗、麦色，龟头饱满圆润。\\\\n"
            "和凯尔的修长白净完全不同、和乔治的偏粗圆钝也不同——\\\\n"
            "他的阴茎和他的人一样好看。她握住——触感比视觉更诚实。手法已经熟练但对象是新的。\\\\n"
            "他呼吸变重但她保持节奏——黎恩在看。她手上在为别人做眼睛在分享。\\\\n"
            "第二局她又输了——代价：用胸。这是真正的第一次：第一次给别人乳交。\\\\n"
            "她解开上衣时手指比刚才慢——月光下双乳泛淡金。\\\\n"
            "双手捧起乳房将他性器夹在乳沟间——不是黎恩的是别人的。\\\\n"
            "她低头看着自己的胸在做一件从没想过会做的事。\\\\n"
            "乳沟间的触感陌生——和手完全不同。她抬头看黎恩——不是求助是分享。\\\\n"
            "你看——我在为别人做了。用胸。\\\\n"
            "两局结束。艾德里安没有要求更多——站起来倒了杯水递给她。\\\\n"
            "今天到此为止——不是轻佻是郑重。菲娜接过水杯——手还在微微颤抖但不是害怕。\\\\n\\\\n"
            "占有欲确认：\\\\n"
            "艾德里安走后菲娜靠在黎恩肩上——两局。手不是第一次了——凯尔和乔治之后这是第三次。\\\\n"
            "胸——这才是第一次。黎恩收紧手臂——感觉怎么样。\\\\n"
            "她想了想——手已经习惯了。胸——低头看到的是他的不是你的。不一样。\\\\n"
            "黎恩低头吻她额头——谢谢你。她抬头——谢什么。告诉我。每一个第一次都告诉我。\\\\n\\\\n"
            "变量更新：shared_experience_level +25, possessiveness_intensity +30, seraphina_acceptance +12, adrian_closeness +20, trust_level +15\\\\n"
            "核心：★乳交初体验——手交已是第三次（树后凯尔为首、乔治为次），乳才是真正的第一次。\\\\n"
            "艾德里安自己叫停因为他知道两局已经够了——不是体力不够是尊重她的第一次。"
        ),
    ))

    # === uid 238: N29 酒后扑克——第一次给别人口交 ===
    entries.append(make_entry(
        uid=238,
        keys=["酒后扑克", "ntrs", "n29", "艾德里安", "口交", "扑克", "黎恩请求"],
        comment="【NTRS事件】 N29 酒后扑克——第一次给别人口交，黎恩赢的黎恩请求的",
        order=442,
        probability=80,
        content=(
            "【NTRS事件——N29：酒后扑克——第一次给别人口交】\\\\n\\\\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 62, adrian_closeness >= 50\\\\n"
            "性行为等级：6（口交·第一次给黎恩以外的人口交——黎恩赢的请求）\\\\n"
            "情感阶段：B→C（首次口交——黎恩赢的、黎恩请求的）\\\\n"
            "黎恩知情：是——黎恩赢的、黎恩请求的\\\\n\\\\n"
            "场景描述：\\\\n"
            "之后几周——几次正经扑克让三人熟了。艾德里安嘴贱但守规矩、从容但不越界。\\\\n"
            "某个晚上又是扑克——喝着酒打着牌不赌东西。\\\\n"
            "酒过几巡。黎恩洗牌——三局全赢。他的手在桌下攥住了菲娜的手指。\\\\n"
            "我的条件——我想看你给他口交。声音平稳。\\\\n"
            "菲娜手指僵了一下。口——曾经只给黎恩。慌乱——看黎恩又看艾德里安。\\\\n"
            "黎恩没有松手——手指穿过她指缝扣紧。不是推她过去是陪她。\\\\n"
            "她在他指间慢慢松开——跪到艾德里安面前。\\\\n"
            "他解开裤子——偏长、偏粗、麦色，龟头饱满圆润。她含住——第一次给黎恩之外的人。\\\\n"
            "嘴里的形状不一样。温度一样。脉搏不一样。\\\\n"
            "她闭上眼睛——脑海里不是艾德里安是黎恩的手在她手心里。\\\\n"
            "释放时她吞下去了。擦嘴角时黎恩把她拉起来——吻住她。\\\\n"
            "嘴里还有别人的味道——他不在意。他在意的是她做到了。\\\\n\\\\n"
            "占有欲确认：\\\\n"
            "事后她靠在黎恩胸口——嘴里还是别人的味道。但我是闭着眼睛的。想的是你的手。\\\\n"
            "黎恩收紧手臂——我知道。她抬头——脚、手、胸、嘴——都给出去了。\\\\n"
            "只剩——她没说完。黎恩低头——剩下的全部。留给我。她点头——全部。只给你。\\\\n\\\\n"
            "变量更新：shared_experience_level +25, possessiveness_intensity +35, seraphina_acceptance +15, adrian_closeness +20, trust_level +15, bond_intimacy +15\\\\n"
            "核心：★最后一个「第一次」——口交给别人。和艾德里安的手交+乳交形成三阶段弧线（手非初次但乳口均为初次）。\\\\n"
            "黎恩赢的、黎恩请求的——不是她输了是他选的人。结束后她确认：脚手胸嘴都给过了，剩下的全部只给黎恩。"
        ),
    ))'''

if insert_pos > 0:
    bp = bp[:insert_pos] + n28_n29_entries + bp[insert_pos:]
    print('✅ N28 + N29 entries inserted into build.py')
else:
    print('❌ Could not insert N28/N29')

# Also update the collect step labels if needed — the "2z" step now has 2 more entries
# but the auto-count handles it, so that's fine.

with open('C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py', 'w', encoding='utf-8') as f:
    f.write(bp)

print('✅ build_eldoria.py saved')

# ============================================================
# PART 2: Update 06_条目规划与格式.md
# ============================================================
with open('C:/Users/lx/Desktop/世界书/docs/06_条目规划与格式.md', 'r', encoding='utf-8') as f:
    doc6 = f.read()

# Update N28 title in mapping table if present
doc6 = doc6.replace('艾德里安的扑克——手与乳的初次', '艾德里安的扑克——乳的初次')
print('✅ 06_条目规划 N28 title updated')

with open('C:/Users/lx/Desktop/世界书/docs/06_条目规划与格式.md', 'w', encoding='utf-8') as f:
    f.write(doc6)

print('\n=== All sync operations complete ===')
