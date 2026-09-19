# -*- coding: utf-8 -*-
import re

FORBIDDEN_WORDS = [
    "肉刃", "肉棒", "肉茎", "昂扬", "甬道", "花径", "花心", "白浊", "深射",
    "深喉", "双乳", "雪乳", "乳沟", "胸脯", "解衣", "解甲", "温存", "避人耳目",
    "夹磨", "破身", "服侍", "侍奉", "伺候", "娇喘", "娇躯", "柔荑",
    "抽吸", "水渍", "浪子", "胯下", "云雨", "风月", "春情", "艳色", "大口吞咽", "灌入",
    "全数", "尽数", "嗓音微哑", "微哑", "招供", "窗棂", "推拉",
    "惊惶", "惊恐", "恐慌", "恐惧", "吓得", "吓了一跳", "大受惊吓", "提到了嗓子眼",
    "雷鼓", "心跳如擂鼓", "死死", "哆嗦", "发抖", "颤抖", "受困被迫", "被迫",
    "被动承受", "怯生生", "浑身一僵", "连一声咳嗽都没敢"
]

def validate_text(text, label=""):
    errors = []
    for w in FORBIDDEN_WORDS:
        matches = re.findall(rf'.{{0,12}}{w}.{{0,12}}', text)
        if matches:
            for m in matches:
                errors.append(f"[{label}] Forbidden word '{w}': ...{m.strip()}...")
    return errors

def count_chinese(text):
    return len(re.findall(r'[\u4e00-\u9fa5]', text))

