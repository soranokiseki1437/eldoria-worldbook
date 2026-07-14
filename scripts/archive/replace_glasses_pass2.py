#!/usr/bin/env python3
"""Second-pass cleanup: catch residual 推眼镜/摘眼镜/镜片 patterns"""
import os, re, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(BASE, 'docs', 'story')

REPLACEMENTS_2 = [
    # standalone 推眼镜 (verb only, missed by first pass)
    ('艾玛推眼镜：', '艾玛指尖捻了捻辫梢：'),
    ('艾玛推眼镜，', '艾玛指尖捻了捻辫梢，'),
    ('艾玛推眼镜。', '艾玛指尖捻了捻辫梢。'),
    ('艾玛推眼镜\n', '艾玛指尖捻了捻辫梢\n'),
    ('她推眼镜，', '她指尖捻了捻辫梢，'),
    ('她推眼镜。', '她指尖捻了捻辫梢。'),
    ('推眼镜，', '指尖捻了捻辫梢，'),
    ('推眼镜。', '指尖捻了捻辫梢。'),
    ('推眼镜:', '指尖捻了捻辫梢:'),
    ('推眼镜；', '指尖捻了捻辫梢；'),
    ('艾玛推眼镜"', '艾玛指尖捻了捻辫梢"'),
    ('她推眼镜"', '她指尖捻了捻辫梢"'),
    # 没有推眼镜
    ('没有推眼镜，', '没有碰辫梢，'),
    ('没有推眼镜。', '没有碰辫梢。'),
    # 摘了眼镜
    ('摘了眼镜也站着', '解了发辫也站着'),
    ('摘了眼镜', '解了发辫'),
    ('摘眼镜放桌上', '解开发辫让长发散落'),
    ('摘眼镜放', '发绳放在'),
    ('摘眼镜是交付信号', '解开发辫是交付信号'),
    ('摘眼镜告白', '解开发辫告白'),
    ('摘眼镜亲吻', '解开发辫亲吻'),
    ('摘眼镜吻他', '解开发辫吻他'),
    ('摘眼镜，', '解开发辫，'),
    ('摘眼镜。', '解开发辫。'),
    # 镜片
    ('透过镜片看着', '透过散落的发丝看着'),
    ('镜片摘掉后', '发辫解开后'),
    # 镜框
    ('按住艾玛的镜框', '按住艾玛的辫梢'),
    ('艾玛的镜框', '艾玛的辫梢'),
    # 推三次眼镜
    ('推三次眼镜', '手指把辫梢攥了三次'),
    ('连推三次眼镜', '手指把辫梢攥了三次'),
    # 主动脱衣摘眼镜
    ('主动脱衣摘眼镜', '主动解辫脱衣'),
    # 习惯性推眼镜碰手
    ('习惯性地去推眼镜，碰到', '习惯性地去碰辫梢，碰到'),
    # 艾玛推眼镜: (with colon, single character variant)
    ('推眼镜。\n', '指尖捻了捻辫梢。\n'),
    # 残留的 "她的眼镜"
    ('她的眼镜', '她的辫梢发绳'),
]

def main():
    txt_files = glob.glob(os.path.join(STORY_DIR, '*', '*.TXT'))
    txt_files.sort()
    total = 0
    for fp in txt_files:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        changed = False
        for old, new in REPLACEMENTS_2:
            if old in content:
                content = content.replace(old, new)
                changed = True
        if changed:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            total += 1

    # Final check
    remaining = 0
    for fp in txt_files:
        with open(fp, 'r', encoding='utf-8') as f:
            c = f.read()
        # Only count non-凯尔/乔治/玲 (they wear real glasses)
        lines = c.split('\n')
        for ln in lines:
            if ('眼镜' in ln or '镜片' in ln or '镜框' in ln) and '凯尔' not in ln and '乔治' not in ln and '玲' not in ln and '玲与' not in ln:
                remaining += 1
    print(f'第二遍处理: {total} 文件')
    print(f'残留眼镜引用: {remaining} 行 (不含凯尔/乔治/玲)')

if __name__ == '__main__':
    main()
