"""A-class: Replace clearly excessive narrative dashes in 情境 with commas.
Rules:
- KEEP dashes inside dialogue (between paired quotes "")
- KEEP dashes in title separator (file name field)
- REPLACE dashes with ， when connecting clauses (both sides are full sentence fragments)
- KEEP dashes for dramatic emphasis when uncertain
"""
import os
import re

SECTION_HEADERS = [
    '情境:', '占有欲确认:', '核心:', '章节任务:', '章节终止条件:',
    '好感影响:', '第三者:', '黎恩知情:', 'NSFW:', '性行为等级:', '阶段:',
]

def is_inside_dialogue(text_before_dash):
    """Check if a position is inside quoted dialogue."""
    return text_before_dash.count('"') % 2 == 1

def should_replace_dash(line, pos):
    """Determine if a dash in 情境 should be replaced with comma."""
    before = line[:pos]
    after = line[pos+2:]  # skip ——

    # NEVER replace dashes inside dialogue
    if is_inside_dialogue(before):
        return False

    # Get context around dash
    ctx_before = before.rstrip()[-30:] if len(before.rstrip()) >= 30 else before.rstrip()
    ctx_after = after.lstrip()[:30]

    # KEEP: dash before a quote (dialogue start)
    if ctx_after.lstrip().startswith('"'):
        return False

    # KEEP: dash after ... or ellipsis
    if ctx_before.rstrip().endswith('...') or ctx_before.rstrip().endswith('…'):
        return False

    # KEEP: dash in structural enumerations like "一、在场——" or "二、知情——"
    if re.search(r'[一二三四五六七八九十]、', ctx_before[-15:]):
        return False

    # REPLACE: dash connecting two clauses (both sides have complete phrases)
    # Simple heuristic: if the dash is between two segments that each have 3+ chars
    # and the dash isn't followed by a key emphasis word
    before_chars = ctx_before.rstrip()[-3:]
    after_chars = ctx_after.lstrip()[:3]

    # KEEP: dash that introduces a dramatic reveal (followed by "那是"/"这是")
    if re.match(r'^(那是|这是|那个|这个)', ctx_after.lstrip()):
        return False

    # Most other narrative dashes are connectors → replace with ，
    return True

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    current_section = None
    modified = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect section
        for sec in SECTION_HEADERS:
            if stripped.startswith(sec):
                current_section = sec
                break

        # Only process 情境 dashes
        if current_section == '情境:' and '——' in line:
            new_line = list(line)
            # Process dashes from right to left to preserve positions
            positions = [m.start() for m in re.finditer('——', line)]
            for pos in reversed(positions):
                if should_replace_dash(line, pos):
                    new_line[pos:pos+2] = '，'
                    modified = True
            line = ''.join(new_line)

        new_lines.append(line)

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        # Count how many were replaced
        return True
    return False

def main():
    base = r'C:\Users\lx\Desktop\世界书\docs\story'
    stages = ['1：试探和暧昧', '2：挑逗和接受']

    total_fixed = 0
    for stage in stages:
        stage_dir = os.path.join(base, stage)
        if not os.path.isdir(stage_dir):
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
