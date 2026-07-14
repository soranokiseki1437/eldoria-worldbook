"""将章节终止条件从4+条压缩到最多3条。合并相邻条目。"""
import re, glob, os, sys

STORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'story')

def compress_items(items, target=3):
    """将N个item合并为目标数量。保持语义连贯，合并相邻项。"""
    n = len(items)
    if n <= target:
        return items

    # Group items into 'target' groups, merging adjacent items
    result = []
    group_sizes = []

    if target == 3:
        if n == 4:
            # Keep 1, 2, merge 3+4
            result = [items[0], items[1], items[2] + items[3]]
        elif n == 5:
            # Keep 1, merge 2+3, merge 4+5
            result = [items[0], items[1] + items[2], items[3] + items[4]]
        elif n == 6:
            # Merge 1+2, merge 3+4, merge 5+6
            result = [items[0] + items[1], items[2] + items[3], items[4] + items[5]]
        elif n == 7:
            # Merge 1+2, merge 3+4+5, merge 6+7
            result = [items[0] + items[1], items[2] + items[3] + items[4], items[5] + items[6]]
        else:
            # General case: distribute items across 3 groups
            per_group = n // 3
            remainder = n % 3
            idx = 0
            for g in range(3):
                size = per_group + (1 if g < remainder else 0)
                merged = ''.join(items[idx:idx + size])
                result.append(merged)
                idx += size
    elif target == 2 and n >= 4:
        # For chapters that can be reduced to 2
        mid = n // 2
        result = [''.join(items[:mid]), ''.join(items[mid:])]

    return result


def process_chapter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the term field boundaries
    term_match = re.search(r'^章节终止条件: ', content, re.MULTILINE)
    if not term_match:
        return False

    start_pos = term_match.start()
    end_pos = content.find('\n\n', start_pos)
    if end_pos == -1:
        end_pos = len(content)

    full_term = content[start_pos:end_pos]
    term_body = full_term[len('章节终止条件: '):]

    # Parse individual items
    # Items are lines like "1.xxx" or "2.xxx"
    item_pattern = re.findall(r'(\d+)\.\s*(.+?)(?=\n\d+\.|\Z)', term_body, re.DOTALL)
    if not item_pattern:
        return False

    items = []
    for num, text in item_pattern:
        text = text.strip()
        # Ensure it ends with proper punctuation
        if text and text[-1] not in '。！？':
            text += '。'
        items.append(text)

    n = len(items)
    if n <= 3:
        return False

    # Compress to 3
    merged = compress_items(items, 3)

    # Rebuild term with proper numbering
    new_term_lines = []
    for i, item in enumerate(merged, 1):
        new_term_lines.append(f'{i}.{item}')

    new_term = '\n'.join(new_term_lines)
    new_field = f'章节终止条件: {new_term}'

    # Replace in content
    content = content[:start_pos] + new_field + content[end_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return n


def main():
    stages = sorted([d for d in os.listdir(STORY_DIR)
                     if os.path.isdir(os.path.join(STORY_DIR, d)) and d[0].isdigit()])

    total = 0
    compressed = 0

    for stage in stages:
        stage_path = os.path.join(STORY_DIR, stage)
        txts = sorted(glob.glob(os.path.join(stage_path, '[0-9]*.TXT')))
        for t in txts:
            total += 1
            orig_n = process_chapter(t)
            if orig_n:
                compressed += 1
                cid = os.path.basename(t)[:3]
                print(f'  [{cid}] {orig_n}→3')

    print(f'\n扫描 {total} 章，压缩 {compressed} 章')


if __name__ == '__main__':
    main()
