#!/usr/bin/env python3
"""Comprehensive threshold recovery using original threshold data.

Reads the original threshold analysis, parses event→original_value mappings,
applies the CORRECT single-pass reduction, and fixes 05_事件系统.md.

Strategy: For each event name, find its trigger condition in the file,
extract the current (cascaded) threshold value, compute what the correct
reduced value should be, and replace it.
"""

import re

# ============================================================
# CORRECT SINGLE-PASS REDUCTION MAPS
# ============================================================
CORRECT = {
    'trust': {
        100: 90, 95: 80, 90: 75, 88: 72, 85: 70,
        80: 65, 75: 60, 70: 55, 65: 50, 60: 45,
        55: 40, 50: 38, 45: 35, 40: 30, 35: 28,
        30: 22, 25: 20,
    },
    'bond': {
        100: 90, 90: 80, 85: 75, 82: 72, 80: 70,
        75: 65, 70: 58, 65: 55, 60: 50, 55: 48,
        50: 42, 45: 38, 40: 32, 35: 28, 30: 22, 20: 15,
    },
    'acceptance': {
        100: 76, 95: 76, 90: 72, 85: 68, 80: 64,
        75: 60, 70: 56, 65: 52, 60: 48, 50: 40,
        45: 32, 40: 32, 30: 25,
    },
    'abandon': {
        90: 80, 70: 60, 60: 50, 50: 40, 45: 35,
        40: 30, 35: 25, 30: 20, 20: 15,
    },
    'despair': {
        85: 75, 80: 70, 70: 60, 60: 50, 50: 40,
        40: 30, 30: 25, 25: 20, 20: 15, 15: 10,
    },
    'shared': {
        90: 82, 80: 72, 70: 62, 60: 52, 50: 45,
        45: 38, 40: 35, 35: 28, 30: 25, 25: 20,
        20: 18, 15: 12, 10: 8,
    },
    'exploration': {
        80: 75, 70: 65, 60: 55, 50: 45, 40: 35,
        30: 25, 25: 20, 10: 8,
    },
    'thalion': {
        95: 85, 90: 80, 85: 75, 80: 70, 70: 60,
        60: 50, 55: 45, 50: 40, 40: 30, 30: 20,
    },
    'possess': {
        90: 82, 85: 75, 80: 70, 75: 60, 70: 58,
    },
    'corruption': {},  # Unchanged
    'ntrs_awakened': {},  # Binary, unchanged
}

# ============================================================
# ORIGINAL THRESHOLDS BY EVENT (from transcript analysis)
# Format: event_name_substring → {var: original_value}
# ============================================================

