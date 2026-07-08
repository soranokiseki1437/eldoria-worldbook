"""D-class fix: Add missing periods to 情境 bullet points."""
import os
import re
import sys

SECTION_HEADERS = {
    '情境:', '占有欲确认:', '核心:', '章节任务:', '章节终止条件:',
    '好感影响:', '第三者:', '黎恩知情:', 'NSFW:', '性行为等级:', '阶段:',
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    current_section = None
    modified = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect section boundaries
        if stripped in SECTION_HEADERS:
            current_section = stripped
            new_lines.append(line)
            continue

        # Only process 情境 bullets
        if current_section == '情境:' and stripped.startswith('- '):
            # Check if it ends with 。！？. or closing quote or digit
            if re.search(r'[。！？\.\d]$', stripped):
                pass  # Already has ending punctuation or is a number (好感影响 style)
            elif stripped.endswith('"') or stripped.endswith('"'):
                # Ends with quote - check char before quote
                pass  # Quotes are fine
            elif stripped.endswith('，') or stripped.endswith('、'):
                line = line.rstrip('，、') + '。'
                modified = True
            else:
                line = line + '。'
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
