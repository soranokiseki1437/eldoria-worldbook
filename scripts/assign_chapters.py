# -*- coding: utf-8 -*-
"""
assign_chapters.py — 章节-事件映射权威数据源
=============================
DEFAULT_CHAPTERS 是章节↔事件映射的唯一权威数据。
被 assemble_md.py / update_chapter_map.py / build_eldoria.py 导入使用。

NTRS路线(N) = 第12-20章
被动NTR路线(PN) = 第22-30章
主线通用 = 第1-11章

用法:
  python scripts/assign_chapters.py              # 调用 assemble_md 刷新05MD索引
  python scripts/assign_chapters.py --check      # 仅验证 DEFAULT_CHAPTERS 数据完整性
"""

import re, sys, os
from datetime import datetime
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# 权威章节定义
# 手动维护：增删改事件时，在此处调整事件所属章节的列表。
# 修改后运行 assign_chapters.py 即可同步所有下游数据。
# ============================================================
DEFAULT_CHAPTERS = OrderedDict()

# —— 第1-11章：主线通用 ——
# E系列（纯数字）事件分布在前期章节
_main = [
    (1, '林间空地的苏醒', ['E1', 'W1'],
     '黎恩在陌生的森林中醒来，初遇Seraphina'),
    (2, '森林的低语', ['E2', 'E3', 'P1', 'P2'],
     '第一场战斗→心木废墟初探→深度情感交流'),
    (3, '心木废墟', ['E4', 'P3', 'W2'],
     '低语林地的幻影→第一次约会→净化仪式'),
    (4, 'VII班同伴的到来', ['E5', 'E6', 'E7', 'P4', 'P5'],
     '亚莉莎、劳拉&乔治、艾玛&菲陆续抵达→守护者契约'),
    (5, '森林的庆典', ['E8', 'W3'],
     '森林庆典第一晚→银流河净化'),
    (6, '信任的建立', ['E9', 'P6', 'W4'],
     '古老先灵低语→净化仪式准备→腐化区域扩张'),
    (7, '鬼之力的觉醒', ['E10', 'P7', 'W5'],
     '黑兔亚尔缇娜登场→与Thalion战斗→先灵第二次对话'),
    (8, '路线分化', ['E11', 'E12', 'E13', 'E14', 'E15', 'P8', 'P9', 'W6'],
     '艾德里安/雷恩/凯尔/爱丽榭/玲登场→温泉→守护夜→森林意志'),
    (9, '纯爱深化', ['P10', 'P11', 'P13', 'P14', 'W7'],
     '古老先灵启示→终极战斗准备→契约之夜→温泉清晨→同伴日常'),
    (10, 'Thalion的阴影', ['P12', 'P15', 'P16', 'W8'],
     '终局抉择→鬼之圣光交融→足下誓言→雾帷边缘异象'),
    (11, '决战前夕', ['P17', 'P18', 'P19', 'P20', 'P21', 'P22'],
     '决战前夜——纯爱NSFW收尾事件'),
]
for _ch, _t, _ev, _a in _main:
    DEFAULT_CHAPTERS[_ch] = {'title': _t, 'stage': '序章', 'events': _ev, 'anchor': _a}

# —— 断章：未分类事件（G/H/R系列暂存于此，后续细化分配） ——
DEFAULT_CHAPTERS[99] = {
    'title': '断章：通用SFW / 隐藏事件 / 黎恩专属',
    'stage': '通用',
    'events': ['G1','G2','G3','G4','G5','G6','G7',
               'H1','H2','H3','H4',
               'R1','R2','R3','R4','R5','R6','R7','R8'],
    'anchor': '跨章节通用事件：日常互动、隐藏剧情、黎恩个人线——暂未分配到具体章节',
}

