#!/usr/bin/env python3
"""
短对话扫描 v2 — 全面对白/描写质量扫描

对白检查（引号内）:
  D1 二字崩     ≤2字独立对话（嗯。/好。/哦。等）
  D2 短对白     3-6字以。结尾（简短回应/冷漠感）
  D3 疑似问句。 含疑问词(什么/吗/呢/怎么/谁/哪/几/啥)却以。结尾
  D4 引号内多句 引号内≥2个。
  D5 短句接龙   连续≥3个对话turn且每个≤12字（碎片化报告感）
  D6 零间隔对话 两个引号紧邻或仅隔标点（无动作/无归属的报告式对白）

描写检查（非引号叙事）:
  N1 短句三连   连续3句≤20字且无逗号（≤12字标记为严）
  N2 电报超短句 非对话句≤4字
  N3 电报连发   连续3句每句≤10字（无逗号）

用法:
  python scripts/scan_short_dialogue.py --stage 4
  python scripts/scan_short_dialogue.py --all
  python scripts/scan_short_dialogue.py --chapters 120,152,155
  python scripts/scan_short_dialogue.py --chapters 120-160,500-510
  python scripts/scan_short_dialogue.py --all --diff          # 只报与git HEAD不同（新产生）的发现
  python scripts/scan_short_dialogue.py --all --output        # 输出到 方案/短对话扫描_*.txt
"""
import os, re, sys, subprocess, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = ROOT / "docs" / "story"
PLAN_DIR = ROOT / "方案"

STAGE_DIRS = {
    "0": "0：序章", "1": "1：试探和暧昧", "2": "2：挑逗和接受",
    "3": "3：渐进接触", "4": "4：跨线", "5": "5：享受和掌控",
    "6": "6：放纵", "7": "7：终局", "8": "8：后日谈",
}

FIELDS = ["情境", "核心", "章节任务", "章节终止条件"]

def count_chinese(s: str) -> int:
    n = 0
    for ch in s:
        if ('一' <= ch <= '鿿' or ch in '，。！？…—、：；'
                '“”‘’（）【】《》'):
            n += 1
    return n

def split_by_period(text: str) -> list[str]:
    """按。分割（跳过引号内的。）"""
    sentences = []
    in_quote = False
    seg_start = 0
    for i, ch in enumerate(text):
        if ch in '"“':
            in_quote = True
        elif ch in '"”':
            in_quote = False
        elif ch == '。' and not in_quote:
            seg = text[seg_start:i].strip()
            if seg:
                sentences.append(seg)
            seg_start = i + 1
    if seg_start < len(text):
        seg = text[seg_start:].strip()
        if seg:
            sentences.append(seg)
    return sentences

QUESTION_RE = re.compile(r'[什么吗呢怎么谁哪几啥][呀呢么]*[。.]$|[？?]')

