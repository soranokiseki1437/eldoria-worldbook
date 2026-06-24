#!/usr/bin/env python3
"""Add missing 性行为等级 and 情感阶段 metadata to N8-N15 and S-series events.
Also ensures 黎恩知情 is present on NTRS events that lack it."""

import re

PATH = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# ============================================================
# N8-N15: Add 性行为等级 and 情感阶段 after 触发条件
# ============================================================
n_metadata = {
    # '事件 name in YAML': (insert_after_trigger_text, search_marker)
    '事件: N8 劳拉的直率': (
        '\n    性行为等级: 4（手交——劳拉提供，黎恩注视）\n    情感阶段: C（同伴参与——动机：劳拉主动以手交表达诚意，她认可这种直率）\n    黎恩知情: 是——黎恩在旁注视',
    ),
    '事件: N9 与爱丽榭的禁忌': (
        '\n    性行为等级: 4+（手交+可能更多——禁忌的兄妹边界）\n    情感阶段: C（禁忌试探——动机：爱丽榭是黎恩的妹妹，这种禁忌本身就带着特殊的刺激和风险）\n    黎恩知情: 是——黎恩在场，面对禁忌的复杂性',
    ),
    '事件: N10 艾玛的仪式性共享': (
        '\n    性行为等级: 5+（足交+可能手交——魔法仪式包装）\n    情感阶段: C（学术包装的共享——动机：艾玛以研究为名接近，她用仪式回应，共享已日常化）\n    黎恩知情: 是——黎恩在仪式圈外观礼',
    ),
    '事件: N11 菲的精神见证': (
        '\n    性行为等级: 4+（手交+精神共鸣——菲以猎兵的方式体验）\n    情感阶段: C（精神见证——动机：菲不说废话只做，她以同样直接的方式回应，共享进入无言默契）\n    黎恩知情: 是——黎恩在旁，菲的精神共鸣也涉及他',
    ),
    '事件: N12 温泉NTRS版': (
        '\n    性行为等级: 9+（插入+群交——温泉多人共享）\n    情感阶段: C→D（温泉狂欢——动机：水面上下双重世界，她在众目睽睽下只注视黎恩）\n    黎恩知情: 是——黎恩在温泉中，水汽为幕',
    ),
    '事件: N13 胜利庆典后的失控': (
        '\n    性行为等级: 9+（插入——战斗后的释放式群交）\n    情感阶段: D（胜利释放——动机：战斗胜利后的生命力爆发，以身体庆祝活着）\n    黎恩知情: 是——黎恩是庆典中心，她在众人中最终回到他怀里',
    ),
    '事件: N15 终局抉择（NTRS版本）': (
        '\n    性行为等级: 9+（插入+群交——终极结局场景）\n    情感阶段: D（终局抉择——动机：所有体验汇聚于此刻，她做出最终决定）\n    黎恩知情: 是——黎恩面对终局抉择',
    ),
}

# S-series events that need 性行为等级 (have 情感阶段/黎恩知情 from labels script)
s_metadata_simple = {
    '事件: 隐奸——黎恩的窥视': '    性行为等级: 10（隐奸——她不知道黎恩在观看）\n',
    '事件: 群交——圣光之环': '    性行为等级: 9+（群交+插入+口交——五层递进仪式）\n',
    '事件: 温泉混浴——银流河的夜晚': '    性行为等级: 9+（插入——水中共享，第三者触碰）\n',
    '事件: 夜袭——黑暗中的访客': '    性行为等级: 9+（插入——深夜不确定性来访）\n',
    '事件: 野外暴露——圣光之森': '    性行为等级: 9+（插入+暴露——圣光花田三人或隐奸）\n',
    '事件: 艾德里安的赌局——浪子的真心': '    性行为等级: 9（插入——赌局中的三人）\n',
    '事件: 凯尔的第一次——学者的试炼': '    性行为等级: 9（插入——她引导处女男）\n',
    '事件: 雷恩的慰藉——骑士的温柔': '    性行为等级: 9（插入——战后温柔的第三插）\n',
    '事件: 圣光之镜——欲望的倒影': '    性行为等级: 9+（插入+群交——镜湖众人欲望交汇）\n',
    '事件: 玉足之戏——足交NTRS': '    性行为等级: 5（足交——多人足交，观察黎恩反应）\n',
    '事件: 丝袜之诱——角色各自的足部魅力': '    性行为等级: 5（足交——多角色丝袜足交）\n',
}

