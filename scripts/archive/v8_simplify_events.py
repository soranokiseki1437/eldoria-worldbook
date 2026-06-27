# -*- coding: utf-8 -*-
"""
v8_simplify_events.py — V8.0 事件批量简化
==========================================
阶段二：批量清理170事件 —
  删除：触发、玩家选择、路线分支、变量
  新增：好感影响（从变量映射生成）
  重排字段顺序

用法:
  python scripts/v8_simplify_events.py           # 执行转换（先备份）
  python scripts/v8_simplify_events.py --dry-run # 仅预览，不写入
"""

import os, re, sys, shutil
from datetime import datetime
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_DIR = os.path.join(PROJECT_DIR, 'docs', 'event')
BACKUP_DIR = os.path.join(PROJECT_DIR, 'backups')

# 章节目录名（按顺序）
CHAPTER_DIRS = [
    '0：序章', '1：试探和暧昧', '2：挑逗和接受', '3：渐进接触',
    '4：跨线', '5：享受和掌控', '6：放纵', '7：终局', '8：后日谈'
]

# ============================================================
# 字段配置
# ============================================================

# 新字段顺序（输出时按此顺序排列）
NEW_FIELD_ORDER = [
    'ID', '名称', 'NSFW', '性行为等级', '情感阶段', '第三者',
    '黎恩知情', '占有欲确认', '好感影响', '情境', '核心'
]

# 要删除的字段
DELETE_FIELDS = ['触发', '玩家选择', '路线分支', '变量']

# 条件字段（不存在时也要补空行）
CONDITIONAL_FIELDS = ['性行为等级', '情感阶段', '第三者', '黎恩知情', '占有欲确认']

# ============================================================
# 变量→好感映射
# ============================================================

# 12角色名（中文，用于匹配和输出）
CHARACTER_NAMES = [
    'Seraphina', '凯尔', '雷恩', '艾德里安', '乔治',
    '劳拉', '菲', '亚莉莎', '艾玛', '爱丽榭', '玲', '亚尔缇娜'
]

# 角色专属变量 → 角色名映射
CHAR_VAR_MAP = {
    # 凯尔
    'kael_closeness': '凯尔',
    'kael_daily_sessions': None,  # 丢弃
    # 雷恩
    'rain_closeness': '雷恩',
    'rain_candidate': None,
    'reans_serenity': '雷恩',
    # 艾德里安
    'adrian_closeness': '艾德里安',
    'adrian_full_marker': None,
    # 乔治
    'george_closeness': '乔治',
    # 劳拉
    'sub_lauras': '劳拉',
    'bond_laura': '劳拉',
    'laura_intimacy': '劳拉',
    # 菲
    'sub_fies': '菲',
    # 标记（丢弃）
    'first_insertion_marker': None,
    'second_insertion_marker': None,
    'group_marker': None,
    'reclaim_marker': None,
    'humiliation_marker': None,
    'jealousy_marker': None,
    'independence_marker': None,
    'swallow_marker': None,
    'hidden_affair': None,
    'oral_skill': None,
    'combat_synergy': 'Seraphina',
}

# 核心关系变量 → Seraphina
CORE_VARS = {
    'trust', 'trust_level', 'bond', 'bond_level',
    'hope', 'hope_level', 'possess', 'possessiveness_intensity',
    'acceptance', 'shared', 'shared_experience_level',
    'self_awareness',
}

# 丢弃变量（不含角色专属标记——那些在CHAR_VAR_MAP中已标None）
DISCARD_VARS = {
    'ntrs_awakened', 'corruption_level', 'exploration_progress',
    'thalions_influence',
    # 被动NTR残留变量
    'abandonment_count', 'seraphina_despair', 'courage_level',
    # 角色状态标记（非好感值）
    'sub_alisas_status', 'sub_elise_status', 'sub_altina_status',
}

# intimacy_前缀 → Seraphina
INTIMACY_PREFIX = 'intimacy_'


def map_variable_to_character(var_name):
    """将变量名映射到角色名。返回None表示丢弃。"""
    # 精确匹配角色专属映射
    if var_name in CHAR_VAR_MAP:
        return CHAR_VAR_MAP[var_name]
    # 精确匹配丢弃列表
    if var_name in DISCARD_VARS:
        return None
    # 核心变量 → Seraphina
    if var_name in CORE_VARS:
        return 'Seraphina'
    # intimacy_前缀 → Seraphina
    if var_name.startswith(INTIMACY_PREFIX):
        return 'Seraphina'
    # marker后缀 → 丢弃
    if var_name.endswith('_marker'):
        return None
    # 未知变量 → 保留原名（阶段三人工处理）
    return f'未知:{var_name}'