# Pure Love Route
PURE_LOVE_ORIG = {
    '林间空地的苏醒': {},
    '第一次与影牙兽': {},
    '心木废墟': {},
    '低语林地的幻影': {},
    'VII班同伴的到达（亚莉莎）': {'exploration': 10},
    'VII班同伴的到达（劳拉与乔治）': {},
    'VII班同伴的到达（艾玛与菲）': {},
    '森林的庆典': {},
    '古老先灵的低语': {'trust': 30},
    '黑兔的观察': {'abandon': 30, 'trust': None},  # abandon < 30
    '流浪商人的来访': {'exploration': 30},
    '圣殿骑士的踪迹': {'trust': 50},
    '学者的研究': {},
    '义妹的到来': {},
    '杀戮之天使': {},

    # P series
    '深夜的火炉边对话': {'trust': 40, 'bond': 20},
    '鬼之力失控后的安抚': {'trust': 50, 'bond': 30},
    '第一次约会': {'trust': 60, 'bond': 40},
    '守护者的契约': {'trust': 85, 'bond': 70},
    'VII班的"正式介绍"': {'trust': 80, 'bond': 60},
    '心木废墟的净化仪式前置准备': {'trust': 80, 'bond': None, 'exploration': 50},
    '与Thalion的第一次正面战斗': {'trust': 75, 'thalion': 30},
    '温泉事件（纯爱版本）': {'trust': 75},
    '守护夜——并肩作战到黎明': {'trust': 80},
    '古老先灵的启示——森林意志与黎恩的作用': {'trust': 85, 'bond': 70, 'exploration': 60},
    '终极战斗准备——与Thalion的最终对质前夕': {'trust': 90, 'bond': 85},
    '终局抉择（纯爱版本）': {'trust': 90, 'bond': 85},
    'P13 契约之夜': {'trust': 85, 'bond': 75},
    'P14 温泉的清晨': {'trust': 80, 'bond': 75},
    'P15 鬼之圣光交融': {'trust': 88, 'bond': 82},
    'P16 足下的誓言': {'trust': 90, 'bond': 85},

    # G series
    '狩猎竞赛': {'corruption': 20},
    '剑术训练': {'trust': 30},
    '密林探索': {'trust': 60, 'exploration': 50},
    '篝火故事会': {'trust': 35},
    '雷恩的晨间仪式': {'trust': 25},
    '凯尔的精灵语课堂': {'trust': 30},
    '艾德里安的拍卖会': {'trust': 30},

    # W series
    '影牙兽大规模袭击': {'corruption': 15},
    '心木树的净化仪式': {'exploration': 70},
    '银流河的净化与恢复': {},
    '腐化区域的意外扩张': {'corruption': 45},
    '古老先灵的第二次对话': {'trust': 60, 'exploration': 60},
    '"森林意志"的反应': {},
    'VII班同伴的"日常互动"': {},
    '"雾帷边缘"的异象': {'exploration': 80},

    # H series
    '精灵王国的记忆': {'exploration': 40},
    '鬼之力与圣光完全共鸣': {'trust': 100, 'bond': 100},
    '腐化低语者的"真相"': {'exploration': 50},
    '"如果"': {'trust': 100, 'bond': 100},
    'VII班同伴的"秘密对话"': {},

    # R series
    '鬼之力的低语': {'trust': 40},
    '太刀与八叶': {},
    '来自帝国的信': {'exploration': 25},
    '灰之骑神的记忆': {'exploration': 40},
    '独占欲': {'ntrs_awakened': 100},
    '黎恩的第一次': {'trust': 70, 'bond': 70},
    '嫉妒之火': {},
    '夜色中的契约': {'trust': 80, 'bond': 80},
}

# NTRS Route
NTRS_ORIG = {
    '坦白之夜': {'trust': 50, 'bond': 30},
    '边界协商': {'acceptance': 30},
    '第一次见证——NTRS情感阶段A': {'acceptance': 40, 'shared': 10},
    'N3.5 第二次见证': {'acceptance': 45, 'shared': 15},
    '乔治的注视——NTRS情感阶段B': {'acceptance': 50},
    'N4.5 挑逗的萌芽': {'shared': 25},
    '亚莉莎的发现': {'acceptance': 60},
    'N5.5 第一次双人共享': {'acceptance': 65, 'shared': 35},
    '多人共享之夜——NTRS情感阶段C': {'acceptance': 70, 'shared': 50},
    '腐化仪式——NTRS情感阶段C': {'acceptance': 80, 'shared': 80, 'thalion': 50},
    'N8 劳拉的直率': {'acceptance': 65},
    'N9 与爱丽榭的禁忌': {'acceptance': 75},
    'N10 艾玛的仪式性共享': {'acceptance': 80},
    'N11 菲的精神见证': {'acceptance': 85},
    'N12 温泉NTRS版': {'acceptance': 90, 'shared': 70},
    'N13 胜利庆典后的失控': {'shared': 80},
    'N14 终极确认之夜': {'acceptance': 95, 'shared': 90},
    'N15 终局抉择（NTRS版本）': {},

    # NTRS S-series
    '隐奸——黎恩的窥视': {'trust': 55, 'acceptance': 40},
    '群交——圣光之环': {'acceptance': 70, 'shared': 50},
    '温泉混浴——银流河的夜晚': {'trust': 40},
    '夜袭——黑暗中的访客': {'trust': 50},
    '野外暴露——圣光之森': {'trust': 65, 'acceptance': 60},
    '艾德里安的赌局': {'trust': 55, 'acceptance': None},
    '凯尔的第一次': {'trust': 60, 'acceptance': 60},
    '雷恩的慰藉': {'trust': 55, 'acceptance': None},
    '圣光之镜——欲望的倒影': {'trust': 65, 'acceptance': None},
    '玉足之戏': {'acceptance': 60, 'shared': 40},
    '丝袜之诱': {'acceptance': 50, 'shared': 30},
}

