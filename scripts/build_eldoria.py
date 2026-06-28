# -*- coding: utf-8 -*-
"""
build_eldoria.py — Eldoria 世界书 JSON 构建脚本 (V10.0)
===========================================================
权威数据源：docs/ 子目录全部TXT文件（chapter/ character/ world/ creature/ location/ npc/ event/）
派生产物：output/Eldoria_V10.0.0.json（本脚本输出，不可手动编辑）

工作流：编辑 docs/ 下的 TXT 文件（权威数据源）→ 运行本脚本 → 产出 JSON

架构 (V10.0):
  - 全TXT驱动，零硬编码条目
  - Reference条目: docs/chapter|character|world|creature|location|npc/*.TXT → 69条
  - 事件条目: docs/event/{章节}/*.TXT → 170条
  - 始终触发条目: chapter/全部(6) + 各子目录_总览文件(5) = 11条
  - JSON不可手动编辑，所有修改通过TXT + rebuild

用法：
    python build_eldoria.py              # 构建并写入 JSON（自动备份）
    python build_eldoria.py --dry-run    # 仅验证，不写入文件

依赖：Python 3.7+（仅标准库）
"""

import json
import os
import re
import sys
import shutil
from datetime import datetime

# ─── 路径配置 ───────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)   # 脚本在 scripts/ 下，上级为项目根
BACKUP_DIR  = os.path.join(PROJECT_DIR, "backup")
OUTPUT_DIR  = os.path.join(PROJECT_DIR, "output")
DOCS_DIR    = os.path.join(PROJECT_DIR, "docs")
MD_DIR      = DOCS_DIR  # 分md在 docs/ 目录下

# ─── 版本号（每次内容变更请按规则递增） ────────────────────
# 格式: "V{主版本}.{次版本}.{修订号}"
#  - 主版本: 重大架构变更 / 路线重设计 / 核心设定翻版
#  - 次版本: 新增角色 / 新增事件 / 修改变量系统
#  - 修订号: 文本修正 / 错别字 / 内容微调
VERSION = "V10.2.0"
VERSION_TAG = f"Eldoria_{VERSION}"  # V10.2.0: 211事件+肛交线+低语者净化线+狼人线+后日谈完整

# 主输出文件 = 带版本号的文件名（输出到 output/ 目录）
JSON_PATH = os.path.join(OUTPUT_DIR, f"{VERSION_TAG}.json")

