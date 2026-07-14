"""A-class fix: Replace dashes in 核心/章节任务/章节终止条件 with commas/periods."""
import os
import re

CRITICAL_SECTIONS = ['核心:', '章节任务:', '章节终止条件:']
ALL_SECTIONS = CRITICAL_SECTIONS + [
    '情境:', '占有欲确认:', '好感影响:', '第三者:', '黎恩知情:',
    'NSFW:', '性行为等级:', '阶段:',
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    current_section = None
    modified = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect section start (header may have content after colon)
        matched_section = None
        for sec in ALL_SECTIONS:
            if stripped.startswith(sec):
                matched_section = sec
                break

        if matched_section:
            current_section = matched_section

        # Process 核心/章节任务/章节终止条件: replace ALL —— with ，
        if current_section in CRITICAL_SECTIONS and '——' in line:
            line = line.replace('——', '，')
            modified = True

        new_lines.append(line)

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        return True
    return False

def main():
    base = r'C:\Users\lx\Desktop\世界书\docs\story'
    stages = ['1：试探和暧昧', '2：挑逗和接受']

    total_fixed = 0
    for stage in stages:
        stage_dir = os.path.join(base, stage)
        if not os.path.isdir(stage_dir):
            print(f"Directory not found: {stage_dir}")
            continue
        for fname in sorted(os.listdir(stage_dir)):
            if fname.endswith('.TXT') and not fname.startswith('_'):
                fpath = os.path.join(stage_dir, fname)
                if fix_file(fpath):
                    total_fixed += 1
                    print(f"  Fixed: {fname}")

    print(f"\nTotal files modified: {total_fixed}")

if __name__ == '__main__':
    main()