# S12-S15: Need 性行为等级 (already have 情感阶段 and 黎恩知情 from previous session)
s_foot_metadata = {
    '事件: S12 足部护理——银流河的温柔': '    性行为等级: 5（足交——银流河畔日常足交入口）\n',
    '事件: S13 温泉夜——水汽中的足交': '    性行为等级: 5（足交——水中足交，浮力改变触感）\n',
    '事件: S14 月光下的誓言——心木树下的足交': '    性行为等级: 5（足交——心木树下仪式性足交）\n',
    '事件: S15 晨露中的裸足——黎明的足交': '    性行为等级: 5（足交——清晨醒来第一件事）\n',
}

# S16-S30 events that need 性行为等级 (most have simple structure)
s_late_metadata = {
    '事件: S16 银流河畔的初次手交': '    性行为等级: 4（手交——Seraphina温柔学习）\n',
    '事件: S17 桌下之手——隐奸手交': '    性行为等级: 4（手交——公共场合隐蔽手交）\n',
    '事件: S18 艾玛的手交实证研究': '    性行为等级: 4（手交——艾玛学术包装）\n',
    '事件: S19 初次的唇——口交入门': '    性行为等级: 6（口交——Seraphina口交入门）\n',
    '事件: S20 桌下之口——隐奸口交': '    性行为等级: 6（口交——公共场合隐蔽口交）\n',
    '事件: S21 玲的口交游戏': '    性行为等级: 6（口交——玲小恶魔式口交）\n',
    '事件: S22 圣光之谷——乳交': '    性行为等级: 7（乳交——Seraphina双乳包裹）\n',
    '事件: S23 骑士的胸怀——劳拉的乳交': '    性行为等级: 7（乳交——劳拉剑士的胸）\n',
    '事件: S24 大腿之间——腿交': '    性行为等级: 8（腿交——Seraphina双腿并拢缝隙）\n',
    '事件: S25 菲的直接本番': '    性行为等级: 9（插入——菲不废话直接做）\n',
    '事件: S26 亚莉莎的傲娇本番': '    性行为等级: 9（插入——傲娇千金的本番）\n',
    '事件: S27 玲的游戏本番': '    性行为等级: 9（插入——玲的捉弄式本番）\n',
    '事件: S28 劳拉的骑士本番': '    性行为等级: 9（插入——劳拉卸甲后的本番）\n',
    '事件: S29 密林即兴——站立后入': '    性行为等级: 9+（插入+暴露——密林站立后入）\n',
    '事件: S30 镜湖倒影——欲望本番': '    性行为等级: 9（插入——湖面交合倒影）\n',
}

# Process N8-N15
for event_name, (insert_text,) in n_metadata.items():
    pos = content.find(event_name)
    if pos == -1:
        print(f"WARNING: N-series not found: {event_name[:60]}")
        continue

    # Find trigger line end
    trigger_pos = content.find('触发条件:', pos)
    if trigger_pos == -1 or trigger_pos > pos + 500:
        print(f"WARNING: No trigger found for: {event_name[:60]}")
        continue

    trigger_end = content.find('\n', trigger_pos)
    if trigger_end == -1:
        continue

    # Check if 性行为等级 already exists nearby
    next_lines = content[trigger_end:trigger_end+200]
    if '性行为等级:' in next_lines:
        print(f"SKIP (already has 性行为等级): {event_name[:60]}")
        continue

    content = content[:trigger_end] + insert_text + content[trigger_end:]
    changes.append(f"  N-series metadata: {event_name[:60]}")
    print(f"OK: {event_name[:60]}")

# Process S-series simple (insert after 触发条件)
all_s = {**s_metadata_simple, **s_foot_metadata, **s_late_metadata}
for event_name, insert_text in all_s.items():
    pos = content.find(event_name)
    if pos == -1:
        print(f"WARNING: S-series not found: {event_name[:60]}")
        continue

    # Find trigger line
    trigger_pos = content.find('触发条件:', pos)
    if trigger_pos == -1 or trigger_pos > pos + 500:
        print(f"WARNING: No trigger found for: {event_name[:60]}")
        continue

    trigger_end = content.find('\n', trigger_pos)
    if trigger_end == -1:
        continue

    # Check if 性行为等级 already exists nearby
    next_lines = content[trigger_end:trigger_end+200]
    if '性行为等级:' in next_lines:
        print(f"SKIP (already has 性行为等级): {event_name[:60]}")
        continue

    content = content[:trigger_end] + '\n' + insert_text.rstrip('\n') + content[trigger_end:]
    changes.append(f"  S-series 性行为等级: {event_name[:60]}")
    print(f"OK: {event_name[:60]}")