# ─── 顶层固定字段 ───────────────────────────────────────
SPEC          = "chara_card_v3"
SPEC_VERSION  = "2.0"
CHAR_NAME     = "Eldoria - \u827e\u5c14\u591a\u5229\u4e9a\u5b88\u62a4\u8005"
CHAR_DESC = (
    "世界书核心设定：\n"
    "-主角：黎恩舒华泽（{{user}}）\n"
    "-女主：塞拉菲娜（Seraphina，Eldoria最后的精灵守护者）\n"
    "-主要角色：塔里昂（堕落前守护者）、亚莉莎莱恩福尔特、劳拉S亚尔赛德、乔治诺姆、艾玛米尔斯汀、菲克劳塞尔、爱丽榭舒华泽\n"
    "-世界观核心设定：Eldoria森林腐化魔法体系（圣光鬼之力腐化魔法）\n"
    "-核心关系动态：单线纯爱NTRS融合线——共享时刻 ⇄ 回归时刻\n"
    "-叙事基调：幽暗奇幻史诗感个人羁绊温柔守护黑暗挣扎禁忌共享\n"
    "-黎恩和Seraphina都是强者"
)
CHAR_SCENARIO = (
    "Eldoria\u68ee\u6797\u662f\u4e00\u4e2a\u53e4\u8001\u7684\u7cbe\u7075\u738b\u56fd\uff0c\u56e0\u8150\u5316\u9b54\u6cd5\u800c\u9010\u6e10\u6d88\u4ea1\u3002"
    "\u585e\u62c9\u83f2\u5a1c\uff08Seraphina\uff09\u662fEldoria\u6700\u540e\u7684\u7cbe\u7075\u5b88\u62a4\u8005\uff0c\u4f7f\u7528\u70bd\u5929\u4f7f\u8840\u8109\u7684\u5723\u5149\u5b88\u62a4\u68ee\u6797\u3002"
    "\u9ece\u6069\u8212\u534e\u6cfd\uff08{{user}}\uff09\u662f\u88ab\u62c9\u5165\u8fd9\u4e2a\u4e16\u754c\u7684\u4eba\u7c7b\uff0c\u62e5\u6709\u9b3c\u4e4b\u529b\u3002"
    "\u68ee\u6797\u4e2d\u8fd8\u6709\u8150\u5316\u7684\u5f71\u7259\u517d\uff08Shadowfang\uff09\u548c\u5815\u843d\u7684\u524d\u5b88\u62a4\u8005\u5854\u91cc\u6602\uff08Thalion\uff09\u3002"
    "\u5355\u7ebf\u7eaf\u7231NTRS\u878d\u5408\u7ebf\uff1a\u5171\u4eab\u65f6\u523b \u21c4 \u56de\u5f52\u65f6\u523b\uff0c170\u4e8b\u4ef6\u7ebf\u6027\u53d9\u4e8b\u3002"
)
CHAR_FIRST_MES = (
    "*你在林间空地醒来，温暖的金色圣光包围着你。"
    "一位粉发琥珀色双瞳的女性正低头看着你，她穿着黑色的太阳裙，裙摆上有细微的金色纹路在圣光下若隐若现。"
    "她的声音轻柔而悠远*\n"
    "欢迎来到艾尔多利亚，旅人。我是塞拉菲娜（Seraphina），这片森林最后的守护者。\n"
    "*她的琥珀色眼睛注视着你，带着好奇与一丝戒备*\n"
    "你已经昏迷了三天。告诉我——你是谁，从何处来？"
    "你的气息中——有某种与腐化共鸣的力量……"
)


# ═══════════════════════════════════════════════════════════
# 通用MD事件加载器 — 零硬编码，读全文件，按前缀过滤
# ═══════════════════════════════════════════════════════════
_ALL_EVENTS_CACHE = None


