#!/usr/bin/env python3
"""Add N3.5 and N5.5 entries to build_eldoria.py"""
import re

with open('C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove corrupted line
content = content.replace(
    '\ndef build(dry_run=False):    return entries\n\n\ndef build(dry_run=False):',
    '\n\ndef build(dry_run=False):'
)

# 2. Add new entry function after get_uid189_200_entries
new_function = '''
def get_uid201_202_entries():
    """NTRS路线桥接事件: N3.5 第二次见证(阶段A->B过渡) + N5.5 第一次双人共享(阶段B->C过渡)"""
    entries = []

    # === uid 201: N3.5 第二次见证——习惯的萌芽 ===
    entries.append(make_entry(
        uid=201,
        keys=["N3.5", "第二次见证", "习惯的萌芽", "NTRS情感过渡", "阶段A到B"],
        comment="【NTRS桥接事件】N3.5 第二次见证——从紧张到习惯的过渡",
        content=(
            "NTRS情感阶段A→B过渡——第二次见证：习惯的萌芽\\n\\n"
            "同一个森林深处的空地。但这一次——月光不那么冷了。\\n"
            "腐化低语者再次出现。Seraphina解开上衣——她的手指没有发抖。\\n"
            "她没有回头看黎恩。不是因为她不需要确认——是因为她已经知道了答案。\\n"
            "低语者的爪子覆上她的乳房——冰冷如上次。她的身体微微绷紧——\\n"
            "但不是抗拒。是身体对冷触的自然反应，不是恐惧。\\n"
            "她的呼吸保持平稳。琥珀色眼睛看着低语者——\\n"
            "不是寻求许可，不是紧张。是平静的注视。\\\"你可以继续。\\\"\\n"
            "低语者的爪子沿着乳缘滑动——比上次更缓慢，更探索。\\n"
            "她的圣光微微亮起——不是防御，是本能的温度调节。\\n"
            "金色暖光包裹着冰冷的爪子。她没有颤抖。没有咬唇。她只是——接受了。\\n"
            "结束后她穿好衣服，走向黎恩。步伐比N3时稳得多。\\n"
            "\\\"我没事。\\\"她说——不是问'你还好吗'。是告诉他她没事。\\n"
            "\\\"没有上次那么可怕了。\\\"她小声说。\\n"
            "\\\"你觉得——\\\"她抬头，琥珀色眼睛很认真，\\\"如果换成乔治——会不会不一样？\\\"\\n"
            "不是挑逗。是好奇。是第一次主动思考——'如果是别人呢？'\\n\\n"
            "占有欲确认:\\n"
            "黎恩进入她时——她全程睁着眼睛看他。不像N3那样闭上眼睛松一口气——\\n"
            "这一次她在体验。\\\"你是我的。\\\"\\\"我是你的。\\\"和N3一样的词，\\n"
            "但语气不同。不是证明。是确认——像呼吸一样自然。\\n\\n"
            "核心: N3和N4之间的桥接——从'紧张试探'到'发现游戏有趣'的过渡。\\n"
            "她不再害怕。但还没开始享受。她只是在确认——\\n"
            "'这件事可以存在。我们可以继续。'"
        ),
        order=12035,
        keysecondary=["NTRS", "第二次见证", "习惯萌芽", "Seraphina放松", "阶段A到B"],
        probability=95,
        selective=True,
        position=1,
        depth=4
    ))

    # === uid 202: N5.5 第一次双人共享——桥接单人到多人 ===
    entries.append(make_entry(
        uid=202,
        keys=["N5.5", "第一次双人共享", "NTRS桥接", "阶段B到C", "双人"],
        comment="【NTRS桥接事件】N5.5 第一次双人共享——从一对一到多人的过渡",
        content=(
            "NTRS情感阶段B→C过渡——第一次双人共享：同时引导两人\\n\\n"
            "篝火已烧到只剩暗红色的炭。Seraphina坐在中间——\\n"
            "左边是乔治，右边是凯尔。两人都紧张——\\n"
            "乔治的手在膝上握拳，凯尔又在推眼镜。\\n"
            "Seraphina的视线在两人之间转了一圈——然后看向黎恩。\\n"
            "不是寻求许可——是让他知道她在想什么。\\n"
            "\\\"我想——试一下。\\\"她说。第一次不是问句。\\n\\n"
            "她先转向乔治——右手放在他的腰带扣上。动作从容——\\n"
            "这不是她的第一次手交了。乔治的呼吸在她握住时卡住。\\n"
            "\\\"放松——\\\"她的声音是安抚的，但眼神带着笑意。\\n"
            "然后是凯尔——她的左手同时覆上他的大腿。身体微微旋转——\\n"
            "圣光在双腕处同时亮起，像是某种奇异的节奏器——\\n"
            "让两只手保持着不同的节奏。一边快，一边慢。一边紧，一边松。\\n"
            "她在同时处理两个男人——琥珀色眼睛在两个目标之间切换，\\n"
            "带着某种近乎专业的专注。然后她转回头——看向黎恩。\\n"
            "那个微笑。他认得的——N4时第一次出现的笑。\\n"
            "但现在不是调皮。是得意。\\n"
            "\\\"你看——同时两个也可以。\\\"\\n"
            "她的左右手同时加快了节奏——乔治后仰闭上眼，凯尔用手背捂住嘴。\\n"
            "她看黎恩——不眨眼。\\\"下次——还可以更多吗？\\\"\\n"
            "不是挑逗。是认真地问——她在规划下一次，而她需要黎恩知道。\\n\\n"
            "占有欲确认:\\n"
            "两人离开后。她留在原地——手腕有些酸。\\n"
            "黎恩走向她时她站起来。\\\"比想象的累——\\\"她活动手腕，\\n"
            "但表情是满意的，\\\"但是——好玩。\\\"\\n"
            "她靠进他怀里——不像N3那样寻求确认，不像N4那样炫耀调皮。\\n"
            "是一种平静的归属感。\\\"谢谢你让我试。\\\"\\n\\n"
            "核心: N5到N6的桥接——从'和一个人做'到'和多人做'的中间步骤。\\n"
            "她第一次同时服务两个第三者——发现'同时两个并不比一个难'。\\n"
            "这是N6（多人共享）的前置——给了她信心：如果两个可以，四个也可以。"
        ),
        order=12036,
        keysecondary=["NTRS", "双人共享", "第一次双人", "乔治", "凯尔", "阶段B到C"],
        probability=95,
        selective=True,
        position=1,
        depth=4
    ))

    return entries
'''

# Insert after get_uid189_200_entries's return entries
content = content.replace(
    "    return entries\n\n\ndef build(dry_run=False):",
    "    return entries\n" + new_function + "\ndef build(dry_run=False):"
)

# 3. Update merge line
content = content.replace(
    "+ new_entries_189_200",
    "+ new_entries_189_200 + new_entries_201_202"
)

# 4. Add call to get new entries
content = content.replace(
    'print(f"[step 2j] 新增 uid 189-200 (NTRS+PN进阶): {len(new_entries_189_200)} 条")\n',
    'print(f"[step 2j] 新增 uid 189-200 (NTRS+PN进阶): {len(new_entries_189_200)} 条")\n\n    # 2k. 获取 uid 201-202 NTRS桥接事件\n    new_entries_201_202 = get_uid201_202_entries()\n    print(f"[step 2k] 新增 uid 201-202 (NTRS桥接 N3.5+N5.5): {len(new_entries_201_202)} 条")\n'
)

with open('C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done. Added N3.5 (uid 201) and N5.5 (uid 202) to build_eldoria.py")
