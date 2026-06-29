#!/usr/bin/env python
"""Audit proposal draft chapters for 3 rules"""
import re, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp = os.path.join(BASE, '方案', '艾玛×矮人兄弟NSFW新增方案.md')

with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all code blocks that are chapter drafts (contain 情境:)
blocks = re.findall(r'```\n(.*?)```', content, re.DOTALL)
chapter_blocks = [b for b in blocks if '情境:' in b and 'NSFW:' in b]

total_dashes = 0
total_negs = 0

for i, block in enumerate(chapter_blocks):
    # Extract chapter name
    name_m = re.search(r'名称: (.+)', block)
    name = name_m.group(1) if name_m else f'Chapter {i+1}'

    # Count dashes in 情境/核心/章节任务/章节终止条件
    sections = re.findall(r'(情境:.+?)(?=核心:|章节任务:|$)', block, re.DOTALL)
    core = re.findall(r'(核心:.+?)(?=章节任务:|$)', block, re.DOTALL)
    task = re.findall(r'(章节任务:.+?)(?=章节终止条件:|$)', block, re.DOTALL)
    cond = re.findall(r'(章节终止条件:.+)$', block, re.DOTALL)

    relevant = ''.join(sections + core + task + cond)
    dashes = len(re.findall(r'——', relevant))

    # Check negations
    negs = re.findall(r'不是[^，。\n]{0,30}是|没[^，。\n]{{0,20}}是|非[^，。\n]{{0,10}}是', relevant)

    # Check 章节任务 format
    task_text = task[0] if task else ''
    task_dashes = len(re.findall(r'——', task_text))
    periods_in_task = task_text.count('。')

    # Check 章节终止条件 format
    cond_text = cond[0] if cond else ''
    cond_dashes = len(re.findall(r'——', cond_text))
    cond_negs = re.findall(r'不|没|非', cond_text)

    print(f'【{name}】')
    print(f'  情境/核心/任务/条件中 破折号: {dashes}处')
    if negs:
        short = [n[:30] for n in negs[:5]]
        print(f'  否定句式: {len(negs)}处 — {short}')
    if task_dashes > 0:
        print(f'  ⚠️ 章节任务含{task_dashes}处破折号(禁止)')
    if periods_in_task > 1:
        print(f'  ⚠️ 章节任务含{periods_in_task}个句号(应为1句精炼陈述句)')
    if cond_dashes > 0:
        print(f'  ⚠️ 章节终止条件含{cond_dashes}处破折号(禁止)')
    if cond_negs:
        print(f'  ⚠️ 章节终止条件含否定词: {cond_negs[:5]}')
    total_dashes += dashes
    total_negs += len(negs)
    print()

print(f'总计: {total_dashes}处破折号, {total_negs}处否定句式')
print(f'目标: 0处破折号(情境/核心/任务/条件), 0处否定句式')