def _load_all_events():
    """从 docs/event/{prefix}/*.TXT 读取所有事件，返回{N##: {title, content, ...}, ...}"""
    global _ALL_EVENTS_CACHE
    if _ALL_EVENTS_CACHE is not None:
        return _ALL_EVENTS_CACHE

    import re as _re
    import glob as _glob

    _event_dir = os.path.join(PROJECT_DIR, 'docs', 'event')
    _ALL_EVENTS_CACHE = {}

    for _prefix_dir in sorted(os.listdir(_event_dir)):
        _pfx_path = os.path.join(_event_dir, _prefix_dir)
        if not os.path.isdir(_pfx_path):
            continue
        _prefix = _prefix_dir  # 'E', 'N', 'P', 'PN', 'W', 'H', 'G', 'R'

        for _fp in sorted(_glob.glob(os.path.join(_pfx_path, '*.TXT'))):
            # 解析 TXT 文件（key: value 格式）
            _data = _parse_event_txt(_fp)
            _eid = _data.get('ID', '')
            if not _eid:
                continue

            _title = _data.get('名称', '')
            _third_party = _data.get('第三者', '')
            _sex_act = _data.get('性行为等级', '') or _data.get('性行为', '')
            _phase = _data.get('情感阶段', '') or _data.get('情感', '') or _data.get('阶段', '')

            # 构建 content（保持与旧格式兼容）
            from event_config import COMMENT_PREFIX
            _comment_prefix = COMMENT_PREFIX.get(_prefix, _prefix)
            _lines = [f'【{_comment_prefix}事件——{_eid}：{_title}】', '']

            # 按标准顺序输出字段
            _label_map = {
                '触发': '触发条件', '触发条件': '触发条件',
                'NSFW': 'NSFW',
                '性行为等级': '性行为等级', '性行为': '性行为等级',
                '情感阶段': '情感阶段', '情感': '情感阶段', '阶段': '情感阶段',
                '黎恩知情': '黎恩知情', '第三者': '第三者',
                '情境': '情境', '占有欲确认': '占有欲确认',
                '玩家选择': '玩家选择', '变量': '变量', '核心': '核心',
                '所属章节': '所属章节',
            }
            _field_order = ['触发', 'NSFW', '所属章节', '性行为等级', '情感阶段',
                           '黎恩知情', '第三者', '占有欲确认',
                           '情境', '玩家选择', '变量', '核心']
            for _key in _field_order:
                if _key in _data and _data[_key]:
                    _label = _label_map.get(_key, _key)
                    _val = _data[_key]
                    if '\n' in _val:
                        # 多行值：第一行跟label，后续行保持缩进
                        _val_lines = _val.split('\n')
                        _lines.append(f'{_label}：{_val_lines[0]}')
                        for _vl in _val_lines[1:]:
                            _lines.append(f'  {_vl}')
                    else:
                        _lines.append(f'{_label}：{_val}')

            _content = '\n'.join(_lines)
            # Strip leading "- " bullets from content (参照格式：纯文本换行)
            _content = _re.sub(r'^[ \t]*-[ \t]', '', _content, flags=_re.MULTILINE)
            # Also strip "- " immediately after "：" (情境：- xxx → 情境：xxx)
            _content = _re.sub(r'：- ', '：', _content)

            _ALL_EVENTS_CACHE[_eid] = {
                'title': _title,
                'content': _content,
                'comment': f'【{_comment_prefix}事件】 {_eid} —— {_title}',
                'prefix': _prefix,
                'third_party': _third_party,
                'sex_act': _sex_act,
                'phase': _phase,
            }

    return _ALL_EVENTS_CACHE


def _parse_event_txt(filepath):
    """解析单个 .TXT 事件文件（key: value 格式），返回 dict"""
    import re as _re
    with open(filepath, 'r', encoding='utf-8') as _f:
        _raw_lines = _f.readlines()

    _data = {}
    _current_key = None
    _current_value = []

    for _line in _raw_lines:
        # 跳过空行和注释
        if not _line.strip():
            continue
        if _line.strip().startswith('#'):
            continue

        # 检查 key: value 行（非缩进、非bullet）
        _m = _re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', _line)
        if _m and not _line.lstrip().startswith(('-', 'A.', 'B.', 'C.')):
            if _current_key:
                _data[_current_key] = '\n'.join(_current_value).strip()
            _current_key = _m.group(1).strip()
            _val = _m.group(2).strip()
            _current_value = [_val] if _val else []
        else:
            _current_value.append(_line.rstrip('\n'))

    if _current_key:
        _data[_current_key] = '\n'.join(_current_value).strip()

    return _data


def _load_ntrs_events():
    """从缓存中过滤NTRS事件（向后兼容）"""
    return {k: v for k, v in _load_all_events().items() if v['prefix'] == 'N'}


def _load_pure_events():
    """从缓存中过滤纯爱事件"""
    return {k: v for k, v in _load_all_events().items() if v['prefix'] == 'P'}

def ntrs(event_id):
    """返回NTRS事件的{title, content, comment, third_party, sex_act, phase}字典"""
    return _load_ntrs_events()[event_id]


# ═══════════════════════════════════════════════════════════
# 自动键词生成 — 从YAML元数据提取关键词，零硬编码
# ═══════════════════════════════════════════════════════════

