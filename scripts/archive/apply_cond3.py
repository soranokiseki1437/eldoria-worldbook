"""
apply_cond3.py — Phase 2: 从Agent输出提取条件3映射并写回TXT
"""
import json
import re
import os
import glob
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_DIR = os.path.join(
    os.path.expanduser("~"), "AppData", "Local", "Temp", "claude",
    "C--Users-lx-Desktop----", "23ed8170-c692-45ec-bf23-c79789a8f10c", "tasks"
)
STORY_DIR = os.path.join(BASE, "docs", "story")
SKIP = {25, 26, 56, 161, 171, 214, 215, 342}


def extract_cond3_from_text(text):
    """从任意文本中尽可能提取 chapter_id -> condition_3 映射"""
    mapping = {}

    # 尝试找到并解析所有可能的JSON对象
    # 匹配各种键名组合

    # 模式A: {"chapter": NNN, ... "condition3": "..."} 或类似
    patterns = [
        # results数组中的对象
        r'\{\s*"(?:chapter|id)"\s*:\s*(\d{3})[^}]*"(?:condition3|new_cond3|condition_3|new_condition_3)"\s*:\s*"([^"]*)"',
        # key-value对象: "NNN": {"condition3": "..."}
        r'"(\d{3})"\s*:\s*\{[^}]*"(?:condition3|new_cond3|condition_3|new_condition_3)"\s*:\s*"([^"]*)"',
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, text):
            ch_id = int(m.group(1))
            cond3 = m.group(2).strip()
            if ch_id >= 97 and ch_id <= 416:
                mapping[ch_id] = cond3

    return mapping


def process_output_file(filepath):
    """处理单个Agent输出文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return {}

    # 只处理Phase 1的Agent输出（Cond3 B）
    if 'Cond3 B' not in content and '条件3' not in content:
        # 也可能是Phase 1但描述不同
        if 'condition3' not in content and 'new_cond3' not in content:
            return {}

    mapping = extract_cond3_from_text(content)
    return mapping


def main():
    print("=" * 60)
    print("Phase 2: 条件3写回TXT")
    print("=" * 60)

    # Step 1: 收集所有映射
    print("\n[1/3] 从Agent输出提取条件3映射...")

    if not os.path.exists(SESSION_DIR):
        print(f"ERROR: Session dir not found: {SESSION_DIR}")
        sys.exit(1)

    output_files = glob.glob(os.path.join(SESSION_DIR, "*.output"))
    print(f"  找到 {len(output_files)} 个输出文件")

    all_mappings = {}
    for f in sorted(output_files):
        mapping = process_output_file(f)
        if mapping:
            # 取最好的值（后面的覆盖前面的，因为同一Agent可能重试了）
            all_mappings.update(mapping)
            print(f"  {os.path.basename(f)[:20]}...: {len(mapping)} chapters")

    print(f"\n  总计提取: {len(all_mappings)} 章的条件3")

    if len(all_mappings) < 100:
        print("  ⚠️  提取数量过少，保存原始数据供调试...")
        debug_file = os.path.join(STORY_DIR, "_cond3_debug.txt")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(all_mappings, ensure_ascii=False, indent=2))
        print(f"  调试数据已保存: {debug_file}")

    # 验证完整性
    expected = set(range(97, 417)) - SKIP
    found = set(all_mappings.keys())
    missing = expected - found
    extra = found - expected

    if missing:
        print(f"\n  ⚠️  缺失 {len(missing)} 章: {sorted(missing)[:30]}")
    if extra:
        # 过滤掉可能是误匹配的小数字
        real_extra = {e for e in extra if e >= 97}
        if real_extra:
            print(f"  ⚠️  多余 {len(real_extra)} 章: {sorted(real_extra)[:20]}")

    # Step 2: 写回
    print(f"\n[2/3] 写回TXT文件...")
    success = 0
    fail = 0

    for ch_id in sorted(all_mappings.keys()):
        if ch_id in SKIP:
            continue
        if ch_id < 97 or ch_id > 416:
            continue

        cond3 = all_mappings[ch_id]
        if not cond3 or len(cond3) < 3:
            continue

        # 查找TXT文件
        txt_path = None
        for root, dirs, files in os.walk(STORY_DIR):
            if root == STORY_DIR:  # 跳过根目录
                continue
            for fname in files:
                if not fname.endswith('.TXT'):
                    continue
                if fname.startswith(f"{ch_id:03d}：") or fname.startswith(f"{ch_id}："):
                    txt_path = os.path.join(root, fname)
                    break
            if txt_path:
                break

        if not txt_path:
            print(f"  WARNING: Chapter {ch_id} TXT not found")
            fail += 1
            continue

        # 读取TXT
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 找到并替换条件3
        # 条件3格式: 在"章节终止条件:"之后的 "3.xxx"
        lines = content.split('\n')
        replaced = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('3.') and i > 5:
                # 确认前几行有章节终止条件
                context = '\n'.join(lines[max(0,i-8):i])
                if '章节终止条件' in context or '2.' in context:
                    lines[i] = f'3.{cond3}'
                    replaced = True
                    break

        if not replaced:
            # 备选：直接找 "3." 行（在章节终止条件区域内）
            for i, line in enumerate(lines):
                stripped = line.strip()
                if '章节终止条件' in stripped:
                    # 从下一行开始找3.
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip().startswith('3.'):
                            lines[j] = f'3.{cond3}'
                            replaced = True
                            break
                    break

        if replaced:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            success += 1
        else:
            print(f"  WARNING: Chapter {ch_id} cond3 line not found: {txt_path}")
            fail += 1

    print(f"  成功: {success}, 失败: {fail}, 跳过: {len(SKIP)}")

    # 保存映射
    map_file = os.path.join(STORY_DIR, "_cond3_mapping.json")
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump({str(k): all_mappings[k] for k in sorted(all_mappings.keys())},
                  f, ensure_ascii=False, indent=2)
    print(f"\n  映射已保存: {map_file}")

    return success, fail


if __name__ == '__main__':
    success, fail = main()
    print(f"\nDone: {success} OK, {fail} failed")
