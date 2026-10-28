import os
import re

target_dir = r"d:\Siegfried\世界书\方案\第二部\主线与世界扩充方案"

categories = {
    "1. Traditional Chinese Medicine & Folk Remedies (中医药与民间土方偏方)": [
        (r"油纸|桐油纸", "油纸包装（中药铺/市井小吃包法，西幻应为油布/亚麻布袋/锡盒/羊皮纸）"),
        (r"生肌(药粉|草药|秘药)?", "武侠玄幻生肌散（去腐生肌中药，西幻应为外伤愈合药粉/创口特效药）"),
        (r"土方(子)?|偏方", "中式土方/偏方（中医药民间土法，西幻应为防晕小窍门/民间经验）"),
        (r"(保住|护住)心脉", "武侠护心脉（西幻应为稳住呼吸/维系生命）"),
        (r"内腑|内脏淤血|淤血(基本)?化尽", "武侠内伤化瘀（西幻应为内伤好转/淤青消退）"),
        (r"温养|调理(安神)?", "中医温养调理（西幻应为舒缓疲倦/调养体力）"),
        (r"雪菊茶", "中式养生雪菊茶（西幻应为高山菊草茶/洋甘菊草药茶）")
    ],
    "2. Maritime & Mechanical Anachronisms (航海器物与机械时代错位)": [
        (r"把着舵轮|掌舵轮|把舵轮", "平底内河驳船把舵轮（18世纪大帆船机械，中世纪内河篷船应为长木舵柄）"),
        (r"舵手大叔", "近现代/大帆船舵手（内河货船应为水手大叔/船员大叔）")
    ],
    "3. Chinese Feudal Society, Clothing & Peasantry (中式服饰与封建农村社会)": [
        (r"羊皮袄", "中国北方农村羊皮袄（西幻应为粗呢背心/羊毛短坎肩/厚斗篷）"),
        (r"佃农", "中国封建租佃制称谓（西幻领地庄园体系应为农工/庄园雇工/短工）"),
        (r"年轻少爷|娇贵少爷", "中国市井少爷称谓（西幻应为年轻老爷/贵族少爷/年轻贵族）")
    ],
    "4. Underworld, Taoist & Xianxia Tropes (中式阴司、道教玄学与江湖气)": [
        (r"催命(符|钟声)?", "阴司催命符/阎王索命（西幻应为死刑令/丧钟敲响）"),
        (r"打手", "中式市井打手（西幻应为雇佣武夫/街头混混/恶霸）"),
        (r"入城打点|打点规费", "中式封建衙门差役打点（西幻应为关卡苛税/入城杂费）")
    ],
    "5. Bureaucratic & Modern Chinese Terminology (旧官府公署与现代公文刑侦词)": [
        (r"公署|商业公署|商贸特许公署|特许公署", "旧中国衙署/现代公署（西幻应为市政厅商业处/行会总会所/商业行会）"),
        (r"水下暗网|排水暗网", "现代网络/刑侦暗网感（若指水下铁网应为水下铁栅/排水铁网）"),
        (r"做实", "现代公检法办案口头禅（办案做实证据，应为确立/完善/闭合）")
    ]
}

findings = {cat: [] for cat in categories}

for dirpath, _, filenames in os.walk(target_dir):
    for f in filenames:
        if f.endswith('.md'):
            fpath = os.path.join(dirpath, f)
            rel_path = os.path.relpath(fpath, target_dir)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines):
                line_str = line.strip()
                for cat, pat_list in categories.items():
                    for pat, note in pat_list:
                        m = re.search(pat, line_str)
                        if m:
                            findings[cat].append({
                                'file': rel_path,
                                'line': idx + 1,
                                'match': m.group(0),
                                'note': note,
                                'text': line_str
                            })

for cat, items in findings.items():
    print(f"=== {cat} (Count: {len(items)}) ===")
    seen = set()
    for item in items:
        key = (item['file'], item['line'])
        if key in seen:
            continue
        seen.add(key)
        print(f"  [{item['file']}:{item['line']}] 命中 '{item['match']}': {item['note']}")
        print(f"    原文: {item['text'][:130]}")
    print()