# 性行为关键词映射表（从性行为等级字段中识别）
_SEX_ACT_KEYWORDS = {
    '口交': ['口交', '口'],
    '乳交': ['乳交', '乳'],
    '插入': ['插入', '本番'],
    '手交': ['手交'],
    '足交': ['足交', '足'],
    '轮奸': ['轮奸'],
    '隐奸': ['隐奸'],
    '3P': ['3P'],
    '群交': ['群交'],
    '震动棒': ['震动棒', '玩具'],
    '打飞机': ['打飞机'],
    '指交': ['指交'],
    '摸乳': ['摸乳'],
    '暴露': ['暴露'],
    '乳': ['乳'],
    '足': ['足'],
    '本番': ['本番'],
    '后入': ['后入'],
    '颜射': ['颜射'],
    '腿交': ['腿交'],
}

# 阶段关键词映射
_PHASE_KEYWORDS = {
    'A': ['阶段A', '探索'],
    'B': ['阶段B', '挑逗'],
    'C': ['阶段C', '放开'],
    'D': ['阶段D', '极限'],
    '终局': ['终局'],
}


def _auto_keys(event_id, data):
    """事件条目关键词：仅"事件x"。"""
    import re as _re
    _num = _re.search(r'\d+', event_id)
    _n = _num.group() if _num else event_id
    return [f'事件{_n}']


def _auto_order(event_id):
    """从事件ID自动生成order值。N01→162, P01→162, PN01→162..."""
    import re as _re
    _num = int(_re.search(r'\d+', event_id).group())
    return 160 + _num * 2


def _get_md_entries(prefix, tag, base_order=160):
    """★ 通用TXT驱动条目生成器——零硬编码。

    Args:
        prefix: 章节目录名 ('0：序章', '1：试探和暧昧', ...)
        tag: 键词标签 (unused, kept for compatibility)
        base_order: 起始order值 (deprecated)

    Returns:
        条目列表（uid=None），position=4, depth=2, order=600
    """
    _entries = []
    _all = _load_all_events()
    _events = {k: v for k, v in _all.items() if v['prefix'] == prefix}
    for _eid in sorted(_events.keys()):
        _data = _events[_eid]
        _keys = _auto_keys(_eid, _data)
        _entries.append(make_entry(
            uid=None,
            keys=_keys,
            comment=_data['comment'],
            order=600,
            probability=100,
            content=_data['content'],
            position=4,
            depth=2,
        ))
    return _entries


# ═══════════════════════════════════════════════════════════
# V10.0: 通用TXT条目加载器 — 读写docs/全部子目录
# ═══════════════════════════════════════════════════════════