def scan_text(text: str, ch_id) -> list[dict]:
    """扫描单章全文，返回 findings: {type, field, quote, context, sev}"""
    findings = []
    lines = text.split('\n')
    cur_field = None
    bullets = []  # (field, line_no, text)
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('情境:') or s.startswith('核心:') or s.startswith('章节任务:') or s.startswith('章节终止条件:'):
            cur_field = s.split(':')[0]
            if len(s) > len(cur_field) + 1 and s[len(cur_field)+1:].strip():
                bullets.append((cur_field, i, s[len(cur_field)+1:].strip()))
            continue
        if cur_field and s:
            bullets.append((cur_field, i, s))

    for field, lineno, txt in bullets:
        # ── 对白检查 ──
        quotes = [(m.group(1), m.start(), m.end()) for m in re.finditer(r'["“]([^"”]*)["”]', txt)]
        for content, qs, qe in quotes:
            cc = count_chinese(content)
            if cc > 50:
                continue
            ctx = txt[max(0, qs-20):min(len(txt), qe+20)]
            # D1 二字崩
            if cc <= 2:
                findings.append({"type": "D1", "field": field, "line": lineno+1,
                                 "quote": content, "context": ctx, "sev": "严",
                                 "note": f"二字崩({cc}字)"})
                continue
            # D4 引号内多句
            pc = content.count('。')
            if pc >= 2:
                findings.append({"type": "D4", "field": field, "line": lineno+1,
                                 "quote": content, "context": ctx, "sev": "中",
                                 "note": f"引号内{pc}个。"})
            # D3 疑似问句句号
            q_end = content[-1] if content else ''
            if q_end == '。' and re.search(r'什么|吗|呢|怎么|谁|哪|几|啥|多久|为什么|多少|是不是|有没有', content) \
               and not re.search(r'没什么|没事|没关系|不知道|没怎么|^[一二三四五六七八九十两半\d]+几?个', content):
                findings.append({"type": "D3", "field": field, "line": lineno+1,
                                 "quote": content, "context": ctx, "sev": "中",
                                 "note": "疑似问句用句号"})
            # D2 短对白
            if q_end == '。' and 3 <= cc <= 6:
                findings.append({"type": "D2", "field": field, "line": lineno+1,
                                 "quote": content, "context": ctx, "sev": "中",
                                 "note": f"短对白({cc}字)"})
        # D6 零间隔对话
        for j in range(len(quotes) - 1):
            prev_content = quotes[j][0]
            if prev_content.endswith('——') or prev_content.endswith('…') or prev_content.endswith('...'):
                continue  # 对话被打断（合法）
            gap = txt[quotes[j][2]:quotes[j+1][1]]
            if not gap.strip() or gap.strip() in '，。、':
                findings.append({"type": "D6", "field": field, "line": lineno+1,
                                 "quote": quotes[j][0] + "|" + quotes[j+1][0],
                                 "context": txt[max(0, quotes[j][1]-15):min(len(txt), quotes[j+1][2]+15)],
                                 "sev": "中", "note": "零间隔对话"})
        # D5 短句接龙：连续≥3个引号turn 每个≤12字
        chain = []
        for content, qs, qe in quotes:
            cc = count_chinese(content)
            if cc <= 12:
                chain.append(content)
            else:
                if len(chain) >= 3:
                    findings.append({"type": "D5", "field": field, "line": lineno+1,
                                     "quote": "｜".join(chain), "context": txt,
                                     "sev": "中", "note": f"{len(chain)}连短对白"})
                chain = []
        if len(chain) >= 3:
            findings.append({"type": "D5", "field": field, "line": lineno+1,
                             "quote": "｜".join(chain), "context": txt,
                             "sev": "中", "note": f"{len(chain)}连短对白"})

        # ── 描写检查 ──
        # 去掉引号内容后按句号分段
        no_quotes = re.sub(r'["“\'\u2018][^"“\'\u2019]*["”\'\u2019]', '', txt)
        segs = split_by_period(no_quotes)
        # N1 短句三连
        j = 0
        while j <= len(segs) - 3:
            w = segs[j:j+3]
            if all('，' not in x and '；' not in x for x in w) and all(count_chinese(x) <= 20 for x in w):
                sev = "严" if all(count_chinese(x) <= 12 for x in w) else "中"
                findings.append({"type": "N1", "field": field, "line": lineno+1,
                                 "quote": '。'.join(w), "context": '。'.join(w),
                                 "sev": sev, "note": f"短句三连(最长{max(count_chinese(x) for x in w)}字)"})
                j += 3
            else:
                j += 1
        # N2 电报超短句
        COMPLETE_START = re.compile(r'^[他她它你我你们她们它们黎恩菲娜劳拉乔治艾玛凯尔玲菲雷恩]')
        ONO = re.compile(r'^[啪嗒咚咔咔噗轰嗡]')
        for x in segs:
            cc = count_chinese(x)
            if cc <= 4 and not re.match(r'^第?[\d一二三四五六七八九十]+', x) \
               and not COMPLETE_START.match(x) and not ONO.match(x):
                findings.append({"type": "N2", "field": field, "line": lineno+1,
                                 "quote": x, "context": x, "sev": "严",
                                 "note": f"电报超短句({cc}字)"})
        # N3 电报连发：连续3句每句≤10字
        j = 0
        while j <= len(segs) - 3:
            w = segs[j:j+3]
            if all('，' not in x and '；' not in x for x in w) and all(count_chinese(x) <= 10 for x in w):
                findings.append({"type": "N3", "field": field, "line": lineno+1,
                                 "quote": '。'.join(w), "context": '。'.join(w),
                                 "sev": "中", "note": "电报连发(≤10字×3)"})
                j += 3
            else:
                j += 1
    return findings


