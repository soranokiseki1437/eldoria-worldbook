import os

target_dir = r"d:\Siegfried\世界书\方案\第二部\主线与世界扩充方案\前十幕大调查工作区"

# 1. Update 04
f04 = os.path.join(target_dir, "04_第五幕与第六幕穿透调查与逐阶段对账.md")
with open(f04, "r", encoding="utf-8") as fp:
    c04 = fp.read()

c04 = c04.replace("* *(注：阶段十七关于视频连线与海港情调的微调分镜已写入阶段详规本体，此处不再重复列入方案)*\n", "")
c04 = c04.replace('坚决否定“亚尔缇娜战术壳接送”等削弱角色自主性与战术壳严肃感的方案；明确法尔肯位于**王国正北部**（绝非西边），将动线重构为：', '明确法尔肯位于**王国正北部**，将动线重构为：')
c04 = c04.replace("*(注：边境伯身边的书吏随从在后续若需具体称呼，应基于剧作工具人处理，docs2未设独立卡)*", "")

with open(f04, "w", encoding="utf-8") as fp:
    fp.write(c04)
print("Updated 04")

# 2. Update 08
f08 = os.path.join(target_dir, "08_前十幕全景硬伤与逻辑病灶综合诊断清单.md")
with open(f08, "r", encoding="utf-8") as fp:
    c08 = fp.read()

c08 = c08.replace('坚决否定“亚尔缇娜战术壳接送”等削弱角色自主性的方案；', "")
c08 = c08.replace("（已在详规微调落地）", "")

with open(f08, "w", encoding="utf-8") as fp:
    fp.write(c08)
print("Updated 08")

# 3. Update 09
f09 = os.path.join(target_dir, "09_前十幕重塑方案与情节增删改建议指南.md")
with open(f09, "r", encoding="utf-8") as fp:
    c09 = fp.read()

c09 = c09.replace('坚决否定“战术壳接送”等削弱角色自主性的方案；', "")

with open(f09, "w", encoding="utf-8") as fp:
    fp.write(c09)
print("Updated 09")

# 4. Update Summary Report
f_sum = os.path.join(target_dir, "前十幕大调查总结报告.md")
with open(f_sum, "r", encoding="utf-8") as fp:
    c_sum = fp.read()

c_sum = c_sum.replace('坚决否定“战术壳接送”等削弱角色自主性的方案；', "")
c_sum = c_sum.replace("（已在详规微调落地）", "")
c_sum = c_sum.replace("（已微调落地）", "")

with open(f_sum, "w", encoding="utf-8") as fp:
    fp.write(c_sum)
print("Updated Summary Report")
