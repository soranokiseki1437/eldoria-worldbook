#!/usr/bin/env python3
"""Add emotional stage labels (情感阶段) and 黎恩知情 fields to S-series NTRS events in 05_事件系统.md"""
import re

path = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Map of event markers -> stage label + 黎恩知情 to insert after "触发条件:" line
# Format: (search_string_after_trigger, insert_text)
labels = {
    # Phase 1 - Foundation (第12章)
    '事件: 隐奸——黎恩的窥视':
        '\n    情感阶段: A（习惯后的第一次隐奸——动机：她已习惯被注视，黎恩开始隐身观看）\n    黎恩知情: 是——黎恩隐身观看',

    # Phase 2 - Discovery (第13章)
    '事件: 玉足之戏——足交NTRS':
        '\n    情感阶段: B（发现吃醋有趣后的多人足交——动机：想看黎恩对不同第三者分别是什么表情）\n    黎恩知情: 是——黎恩坐对面注视',
    '事件: 丝袜之诱——角色各自的足部魅力':
        '\n    情感阶段: B（挑逗——动机：察觉黎恩的恋物偏好，主动利用它作为游戏）\n    黎恩知情: 是——黎恩在场，她借其他女性的丝袜为他足交',

    # Phase 2-3 - Hidden acts (第13章)
    '事件: S17 桌下之手——隐奸手交':
        '\n    情感阶段: B→C（公共场合的禁忌初探——动机：在同伴环绕中秘密服务黎恩的刺激）\n    黎恩知情: 是——黎恩在同一张桌子旁',
    '事件: S20 桌下之口——隐奸口交':
        '\n    情感阶段: B→C（隐奸升级——动机：公共场合口交的极致紧张与刺激）\n    黎恩知情: 是——黎恩在同一张桌子旁',

    # Phase 3 - One-on-One插入 (第14章)
    '事件: 艾德里安的赌局——浪子的真心':
        '\n    情感阶段: B→C（第一次插入第三者——动机：用赌局消解严肃性，试探插入的边界）\n    黎恩知情: 是——黎恩参与赌局后三人一起',
    '事件: 凯尔的第一次——学者的试炼':
        '\n    情感阶段: B→C（引导处女男——动机：她作为引导者掌控全程，享受"教"的权力感）\n    黎恩知情: 是——黎恩在场引导或注视',
    '事件: 雷恩的慰藉——骑士的温柔':
        '\n    情感阶段: B→C（战后温柔的第三插——动机：雷恩以疗伤般的郑重进入，她接受这种不同的温柔）\n    黎恩知情: 是——黎恩可选择见证/加入/给予空间',
    '事件: 圣光之镜——欲望的倒影':
        '\n    情感阶段: C→D（镜湖终极仪式——动机：不反射现实只反射欲望，她向所有人展示自己的渴望）\n    黎恩知情: 是——黎恩在场，镜湖串联所有人的欲望',

    # Phase 4 - Group (第15章前半)
    '事件: 群交——圣光之环':
        '\n    情感阶段: C（群交仪式——动机：放开享受，五层递进，终幕回到黎恩怀里）\n    黎恩知情: 是——黎恩坐环外注视，终幕占有她',
    '事件: 温泉混浴——银流河的夜晚':
        '\n    情感阶段: C（水中共享——动机：水汽为幕，第三者在水中触碰，她始终注视黎恩）\n    黎恩知情: 是——黎恩在场，水汽半掩',
    '事件: 野外暴露——圣光之森':
        '\n    情感阶段: C→D（圣光花粉催化——动机：花粉使圣光失控，衣服透明，第三者被圣光吸引）\n    黎恩知情: 是——黎恩在场，花田中三人或隐奸',
    '事件: 夜袭——黑暗中的访客':
        '\n    情感阶段: A/B（深夜不确定性——动机：门被推开，来者可能是黎恩/第三者/被黎恩撞见）\n    黎恩知情: 取决于分支——黎恩夜袭/第三者夜袭/黎恩撞见',

    # Phase 5 - Executor (第15章中段)
    '事件: S36 主动手交——NTRS阶段C→D':
        '\n    情感阶段: C→D（她成为执行者——动机：不再是被服务/被注视，是她主动走向第三者）\n    黎恩知情: 是——黎恩在旁注视，她是执行者',
    '事件: S37 主动口交——NTRS阶段D':
        '\n    情感阶段: D（熟练口交执行者——动机：从容自控的节奏，抬眼对黎恩笑，掌控感完全）\n    黎恩知情: 是——黎恩在旁注视',
    '事件: S38 主动隐奸（NTRS版）——NTRS阶段D':
        '\n    情感阶段: D（她设计整场游戏——动机：女上位支配第三者，对窗外的黎恩做胜利手势）\n    黎恩知情: 是——黎恩在窗外，是她邀请的观众',
    '事件: S39 桌下之手（给第三者）——NTRS隐奸手交':
        '\n    情感阶段: C→D（双重欺骗——动机：骗同伴、玩第三者、看黎恩——三重刺激同时）\n    黎恩知情: 是——黎恩在桌子对面注视',
    '事件: S40 桌下之口（给第三者）——NTRS隐奸口交':
        '\n    情感阶段: D（隐蔽口交给第三者——动机：利用精灵肺活量长时间含住，同伴讨论声中为第三者口交）\n    黎恩知情: 是——黎恩在桌子对面注视',
    '事件: S41 隐乳交（给第三者）——NTRS隐蔽乳交':
        '\n    情感阶段: D（月下乳交视觉盛宴——动机：她主动展示身体的使用方式，为黎恩提供完美视角）\n    黎恩知情: 是——黎恩在十步外树后，她选的位置刚好够他看到',
}

count = 0
for event_name, label_text in labels.items():
    # Find the event header and insert after the trigger line
    # Pattern: find event name, then find the next "触发条件:" line, insert after it
    event_pos = content.find(event_name)
    if event_pos == -1:
        print(f"WARNING: Could not find event: {event_name[:50]}")
        continue

    # Find the 触发条件 line after this event
    search_start = event_pos
    trigger_pos = content.find('触发条件:', search_start)
    if trigger_pos == -1:
        print(f"WARNING: No trigger found for: {event_name[:50]}")
        continue

    # Find end of trigger line (next \n)
    trigger_end = content.find('\n', trigger_pos)
    if trigger_end == -1:
        continue

    # Check if label already exists (skip if so)
    next_line_start = trigger_end + 1
    if content[next_line_start:next_line_start+5] == '    情感阶段':
        print(f"SKIP (already has label): {event_name[:50]}")
        continue

    # Insert the label after the trigger line
    content = content[:trigger_end] + label_text + content[trigger_end:]
    count += 1
    print(f"OK: {event_name[:60]}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone. Added labels to {count} events.")