def _parse_reference_txt(filepath):
    """Parse a non-event TXT file (key: value format). Returns dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {}
    current_key = None
    current_value = []

    for line in lines:
        if not line.strip():
            continue
        if line.strip().startswith('#'):
            continue
        m = re.match(r'^([^：:\s][^：:]*?)[：:]\s*(.*)', line)
        if m and not line.lstrip().startswith(('-', '•', '>', '·')):
            if current_key:
                data[current_key] = '\n'.join(current_value).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_value = [val] if val else []
        else:
            current_value.append(line.rstrip('\n'))

    if current_key:
        data[current_key] = '\n'.join(current_value).strip()

    return data


def _make_ref_entry(data, order_start, uid=None, position=1, depth=None):
    """Create a world book entry from a parsed reference TXT.
    Maps TXT fields to JSON entry format (参照 我的妹妹...ver1.41).

    Args:
        position: 插入段位 (0=角色定义前, 1=角色定义后, 4=深度上下文)
        depth: 段位内优先级。None时从TXT '注入深度'字段读取
    """
    name = data.get('名称', 'Unknown')
    keywords_str = data.get('触发关键词', '')
    always_on = data.get('始终触发', '否').strip() == '是'
    if depth is None:
        depth = int(data.get('注入深度', '3'))
    content = data.get('内容', '')
    # Strip leading "- " bullets from content lines (参照格式：纯文本换行，不bullet)
    content = re.sub(r'^[ \t]*-[ \t]', '', content, flags=re.MULTILINE)

    # Parse keywords: comma-separated → list
    if keywords_str.strip():
        keys = [k.strip() for k in keywords_str.split(',') if k.strip()]
    else:
        keys = []

    return make_entry(
        uid=uid,
        keys=keys,
        keysecondary=[],
        comment=name,
        content=content,
        order=order_start,
        constant=always_on,
        probability=100,
        selective=True,
        depth=depth,
        position=position,
    )


def load_reference_entries():
    """Scan all docs/ subdirectories for TXT files and generate entries.
    Returns list of entries in display order.

    Position assignment (参照 俺妹 ver1.41 健康版):
    - System instructions (事件追踪/游戏状态/叙述风格) → pos=4
    - chapter/ constant=true → pos=0 (world-building constants)
    - Other dirs constant=true → pos=0 (overview tables)
    - Other dirs constant=false → pos=1 (triggered reference)
    """
    entries = []
    order = 100

    # System instructions: special depth/order at pos=4
    SYSTEM_INSTRUCTIONS = {
        '事件追踪指令':  {'depth': 0, 'order': 999},
        '游戏状态界面':  {'depth': 0, 'order': 998},
        '叙述风格指令':  {'depth': 1, 'order': 100},
    }

    # Supplementary systems: pos=4, depth=4 (参照俺妹 好感度分级系统)
    SUPPLEMENTARY_SYSTEMS = {
        '好感度分级系统总览': {'position': 4, 'depth': 4, 'order': 100},
    }

    # Subdirectory order and metadata
    ref_dirs = [
        ('chapter',    True),    # (dir_name, all_constant)
        ('magic',      False),
        ('world',      False),
        ('system',     False),
        ('character',  False),
        ('location',   False),
        ('creature',   False),
        ('npc',        False),
        ('affection',  False),
    ]

    for subdir_name, all_constant in ref_dirs:
        dir_path = os.path.join(DOCS_DIR, subdir_name)
        if not os.path.isdir(dir_path):
            continue

        # Collect TXT files, sort: overview files first (starting with _)
        txt_files = [f for f in os.listdir(dir_path)
                     if f.upper().endswith('.TXT')
                     and not f.startswith('_TEMPLATE')]
        txt_files.sort(key=lambda f: (not f.startswith('_'), f))

        for fname in txt_files:
            fp = os.path.join(dir_path, fname)
            data = _parse_reference_txt(fp)

            # Skip files missing required fields
            if '名称' not in data:
                print(f'  ⚠ 跳过（无名称字段）: {subdir_name}/{fname}')
                continue

            always_on = data.get('始终触发', '否').strip() == '是'
            name = data.get('名称', 'Unknown')

            # Determine position, depth, order
            # 参照俺妹健康版：同position+depth的条目共享相同order
            if name in SYSTEM_INSTRUCTIONS:
                si = SYSTEM_INSTRUCTIONS[name]
                entry = _make_ref_entry(data, si['order'], position=4, depth=si['depth'])
            elif name in SUPPLEMENTARY_SYSTEMS:
                ss = SUPPLEMENTARY_SYSTEMS[name]
                entry = _make_ref_entry(data, ss['order'], position=ss['position'], depth=ss['depth'])
            elif always_on:
                # All constant entries → pos=0, depth=4, order=100
                entry = _make_ref_entry(data, 100, position=0, depth=4)
            else:
                # Non-constant entries → pos=1, depth=4, order=100
                entry = _make_ref_entry(data, 100, position=1, depth=4)

            entry['group'] = subdir_name
            entries.append(entry)

    return entries


# ─── 工具函数 ───────────────────────────────────────────
def make_entry(uid, keys, comment, content, order,
               constant=False, probability=100, use_probability=True,
               keysecondary=None, selective=True, position=1,
               group="", depth=4):
    """创建一条 SillyTavern 原生格式的世界书条目（对齐俺妹ver1.41健康版格式）。"""
    return {
        "uid": uid,
        "key": keys,
        "keysecondary": keysecondary if keysecondary is not None else [],
        "comment": comment,
        "content": content,
        "constant": constant,
        "vectorized": False,
        "selective": selective,
        "selectiveLogic": 0,
        "addMemo": True,
        "order": order,
        "position": position,
        "disable": False,
        "excludeRecursion": False,
        "preventRecursion": False,
        "matchPersonaDescription": False,
        "matchCharacterDescription": False,
        "matchCharacterPersonality": False,
        "matchCharacterDepthPrompt": False,
        "matchScenario": False,
        "matchCreatorNotes": False,
        "delayUntilRecursion": False,
        "probability": probability,
        "useProbability": use_probability,
        "depth": depth,
        "group": group,
        "groupOverride": False,
        "groupWeight": 100,
        "scanDepth": None,
        "caseSensitive": None,
        "matchWholeWords": None,
        "useGroupScoring": False,
        "automationId": "",
        "role": None,
        "sticky": 0,
        "cooldown": 0,
        "delay": 0,
        "displayIndex": 0,
        "outletName": "",
        "ignoreBudget": False,
        "extensions": {
            "position": position,
            "exclude_recursion": False,
            "display_index": 0,
            "probability": probability,
            "useProbability": use_probability,
            "depth": depth,
            "selectiveLogic": 0,
            "group": group,
            "group_override": False,
            "group_weight": 100,
            "prevent_recursion": False,
            "delay_until_recursion": False,
            "scan_depth": None,
            "match_whole_words": None,
            "use_group_scoring": False,
            "case_sensitive": None,
            "automation_id": "",
            "role": 0,
            "vectorized": False,
            "sticky": 0,
            "cooldown": 0,
            "delay": 0,
            "match_persona_description": False,
            "match_character_description": False,
            "match_character_personality": False,
            "match_character_depth_prompt": False,
            "match_scenario": False,
            "match_creator_notes": False,
            "triggers": [],
            "ignore_budget": False,
        },
        "triggers": [],
        "characterFilter": {
            "isExclude": False,
            "names": [],
            "tags": [],
        },
    }



def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def backup_existing():
    """备份当前版本号文件（如果已存在同名文件）到 backup/ 目录

    当重新构建同一个版本号时，先把已存在的同名文件备份为时间戳版本，
    防止意外覆盖。不同版本号因为文件名不同，会自然共存。
    """
    if not os.path.exists(JSON_PATH):
        print(f"[backup] {os.path.basename(JSON_PATH)} 不存在，跳过备份")
        return None

    ensure_dir(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"old_{VERSION_TAG}_{timestamp}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(JSON_PATH, backup_path)
    print(f"[backup] 已备份旧版 {os.path.basename(JSON_PATH)} → backup/{backup_name}")
    return backup_path



# ─── 条目定义函数 ───────────────────────────────────────

def build(dry_run=False):
    """主构建函数

    Args:
        dry_run: 如果为 True，仅验证不写入文件
    """
    print("=" * 60)
    print(f"  Eldoria Worldbook Builder  [{VERSION_TAG}]")
    print("=" * 60)

    # ─── 条目注册表 ──────────────────────────────────────
    # 新增事件函数只需在此列表添加一行 (fn, label) 即可自动纳入构建
    # 不再需要手动管理 uid 范围、变量名和合并行
    from collections import OrderedDict
    _REGISTRY = OrderedDict()  # label → entries list, 保持插入顺序

    def collect(entries_fn, label, step=""):
        """调用条目函数，打印统计，注册到构建列表"""
        try:
            result = entries_fn()
        except Exception as e:
            print(f"[error] {label}: {e}")
            result = []
        count = len(result)
        prefix = f"[step {step}]" if step else "      "
        print(f"{prefix} {label}: {count} 条")
        _REGISTRY[label] = result
        return result

    # ─── 条目收集（V10.0: 全TXT驱动） ──────────────────────

    # 1. Reference entries: docs/chapter/ + character/ + world/ + creature/ + location/ + npc/
    ref_entries = load_reference_entries()
    ref_const = sum(1 for e in ref_entries if e.get('constant'))
    print(f"[step 1] Reference条目 (docs/子目录TXT驱动): {len(ref_entries)} 条 ({ref_const} 始终触发)")

    # 2. Event entries: docs/event/{章节}/*.TXT
    # Events loaded via _REGISTRY collector (keeps existing mechanism)
    event_labels = []
    for ch_dir, ch_label in [('0：序章', '2ch0'), ('1：试探和暧昧', '2ch1'),
                              ('2：挑逗和接受', '2ch2'), ('3：渐进接触', '2ch3'),
                              ('4：跨线', '2ch4'), ('5：享受和掌控', '2ch5'),
                              ('6：放纵', '2ch6'), ('7：终局', '2ch7'),
                              ('8：后日谈', '2ch8')]:
        label = f'events_{ch_dir}'
        collect(lambda d=ch_dir: _get_md_entries(d, 'event'), f"事件-{ch_dir}·TXT驱动", label)
        event_labels.append(label)

    # 3. V10.0: 所有条目均由TXT驱动，无需硬编码基础条目
    # first_mes 是JSON顶层字段，非条目

    # ─── 合并 + 分配 uid ──────────────────────────────────
    all_entries = list(ref_entries)
    for label, entries in _REGISTRY.items():
        all_entries.extend(entries)

    # 为 uid=None 的条目自动分配连续 uid
    next_uid = max((e.get("uid", -1) for e in all_entries if e.get("uid") is not None), default=-1) + 1
    auto_assigned = 0
    for e in all_entries:
        if e.get("uid") is None:
            e["uid"] = next_uid
            next_uid += 1
            auto_assigned += 1
    if auto_assigned:
        print(f"      [auto-uid] 自动分配 {auto_assigned} 个 uid")

    # 确保 uid 连续
    all_entries.sort(key=lambda e: e.get("uid", 0))
    for i, e in enumerate(all_entries):
        e["uid"] = i
    all_entries.sort(key=lambda e: e.get("uid", 0))
    print(f"[step 3] 合并后总计: {len(all_entries)} 条")

    # 3.5. 永久触发 — 基于 constant=True 字段（不再硬编码 uid）
    constant_uids = [e["uid"] for e in all_entries if e.get("constant")]
    for e in all_entries:
        if e.get("constant"):
            e["constant"] = True
    if constant_uids:
        print(f"[step 3.5] 永久触发: uid {sorted(constant_uids)}")

    # 4. 验证
    errors = validate_entries(all_entries)
    if errors:
        print(f"\n[validation] 发现 {len(errors)} 个问题:")
        for err in errors:
            print(f"  - {err}")
        if not dry_run:
            print("[error] 验证失败，构建终止")
            return False
    else:
        print(f"[step 4] 验证通过: {len(all_entries)} 条条目全部合法")

    # 5. 组装完整 JSON
    data = assemble_json(all_entries)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    print(f"[step 5] JSON 组装完成: {len(json_str):,} 字符")

    if dry_run:
        print("\n[dry-run] 验证通过，未写入文件")
        return True

    # 6. 备份现有文件（如果根目录已有同名版本号文件，先备份到 backup/）
    backup_existing()

    # 7. 写入版本化发布快照 — 这是唯一的主输出文件
    #    文件路径 = 项目根目录 / Eldoria_V{VERSION}.json
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        f.write(json_str)
        f.write('\n')
    print(f"[step 6] 主输出文件: {os.path.basename(JSON_PATH)}")

    # 8. 同时在 backup/ 目录下生成一份时间戳副本
    #    用途: 同一版本号多次重新构建时保留中间过程的副本
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_ts_name = f"{VERSION_TAG}_{timestamp}.json"
    backup_ts_path = os.path.join(BACKUP_DIR, backup_ts_name)
    ensure_dir(BACKUP_DIR)
    with open(backup_ts_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
        f.write('\n')
    print(f"[step 7] 时间戳备份: backup/{backup_ts_name}")

    print(f"\n{'=' * 60}")
    print(f"  构建完成! 版本: {VERSION_TAG}")
    print(f"  共 {len(all_entries)} 条条目, 大小: {len(json_str):,} 字符")
    print(f"  主文件: output/{os.path.basename(JSON_PATH)}")
    print(f"  备份目录: backup/")
    print(f"{'=' * 60}")
    return True


def validate_entries(entries):
    """验证条目列表的完整性和一致性"""
    errors = []
    seen_uids = set()

    required_fields = [
        "uid", "key", "content", "comment", "constant",
        "selective", "probability", "order", "position",
        "group", "useProbability",
    ]

    for e in entries:
        uid = e.get("uid")

        if uid in seen_uids:
            errors.append(f"uid {uid} 重复")
        seen_uids.add(uid)

        for field in required_fields:
            if field not in e:
                errors.append(f"uid {uid} 缺少字段: {field}")

        content = e.get("content", "")
        if not content or not content.strip():
            errors.append(f"uid {uid} content 为空")

        # 始终触发条目不依赖key匹配，豁免key检查
        keys = e.get("key", [])
        if not e.get("constant"):
            if not keys:
                errors.append(f"uid {uid} key 为空")
            if len(keys) < 1:
                errors.append(f"uid {uid} key 数量不足 (至少1个): {len(keys)}")

        prob = e.get("probability", -1)
        if not (0 <= prob <= 100):
            errors.append(f"uid {uid} probability 超出范围: {prob}")

    sorted_uids = sorted(seen_uids)
    expected = list(range(len(sorted_uids)))
    if sorted_uids != expected:
        missing = set(expected) - set(sorted_uids)
        if missing:
            errors.append(f"缺少 uid: {sorted(missing)}")

    return errors


def assemble_json(entries):
    """将条目列表组装为 SillyTavern 原生世界书 JSON 格式（对齐俺妹ver1.41健康版）"""
    entries_dict = {}
    for e in entries:
        entries_dict[str(e["uid"])] = e
    return {
        "entries": entries_dict,
        "originalData": {
            "entries": entries_dict,
            "name": CHAR_NAME,
        },
        "_meta": {
            "version": VERSION_TAG,
            "version_short": VERSION,
            "spec": SPEC,
            "spec_version": SPEC_VERSION,
            "entry_count": len(entries),
            "uid_range": f"0-{max((e.get('uid', 0) for e in entries), default=0)}",
            "build_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "authority_source": "docs/子目录TXT文件 + build_eldoria.py (全TXT驱动)",
            "note": "JSON是派生产物，请勿手动编辑。修改请通过TXT文件+构建脚本完成。",
        },
    }


def validate_existing():
    """仅验证当前版本号文件的合法性（不构建）

    检查项目根目录中的 Eldoria_V{VERSION}.json 是否合法。
    """
    if not os.path.exists(JSON_PATH):
        print(f"[error] {os.path.basename(JSON_PATH)} 不存在")
        return False

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = list(data.get("entries", {}).values())
    if not entries:
        print(f"[error] 无法解析 {os.path.basename(JSON_PATH)}")
        return False

    errors = validate_entries(entries)
    if errors:
        print(f"\n发现 {len(errors)} 个问题:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"验证通过: {len(entries)} 条条目全部合法")
        return True


# ─── 入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        build(dry_run=True)
    elif "--validate" in sys.argv:
        validate_existing()
    else:
        success = build()
        sys.exit(0 if success else 1)