# Passive NTR
PASSIVE_ORIG = {
    '第一次缺席': {'abandon': 20, 'trust': None},  # trust < 45
    'Thalion的第一次诱惑': {'abandon': 40, 'despair': 50, 'thalion': 40},
    '乔治的支持': {'abandon': 50, 'despair': 60},
    '亚莉莎的对比': {'abandon': 50, 'despair': 60},
    '堕落之夜——被动NTR情感阶段B': {'abandon': 70, 'despair': 80, 'thalion': 60},
    'PN6 重新争取': {'abandon': 70},
    'PN7 乔治的担忧与劝说': {},
    'PN8 与亚莉莎的坦诚对话': {},
    'PN9 与Thalion的最终战斗': {},
    'PN10 终局抉择': {},
    'PN11 堕落之夜的细节': {'abandon': 90, 'despair': 85},
    'PN12 重新争取后的重逢': {},
    'PN13 耳边的低语': {'despair': 70, 'thalion': 55},
    'PN14 再次找上门': {'despair': 80, 'thalion': 70},
    'PN15 趁他睡着': {'despair': 60, 'thalion': 80},
    'PN16 主动口交': {'thalion': 85, 'despair': None},  # despair <= 50
    'PN17 野外暴露': {'thalion': 90},
    'PN18 主动邀约': {'thalion': 95},
}

# S-series general thresholds
S_SERIES_ORIG = {
    'S12 足部护理': {'trust': 30},
    'S13 温泉夜': {'trust': 40, 'shared': 30},
    'S14 月光下的誓言': {'trust': 55, 'shared': 45, 'bond': 50},
    'S15 晨露中的裸足': {'shared': 35},
    'S16 银流河畔的初次手交': {'trust': 65, 'bond': 50},
    'S17 桌下之手': {},
    'S18 艾玛的手交实证研究': {},
    'S19 初次的唇': {'trust': 70, 'bond': 60},
    'S20 桌下之口': {},
    'S21 玲的口交游戏': {},
    'S22 圣光之谷': {'trust': 75, 'bond': 70},
    'S23 骑士的胸怀': {},
    'S24 大腿之间': {'trust': 60, 'bond': 50},
    'S25 菲的直接本番': {},
    'S26 亚莉莎的傲娇本番': {},
    'S27 玲的游戏本番': {},
    'S28 劳拉的骑士本番': {},
    'S29 密林即兴': {'trust': 65},
    'S30 镜湖倒影': {'trust': 70},
    'S31 圣光的初触': {'trust': 50, 'bond': 65},
    'S32 银色的探索': {'trust': 55},
    'S33 圣光之泉': {'trust': 75, 'bond': 70},
    'S36 主动手交': {'acceptance': 75, 'shared': 60},
    'S37 主动口交': {'acceptance': 85},
    'S38 主动隐奸': {'acceptance': 90},
    'S39 桌下之手（给第三者）': {'acceptance': 80},
    'S40 桌下之口（给第三者）': {'acceptance': 85},
    'S41 隐乳交（给第三者）': {'acceptance': 90},
}

# C-series
C_SERIES_ORIG = {
    '玲的裸足': {'acceptance': 50},
    '亚莉莎的蕾丝': {'acceptance': 50},
    '菲的裸足': {'acceptance': 50},
    '劳拉的白袜': {'acceptance': 50},
    '艾玛的吊带袜': {'acceptance': 50},
    '亚尔缇娜的任务': {'acceptance': 50},
}

# ============================================================
# Apply fixes
# ============================================================

PATH = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

