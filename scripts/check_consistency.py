#!/usr/bin/env python3
"""check_consistency.py — 全库一致性检查（V10.28 新增）

把所有索引/文档与章节文件（唯一权威源）对照，一次性发现脱节。
检查项:
  1. 章节编号 1..N 连续无重复、无缺口
  2. 文件名与内部 ID/名称 一致（`{ID}：{名称}.TXT`）
  3. 名称符合 `xxx——xxx` 格式（必须含 ——）
  4. 阶段字段与所在目录一致
  5. sex索引: 每条 编号↔标题 与文件系统精确匹配（0 漂移）
  6. 弧总览: 弧详情 **N** 引用、拆分表 Ch 引用、阶段首尾章 与文件系统匹配
  7. 阶段章数合计 == 总章数；统计 弧章+独立章 == 总章数

用法:
  python scripts/check_consistency.py        # 全量检查
  python scripts/check_consistency.py --quiet  # 只输出失败项

退出码: 0 = 全部通过；1 = 存在不一致
"""
import os
import re
import sys
from collections import defaultdict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY_DIR = os.path.join(PROJECT_DIR, 'docs', 'story')
SEX_INDEX = os.path.join(STORY_DIR, '_sex_index.txt')
ARC_FILE = os.path.join(STORY_DIR, '_连续叙事弧线章节总览.md')

QUIET = '--quiet' in sys.argv
FAILED = []


def fail(msg):
    FAILED.append(msg)
    print(f"  ✗ {msg}")


def ok(msg):
    if not QUIET:
        print(f"  ✓ {msg}")


def scan_fs():
    """返回 {id: {'title':..., 'stage':目录名, 'fname':文件名}}"""
    fs = {}
    for root, dirs, files in os.walk(STORY_DIR):
        for f in files:
            if not f.endswith('.TXT'):
                continue
            fp = os.path.join(root, f)
            try:
                txt = open(fp, encoding='utf-8').read()
            except OSError:
                continue
            m_id = re.search(r'^ID:\s*(\d+)', txt, re.M)
            m_name = re.search(r'^名称:\s*(.+)', txt, re.M)
            if not m_id or not m_name:
                continue
            fs[m_id.group(1)] = {
                'title': m_name.group(1).strip(),
                'stage': os.path.basename(root),
                'fname': f,
            }
    return fs