# ============================================================
# Also add 情感阶段 to S17, S20 (they have it but let's verify S16-S30)
# Missing 情感阶段 for S16, S18, S19, S21-S30
# ============================================================
s_emotional = {
    '事件: S16 银流河畔的初次手交': '    情感阶段: 通用（三线分支——纯爱: "第一次交付" / NTRS: "如果是别人的手..." / 被动NTR: "缺席后的补偿"）\n',
    '事件: S18 艾玛的手交实证研究': '    情感阶段: 通用（学术包装——魔女借研究之名行亲密之实）\n',
    '事件: S19 初次的唇——口交入门': '    情感阶段: 通用（三线分支——纯爱: "初次的唇" / NTRS: "如果是别人的唇..." / 被动NTR: "比较的唇"）\n',
    '事件: S21 玲的口交游戏': '    情感阶段: 通用（小恶魔游戏——玲把口交当捉弄，自己先沦陷）\n',
    '事件: S22 圣光之谷——乳交': '    情感阶段: 通用（三线分支——纯爱: "这些光只为你" / NTRS: "这些光会暗吗" / 被动NTR: "光还在吗"）\n',
    '事件: S23 骑士的胸怀——劳拉的乳交': '    情感阶段: 通用（卸甲——剑士的胸用于战斗之外）\n',
    '事件: S24 大腿之间——腿交': '    情感阶段: 通用（三线分支——双腿合拢的柔嫩缝隙）\n',
    '事件: S25 菲的直接本番': '    情感阶段: 通用（猎兵直接——不废话想做就做）\n',
    '事件: S26 亚莉莎的傲娇本番': '    情感阶段: 通用（傲娇反差——嘴上说不要身体最诚实）\n',
    '事件: S27 玲的游戏本番': '    情感阶段: 通用（游戏心态——把性交当捉弄最后先沦陷）\n',
    '事件: S28 劳拉的骑士本番': '    情感阶段: 通用（卸甲仪式——盔甲卸下如卸下防御）\n',
    '事件: S29 密林即兴——站立后入': '    情感阶段: 通用（暴露刺激——一手扶树一手捂嘴）\n',
    '事件: S30 镜湖倒影——欲望本番': '    情感阶段: 通用（镜中倒影——湖面反射两人交合）\n',
}

for event_name, insert_text in s_emotional.items():
    pos = content.find(event_name)
    if pos == -1:
        print(f"WARNING: S-emotional not found: {event_name[:60]}")
        continue

    # Check if 情感阶段 already exists nearby
    nearby = content[pos:pos+600]
    if '情感阶段:' in nearby:
        print(f"SKIP (already has 情感阶段): {event_name[:60]}")
        continue

    # Find 性行为等级 line (which we just added) or 触发条件
    trigger_pos = content.find('触发条件:', pos)
    if trigger_pos == -1 or trigger_pos > pos + 500:
        continue

    # Find end of trigger line
    trigger_end = content.find('\n', trigger_pos)
    if trigger_end == -1:
        continue

    # Insert after trigger (before 性行为等级)
    content = content[:trigger_end] + '\n' + insert_text.rstrip('\n') + content[trigger_end:]
    changes.append(f"  S-series 情感阶段: {event_name[:60]}")
    print(f"OK emotional: {event_name[:60]}")

# ============================================================
# P13-P16: Add 性行为等级
# ============================================================
p_nsfw = {
    '事件: P13 契约之夜（纯爱NSFW）': '    性行为等级: 9（插入——守护者契约完成，灵肉合一）\n',
    '事件: P14 温泉的清晨（纯爱NSFW）': '    性行为等级: 9（插入——温泉后的私密时光）\n',
    '事件: P15 鬼之圣光交融（纯爱NSFW）': '    性行为等级: 9+（插入+力量共鸣——鬼之力与圣光的身体交融）\n',
    '事件: P16 足下的誓言（纯爱NSFW）': '    性行为等级: 5（足交——纯爱足交，200年首次交付）\n',
}

for event_name, insert_text in p_nsfw.items():
    pos = content.find(event_name)
    if pos == -1:
        print(f"WARNING: P-NSFW not found: {event_name[:60]}")
        continue

    # Check if 性行为等级 already exists
    nearby = content[pos:pos+600]
    if '性行为等级:' in nearby:
        print(f"SKIP (already has): {event_name[:60]}")
        continue

    # Find trigger line
    trigger_pos = content.find('触发条件:', pos)
    if trigger_pos == -1 or trigger_pos > pos + 500:
        continue
    trigger_end = content.find('\n', trigger_pos)
    if trigger_end == -1:
        continue

    content = content[:trigger_end] + '\n' + insert_text.rstrip('\n') + content[trigger_end:]
    changes.append(f"  P-series 性行为等级: {event_name[:60]}")
    print(f"OK: {event_name[:60]}")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal changes: {len(changes)}")
for c in changes:
    print(c)
