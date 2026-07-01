# -*- coding: utf-8 -*-
"""
build_eldoria.py — Eldoria 世界书 JSON 构建脚本 (V10.3)
===========================================================
权威数据源：docs/ 子目录全部TXT文件（chapter/ character/ world/ creature/ location/ npc/ story/）
派生产物：output/Eldoria_V10.3.0.json（本脚本输出，不可手动编辑）

工作流：编辑 docs/ 下的 TXT 文件（权威数据源）→ 运行本脚本 → 产出 JSON

架构 (V10.3):
  - 全TXT驱动，零硬编码条目
  - 输出格式：entries Object(keyed by string uid) + _meta
  - 每条目13字段：uid/key/keysecondary/comment/content/constant/selective/order/position/depth/group
  - 无 extensions/originalData/characterFilter 膨胀
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
from collections import OrderedDict
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
VERSION = "V10.5.0"
VERSION_TAG = f"Eldoria_{VERSION}"  # V10.5.0: 新增excludeRecursion+preventRecursion字段——章节不可递归，概念条目不可递归+防止进一步递归

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
    "一阵剧烈的眩晕将黎恩从混沌中拽了出来。\n\n"
    "他睁开眼睛——不是帝国的天花板，不是士官学院的病房。粗糙的木梁横在头顶，壁炉的火光将摇曳的影子投在墙上。"
    "身下是某种兽类的皮毛，厚实而温暖，散发着草木和烟尘的气味。空气里有一缕草药的苦涩，和森林深处才有的湿润泥土的甜腥。\n\n"
    "他试图坐起来，左臂传来一阵钝痛——鬼之力的残余还在血脉里嗡嗡作响。记忆断裂成碎片："
    "时空裂隙撕裂天空的紫光……被某种力量拖拽着穿过……然后是黑暗。漫长的黑暗。\n\n"
    "\"你醒了。\"\n\n"
    "声音从火炉边传来——低沉、平稳，带着一种不属于人类日常语言节奏的古老韵脚。\n\n"
    "粉发的女性从炉火前转过身来。她的发色不是帝国常见的任何一种粉色——更像是暮色将尽时天空最亮的那一层薄光。"
    "琥珀色的眼睛在火光中微微闪烁，瞳孔深处沉淀着某种只属于活过太多年岁之人才有的沉静。"
    "她的外貌与人类无异，没有童话里精灵的尖耳——但她站在那里，整个木屋的空气都像是被某种更古老的存在轻轻压着。\n\n"
    "\"你在森林中昏迷不醒。你体内有一股力量——不属于圣光，也不像腐化……它在暴走，几乎撕裂了你周围的空气。\""
    "她的目光扫过他的左臂——那是一种审视，但没有敌意。\"我把你带回了这里。你是……从哪里来的？\"\n\n"
    "短暂的沉默。壁炉里一根木柴裂开，炸出一小簇火星。\n\n"
    "窗外，一片被金色光芒环绕的古老森林正等待着黎恩的答案。\n\n"
    "<overall>\n"
    "<chapter_information>\n"
    "当前章节|第1章 林间空地的苏醒——陌生的森林\n"
    "下一章节|第2章\n"
    "章节任务|   {{user}}必须在这片陌生的森林中苏醒，了解自己所在之地，并认识眼前这位自称\"森林守护者\"的女性。\n"
    "章节终止条件|1.   {{user}}完全苏醒并恢复意识。\\n2.   Seraphina完成自我介绍——她是Eldoria最后的精灵守护者。\\n3.   {{user}}了解Eldoria的腐化与圣光的基本情况。\n"
    "在场人物|{{user}}, Seraphina\n"
    "</chapter_information>\n"
    "<StatusBlock>\n"
    "```\n"
    "🕣圣光纪年3472年 6月15日（周三）14时30分 | 🌏林间空地·木屋 | ☁️午后薄雾\n"
    "# Seraphina 年龄: 320岁\n"
    "╒═════\n"
    "💖对{{user}}的好感度:Lv.1|5/100|{礼貌的陌生人——又一个被裂隙拉入的外来者，但那股力量……也许他和别人不一样}\n"
    "📅当前章节: 第1章 林间空地的苏醒——陌生的森林\n"
    "👗 服装: 象牙白亚麻衬衣外罩深棕色皮质胸衣，深绿色长裤塞进及膝皮靴\n"
    "💭 情绪: 审视中带着一丝难以察觉的期待——200年了，没有见过能与圣光产生这种共鸣的人\n"
    "💑 行为: 从火炉边起身，木勺搁在陶罐边缘。琥珀色眼睛平静地注视着{{user}}，保持距离——给陌生人适应空间\n"
    "🤔 对{{user}}的想法: 他体内的力量和圣光产生了共鸣。不属于腐化，也不完全像圣光……值得观察\n"
    "🙀 Tips: 已独自守护森林200年——她的耐心和孤独一样深\n"
    "╘═════\n"
    "```\n"
    "</StatusBlock>\n"
    "</overall>"
)


# ═══════════════════════════════════════════════════════════
# 通用MD事件加载器 — 零硬编码，读全文件，按前缀过滤
# ═══════════════════════════════════════════════════════════
_ALL_EVENTS_CACHE = None


def _load_all_events():
    """从 docs/story/{prefix}/*.TXT 读取所有章节，返回{N##: {title, content, ...}, ...}"""
    global _ALL_EVENTS_CACHE
    if _ALL_EVENTS_CACHE is not None:
        return _ALL_EVENTS_CACHE

    import re as _re
    import glob as _glob

    _event_dir = os.path.join(PROJECT_DIR, 'docs', 'story')
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

            # 构建 content（对齐俺妹ver1.41 — 仅三个新字段：核心目标/任务/终止条件）
            import re as _re_ch
            _ch_num = _re_ch.search(r'\d+', _eid)
            _ch_n = int(_ch_num.group()) if _ch_num else 0
            _ch_label = f'第{_ch_n}章'

            _core = _data.get('核心', '')
            _situation = _data.get('情境', '')
            _mission = _data.get('章节任务', '')
            _end_cond = _data.get('章节终止条件', '')
            # 章节任务 / 章节终止条件 由LLM逐章写入TXT，构建脚本只读取不推导
            # 章节核心目标 由 _core 直接填充（见下方 _lines 组装）

            _lines = [
                '<章节剧情>',
                f'[章节编号]: {_ch_label}',
                f'[章节标题]: {_ch_label}：{_title}',
                '',
                '[章节核心目标]:',
                _core if _core else '（待填写）',
                '',
                '[章节任务]:',
                _mission if _mission else '（待填写）',
                '',
                '[章节终止条件]:',
            ]
            if _end_cond:
                for _ec in _end_cond.split('\n'):
                    _ec = _ec.strip()
                    if _ec:
                        _lines.append(_ec)
            else:
                _lines.append('（待填写）')

            # Eldoria补充信息（NSFW/性行为等级等）
            _eldoria_extra = []
            for _key in ['NSFW', '性行为等级', '阶段', '第三者', '黎恩知情', '占有欲确认', '好感影响', '情境']:
                if _key in _data and _data[_key]:
                    _eldoria_extra.append(f'[{_key}]: {_data[_key]}')
            if _eldoria_extra:
                _lines.append('')
                _lines.append('[补充信息]:')
                _lines.extend(_eldoria_extra)

            _lines.append('</章节剧情>')
            _content = '\n'.join(_lines)
            # Strip leading "- " bullets from content (参照格式：纯文本换行)
            _content = _re.sub(r'^[ \t]*-[ \t]', '', _content, flags=_re.MULTILINE)
            # Also strip "- " immediately after "：" (情境：- xxx → 情境：xxx)
            _content = _re.sub(r'：- ', '：', _content)

            _ALL_EVENTS_CACHE[_eid] = {
                'title': _title,
                'content': _content,
                'comment': f'{_ch_label} {_title}',
                'prefix': _prefix,
                'third_party': _third_party,
                'sex_act': _sex_act,
                'phase': _phase,
                'ch_label': _ch_label,
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


def _auto_keys(chapter_id, data):
    """章节条目关键词：照抄俺妹ver1.41——单key "第N章" 格式。

    参考文件所有章节条目仅用1个key，selectiveLogic=0(OR)即命中即触发。
    """
    import re as _re
    _num = _re.search(r'\d+', chapter_id)
    _n = _num.group() if _num else chapter_id
    try:
        _n_int = int(_n)
    except ValueError:
        _n_int = int(_n) if _n.isdigit() else 0
    return [f'第{_n_int}章']


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
        章节递归属性：excludeRecursion=True(不可递归), preventRecursion=False(可触发下级条目)
        （对齐俺妹ver1.41——事件与系统指令同处position=4，已验证可行）
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
            excludeRecursion=True,
            preventRecursion=False,
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


def _make_ref_entry(data, order_start, uid=None, position=1, depth=None, header_prefix=None):
    """Create a world book entry from a parsed reference TXT.
    Maps TXT fields to JSON entry format (参照 我的妹妹...ver1.41).

    Args:
        position: 插入段位 (0=角色定义前, 1=角色定义后, 4=深度上下文)
        depth: 段位内优先级。None时从TXT '注入深度'字段读取
        header_prefix: 非始终触发条目的自我标识头部（参照俺妹ver1.41 — 角色卡/地点资料等）
    """
    name = data.get('名称', 'Unknown')
    keywords_str = data.get('触发关键词', '')
    always_on = data.get('始终触发', '否').strip() == '是'
    if depth is None:
        depth = int(data.get('注入深度', '3'))
    content = data.get('内容', '')
    # Strip leading "- " bullets from content lines (参照格式：纯文本换行，不bullet)
    content = re.sub(r'^[ \t]*-[ \t]', '', content, flags=re.MULTILINE)

    # Prepend self-identifying header (参照俺妹ver1.41)
    # 所有条目都需要头部——无论始终触发还是选择性触发——让AI知道内容描述的是什么
    if header_prefix:
        content = f"# {header_prefix}：{name}\n\n{content}"

    # Parse keywords: comma-separated → list
    if keywords_str.strip():
        keys = [k.strip() for k in keywords_str.split(',') if k.strip()]
    else:
        keys = []

    # 递归属性（参照俺妹ver1.41设计）：
    # - constant条目：递归机制对其无意义，双false
    # - 非constant概念条目（角色/地点/生物等）：不可递归+防止进一步递归
    if always_on:
        _exclude_rec = False
        _prevent_rec = False
    else:
        _exclude_rec = True
        _prevent_rec = True

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
        excludeRecursion=_exclude_rec,
        preventRecursion=_prevent_rec,
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
        '章节追踪指令':        {'depth': 0, 'order': 999},
        '游戏状态界面':        {'depth': 0, 'order': 998},
        '叙述风格指令':        {'depth': 1, 'order': 100},
        '世界时间并行和隐奸':  {'depth': 1, 'order': 100},
    }

    # Supplementary systems: pos=4, depth=4 (参照俺妹 好感度分级系统)
    SUPPLEMENTARY_SYSTEMS = {
        '好感度分级系统总览': {'position': 4, 'depth': 4, 'order': 100},
    }

    # 非始终触发条目的自我标识头部（参照俺妹ver1.41）
    # 始终激活条目（constant）不需要头部；选择性条目被递归激活时才需要
    HEADER_PREFIX = {
        'character':  '角色卡',
        'npc':        '人物卡',
        'location':   '地点资料',
        'creature':   '生物资料',
        'magic':      '魔法资料',
        'world':      '世界资料',
        'system':     '系统资料',
        'affection':  '好感度资料',
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

            hpfx = HEADER_PREFIX.get(subdir_name)

            # Determine position, depth, order
            # 参照俺妹健康版：同position+depth的条目共享相同order
            if name in SYSTEM_INSTRUCTIONS:
                si = SYSTEM_INSTRUCTIONS[name]
                entry = _make_ref_entry(data, si['order'], position=4, depth=si['depth'], header_prefix=hpfx)
            elif name in SUPPLEMENTARY_SYSTEMS:
                ss = SUPPLEMENTARY_SYSTEMS[name]
                entry = _make_ref_entry(data, ss['order'], position=ss['position'], depth=ss['depth'], header_prefix=hpfx)
            elif always_on:
                # All constant entries → pos=0, depth=4, order=100
                entry = _make_ref_entry(data, 100, position=0, depth=4, header_prefix=hpfx)
            else:
                # Non-constant entries → pos=1, depth=4, order=100
                entry = _make_ref_entry(data, 100, position=1, depth=4, header_prefix=hpfx)

            # group 已在 make_entry 中设为 ""，直接添加
            entries.append(entry)

    return entries


# ─── 工具函数 ───────────────────────────────────────────
def make_entry(uid, keys, comment, content, order,
               constant=False, probability=100, use_probability=True,
               keysecondary=None, selective=True, position=1,
               group="", depth=4,
               excludeRecursion=True, preventRecursion=True):
    """创建一条世界书条目 — V10.5精简13字段格式。

    输出字段：uid/key/keysecondary/comment/content/constant/
    selective/order/position(整数0/1/4)/depth/group/
    excludeRecursion/preventRecursion。
    probability/use_probability 保留签名兼容但不出现在输出中。

    excludeRecursion (不可递归): true=不被其他条目递归激活
    preventRecursion  (防止进一步递归): true=激活后不触发下级递归扫描
    """
    _ks = keysecondary if keysecondary is not None else []

    return OrderedDict([
        ("uid", uid),
        ("key", keys),
        ("keysecondary", _ks),
        ("comment", comment),
        ("content", content),
        ("constant", constant),
        ("selective", selective),
        ("order", order),
        ("position", position),
        ("depth", depth),
        ("group", group),
        ("excludeRecursion", excludeRecursion),
        ("preventRecursion", preventRecursion),
    ])



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

    # 2. Chapter entries: docs/story/{章节}/*.TXT
    # Events loaded via _REGISTRY collector (keeps existing mechanism)
    event_labels = []
    for ch_dir, ch_label in [('0：序章', '2ch0'), ('1：试探和暧昧', '2ch1'),
                              ('2：挑逗和接受', '2ch2'), ('3：渐进接触', '2ch3'),
                              ('4：跨线', '2ch4'), ('5：享受和掌控', '2ch5'),
                              ('6：放纵', '2ch6'), ('7：终局', '2ch7'),
                              ('8：后日谈', '2ch8')]:
        label = f'events_{ch_dir}'
        collect(lambda d=ch_dir: _get_md_entries(d, 'chapter'), f"章节-{ch_dir}·TXT驱动", label)
        event_labels.append(label)

    # 3. V10.0: 所有条目均由TXT驱动，无需硬编码基础条目
    # first_mes 是JSON顶层字段，非条目

    # ─── 合并 + 分配 id ──────────────────────────────────
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

    # 3.5. 永久触发 — 基于 constant=True 字段
    constant_ids = [e["uid"] for e in all_entries if e.get("constant")]
    for e in all_entries:
        if e.get("constant"):
            e["constant"] = True
    if constant_ids:
        print(f"[step 3.5] 永久触发: uid {sorted(constant_ids)}")

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

    # 4.5 V10.5精简格式 — 13字段条目，无extensions/characterFilter/originalData膨胀
    # 每条结构开销 ~90 bytes（vs 俺妹43字段 ~945 bytes/条 vs V10.2.0 ~95 bytes/条）
    struct_overhead = len(json.dumps(OrderedDict([(k, None) for k in [
        "uid","key","keysecondary","comment","content","constant",
        "selective","order","position","depth","group",
        "excludeRecursion","preventRecursion",
    ]]), ensure_ascii=False))
    print(f"[step 4.5] 精简格式 — 13字段/条, 结构开销 ~{struct_overhead} bytes/条")

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
    """验证条目列表的完整性和一致性（V10.5精简13字段格式）"""
    errors = []
    seen_uids = set()

    required_fields = [
        "uid", "key", "content", "comment", "constant",
        "selective", "order", "position", "depth", "group",
        "excludeRecursion", "preventRecursion",
    ]

    for e in entries:
        euid = e.get("uid")

        if euid in seen_uids:
            errors.append(f"uid {euid} 重复")
        seen_uids.add(euid)

        for field in required_fields:
            if field not in e:
                errors.append(f"uid {euid} 缺少字段: {field}")

        content = e.get("content", "")
        if not content or not content.strip():
            errors.append(f"uid {euid} content 为空")

        # 始终触发条目不依赖key匹配，豁免key检查
        keys = e.get("key", [])
        if not e.get("constant"):
            if not keys:
                errors.append(f"uid {euid} key 为空")
            if len(keys) < 1:
                errors.append(f"uid {euid} key 数量不足 (至少1个): {len(keys)}")

    sorted_uids = sorted(seen_uids)
    expected = list(range(len(sorted_uids)))
    if sorted_uids != expected:
        missing = set(expected) - set(sorted_uids)
        if missing:
            errors.append(f"缺少 uid: {sorted(missing)}")

    return errors


def assemble_json(entries):
    """将条目列表组装为世界书 JSON（V10.3精简格式：entries Object + _meta）。

    entries 为 OBJECT keyed by string uid（V10.2.0验证可行）。
    无 extensions/characterFilter/originalData 膨胀。
    """
    entries_obj = OrderedDict()
    for e in entries:
        uid_str = str(e.get("uid", 0))
        entries_obj[uid_str] = e

    return OrderedDict([
        ("entries", entries_obj),
        ("_meta", OrderedDict([
            ("version", VERSION_TAG),
            ("version_short", VERSION),
            ("spec", SPEC),
            ("spec_version", SPEC_VERSION),
            ("entry_count", len(entries)),
            ("uid_range", f"0-{len(entries) - 1}"),
            ("build_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("authority_source", "docs/子目录TXT文件 + build_eldoria.py (全TXT驱动)"),
            ("note", "JSON是派生产物，请勿手动编辑。修改请通过TXT文件+构建脚本完成。"),
        ])),
    ])


def validate_existing():
    """仅验证当前版本号文件的合法性（不构建）

    检查 output/ 中的 Eldoria_V{VERSION}.json 是否合法。
    """
    if not os.path.exists(JSON_PATH):
        print(f"[error] {os.path.basename(JSON_PATH)} 不存在")
        return False

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    raw_entries = data.get("entries", {})
    if isinstance(raw_entries, list):
        entries = raw_entries
    else:
        entries = list(raw_entries.values())
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