# -*- coding: utf-8 -*-
import os
import re
import glob

BASE_DIR = r"方案\第二部\主线与世界扩充方案\分阶段详规"

cn_nums = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
def int_to_cn(num):
    if num <= 10:
        return cn_nums[num]
    elif num < 20:
        return "十" + (cn_nums[num % 10] if num % 10 != 0 else "")
    elif num < 100:
        tens = num // 10
        rem = num % 10
        return cn_nums[tens] + "十" + (cn_nums[rem] if rem != 0 else "")
    return str(num)

cn_to_int = {int_to_cn(i): i for i in range(1, 69)}

def count_cn(text):
    return len(re.findall(r'[\u4e00-\u9fa5]', text))

def count_non_ws(text):
    return len(re.findall(r'\S', text))

files = glob.glob(os.path.join(BASE_DIR, "*", "阶段*.md"))
files = sorted(files, key=lambda p: cn_to_int[re.match(r"阶段([一二三四五六七八九十]+)_", os.path.basename(p)).group(1)])

act_stats = {}
all_data = []

for f in files:
    fname = os.path.basename(f)
    act_dir = os.path.basename(os.path.dirname(f))
    m = re.match(r"阶段([一二三四五六七八九十]+)_(.*?)详规\.md", fname)
    st_cn = m.group(1)
    st_num = cn_to_int[st_cn]
    st_title = m.group(2)
    
    with open(f, "r", encoding="utf-8") as fp:
        c = fp.read()
    
    cn_total = count_cn(c)
    sec2_m = re.search(r"## 二、[^\n]*\n(.*?)(?=\n## 三、|\Z)", c, re.DOTALL)
    cn_sec2 = count_cn(sec2_m.group(1)) if sec2_m else cn_total
    non_ws_total = count_non_ws(c)
    
    item = {
        "num": st_num,
        "cn_str": st_cn,
        "title": st_title,
        "act": act_dir,
        "cn_total": cn_total,
        "cn_sec2": cn_sec2,
        "non_ws": non_ws_total,
        "fname": fname
    }
    all_data.append(item)
    
    if act_dir not in act_stats:
        act_stats[act_dir] = []
    act_stats[act_dir].append(item)

print(f"Total stages counted: {len(all_data)}")
for a_dir, items in act_stats.items():
    a_cn = sum(it["cn_total"] for it in items)
    a_sec2 = sum(it["cn_sec2"] for it in items)
    print(f"\n### {a_dir} (共 {len(items)} 阶段，纯汉字合计: {a_cn:,}，演进正文: {a_sec2:,})")
    for it in items:
        print(f"| **阶段{it['cn_str']}** | `{it['fname']}` | {it['cn_total']:,} 字 | {it['cn_sec2']:,} 字 | {it['non_ws']:,} 字符 |")

total_cn = sum(it["cn_total"] for it in all_data)
total_sec2 = sum(it["cn_sec2"] for it in all_data)
avg_cn = total_cn / len(all_data)
avg_sec2 = total_sec2 / len(all_data)
max_cn_item = max(all_data, key=lambda x: x["cn_total"])
min_cn_item = min(all_data, key=lambda x: x["cn_total"])
over_7k = [x for x in all_data if x["cn_sec2"] >= 7000]

print("\n" + "="*50)
print(f"全书 14 幕 68 阶段汇总统计：")
print(f"全书纯汉字总字数: {total_cn:,} 字")
print(f"情境演进正文纯汉字: {total_sec2:,} 字")
print(f"平均单阶段纯汉字: {avg_cn:.1f} 字（正文: {avg_sec2:.1f} 字）")
print(f"单阶段纯汉字最大: 阶段{max_cn_item['cn_str']} ({max_cn_item['cn_total']:,} 字) - {max_cn_item['title']}")
print(f"单阶段纯汉字最小: 阶段{min_cn_item['cn_str']} ({min_cn_item['cn_total']:,} 字) - {min_cn_item['title']}")
print(f"演进正文 >= 7000 字阶段数: {len(over_7k)}")
for x in over_7k:
    print(f"  - 阶段{x['cn_str']}: 正文 {x['cn_sec2']:,} 字 (总字数: {x['cn_total']:,}) - {x['title']}")
print("="*50)