def parse_variable_line(var_text):
    """
    解析旧的变量行，返回好感影响字典 {角色名: value, ...}
    value可以是int或'微量'等特殊字符串
    """
    if not var_text or not var_text.strip():
        return {}

    # 取第一行（去掉可能的多行内容）
    first_line = var_text.split('\n')[0].strip()
    # 去掉开头的 "变量:" 如果存在
    first_line = re.sub(r'^变量[：:]\s*', '', first_line).strip()

    # 特殊处理
    if '取决于选择' in first_line:
        return {}
    if '全角色好感度上升' in first_line or '所有角色好感度上升' in first_line:
        return {'全角色': '微量'}

    result = {}
    # 按逗号分割
    segments = [s.strip() for s in first_line.split(',') if s.strip()]

    for seg in segments:
        char_name, value = parse_segment(seg)
        if char_name and value is not None:
            if char_name in result:
                if isinstance(result[char_name], int) and isinstance(value, int):
                    result[char_name] += value
                else:
                    result[char_name] = value
            else:
                result[char_name] = value

    return result


def parse_segment(seg):
    """
    解析变量段，返回 (角色名, 值) 或 (None, None)
    """
    # 剥离去AI括号描述（中文括号）
    seg = re.sub(r'（[^）]*）', '', seg).strip()
    # 剥离句号后的描述文字
    seg = re.split(r'。', seg)[0].strip()
    if not seg:
        return None, None

    # 1. 检查 "角色名好感度" 或 "角色名好感" 模式
    for cname in CHARACTER_NAMES:
        if cname == 'Seraphina':
            continue  # Seraphina通常用变量名而非"Seraphina好感度"
        pattern = re.escape(cname) + r'(?:好感度|好感)'
        if re.search(pattern, seg):
            m = re.search(r'\+(\d+)', seg)
            if m:
                return cname, int(m.group(1))
            m = re.search(r'\+(\d+)~(\d+)', seg)
            if m:
                return cname, round((int(m.group(1)) + int(m.group(2))) / 2)

    # 2. 检查 "全角色" 模式
    if '全角色' in seg and ('好感' in seg or '微量' in seg):
        return '全角色', '微量'

    # 3. 通用变量名+数值模式
    m = re.match(r'([a-z][a-z_]*[a-z])\s*([+=])\s*(\d+)(?:\s*~\s*(\d+))?', seg)
    if not m:
        # Try without strict prefix (variable might have Chinese prefix like "劳拉本番序列")
        # Check for known variable prefixes
        for var_prefix in ['kael', 'rain', 'adrian', 'george', 'laura', 'bond', 'trust',
                           'possess', 'shared', 'accept', 'hope', 'intimacy', 'sub_',
                           'self_', 'ntrs_', 'corruption', 'exploration', 'thalion',
                           'combat', 'oral', 'swallow', 'reclaim', 'humiliation',
                           'jealousy', 'independence', 'hidden', 'group', 'first_',
                           'second_']:
            if seg.startswith(var_prefix):
                m2 = re.search(r'(\d+)', seg)
                if m2:
                    # Found a known prefix with a number
                    var_name = var_prefix.rstrip('_')
                    # See if map_variable_to_character can handle it
                    char = map_variable_to_character(var_name)
                    if char and char != f'未知:{var_name}':
                        return char, int(m2.group(1))
                    elif char is None:
                        return None, None
        return None, None

    var_name = m.group(1)
    # op = m.group(2)  # += or =
    val1 = int(m.group(3))
    val2 = int(m.group(4)) if m.group(4) else None

    # 范围值取中间（四舍五入）
    if val2 is not None:
        value = round((val1 + val2) / 2)
    else:
        value = val1

    # 映射到角色
    char = map_variable_to_character(var_name)
    if char is None:
        return None, None

    return char, value


def format_haogan_field(haogan_dict):
    """格式化好感影响字段"""
    if not haogan_dict:
        return '好感影响:'

    lines = ['好感影响:']
    for cname in CHARACTER_NAMES:
        if cname in haogan_dict:
            val = haogan_dict[cname]
            lines.append(f'  - {cname}: +{val}' if isinstance(val, int) else f'  - {cname}: {val}')
    # 处理非标准角色（如全角色、未知:xxx等）
    for key, val in haogan_dict.items():
        if key not in CHARACTER_NAMES:
            lines.append(f'  - {key}: +{val}' if isinstance(val, int) else f'  - {key}: {val}')

    return '\n'.join(lines)


# ============================================================
# 事件解析
# ============================================================

def parse_event(text):
    """
    解析事件TXT为OrderedDict {字段名: 字段内容（含首行key: value）}
    """
    lines = text.split('\n')
    fields = OrderedDict()
    current_key = None
    current_lines = []

    for line in lines:
        # 检查是否为新字段（非缩进行，匹配 key: value 格式）
        m = re.match(r'^(\S[^:]*?):\s*(.*)', line)
        if m:
            # 保存上一个字段
            if current_key is not None:
                fields[current_key] = '\n'.join(current_lines).rstrip()
            current_key = m.group(1)
            current_lines = [line]
        else:
            if current_key is not None:
                current_lines.append(line)
            # 如果还没有遇到任何key，跳过文件头的空行

    # 保存最后一个字段
    if current_key is not None:
        fields[current_key] = '\n'.join(current_lines).rstrip()

    return fields