# —— 第12-20章：NTRS路线 ——
_ntrs = [
    (12, '坦白与试探', 'A', ['N01','N02','N03','N04','N05','N06','N07','N08','N09','N10','N11','N12'],
     '坦白→边界→注视→足控发现→坐骑蹭触→窗边口交→雷恩铺垫→装睡→雷恩初访→同意触碰→艾察觉→乔治注视'),
    (13, '挑逗的萌芽', 'A→B', ['N13','N14','N15','N16','N17','N18','N19','N20','N21','N22','N23','N24','N25','N26'],
     '凯尔告白→第一次低语者→丝袜展示→扣穴试探→雷恩指交→乔治逃跑→乔治同意→艾指尖→圣光之泉→乔治足交→凯尔臣服'),
    (14, '渐进的接触', 'B', ['N27','N28','N29','N30','N31','N32','N33','N34','N35','N36','N37','N38','N39','N40','N41','N42','N43'],
     '玲口交→玲裸足→桌下之手→菲裸足→桌下之口→树后秘密→双人共享→艾扑克→酒后口交→凯尔乳交→酒后之夜→凯尔再战→黎恩安排→凯尔山洞→乔治的唇→装睡代价→全身被舔→不准丢下'),
    (15, '跨线', 'C', ['N44','N45','N46','N47','N48','N49','N50','N51','N52','N53','N54','N55','N56','N57','N58','N59','N60'],
     '★被干软提问→白丝勾引雷恩→第二次低语者→温柔疗愈选凯尔→第一次被插入(凯尔)→翌日疗愈→走廊绯红→犹豫说不要→桌下吞精→黎恩提议再试→早晨喂奶不痛了→雷恩第二次→弯腰弧度→开裆裤袜→试衣镜前→隐奸设计'),
    (16, '放开', 'D前半', ['N61','N62','N63','N64','N65','N66','N67','N68','N69'],
     '圈子开放→劳拉乳交→姐妹足交→艾德里安本番→亚莉莎→四人共享→劳拉白袜→艾玛手交实证→艾玛传送门→菲的早晨'),
    (17, '享受', 'D后半', ['N70','N71','N72','N73','N74','N75','N76','N77','N78','N79','N80'],
     '醉诱→温泉羞辱→密林即兴→菲本番→镜湖→胜利3P→温泉晕厥→艾玛吊带袜→亚莉莎本番→花田3P→玲本番'),
    (18, '极限', 'E前半', ['N81','N82','N83','N84','N85','N86','N87','N88','N89','N90'],
     '主动手交→艾德里安舌→雷恩裸足→劳拉骑士→雷恩跪礼→凯尔独白→第一次自己决定→凯尔观摩→主动口交→桌下之手'),
    (19, '反转', 'E后半', ['N91','N92','N93','N94','N95','N96','N97','N98','N99','N100'],
     '桌下之口→凯尔邀请→乔治震动棒→腐化迷雾→黑暗乳交→催情茶→低语者轮奸→洗干净回归'),
    (20, '终局', '终局', ['N101','N102','N103'],
     '她的情书→终局抉择'),
]
for _ch, _t, _s, _ev, _a in _ntrs:
    DEFAULT_CHAPTERS[_ch] = {'title': _t, 'stage': _s, 'events': _ev, 'anchor': _a}

# —— 第22-30章：被动NTR路线 ——
_pn = [
    (22, 'PN：裂痕', 'A', ['PN1','PN2','PN3','PN4','PN5'],
     '黎恩缺席→Thalion诱惑→乔治误解→亚莉莎对比→寂寞释放'),
    (23, 'PN：腐蚀', 'A→B', ['PN6','PN7','PN8','PN9','PN10','PN11'],
     'Thalion强迫摸乳→指交→甜言蜜语→腐蚀低语→药与酒→肉体展示'),
    (24, 'PN：沦陷', 'B', ['PN12','PN13','PN14','PN15','PN16','PN17'],
     '被迫手交→指交陷阱→被迫口交→乳间耻辱→半推半就→骑虎难下'),
    (25, 'PN：堕落', 'B→C', ['PN18','PN19','PN20','PN21'],
     '★堕落之夜(Thalion插入)→足交玷污→耳边低语→不敢出声'),
    (26, 'PN：沉溺', 'C→D', ['PN22','PN23','PN24','PN25'],
     '再次找上门→窗外影子→趁他睡着→半开的门'),
    (27, 'PN：觉醒', 'D', ['PN26','PN27','PN28','PN29'],
     '主动口交→镜中自己→野外暴露→主动索求'),
    (28, 'PN：放肆', 'D+', ['PN30','PN31','PN32','PN33'],
     '主动邀约→故意遗留→Thalion伪装→桌下之手'),
    (29, 'PN：巅峰', 'D+巅峰', ['PN34','PN35','PN36'],
     '桌面下的脚→桌下之口→隐乳交'),
    (30, 'PN：终局', '终局', ['PN37'],
     '与Thalion的最终战斗'),
]
for _ch, _t, _s, _ev, _a in _pn:
    DEFAULT_CHAPTERS[_ch] = {'title': _t, 'stage': _s, 'events': _ev, 'anchor': _a}


