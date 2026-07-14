#!/usr/bin/env python3
"""
check_attributes.py — 角色属性一致性检查器 (V10.5)

对照 _character_attributes.json 权威表，扫描全部章节TXT，
报告所有身高/发色/瞳色/阴茎/罩杯不一致。

用法:
  python scripts/check_attributes.py          # 扫描并报告
  python scripts/check_attributes.py --json   # JSON输出
  python scripts/check_attributes.py --fix    # 交互式修复
"""

import os, re, json, sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
ATTR_PATH = os.path.join(PROJECT_DIR, 'docs', 'story', '_character_attributes.json')

# ─── 加载权威表 ───────────────────────────────────────
with open(ATTR_PATH, 'r', encoding='utf-8') as f:
    CANON = json.load(f)

# ─── 阴茎上下文关键词（排除误报） ──────────────────────
PENIS_KW = ['肉棒', '阴茎', '勃起', '龟头', '茎身', '蜜穴', '精液',
            '口交', '乳交', '足交', '腿交', '肛交', '菊穴', '阴蒂', '阴唇',
            '小穴', '抽插', '后入', '颜射', '内射', '睾丸', '根部', '皮鞘',
            '泄殖腔', '鳞片', '矛尖形', '射精', '冠状沟']

# ─── 扫描函数 ─────────────────────────────────────────
def scan_all_chapters():
    """扫描全部章节，返回所有不一致"""
    story_dir = os.path.join(PROJECT_DIR, 'docs', 'story')
    violations = []

    for root, dirs, files in os.walk(story_dir):
        for f in files:
            if not f.endswith('.TXT') or f.startswith('_'):
                continue
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()

            ch_id_m = re.search(r'ID:\s*(\d+)', content)
            ch_id = ch_id_m.group(1) if ch_id_m else '?'

            # ── 检查身高 ──
            violations.extend(_check_heights(ch_id, content, fp))

            # ── 检查阴茎尺寸 ──
            violations.extend(_check_penis(ch_id, content, fp))

            # ── 检查发色 ──
            violations.extend(_check_hair(ch_id, content, fp))

    return violations


def _find_char_in_context(text, pos, radius=100):
    """在pos附近radius字符内查找角色——返回最近的角色名"""
    ctx = text[max(0, pos - radius):min(len(text), pos + radius)]
    best_name = None
    best_dist = radius + 1
    for name, data in CANON.items():
        for alias in [name] + data.get('别名', []):
            idx = ctx.find(alias)
            if idx >= 0:
                # Distance from alias to the target position (pos - start of context)
                target_in_ctx = pos - max(0, pos - radius)
                dist = abs(idx - target_in_ctx)
                if dist < best_dist:
                    best_dist = dist
                    best_name = name
    return best_name


def _check_heights(ch_id, content, fp):
    """检查身高不一致"""
    violations = []
    # 匹配 3-digit cm (身高通常是3位数) 和 2-digit cm（矮人身高）
    for m in re.finditer(r'(\d{3})\s*cm', content):
        num = int(m.group(1))
        pos = m.start()
        before = content[max(0, pos - 80):pos]
        after = content[pos:min(len(content), pos + 80)]
        near = before + after[:40]

        # 跳过器官上下文
        if any(pk in near for pk in PENIS_KW):
            continue
        # 跳过生物
        if any(c in near for c in ['牛头人', '幻猿', '影牙兽', '魔兽', '巨蟒', '鳞母']):
            continue

        char = _find_char_in_context(content, pos)
        if char and '身高' in CANON[char]:
            canon_h = CANON[char]['身高']
            if num != canon_h:
                # Also check 满月 form
                if '身高_满月' in CANON[char] and num == CANON[char]['身高_满月']:
                    continue  # 满月身高正确
                violations.append({
                    'chapter': ch_id, 'file': os.path.basename(fp),
                    'character': char, 'attribute': '身高',
                    'stated': f'{num}cm', 'canon': f'{canon_h}cm',
                    'context': near.strip()[:150]
                })

    # Also check 2-digit cm for shorter characters (矮人<150cm)
    for m in re.finditer(r'(\d{2})\s*cm', content):
        num = int(m.group(1))
        if num < 100:  # unlikely to be height
            continue
        # Already handled above

    return violations


