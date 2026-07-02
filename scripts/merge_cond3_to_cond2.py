#!/usr/bin/env python3
"""将条件3内容合并到条件2末尾，条件3留空（待用户手动填写）。

已改过的章节（跳过）：25, 26, 56, 161, 171, 214, 215, 342
"""

import os, re

STORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'story')
SKIP_IDS = {'25', '26', '56', '161', '171', '214', '215', '342'}

def process_file(fp, ch_id):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find 章节终止条件 section
    pattern = re.compile(
        r'(章节终止条件[：:]\s*)(.*)',
        re.DOTALL
    )

    m = pattern.search(content)
    if not m:
        return False, "未找到章节终止条件"

    prefix = m.group(1)
    cond_block = m.group(2)

    # Parse individual conditions
    # Format: 1.xxx\n2.xxx\n3.xxx (possibly with the first on same line as prefix)
    # Find all numbered conditions
    conds = re.findall(r'(\d+)[\.\、]\s*(.*?)(?=\n\d+[\.\、]|\Z)', cond_block, re.DOTALL)

    if len(conds) < 3:
        return False, f"条件不足3条（实际{len(conds)}条）"

    cond1 = conds[0][1].strip()
    cond2 = conds[1][1].strip()
    cond3 = conds[2][1].strip()

    if not cond3 or cond3 == '（待填写）':
        return False, "条件3已为空"

    # Merge: cond2 + cond3
    new_cond2 = cond2 + cond3

    # Rebuild conditions block
    new_block = f'1.{cond1}\n2.{new_cond2}\n3.（待填写）'

    # Replace in content
    new_content = content[:m.start()] + prefix + new_block + content[m.end():]

    # Ensure trailing newline preserved
    if content.endswith('\n') and not new_content.endswith('\n'):
        new_content += '\n'

    # If old block had trailing content, keep it
    # (the regex captures the rest after cond3 to end of string)

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f'条件3({len(cond3)}字)→条件2'

def main():
    processed = 0
    skipped = 0
    errors = []

    for root, dirs, files in os.walk(STORY_DIR):
        for f in sorted(files):
            if f.startswith('_') or not f.endswith('.TXT'):
                continue
            fp = os.path.join(root, f)

            # Extract ID from filename
            fname_id = f.split('：')[0]
            try:
                ch_id = str(int(fname_id))
            except ValueError:
                continue

            if ch_id in SKIP_IDS:
                skipped += 1
                continue

            ok, msg = process_file(fp, ch_id)
            if ok:
                processed += 1
            else:
                errors.append(f'Ch{ch_id}: {msg}')

    print(f'已处理: {processed} 章')
    print(f'已跳过(用户改过): {skipped} 章')
    print(f'错误: {len(errors)}')
    for e in errors[:20]:
        print(f'  {e}')
    if len(errors) > 20:
        print(f'  ... 还有 {len(errors) - 20} 个')

if __name__ == '__main__':
    main()