def load_file(path) -> tuple:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except OSError:
        return None, None, f"读取失败"
    m = re.search(r'^ID:\s*(\d+)', text, re.M)
    name_m = re.search(r'^名称:\s*(.+)', text, re.M)
    ch_id = m.group(1) if m else None
    name = name_m.group(1).strip() if name_m else ''
    return ch_id, name, text


def parse_chapters(spec: str) -> set | None:
    """'120,152,155' / '120-160,500-510' → set of ints; None=全部"""
    result = set()
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            result.update(range(int(a), int(b) + 1))
        elif part:
            result.add(int(part))
    return result


def main():
    ap = argparse.ArgumentParser(description="短对话扫描 v2 — 全面对白/描写质量扫描")
    ap.add_argument('--stage', help='仅扫某阶段 (0-8)')
    ap.add_argument('--all', action='store_true', help='扫全部章节')
    ap.add_argument('--chapters', help='指定章节: 120,152 或 120-160')
    ap.add_argument('--diff', action='store_true', help='与git HEAD对比，只报新产生发现')
    ap.add_argument('--output', action='store_true', help='输出报告到 方案/')
    args = ap.parse_args()

    if args.stage is None and not args.all and not args.chapters:
        ap.error('需要 --stage N / --all / --chapters')

    chapter_filter = parse_chapters(args.chapters) if args.chapters else None
    stage_filter = args.stage if args.stage is not None else None

    results = []
    for stage_key, stage_dir in STAGE_DIRS.items():
        if stage_filter is not None and stage_key != stage_filter:
            continue
        sp = STORY_DIR / stage_dir
        if not sp.is_dir():
            continue
        for f in sorted(sp.glob('*.TXT')):
            if f.name.startswith('_'):
                continue
            ch_id, name, text = load_file(f)
            if ch_id is None or not name:
                continue
            if chapter_filter is not None and int(ch_id) not in chapter_filter:
                continue
            findings = scan_text(text, ch_id)
            if args.diff:
                old = subprocess.run(['git', 'show', f'HEAD:{f.relative_to(ROOT)}'],
                                     capture_output=True, text=True)
                if old.returncode != 0:
                    continue
                old_findings = scan_text(old.stdout, ch_id)
                old_keys = {(x['type'], x['quote']) for x in old_findings}
                findings = [x for x in findings if (x['type'], x['quote']) not in old_keys]
            results.append({"id": ch_id, "name": name, "stage": stage_dir, "findings": findings})

    # 输出
    total = {"D1": 0, "D2": 0, "D3": 0, "D4": 0, "D5": 0, "D6": 0, "N1": 0, "N2": 0, "N3": 0}
    chapter_count = 0
    for r in results:
        if r["findings"]:
            chapter_count += 1
        for x in r["findings"]:
            total[x["type"]] += 1

    if args.output:
        stage_label = STAGE_DIRS.get(stage_filter, "全阶段") if stage_filter else "全阶段"
        fname = f"短对话扫描v2_{stage_label}.txt"
        out_path = PLAN_DIR / fname
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(f"# 短对话扫描v2 — {stage_label}  (diff={'开' if args.diff else '关'})\n")
            fh.write(f"# D1二字崩 D2短对白 D3问句句号 D4引号内多句 D5短句接龙 D6零间隔对话 N1短句三连 N2电报超短句 N3电报连发\n")
            fh.write(f"# 汇总: {total}  |  有发现章节 {chapter_count}\n\n")
            for r in results:
                if not r["findings"]:
                    continue
                fh.write(f"## Ch{r['id']}: {r['name']} [{r['stage']}]\n")
                for x in sorted(r["findings"], key=lambda z: z["line"]):
                    fh.write(f"  [{x['type']}/{x['sev']}] {x['field']}L{x['line']} {x['note']}: {x['quote']}\n")
                fh.write("\n")
        print(f"✅ 报告已写入: {out_path}")

    print(f"=== 汇总: {total} | 有发现章节 {chapter_count} ===")
    for r in results:
        if not r["findings"]:
            continue
        print(f"\n## Ch{r['id']}: {r['name']} [{r['stage']}]")
        for x in sorted(r["findings"], key=lambda z: z["line"]):
            print(f"  [{x['type']}/{x['sev']}] {x['field']}L{x['line']} {x['note']}: {x['quote']}")
    if not results:
        print("（无章节被扫描）")


if __name__ == '__main__':
    main()
