"""批量应用章节任务和终止条件重写。读取JSON映射文件，写入TXT。
修复：正确处理多行字段替换。"""
import json, re, sys, glob, os

STORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'story')

def apply_rewrites(mapping_file):
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    updated = 0
    for stage_dir, chapters in mapping.items():
        stage_path = os.path.join(STORY_DIR, stage_dir)
        if not os.path.isdir(stage_path):
            print(f"  ⚠ 目录不存在: {stage_dir}")
            continue

        for cid_str, fields in chapters.items():
            pattern = os.path.join(stage_path, f'{int(cid_str):03d}：*.TXT')
            matches = glob.glob(pattern)
            if not matches:
                print(f"  ⚠ 未找到章节: {stage_dir}/{cid_str}")
                continue

            filepath = matches[0]
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if '章节任务' in fields:
                new_task = fields['章节任务']
                # Match single-line field (章节任务 is always single-line)
                content = re.sub(
                    r'^章节任务: .+$',
                    f'章节任务: {new_task}',
                    content,
                    flags=re.MULTILINE
                )

            if '章节终止条件' in fields:
                new_term = fields['章节终止条件']
                # Match the field line + all continuation lines until blank line or EOF
                # Continuation lines are non-empty lines that follow the field header
                content = re.sub(
                    r'^章节终止条件:[\s\S]*?(?=\n\n|\n\Z|\Z)',
                    f'章节终止条件: {new_term}',
                    content,
                    flags=re.MULTILINE
                )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            updated += 1
            print(f"  ✓ {stage_dir}/{cid_str}")

    print(f"\n共更新 {updated} 个章节")
    return updated

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python rewrite_tasks.py <mapping.json>")
        sys.exit(1)
    apply_rewrites(sys.argv[1])
