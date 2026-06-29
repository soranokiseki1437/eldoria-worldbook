#!/usr/bin/env python3
"""
艾玛"推眼镜→辫子"全局替换脚本
2026-06-30 · 替换体系见 方案/艾玛推眼镜替换体系.md
"""

import os
import re
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(BASE, 'docs', 'story')

# ── 替换规则（按优先级排序，先匹配长字符串）──
REPLACEMENTS = [
    # ═══ 推眼镜次数体系 ═══
    # 连推三次（先匹配更长的）
    ('连推了三次眼镜', '手指把辫梢攥了三次'),
    ('推了第三次眼镜', '攥住辫梢，指节收紧'),
    # 推两次
    ('推了两次眼镜', '手指穿过辫子，从发根梳到发尾'),
    # 推一次
    ('推了一次眼镜', '手指轻触辫尾'),
    # 推三下（变体）
    ('推了三下眼镜', '手指把辫梢攥了三下'),
    # 推两下（变体）
    ('推了两下眼镜', '手指穿过发丝，梳了两次'),
    # 推一下（变体）
    ('推了一下眼镜', '手指碰了碰辫尾'),

    # ═══ 单次推眼镜（放在次数之后，避免误匹配）═══
    ('又推了推眼镜', '又捻了捻辫梢'),
    ('推了推眼镜', '指尖捻了捻辫梢'),
    ('推推眼镜', '捻捻辫梢'),

    # ═══ 推眼镜 + 后续动作 ═══
    ('推眼镜的手精准', '碰辫梢的手指精准'),
    ('推眼镜的手', '碰辫梢的手指'),
    ('推眼镜，镜片反光', '指尖捻了捻辫梢，睫毛低垂'),
    ('推眼镜，薄荷蓝瞳', '指尖捻了捻辫梢，薄荷蓝瞳'),

    # ═══ 推眼镜的变体 ═══
    ('推了推镜框', '指尖碰了碰辫梢'),
    ('推一下眼镜', '碰一下辫梢'),
    ('推眼镜的频率', '捻辫梢的频率'),

    # ═══ 摘眼镜/戴眼镜 ═══
    ('推了推不存在的眼镜——推到鼻梁，没有镜框——笑了', '手指习惯性去碰辫梢，辫子是散开的指尖落了空，笑了'),
    ('推了推不存在的眼镜', '手指习惯性去碰辫梢落了空'),
    ('摘下眼镜放在工作台上——这是她的交付信号', '解开发辫让紫色长发散落肩上——这是她的交付信号'),
    ('摘下眼镜放在桌上——这是她的信号', '解开发辫让紫色长发散落——这是她的信号'),
    ('摘下眼镜放在工作台上', '解开发辫让紫色长发散落'),
    ('摘下眼镜放在桌上', '解开发辫让紫色长发散落'),
    ('摘下眼镜放在一旁', '解开发辫，让长发散落'),
    ('摘下眼镜，放在', '解开发辫，发绳放在'),
    ('摘掉眼镜', '解开发辫'),
    ('摘下眼镜', '解开发辫'),
    ('把眼镜戴回去', '重新编好辫子'),
    ('戴回眼镜', '重新编好辫子'),
    ('戴上眼镜', '重新编好辫子'),
    ('把眼镜放在', '把发绳放在'),

    # ═══ 眼镜后/镜片后 → 发丝间/睫毛下 ═══
    ('薄荷蓝瞳从镜片后', '薄荷蓝瞳从发丝间'),
    ('从镜片后', '从发丝间'),
    ('镜片后', '发丝间'),
    ('眼镜后', '发丝间'),

    # ═══ 镜片相关 ═══
    ('镜片反光，看不清她的眼睛', '睫毛低垂，看不清她的眼睛'),
    ('镜片反光遮住了', '睫毛低垂遮住了'),
    ('镜片反光', '睫毛低垂'),
    ('擦了擦镜片', '理了理发丝'),

    # ═══ 没有眼镜的描述 ═══
    ('没有镜片遮挡', '散发披肩'),
    ('没戴眼镜', '发辫散开'),
    ('眼镜被雾气糊到看不清', '散落的发丝被雾气沾到脸颊'),
    ('摘了眼镜用手背擦眼角', '擦了擦眼角，发丝从指缝滑落'),

    # ═══ 眼镜作为物品 ═══
    ('眼镜放在', '发绳放在'),
    ('她的眼镜', '她的辫梢发绳'),
    ('魔女推眼镜', '魔女捻辫梢'),
]

# ── 需要人工确认的标记 ──
WARN_PATTERNS = [
    (r'眼镜', '需确认：是否还有残留的"眼镜"引用'),
    (r'镜片', '需确认：是否还有残留的"镜片"引用'),
    (r'镜框', '需确认：是否还有残留的"镜框"引用'),
]


def replace_in_file(filepath):
    """对单个文件执行所有替换"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    for old, new in REPLACEMENTS:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes.append(f'  {old[:40]}... → {new[:40]}... ({count}处)')

    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'\n📝 {os.path.basename(filepath)}')
        for c in changes:
            print(c)

    return content


def check_residual(content, filepath):
    """检查是否有残留的眼镜引用"""
    warnings = []
    for pattern, msg in WARN_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            warnings.append(f'  ⚠️ {msg}: {len(matches)}处')
    if warnings:
        print(f'\n🔍 {os.path.basename(filepath)} 残留检查:')
        for w in warnings:
            print(w)


def main():
    txt_files = glob.glob(os.path.join(STORY_DIR, '*', '*.TXT'))
    txt_files.sort()

    total_changes = 0
    processed = 0

    for filepath in txt_files:
        # 只处理包含眼镜相关内容的文件
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if not any(kw in content for kw in ['推眼镜', '摘眼镜', '戴眼镜', '镜片', '眼镜', '戴上眼镜', '镜框']):
            continue

        new_content = replace_in_file(filepath)
        check_residual(new_content, filepath)
        processed += 1

    print(f'\n\n{"="*50}')
    print(f'处理文件数: {processed}')
    print(f'替换规则数: {len(REPLACEMENTS)}')


if __name__ == '__main__':
    main()
