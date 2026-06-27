#!/usr/bin/env python3
"""
全章重编号脚本 — 从磁盘读取实际文件名，按指定顺序重编号
两阶段重命名（→临时名→最终名）防碰撞，同时更新内部ID行
"""
import os
import re

BASE = r"C:\Users\lx\Desktop\世界书\docs\event"

# 各章节事件顺序：用 (number_prefix, is_insert) 标识
# number_prefix用于匹配现有文件（匹配"XX：..."开头的文件）
# is_insert标记表示这是新插入的_INSERT_文件
CHAPTER_SPEC = {
    "0：序章": [
        ("01", False), ("02", False), ("03", False), ("04", False),
        ("05", False), ("06", False), ("07", False),
        ("_INSERT_R02", True),
        ("08", False),
        ("_INSERT_G01", True),
        ("09", False), ("10", False), ("11", False),
        ("_INSERT_R01", True),
        ("12", False), ("13", False),
        ("_INSERT_P13", True),
        ("_INSERT_P22", True),
        ("_INSERT_P16", True),
        ("14", False), ("15", False), ("16", False), ("17", False),
        ("18", False), ("19", False), ("20", False), ("21", False),
        ("22", False),
        ("_INSERT_P10", True),
        ("23", False), ("24", False), ("25", False), ("26", False),
        ("27", False),
        ("_INSERT_W07", True),
        ("28", False),
        ("_INSERT_P14", True),
        ("29", False), ("30", False),
    ],
    "1：试探和暧昧": [
        ("31", False),
        ("_INSERT_R03", True),
        ("32", False), ("33", False),
        ("_INSERT_G02", True),
        ("34", False), ("35", False), ("36", False), ("37", False),
        ("38", False), ("39", False),
        ("_INSERT_G05", True),
        ("40", False), ("41", False), ("42", False), ("43", False),
        ("44", False), ("45", False), ("46", False),
        ("_INSERT_H1", True),
        ("47", False), ("48", False),
        ("_INSERT_R06", True),
        ("_INSERT_R08", True),
    ],
    "2：挑逗和接受": [
        ("49", False), ("50", False),
        ("_INSERT_G06", True),
        ("51", False), ("52", False), ("53", False), ("54", False),
        ("55", False), ("56", False),
        ("_INSERT_P19", True),
        ("57", False),
        ("_INSERT_P17", True),
    ],
    "3：渐进接触": [
        ("58", False), ("59", False), ("60", False), ("61", False),
        ("62", False), ("63", False), ("64", False),
        ("_INSERT_G03", True),
        ("65", False), ("66", False), ("67", False), ("68", False),
        ("69", False), ("70", False), ("71", False), ("72", False),
        ("73", False), ("74", False), ("75", False),
        ("_INSERT_P21", True),
        ("76", False), ("77", False),
        ("_INSERT_P18", True),
        ("78", False), ("79", False), ("80", False),
        ("_INSERT_P15", True),
    ],
    "4：跨线": [
        ("81", False), ("82", False),
        ("_INSERT_R04", True),
        ("83", False),
        ("_INSERT_R05", True),
        ("84", False),
        ("_INSERT_H2", True),
        ("85", False), ("86", False), ("87", False), ("88", False),
        ("89", False), ("90", False),
    ],
    "5：享受和掌控": [
        ("91", False), ("92", False), ("93", False), ("94", False),
        ("95", False), ("96", False), ("97", False), ("98", False),
        ("99", False),
        ("_INSERT_G04", True),
        ("100", False), ("101", False), ("102", False), ("103", False),
        ("104", False), ("105", False), ("106", False), ("107", False),
        ("108", False), ("109", False), ("110", False), ("111", False),
        ("112", False), ("113", False), ("114", False), ("115", False),
        ("116", False), ("117", False),
        ("_INSERT_G07", True),
        ("118", False), ("119", False), ("120", False), ("121", False),
    ],
    "6：放纵": [
        ("122", False), ("123", False), ("124", False), ("125", False),
        ("126", False), ("127", False), ("128", False), ("129", False),
        ("130", False), ("131", False), ("132", False),
        ("_INSERT_R07", True),
        ("133", False), ("134", False), ("135", False), ("136", False),
        ("137", False), ("138", False),
        ("_INSERT_P20", True),
        ("_INSERT_H4", True),
    ],
    "7：终局": [
        ("_INSERT_P11", True),
        ("139", False), ("140", False),
        ("_INSERT_W08", True),
        ("_INSERT_H3", True),
        ("141", False),
    ],
    "8：后日谈": [
        ("_INSERT_P12", True),
    ],
}

