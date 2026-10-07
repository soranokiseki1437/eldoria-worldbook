import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. 提取 docs2 中所有角色的年龄设定
docs2_dir = r'd:\Siegfried\世界书\docs2'
plan_dir = r'd:\Siegfried\世界书\方案\第二部'

docs_ages = {}
for sub in ['character', 'npc']:
    d = os.path.join(docs2_dir, sub)
    for f in glob.glob(os.path.join(d, '*.TXT')):
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        name_m = re.search(r'^(?:名称|角色名)[:：]\s*(\S+)', c, re.M)
        # search for age in content
        age_m = re.search(r'年龄[:：]\s*([^\n,，;；()（）]+)', c)
        if not age_m:
            age_m = re.search(r'(\d+)\s*岁', c)
        if name_m:
            name = name_m.group(1)
            base = os.path.splitext(os.path.basename(f))[0]
            age = age_m.group(1).strip() if age_m else '未知'
            docs_ages[base] = age
            docs_ages[name] = age

print("=== docs2 中的年龄基准 ===")
for k, v in sorted(docs_ages.items()):
    if len(k) < 10:
        print(f"  {k}: {v}")

print("\n=== 检查方案文件中与 docs2 年龄不一致之处 ===")
# Search in plan_dir for pattern like "角色名.*?[（(]?(\d+)岁"
characters_to_check = ['卢卡斯', '莫尔茨', '朱利安', '雷恩', '劳拉', '黎恩', '菲娜', '艾德里安', '乔治', '凯尔', '菲', '亚莉莎', '罗恩', '艾玛', '法林', '奥蕾莉亚', '加尔', '玲', '爱丽榭', '亚尔缇娜', '科林', '汉斯', '提米', '阿达尔伯特', '克莱门特三世', '埃德蒙', '瓦卢瓦', '瓦尔特', '艾琳娜', '玛格丽特', '戈德弗里', '维克托', '亨里克']

age_pattern = re.compile(r'([\u4e00-\u9fa5]{2,6})[^\n\d]{0,8}?[（(]?(\d{1,3})\s*岁[)）]?')

age_conflicts = []
for root, dirs, files in os.walk(plan_dir):
    for f in files:
        if not f.endswith('.md'): continue
        fpath = os.path.join(root, f)
        relpath = os.path.relpath(fpath, plan_dir)
        with open(fpath, 'r', encoding='utf-8') as fp:
            for idx, line in enumerate(fp, 1):
                for m in age_pattern.finditer(line):
                    char = m.group(1).strip()
                    age = m.group(2).strip()
                    for target in characters_to_check:
                        if target in char:
                            # compare with docs_ages
                            expected = None
                            for dk in docs_ages:
                                if target in dk:
                                    # extract digits from expected
                                    digits = re.findall(r'\d+', docs_ages[dk])
                                    if digits:
                                        expected = digits[0]
                                        break
                            if expected and age != expected:
                                age_conflicts.append((relpath, idx, target, age, expected, line.strip()))

print(f"发现 {len(age_conflicts)} 处年龄冲突:")
for rel, idx, target, age, expected, line in age_conflicts:
    print(f"  [{rel}:{idx}] {target}: 方案中写为 {age}岁，但 docs2 设定为 {expected}岁\n     -> {line}")
