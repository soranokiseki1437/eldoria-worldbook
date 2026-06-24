"""Fix all 菲娜 银发→粉发 across authoritative source files."""
import re

files_to_fix = [
    'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md',
    'C:/Users/lx/Desktop/世界书/scripts/build_eldoria.py',
]

total = 0
for filepath in files_to_fix:
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()

    original = c
    count = 0

    # ── 05_事件系统.md fixes ──
    if '05_事件系统' in filepath:
        # 1. N29: "银发垂落在肩胛骨之间" → "粉发垂落在肩胛骨之间"
        c, n = re.subn(r'(她坐在身后不远处——看着她的背影。)银发(垂落)', r'\1粉发\2', c); count += n

        # 2. N31: "手指轻轻插进银发" → "粉发"
        c, n = re.subn(r'(他的手终于落在她后脑——手指轻轻插进)银发', r'\1粉发', c); count += n

        # 3. N57 标题 "树后的银发" → "树后的粉发"
        c, n = re.subn(r'树后的银发', '树后的粉发', c); count += n

        # 4. N57-like event D阶段: "银发在艾德里安膝间晃动" (菲娜)
        c, n = re.subn(r'(桌布褶皱缝隙间——)银发(在艾德里安膝间晃动)', r'\1粉发\2', c); count += n

        # 5. N57 凯尔: "月光下银发垂腰" (菲娜)
        c, n = re.subn(r'(她跨坐凯尔。月光下)银发(垂腰)', r'\1粉发\2', c); count += n

        # 6. N58: "额头抵额头银发垂落笼罩两人" (菲娜)
        c, n = re.subn(r'(额头抵额头)银发(垂落笼罩两人)', r'\1粉发\2', c); count += n

        # 7. 被动NTR: "银发有些乱" (菲娜 PN event)
        c, n = re.subn(r'(里面只有一件薄睡裙。)银发(有些乱)', r'\1粉发\2', c); count += n

        # 8. 07示例: "她的银发在月光下"
        c, n = re.subn(r'(Seraphina坐在你身边，\n\s+)她的银发(在月光下泛着微光)', r'\1她的粉发\2', c); count += n

        # 9. 被动NTR: "银发滑过指尖" (his fingers touch HER face)
        c, n = re.subn(r'(他的手指触碰她的脸颊——)银发(滑过指尖)', r'\1粉发\2', c); count += n

        # 10. D阶段雷恩: "银发散肩" (菲娜)
        c, n = re.subn(r'(她靠墙)银发(散肩低头看他)', r'\1粉发\2', c); count += n

    # ── build_eldoria.py fixes ──
    elif 'build_eldoria' in filepath:
        # 1. "银发在月光下泛着淡粉" → "粉发在月光下泛着淡粉"
        c, n = re.subn(r'(Seraphina全身赤裸，)银发(在月光下泛着淡粉)', r'\1粉发\2', c); count += n

        # 2. "她的银发垂在裸露的背上" → "她的粉发垂在裸露的背上"
        c, n = re.subn(r'(Thalion站在Seraphina身后——她的)银发(垂在裸露的背上)', r'\1粉发\2', c); count += n

        # 3. N29: "银发垂落在肩胛骨之间" (build.py has \\n line breaks)
        c, n = re.subn(r'(看着她的背影。)银发(垂落在肩胛骨之间)', r'\1粉发\2', c); count += n

    if c != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'✅ {filepath.split("/")[-1]}: {count} fixes')
        total += count
    else:
        print(f'⚠️ {filepath.split("/")[-1]}: NO changes made')

print(f'\nTotal fixes: {total}')