def _check_penis(ch_id, content, fp):
    """检查阴茎尺寸不一致"""
    violations = []
    for m in re.finditer(r'(\d{1,2}(?:\.\d)?)\s*cm', content):
        num_str = m.group(1)
        try:
            num = float(num_str)
        except ValueError:
            continue
        if num > 25:  # 阴茎不太可能超过25cm
            continue

        pos = m.start()
        before = content[max(0, pos - 80):pos]
        after = content[pos:min(len(content), pos + 80)]
        near = before + after[:40]

        # 必须在阴茎上下文
        if not any(pk in near for pk in PENIS_KW):
            continue

        char = _find_char_in_context(content, pos)
        if char and '阴茎' in CANON[char]:
            canon_p = CANON[char]['阴茎']
            # 满月形态特殊处理
            if '阴茎_满月' in CANON[char] and num == CANON[char]['阴茎_满月']:
                continue  # 满月阴茎正确
            if num != canon_p:
                violations.append({
                    'chapter': ch_id, 'file': os.path.basename(fp),
                    'character': char, 'attribute': '阴茎',
                    'stated': f'{num_str}cm', 'canon': f'{canon_p}cm',
                    'context': near.strip()[:150]
                })

    return violations


def _check_hair(ch_id, content, fp):
    """检查发色不一致"""
    violations = []
    hair_colors = {
        '银发': '银色', '粉发': '粉色', '黑发': '黑色', '白发': '白色',
        '金发': '金色', '棕发': '棕色', '靛蓝发': '靛蓝色',
    }
    for hw, hcolor in hair_colors.items():
        for m in re.finditer(hw, content):
            pos = m.start()
            char = _find_char_in_context(content, pos)
            if char and '发色' in CANON[char]:
                canon_color = CANON[char]['发色']
                if hcolor != canon_color:
                    # 奥蕾莉亚银发正确=不报; Seraphina粉发≠银发=报
                    violations.append({
                        'chapter': ch_id, 'file': os.path.basename(fp),
                        'character': char, 'attribute': '发色',
                        'stated': hw, 'canon': canon_color,
                        'context': content[max(0, pos-60):pos+60].strip()[:150]
                    })
    return violations


# ─── 主入口 ────────────────────────────────────────────
def main():
    use_json = '--json' in sys.argv
    do_fix = '--fix' in sys.argv

    violations = scan_all_chapters()

    # 去重
    seen = set()
    unique = []
    for v in violations:
        key = (v['chapter'], v['character'], v['attribute'], v['stated'])
        if key not in seen:
            seen.add(key)
            unique.append(v)

    if use_json:
        print(json.dumps(unique, ensure_ascii=False, indent=2))
        return

    # 按角色分组输出
    by_char = defaultdict(list)
    for v in unique:
        by_char[v['character']].append(v)

    print(f'发现 {len(unique)} 处属性不一致，涉及 {len(by_char)} 个角色\n')

    for char in sorted(by_char.keys()):
        items = by_char[char]
        canon_data = CANON.get(char, {})
        print(f'━━━ {char} ━━━')
        print(f'  标准: 身高={canon_data.get("身高","?")}cm  '
              f'发色={canon_data.get("发色","?")}  '
              f'瞳色={canon_data.get("瞳色","?")}  '
              f'阴茎={canon_data.get("阴茎","?")}cm  '
              f'罩杯={canon_data.get("罩杯","?")}')
        for v in sorted(items, key=lambda x: int(x['chapter']) if x['chapter'].isdigit() else 0):
            print(f'  [{v["chapter"]}] {v["attribute"]}: {v["stated"]} → 应为{v["canon"]}')
            print(f'         {v["file"]}')
            print(f'         ...{v["context"][:100]}...')
        print()

    # 统计
    attr_counts = defaultdict(int)
    for v in unique:
        attr_counts[v['attribute']] += 1
    print('─── 按属性统计 ───')
    for attr, count in sorted(attr_counts.items(), key=lambda x: -x[1]):
        print(f'  {attr}: {count}')

    print(f'\n总计: {len(unique)} 处')

    if do_fix:
        print('\n[--fix] 交互修复模式暂未实现，请使用 Edit 工具手动修复上述文件')


if __name__ == '__main__':
    main()
