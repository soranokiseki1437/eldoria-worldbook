import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docs2_dir = r'd:\Siegfried\世界书\docs2'
plan_dir = r'd:\Siegfried\世界书\方案\第二部'

# 1. 军队世俗词（第二部严禁）
military_terms = [
    '军队', '军官', '青年将领', '军纪', '军令', '军粮', '武将', 
    '退伍军人', '将校', '官军', '军士', '守军', '官兵', '行军打仗', '兵营'
]

# 2. 古风话本词（严禁）
ancient_terms = [
    '娇躯', '未着片缕', '软若无骨', '大开敞怀', '一览无余', 
    '神魂颠倒', '满面春风', '春潮', '泄火', '泄泄火', '小的', 
    '做牛做马', '粉身碎骨', '求大人恩典', '好好疼你', '有志气', '恶霸', '恶少',
    '盘缠', '银票', '碎银', '文钱', '掌柜', '衙门', '官府'
]

# 3. 称谓标签代词（旁白严禁作为主语代称）
label_pronouns = [
    '娇妻', '小妻子', '爱侣'
]

def scan_dir(target_dir, label):
    print(f"\n=================== 扫描 {label} ===================")
    findings = []
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if not (f.endswith('.TXT') or f.endswith('.md')): continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, target_dir)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines, 1):
                # check military
                for term in military_terms:
                    # check if it's in a rule/forbidden statement like '严禁“军队”'
                    if term in line:
                        if any(fbd in line for fbd in ['严禁', '禁止', '绝无', '避免', '绝不', '不得出现', '不使用', '替换为', '死刑']):
                            continue
                        findings.append((rel, idx, '军队词汇', term, line.strip()))
                # check ancient
                for term in ancient_terms:
                    if term in line:
                        if any(fbd in line for fbd in ['严禁', '禁止', '绝无', '避免', '绝不', '不得出现', '不使用', '替换为', '死刑']):
                            continue
                        findings.append((rel, idx, '古风词汇', term, line.strip()))
                # check label pronouns
                for term in label_pronouns:
                    if term in line:
                        if any(fbd in line for fbd in ['严禁', '禁止', '绝无', '避免', '绝不', '不得出现', '不使用', '替换为', '死刑']):
                            continue
                        findings.append((rel, idx, '违规代称', term, line.strip()))
    return findings

f1 = scan_dir(docs2_dir, 'docs2 实体库')
print(f"docs2 发现违规词: {len(f1)} 处")
for rel, idx, cat, term, l in f1:
    print(f"  [{rel}:{idx}] [{cat}: {term}] -> {l[:100]}")

f2 = scan_dir(plan_dir, '方案/第二部 方案库')
print(f"\n方案/第二部 发现违规词: {len(f2)} 处")
# print summary of categories
cats = {}
for rel, idx, cat, term, l in f2:
    key = f"{cat}: {term}"
    cats[key] = cats.get(key, 0) + 1
for k, count in sorted(cats.items(), key=lambda x: -x[1])[:20]:
    print(f"  {k} -> {count} 次")

# Sample some distinct issues
print("\n部分典型案例文本:")
for rel, idx, cat, term, l in f2[:15]:
    print(f"  [{rel}:{idx}] [{cat}: {term}] -> {l[:100]}")