def parse_all_events(md_text):
    """解析所有事件（任意前缀）"""
    events = []
    for m in re.finditer(
        r'^### 事件([A-Z]*\d{1,3})[：:]([^\n]+)\n\n```yaml\n(.*?)\n```',
        md_text, re.DOTALL | re.MULTILINE
    ):
        events.append({
            'eid': m.group(1), 'title': m.group(2).strip(),
            'yaml_text': m.group(3), 'full_match': m.group(0),
            'start_pos': m.start(), 'end_pos': m.end(),
        })
    return events


def inject_chapter_field(yaml_text, chapter_num):
    """在YAML中注入或更新 所属章节"""
    field = f'第{chapter_num}章'
    # 更新已有
    if re.search(r'^\s*所属章节[：:]', yaml_text, re.MULTILINE):
        return re.sub(r'^\s*所属章节[：:]\s*.+$', f'    所属章节: {field}',
                      yaml_text, flags=re.MULTILINE)
    # 插入到触发条件之后
    m = re.search(r'^(\s*触发条件[：:].+)$', yaml_text, re.MULTILINE)
    if m:
        pos = m.end()
        return yaml_text[:pos] + f'\n    所属章节: {field}' + yaml_text[pos:]
    # 回退：事件行之后
    m = re.search(r'^(\s*事件[：:].+)$', yaml_text, re.MULTILINE)
    if m:
        pos = m.end()
        return yaml_text[:pos] + f'\n    所属章节: {field}' + yaml_text[pos:]
    return yaml_text


def generate_summary():
    """从DEFAULT_CHAPTERS统计事件数量，生成总览"""
    from collections import Counter
    counts = Counter()
    for ch in DEFAULT_CHAPTERS.values():
        for eid in ch['events']:
            pfx = re.match(r'[A-Z]*', eid).group() or 'E'
            counts[pfx] += 1

    lines = ['## 一、事件系统总览（脚本自动生成）', '',
             '```yaml',
             '  事件类型与数量:']
    for pfx, label in [('E', '固定事件（纯数字）'), ('P', '纯爱路线'), ('N', 'NTRS路线'),
                        ('PN', '被动NTR路线'), ('W', '世界事件'),
                        ('G', '通用SFW'), ('H', '隐藏事件'), ('R', '黎恩专属')]:
        if counts[pfx]:
            lines.append(f'    {label}: {counts[pfx]}个')
    lines.append(f'    ──')
    lines.append(f'    总计: {sum(counts.values())}个事件')
    lines.append(f'    NTRS章节: 第12-20章 | 被动NTR章节: 第22-30章 | 断章: 第99章')
    lines.append('```')
    return '\n'.join(lines)


def generate_chapter_architecture():
    """生成章节架构YAML"""
    lines = ['## 章节架构（脚本自动生成，勿手动编辑）', '',
             '> `scripts/assign_chapters.py` 自动生成。修改章节事件列表请编辑脚本中的 DEFAULT_CHAPTERS。', '',
             '```yaml', '章节:']
    for ch_num in sorted(DEFAULT_CHAPTERS.keys()):
        ch = DEFAULT_CHAPTERS[ch_num]
        lines.append(f'  - 编号: {ch_num}')
        lines.append(f'    标题: "{ch["title"]}"')
        lines.append(f'    阶段: {ch["stage"]}')
        lines.append(f'    事件: [{", ".join(ch["events"])}]')
        lines.append(f'    主线锚点: "{ch["anchor"]}"')
    lines.append('```')
    return '\n'.join(lines)


