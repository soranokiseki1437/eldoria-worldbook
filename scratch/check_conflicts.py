import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docs2_dir = r'd:\Siegfried\世界书\docs2'
id_to_name = {}
name_to_id = {}

for sub in ['character', 'npc', 'location', 'creature', 'magic', 'world']:
    dirpath = os.path.join(docs2_dir, sub)
    for f in glob.glob(os.path.join(dirpath, '*.TXT')):
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        id_m = re.search(r'^ID:\s*(\S+)', c, re.M)
        name_m = re.search(r'^名称:\s*(\S+)', c, re.M)
        if id_m and name_m:
            cid = id_m.group(1)
            cname = name_m.group(1)
            id_to_name[cid] = cname
            base_fname = os.path.splitext(os.path.basename(f))[0]
            name_to_id[cname] = cid
            name_to_id[base_fname] = cid

plan_dir = r'd:\Siegfried\世界书\方案\第二部'

print("=== 1. 检查方案文档中引用的 ID 与 docs2 实体名称是否一致 ===")
pattern = re.compile(r'([^\s`（(、,，:：*]{2,15})\s*[`(（]?((CHR|NPC|LOC|CRT|MAG|WLD)_D2_\d+)[`)）]?')

conflicts = []
for root, dirs, files in os.walk(plan_dir):
    for f in files:
        if not f.endswith('.md'):
            continue
        fpath = os.path.join(root, f)
        relpath = os.path.relpath(fpath, plan_dir)
        with open(fpath, 'r', encoding='utf-8') as fp:
            for idx, line in enumerate(fp, 1):
                for m in pattern.finditer(line):
                    text_name = m.group(1).strip()
                    ref_id = m.group(2).strip()
                    if ref_id in id_to_name:
                        actual_name = id_to_name[ref_id]
                        # check match
                        matched = False
                        if text_name in actual_name or actual_name in text_name:
                            matched = True
                        for part in re.split(r'[·\s]', actual_name):
                            if part and (part in text_name or text_name in part):
                                matched = True
                        if not matched:
                            conflicts.append((relpath, idx, text_name, ref_id, actual_name, line.strip()))
                    else:
                        conflicts.append((relpath, idx, text_name, ref_id, 'UNKNOWN_ID', line.strip()))

for rel, idx, tname, rid, aname, line in conflicts:
    print(f"[{rel}:{idx}] 引用矛盾: 文中写作 '{tname}' 但标注 ID 为 {rid} (docs2 中 {rid} 实际是 '{aname}')\n   -> 原文: {line}\n")

print(f"共发现 {len(conflicts)} 处 ID 引用矛盾/错配\n")