def main():
    print("=" * 60)
    print("  Eldoria 全库一致性检查")
    print("=" * 60)

    fs = scan_fs()
    n = len(fs)
    print(f"\n[1] 章节编号连续性 (共 {n} 章)")
    ids = sorted(int(k) for k in fs)
    gaps = [i for i in range(1, ids[-1] + 1) if str(i) not in fs]
    dups = len(ids) - len(set(ids))
    if gaps:
        fail(f"编号缺口 {len(gaps)} 个: {gaps[:20]}")
    elif dups:
        fail(f"编号重复 {dups} 个")
    else:
        ok(f"编号 1-{ids[-1]} 连续无缺口")

    print("\n[2] 文件名与 ID/名称 一致")
    bad_fname = []
    for nid, info in fs.items():
        m = re.match(r'^(\d+)：(.+?)\.TXT$', info['fname'])
        if not m:
            bad_fname.append((nid, info['fname']))
        elif int(m.group(1)) != int(nid) or m.group(2) != info['title']:
            # 前导零文件名（031：...）为既有命名习惯，仅比较数值
            bad_fname.append((nid, info['fname'], info['title']))
    if bad_fname:
        for b in bad_fname[:15]:
            fail(f"Ch{b[0]}: 文件名 {b[1]!r} != 名称 {b[2]!r}" if len(b) == 3 else f"Ch{b[0]}: 文件名格式异常 {b[1]!r}")
    else:
        ok("全部文件名 = `{ID}：{名称}.TXT`")

    print("\n[3] 名称格式 (xxx——xxx)")
    bad_fmt = [(nid, info['title']) for nid, info in fs.items() if '——' not in info['title']]
    if bad_fmt:
        for nid, t in bad_fmt:
            fail(f"Ch{nid}: 名称缺 —— {t!r}")
    else:
        ok("全部名称含 ——")

    print("\n[4] 阶段字段与目录一致")
    bad_stage = []
    for nid, info in fs.items():
        # 目录名 "6：放纵" → 阶段 "放纵"
        stage_name = re.sub(r'^\d+：', '', info['stage'])
        fp = None
        for root, dirs, files in os.walk(STORY_DIR):
            if info['fname'] in files:
                fp = os.path.join(root, info['fname'])
                break
        if fp:
            txt = open(fp, encoding='utf-8').read()
            m = re.search(r'^阶段:\s*(.+)', txt, re.M)
            if m and m.group(1).strip() != stage_name:
                bad_stage.append((nid, m.group(1).strip(), stage_name))
    if bad_stage:
        for nid, got, want in bad_stage:
            fail(f"Ch{nid}: 阶段={got} 目录={want}")
    else:
        ok("全部章节阶段字段与目录一致")

    print("\n[5] sex索引 编号↔标题")
    sex_bad = 0
    sex_total = 0
    non_int = []
    cur_tag = None
    for line in open(SEX_INDEX, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('##'):
            cur_tag = line.split()[1].split('(')[0] if len(line.split()) > 1 else '?'
            continue
        m = re.match(r'^([\d.]+):\s*(.+)', line)
        if not m:
            continue
        num, title = m.group(1), m.group(2).strip()
        if '.' in num:
            non_int.append((num, title))
            continue
        sex_total += 1
        if num not in fs or fs[num]['title'] != title:
            sex_bad += 1
            if sex_bad <= 10:
                fail(f"Ch{num}: 索引={title!r} vs fs={fs.get(num, {}).get('title', '?')!r}")
    if non_int:
        fail(f"sex索引含 {len(non_int)} 条非整数编号: {[n for n, _ in non_int]}")
    elif sex_bad == 0:
        ok(f"sex索引 {sex_total} 条全部匹配")

    print("\n[6] 弧总览 引用匹配")
    arc_bad = 0
    if os.path.exists(ARC_FILE):
        lines = open(ARC_FILE, encoding='utf-8').read().split('\n')
        # 6a. 弧详情 **N** 引用
        for line in lines:
            if not line.startswith('- **'):
                continue
            for m in re.finditer(r'\*\*(\d+)\*\*\s*([^+：]+?)(?=\s*\+ \*\*|\s*：|$)', line):
                num, title = m.group(1), m.group(2).strip()
                if fs.get(num, {}).get('title') != title:
                    arc_bad += 1
                    if arc_bad <= 10:
                        fail(f"弧详情: **{num}** {title} (fs={fs.get(num, {}).get('title', '?')})")
        # 6b. 拆分表 Ch 引用
        for line in lines:
            if '拆分形成连续弧' not in line:
                continue
            fields = line.split('|')
            parts = re.findall(r'Ch(\d+)（([上中下])）', fields[2])
            titles = [t.strip() for t in re.split(r'→', fields[3].strip())]
            for (num, lbl), title in zip(parts, titles):
                if fs.get(num, {}).get('title') != title:
                    arc_bad += 1
                    if arc_bad <= 10:
                        fail(f"拆分表: Ch{num}（{lbl}）{title} (fs={fs.get(num, {}).get('title', '?')})")
        # 6c. 阶段首尾章
        for line in lines:
            m = re.match(r'^\| \d：\S+ \| (\d+) (\S+) \| (\d+) (\S+) \| (\d+) \|$', line)
            if m:
                for num, title in ((m.group(1), m.group(2)), (m.group(3), m.group(4))):
                    if fs.get(num, {}).get('title') != title:
                        arc_bad += 1
                        if arc_bad <= 10:
                            fail(f"阶段表: Ch{num} {title} (fs={fs.get(num, {}).get('title', '?')})")
        # 6d. 阶段章数合计
        stage_sum = sum(int(m.group(5)) for line in lines
                        if (m := re.match(r'^\| \d：\S+ \| (\d+) (\S+) \| (\d+) (\S+) \| (\d+) \|$', line)))
        if stage_sum != n:
            arc_bad += 1
            fail(f"阶段章数合计 {stage_sum} != 总章数 {n}")
        # 6e. 统计 弧+独立 == 总章数
        stats = {}
        for line in lines:
            m = re.match(r'^\| (\S+) \| (\d+) \|$', line)
            if m:
                stats[m.group(1)] = int(m.group(2))
        if stats.get('弧涉及章节数') is not None:
            total_arc = stats.get('弧涉及章节数', 0) + stats.get('独立章数', 0)
            if total_arc != n:
                arc_bad += 1
                fail(f"统计 弧{stats.get('弧涉及章节数')}+独立{stats.get('独立章数')}={total_arc} != 总章数 {n}")
    if arc_bad == 0:
        ok("弧总览全部引用/统计闭合")

    print("\n" + "=" * 60)
    if FAILED:
        print(f"  ❌ 发现 {len(FAILED)} 处不一致（含重复计数）")
        sys.exit(1)
    else:
        print("  ✅ 全部检查通过，索引与章节文件完全一致")
        sys.exit(0)


if __name__ == '__main__':
    main()