def update_md_file(md_path, dry_run=False):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    events = parse_all_events(md_text)
    print(f"📋 {len(events)} 个事件（N + PN）")

    # 构建 eid → chapter 查找表
    eid_to_chapter = {}
    for ch_num, ch in DEFAULT_CHAPTERS.items():
        for eid in ch['events']:
            eid_to_chapter[eid] = ch_num

    # 注入 所属章节
    replacements = []
    for ev in events:
        ch_num = eid_to_chapter.get(ev['eid'])
        if ch_num is None:
            print(f"  ⚠ {ev['eid']}: 未在章节定义中找到")
            continue
        old_yaml = ev['yaml_text']
        new_yaml = inject_chapter_field(old_yaml, ch_num)
        old_block = ev['full_match']
        new_block = old_block.replace(f'```yaml\n{old_yaml}\n```',
                                      f'```yaml\n{new_yaml}\n```')
        replacements.append((ev['start_pos'], ev['end_pos'], new_block, ev['eid'], ch_num))

    # 从后往前替换
    replacements.sort(key=lambda x: x[0], reverse=True)
    for start, end, new_block, eid, ch_num in replacements:
        md_text = md_text[:start] + new_block + md_text[end:]
        print(f"  ✅ {eid} → 第{ch_num}章")

    print(f"  注入: {len(replacements)} 个事件")

    # 写总览
    summary_text = generate_summary()
    # 替换已有总览块（匹配到下一个 ## 大节标题之前）
    existing_summary = re.search(
        r'\n## 一、事件系统总览.*?\n```\n', md_text, re.DOTALL)
    if existing_summary:
        md_text = md_text[:existing_summary.start()] + '\n' + summary_text + '\n' + md_text[existing_summary.end():]
    else:
        # 在文件头之后插入
        header_end = md_text.find('\n---\n')
        if header_end > 0:
            md_text = md_text[:header_end+5] + '\n' + summary_text + '\n' + md_text[header_end+5:]
    print("  📊 事件总览已更新")

    # 写章节架构
    arch_text = generate_chapter_architecture()
    existing = re.search(
        r'\n## 章节架构（脚本自动生成.*$', md_text, re.DOTALL)
    if existing:
        md_text = md_text[:existing.start()] + '\n' + arch_text + '\n\n' + md_text[existing.end():]
    else:
        # 在七、隐藏事件之前
        pos = md_text.find('\n## 七、隐藏事件')
        if pos > 0:
            md_text = md_text[:pos] + '\n' + arch_text + '\n\n' + md_text[pos:]
        else:
            md_text = md_text.rstrip() + '\n\n' + arch_text + '\n'
    print("  📐 章节架构已更新")

    if dry_run:
        print("\n[干运行] 未修改文件")
        return True

    # 备份
    bak = os.path.join(PROJECT_DIR, 'backups',
                       f'05_事件系统.md.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
    os.makedirs(os.path.dirname(bak), exist_ok=True)
    with open(md_path, 'r', encoding='utf-8') as f:
        with open(bak, 'w', encoding='utf-8') as bf:
            bf.write(f.read())

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_text)

    print(f"\n📦 备份: {bak}")
    print(f"✅ 完成: {len(replacements)} 事件, {len(DEFAULT_CHAPTERS)} 章架构")
    return True


if __name__ == '__main__':
    check_only = '--check' in sys.argv
    if check_only:
        # 仅验证 DEFAULT_CHAPTERS 数据完整性
        total = sum(len(ch_data['events']) for ch_data in DEFAULT_CHAPTERS.values())
        print(f'DEFAULT_CHAPTERS: {len(DEFAULT_CHAPTERS)}章, {total}事件')
        # Check for duplicate event IDs across chapters
        all_eids = []
        for ch_num, ch_data in DEFAULT_CHAPTERS.items():
            for eid in ch_data['events']:
                if eid in all_eids:
                    print(f'  ⚠️ 重复: {eid} (首次在第{all_eids.index(eid)}章)')
                all_eids.append(eid)
        print(f'  无重复事件ID') if len(all_eids) == len(set(all_eids)) else None
        sys.exit(0)
    # 默认：调用 assemble_md 刷新05MD索引
    from assemble_md import assemble_md
    assemble_md()
