#!/usr/bin/env python3
"""
恢复从 05_事件系统.md 丢失的 N1-N7, PN1-PN5, G1-G3 事件章节。
从备份 full_20260616_230654/05_事件系统.md 提取完整 YAML，
适配角色名称变更（尤西斯→乔治），插入当前 docs/05_事件系统.md。
"""
import re, os

BASE = r"C:\Users\lx\Desktop\世界书"
BACKUP = os.path.join(BASE, "backup", "full_20260616_230654", "05_事件系统.md")
CURRENT = os.path.join(BASE, "docs", "05_事件系统.md")

# 读取备份
with open(BACKUP, "r", encoding="utf-8") as f:
    backup_text = f.read()

# 读取当前
with open(CURRENT, "r", encoding="utf-8") as f:
    current_text = f.read()

# ============================================================
# 从备份中提取各章节
# ============================================================

def extract_section(text, start_marker, end_marker=None):
    """提取两个markdown标题之间的内容"""
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return None
    if end_marker:
        end_idx = text.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            return text[start_idx:]
        return text[start_idx:end_idx]
    return text[start_idx:]

# NTRS路线事件 (从 "## 四、NTRS路线事件" 到下一个 "## ")
ntrs_start = "## 四、NTRS路线事件"
# 找到下一个 ## 标题
ntrs_end_marker = "## 五、被动NTR路线事件"
ntrs_section = extract_section(backup_text, ntrs_start, ntrs_end_marker)

# 被动NTR路线事件
pntr_start = "## 五、被动NTR路线事件"
pntr_end_marker = "## 六、世界事件"
pntr_section = extract_section(backup_text, pntr_start, pntr_end_marker)

# 世界事件
world_start = "## 六、世界事件"
world_end_marker = "## 七、隐藏事件"
world_section = extract_section(backup_text, world_start, world_end_marker)

# 隐藏事件
hidden_start = "## 七、隐藏事件"
hidden_end_marker = "## 九、NSFW事件（详细版）"
hidden_section = extract_section(backup_text, hidden_start, hidden_end_marker)

# 通用事件 (## 十、新增通用事件)
general_start = "## 十、新增通用事件"
general_end_marker = "```yaml\n  事件触发的核心原则:"
general_section = extract_section(backup_text, general_start, general_end_marker)

# ============================================================
# 适配：角色名替换
# ============================================================
def adapt_names(text):
    """将旧角色名替换为当前项目使用的名称"""
    # 尤西斯 → 乔治
    text = text.replace("尤西斯·艾尔巴雷亚", "乔治")
    text = text.replace("尤西斯", "乔治")
    # 注意：不要替换 "jusis_closeness" 变量名（代码层面保持不变）
    # 但叙事文本中的角色名需要替换
    return text

# ============================================================
# 适配各章节
# ============================================================
if ntrs_section:
    ntrs_section = adapt_names(ntrs_section)
if pntr_section:
    pntr_section = adapt_names(pntr_section)
if world_section:
    world_section = adapt_names(world_section)
if hidden_section:
    hidden_section = adapt_names(hidden_section)
if general_section:
    general_section = adapt_names(general_section)

# ============================================================
# 插入到当前文件
# 插入位置：P16 (纯爱最后) 之后，S系列之前
# ============================================================
insert_marker = "## S系列、核心NSFW事件（S1-S30）"

insert_content = ""

# 1. NTRS路线事件
if ntrs_section:
    # 调整章节编号以适应当前结构
    # 当前已有：一、二、三、然后应该是四
    insert_content += ntrs_section.replace("## 四、NTRS路线事件", "## 四、NTRS路线事件（N1-N15）")
    insert_content += "\n\n---\n\n"

# 2. 被动NTR路线事件
if pntr_section:
    insert_content += pntr_section.replace("## 五、被动NTR路线事件", "## 五、被动NTR路线事件（PN1-PN10）")
    insert_content += "\n\n---\n\n"

# 3. 世界事件
if world_section:
    insert_content += world_section.replace("## 六、世界事件", "## 六、世界事件（W1-W8）")
    insert_content += "\n\n---\n\n"

# 4. 隐藏事件
if hidden_section:
    insert_content += hidden_section.replace("## 七、隐藏事件", "## 七、隐藏事件（H1-H5）")
    insert_content += "\n\n---\n\n"

# 5. 通用事件
if general_section:
    insert_content += general_section.replace("## 十、新增通用事件", "## 通用SFW事件（G1-G7）")
    insert_content += "\n\n---\n\n"

# 执行插入
if insert_marker in current_text:
    current_text = current_text.replace(
        insert_marker,
        insert_content + "\n" + insert_marker
    )
    print(f"✅ 已插入恢复内容 ({len(insert_content)} 字符)")
else:
    print(f"❌ 找不到插入标记: {insert_marker}")
    # 尝试找其他标记
    for line in current_text.split('\n'):
        if 'S系列' in line and 'NSFW' in line:
            print(f"  可能匹配: {line.strip()}")
    exit(1)

# 更新事件系统总览中的数量
# 原: "NTRS路线事件: 16个" (保持)
# 原: "被动NTR路线事件: 11个" (保持)

# ============================================================
# 写入
# ============================================================
with open(CURRENT, "w", encoding="utf-8") as f:
    f.write(current_text)

print("✅ 05_事件系统.md 已更新")

# ============================================================
# 验证
# ============================================================
with open(CURRENT, "r", encoding="utf-8") as f:
    verify = f.read()

checks = [
    ("N1 坦白之夜", "### 事件N1：坦白之夜"),
    ("N7 腐化仪式", "### 事件N7：腐化仪式"),
    ("PN1 第一次缺席", "### 事件PN1：第一次缺席"),
    ("PN5 堕落之夜", "### 事件PN5：堕落之夜"),
    ("G1 狩猎竞赛", "### 事件G1：狩猎竞赛"),
    ("G3 密林探索", "### 事件G3：密林探索"),
    ("W1-W8 世界事件", "W1: 影牙兽大规模袭击"),
    ("H1-H5 隐藏事件", "H1: 精灵王国的记忆"),
]

all_ok = True
for name, marker in checks:
    if marker in verify:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name} — 未找到 '{marker}'")
        all_ok = False

# 统计事件标题
event_headers = re.findall(r'^### 事件\w+：', verify, re.MULTILINE)
print(f"\n📊 事件标题总数: {len(event_headers)}")

if all_ok:
    print("\n🎉 所有恢复内容验证通过！")
else:
    print("\n⚠️ 部分内容验证失败，请检查")