def find_file_by_prefix(directory, prefix):
    """在目录中查找以prefix开头的文件（精确匹配"XX："或"_INSERT_XX："开头）"""
    for fname in os.listdir(directory):
        # 匹配模式：数字编号 + ： 或 _INSERT_标记 + ：
        if fname.startswith(prefix + '：') or fname.startswith(prefix + ':'):
            return fname
        # 也匹配只有数字无冒号的情况
        if prefix.isdigit() and fname.startswith(prefix) and ('：' in fname or ':' in fname or fname.startswith(prefix + '.')):
            return fname
    # 放宽匹配：只要以prefix开头
    for fname in os.listdir(directory):
        if fname.startswith(prefix):
            return fname
    return None

def update_id_in_file(filepath, new_id):
    """更新TXT文件内部的ID行"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'^ID:\s*.*$', f'ID: {new_id}', content, flags=re.MULTILINE)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"    ⚠ ID更新失败: {e}")

def renumber_all():
    """主函数：查找文件→两阶段重命名→更新ID"""
    global_num = 1
    all_changes = []
    total_expected = sum(len(spec) for spec in CHAPTER_SPEC.values())

    for chapter, spec in CHAPTER_SPEC.items():
        chapter_dir = os.path.join(BASE, chapter)
        if not os.path.isdir(chapter_dir):
            print(f"  ⚠ 目录不存在: {chapter_dir}")
            continue

        print(f"\n{'='*60}")
        print(f"  {chapter} — {len(spec)} events")
        print(f"{'='*60}")

        # Phase 0: Resolve file names
        resolved = []
        for prefix, is_insert in spec:
            fname = find_file_by_prefix(chapter_dir, prefix)
            if fname:
                resolved.append(fname)
            else:
                print(f"  ❌ 找不到文件: prefix={prefix}")
                # Try listing files with similar prefix
                similar = [f for f in os.listdir(chapter_dir) if f.startswith(prefix[:2])]
                if similar:
                    print(f"     相似文件: {similar[:3]}")

        if not resolved:
            print(f"  ⚠ 无文件解析成功")
            continue

        # Phase 1: Rename all to temp names
        temp_map = {}
        for old_name in resolved:
            old_path = os.path.join(chapter_dir, old_name)
            final_num = global_num
            temp_name = f"_TMP_{final_num:04d}_.TXT"
            temp_path = os.path.join(chapter_dir, temp_name)

            try:
                os.rename(old_path, temp_path)
                temp_map[temp_name] = (old_name, final_num)
                global_num += 1
            except Exception as e:
                print(f"  ❌ 重命名失败: {old_name} -> {temp_name}: {e}")

        # Phase 2: Rename from temp to final names
        for temp_name, (old_name, final_num) in temp_map.items():
            temp_path = os.path.join(chapter_dir, temp_name)

            # Extract name part
            if old_name.startswith('_INSERT_'):
                # 格式: _INSERT_XX：中文名.TXT
                parts = old_name.split('：', 1)
                name_part = parts[1] if len(parts) > 1 else old_name
            elif '：' in old_name:
                name_part = old_name.split('：', 1)[1]
            elif ':' in old_name:
                name_part = old_name.split(':', 1)[1]
            else:
                name_part = old_name

            final_name = f"{final_num:02d}：{name_part}"
            final_path = os.path.join(chapter_dir, final_name)

            try:
                os.rename(temp_path, final_path)
                update_id_in_file(final_path, str(final_num))
                all_changes.append((chapter, old_name, final_name, final_num))
                short_old = old_name[:50] + "..." if len(old_name) > 50 else old_name
                print(f"  {short_old}")
                print(f"    → {final_name}")
            except Exception as e:
                print(f"  ❌ 最终重命名失败: {temp_name} -> {final_name}: {e}")

    print(f"\n{'='*60}")
    print(f"  总计: {len(all_changes)}/{total_expected} events renumbered (1-{global_num-1})")
    print(f"{'='*60}")
    return all_changes

if __name__ == '__main__':
    changes = renumber_all()
    if changes:
        print(f"\n✅ 重编号完成！{len(changes)}个事件已重新编号。")
    else:
        print("\n❌ 重编号失败！")
