#!/usr/bin/env python3
"""逐角色穷举所有章节中的cm身高/阴茎尺寸，对照_character_attributes.txt权威设定"""
import os, re

STORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "story")

# 权威设定：{角色关键词: {身高cm, 阴茎cm(可选), 别名列表}}
TRUTH = {
    "Seraphina":  {"h": 168, "aliases": ["Seraphina", "菲娜", "炽天使"]},
    "黎恩":       {"h": 178, "p": 18,  "aliases": ["黎恩", "舒华泽"]},
    "奥蕾莉亚":   {"h": 178, "aliases": ["奥蕾莉亚", "黄金罗刹", "罗刹"]},
    "劳拉":       {"h": 170, "aliases": ["劳拉", "亚尔赛德"]},
    "亚尔缇娜":   {"h": 142, "aliases": ["亚尔缇娜", "黑兔"]},
    "艾玛":       {"h": 159, "aliases": ["艾玛", "米尔斯汀"]},
    "菲":         {"h": 150, "aliases": ["菲", "克劳塞尔"]},
    "凯尔":       {"h": 175, "p": 13.5, "aliases": ["凯尔"]},
    "亚莉莎":     {"h": 165, "aliases": ["亚莉莎", "莱恩福尔特"]},
    "爱丽榭":     {"h": 158, "aliases": ["爱丽榭"]},
    "玲":         {"h": 145, "aliases": ["玲", "布莱特"]},
    "艾德里安":   {"h": 182, "p": 17, "aliases": ["艾德里安"]},
    "雷恩":       {"h": 188, "p": 15.5, "aliases": ["雷恩"]},
    "乔治":       {"h": 172, "p": 15, "aliases": ["乔治", "诺姆"]},
    "多尔金":     {"h": 148, "p": 13, "aliases": ["多尔金"]},
    "哈根":       {"h": 142, "p": 14, "aliases": ["哈根"]},
    "法林":       {"h": 139, "p": 14.5, "aliases": ["法林"]},
    "罗恩":       {"h": 183, "p": 16, "aliases": ["罗恩"], "h_fullmoon": 205, "p_fullmoon": 21},
    "月语者":     {"h": 185, "p": 18, "aliases": ["月语者"], "h_fullmoon": 215, "p_fullmoon": 22},
    "加尔":       {"h": 175, "p": 20, "aliases": ["加尔"]},
    "牛头人":     {"h": 364, "p": 22, "aliases": ["牛头人"]},
    "幻猿":       {"h": 277, "p": 14, "aliases": ["幻猿"]},
    "Thalion":    {"h": 185, "aliases": ["Thalion"]},
    "普通狼人":   {"p_norm": 18, "p_full": 22, "aliases": ["普通狼人"]},
    "普通蜥蜴人": {"p": 19, "aliases": ["普通蜥蜴人"]},
}

def find_cm_numbers(text):
    """返回[(数字, 后续5字上下文)]"""
    results = []
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*cm', text):
        ctx = text[m.end():m.end()+10]
        results.append((float(m.group(1)), ctx))
    return results

def main():
    errors = []
    for root, dirs, files in os.walk(STORY):
        for fn in files:
            if not fn.endswith(".TXT") or fn.startswith("_"):
                continue
            fpath = os.path.join(root, fn)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            # 找到所有cm
            cm_nums = find_cm_numbers(content)
            if not cm_nums:
                continue

            # 对每个cm，判断最近的角色名
            for val, ctx in cm_nums:
                # 在cm前后200字内找角色名
                for m in re.finditer(r'(\d+(?:\.\d+)?)\s*cm', content):
                    if float(m.group(1)) != val:
                        continue
                    pos = m.start()
                    window = content[max(0,pos-300):pos+100]
                    # 找最近的角色
                    found_char = None
                    for cname, cinfo in TRUTH.items():
                        for alias in cinfo["aliases"]:
                            if alias in window:
                                found_char = cname
                                break
                        if found_char:
                            break
                    if not found_char:
                        continue

                    cinfo = TRUTH[found_char]
                    # 判断是身高还是阴茎（cm前有"约"或cm后有"的"等→身高；cm前有肉棒/阴茎→阴茎）
                    before = content[max(0,pos-30):pos]
                    is_penis = any(w in before for w in ["肉棒", "阴茎", "鸡巴", "茎身", "勃起"])

                    if is_penis:
                        expected = cinfo.get("p")
                        # 满月特殊
                        if "满月" in window:
                            expected = cinfo.get("p_fullmoon", expected)
                    else:
                        expected = cinfo.get("h")
                        if "满月" in window:
                            expected = cinfo.get("h_fullmoon", expected)

                    if expected is not None and val != expected:
                        rel = os.path.relpath(fpath, STORY)
                        errors.append(f"  {rel}\n    {found_char}: {val}cm → 应为{expected}cm | ...{content[max(0,pos-40):pos+40].strip()}...")

    if errors:
        print(f"发现 {len(errors)} 处身高/尺寸错误:\n")
        for e in errors:
            print(e)
    else:
        print("✅ 所有角色身高/阴茎尺寸均与设定一致，零错误")

if __name__ == "__main__":
    main()