def fix_event_threshold(event_key, var_name, orig_val):
    """Find an event by name key and fix its threshold for var_name."""
    global content, changes

    # Search for the event within YAML (事件: key) to avoid chapter mapping table
    yaml_key = f'事件: {event_key}'
    pos = content.find(yaml_key)
    if pos == -1:
        # Fall back to header search
        pos = content.find(event_key)
        if pos == -1:
            return False

    correct_val = CORRECT[var_name].get(orig_val)
    if correct_val is None:
        return False

    # Find the trigger condition section (look up to 1500 chars forward)
    region = content[pos:pos+1500]

    # Match any value for this variable
    var_patterns = {
        'trust': r'trust(?:_level)?',
        'bond': r'bond(?:_level)?',
        'acceptance': r'(?:seraphina_)?acceptance',
        'abandon': r'abandon(?:ment(?:_count)?)?',
        'despair': r'(?:seraphina_)?despair',
        'shared': r'shared(?:_experience(?:_level)?)?',
        'exploration': r'exploration(?:_progress)?',
        'thalion': r'thalions?_influence',
        'possess': r'possess(?:iveness(?:_intensity)?)?',
    }

    pattern = var_patterns.get(var_name, var_name)
    match = re.search(rf'({pattern})\s*>=\s*(\d+)', region)
    if not match:
        match = re.search(rf'({pattern})\s*<\s*(\d+)', region)

    if match:
        old_val = int(match.group(2))
        if old_val != correct_val:
            start = pos + match.start(2)
            end = pos + match.end(2)
            content = content[:start] + str(correct_val) + content[end:]
            changes.append(f"  {event_key[:50]}: {var_name} {old_val}→{correct_val} (was orig {orig_val})")
            return True
    return False

# Process all event groups
all_events = {
    **PURE_LOVE_ORIG, **NTRS_ORIG, **PASSIVE_ORIG,
    **S_SERIES_ORIG, **C_SERIES_ORIG,
}

for event_key, vars_dict in all_events.items():
    for var_name, orig_val in vars_dict.items():
        if orig_val is not None:
            fix_event_threshold(event_key, var_name, orig_val)

# ============================================================
# Also fix character goodwill thresholds
# C1-C6: 好感 thresholds
# ============================================================
goodwill_fixes = [
    ('玲的裸足', r'玲好感\s*>=\s*(\d+)', {35: 30}),
    ('亚莉莎的蕾丝', r'亚莉莎好感\s*>=\s*(\d+)', {40: 35}),
    ('菲的裸足', r'菲好感\s*>=\s*(\d+)', {35: 30}),
    ('劳拉的白袜', r'劳拉好感\s*>=\s*(\d+)', {45: 40}),
    ('艾玛的吊带袜', r'艾玛好感\s*>=\s*(\d+)', {40: 35}),
    ('亚尔缇娜的任务', r'亚尔缇娜好感\s*>=\s*(\d+)', {40: 35}),
]

for event_key, pattern, mapping in goodwill_fixes:
    pos = content.find(event_key)
    if pos == -1:
        continue
    region = content[pos:pos+800]
    match = re.search(pattern, region)
    if match:
        old_val = int(match.group(1))
        if old_val in mapping:
            correct = mapping[old_val]
            start = pos + match.start(1)
            end = pos + match.end(1)
            content = content[:start] + str(correct) + content[end:]
            changes.append(f"  Goodwill: {event_key[:30]} {old_val}→{correct}")

# Fix S-series character goodwill thresholds
s_char_fixes = [
    ('艾玛的手交实证研究', r'艾玛好感\s*>=\s*(\d+)', 50, 45),
    ('玲的口交游戏', r'玲好感\s*>=\s*(\d+)', 55, 50),
    ('菲的直接本番', r'菲好感\s*>=\s*(\d+)', 60, 55),
    ('亚莉莎的傲娇本番', r'亚莉莎好感\s*>=\s*(\d+)', 60, 55),
    ('劳拉的骑士本番', r'劳拉好感\s*>=\s*(\d+)', 60, 55),
    ('骑士的胸怀——劳拉的乳交', r'劳拉好感\s*>=\s*(\d+)', 55, 50),
]

for event_key, pattern, old_target, new_target in s_char_fixes:
    pos = content.find(event_key)
    if pos == -1:
        continue
    region = content[pos:pos+800]
    match = re.search(pattern, region)
    if match:
        old_val = int(match.group(1))
        if old_val == old_target or old_val < old_target - 20:  # cascaded
            correct = new_target
            start = pos + match.start(1)
            end = pos + match.end(1)
            content = content[:start] + str(correct) + content[end:]
            changes.append(f"  S-char: {event_key[:30]} {old_val}→{correct}")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Total fixes: {len(changes)}")
for c in changes:
    print(c)