def rebuild_event(fields, old_var_text=''):
    """
    按新字段顺序重建事件文本。
    fields: 原始解析的字段字典
    old_var_text: 原始变量字段内容（用于映射）
    """
    # 映射旧变量→好感影响
    haogan = parse_variable_line(old_var_text)

    output_lines = []

    for fkey in NEW_FIELD_ORDER:
        if fkey == '好感影响':
            output_lines.append(format_haogan_field(haogan))
            output_lines.append('')  # 空行分隔
            continue

        if fkey in fields:
            content = fields[fkey]
            output_lines.append(content)
            output_lines.append('')  # 字段间空行
        elif fkey in CONDITIONAL_FIELDS:
            # 条件字段不存在时补空行
            output_lines.append(f'{fkey}:')
            output_lines.append('')
        else:
            # 必填字段缺失（异常）
            output_lines.append(f'{fkey}:')
            output_lines.append('')

    # 移除末尾多余空行
    while output_lines and output_lines[-1] == '':
        output_lines.pop()

    return '\n'.join(output_lines) + '\n'


# ============================================================
# 主流程
# ============================================================

def process_all_events(dry_run=False):
    """遍历所有章节目录，处理每个TXT文件"""
    total = 0
    skipped = []
    errors = []
    stats = {
        'fields_deleted': 0,
        'haogan_generated': 0,
        'haogan_empty': 0,
    }

    for ch_dir in CHAPTER_DIRS:
        ch_path = os.path.join(EVENT_DIR, ch_dir)
        if not os.path.isdir(ch_path):
            print(f"  ⚠ 目录不存在: {ch_dir}")
            continue

        txt_files = sorted([
            f for f in os.listdir(ch_path)
            if f.endswith('.TXT') and not f.startswith('_')
        ])

        if not txt_files:
            print(f"  📭 {ch_dir}: 无事件文件")
            continue

        print(f"\n📂 {ch_dir} ({len(txt_files)} 个事件)")

        for fname in txt_files:
            fpath = os.path.join(ch_path, fname)
            total += 1

            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    original_text = f.read()

                fields = parse_event(original_text)

                # 统计删除的字段
                deleted_count = sum(1 for k in DELETE_FIELDS if k in fields)
                stats['fields_deleted'] += deleted_count

                # 提取旧变量文本
                old_var = fields.pop('变量', '')

                # 删除不需要的字段
                for dk in DELETE_FIELDS:
                    fields.pop(dk, None)

                # 生成新文本
                new_text = rebuild_event(fields, old_var)

                # 统计好感影响
                haogan = parse_variable_line(old_var)
                if haogan:
                    stats['haogan_generated'] += 1
                else:
                    stats['haogan_empty'] += 1

                if dry_run:
                    event_id = fields.get('ID', '???').split(':')[-1].strip()
                    print(f"  📝 {fname} → ID:{event_id} | 删{deleted_count}字段 | 好感:{len(haogan)}角色")
                else:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(new_text)

            except Exception as e:
                errors.append((fpath, str(e)))
                print(f"  ❌ {fname}: {e}")

    print(f"\n{'='*50}")
    print(f"📊 统计:")
    print(f"  总事件: {total}")
    print(f"  删除字段: {stats['fields_deleted']}")
    print(f"  生成好感影响: {stats['haogan_generated']}")
    print(f"  空好感影响: {stats['haogan_empty']}")
    if skipped:
        print(f"  跳过: {len(skipped)}")
    if errors:
        print(f"  ❌ 错误: {len(errors)}")
        for path, err in errors:
            print(f"    - {os.path.basename(path)}: {err}")
    print(f"{'='*50}")

    return total, errors


def backup_events():
    """备份当前章节目录"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_root = os.path.join(BACKUP_DIR, f'v8_pre_simplify_{timestamp}')
    os.makedirs(backup_root, exist_ok=True)

    for ch_dir in CHAPTER_DIRS:
        src = os.path.join(EVENT_DIR, ch_dir)
        if os.path.isdir(src):
            dst = os.path.join(backup_root, ch_dir)
            shutil.copytree(src, dst)
            count = len([f for f in os.listdir(dst) if f.endswith('.TXT')])
            print(f"  💾 {ch_dir}: {count} 文件")

    print(f"\n📦 备份: {backup_root}")
    return backup_root


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv or '--dry' in sys.argv

    if dry_run:
        print("🔍 干运行模式 (--dry-run)，不会修改文件\n")
    else:
        print("💾 备份当前事件...\n")
        backup_events()
        print("\n⚠ 开始批量转换...\n")

    total, errors = process_all_events(dry_run=dry_run)

    if dry_run:
        print("\n✅ 干运行完成。确认无误后运行 python scripts/v8_simplify_events.py 执行转换。")
    elif errors:
        print(f"\n⚠ 转换完成但{len(errors)}个文件出错，请检查。")
        sys.exit(1)
    else:
        print("\n✅ 批量转换完成。进入阶段三：串行逐个审查。")
