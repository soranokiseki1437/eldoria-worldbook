#!/usr/bin/env python3
"""
短对话扫描 — 引号内句号断句(F) + 短对话(D) + 叙事短句三连(T)
只扫描 ≥Ch187。

用法:
  python scripts/scan_short_dialogue.py --stage 4              # stdout
  python scripts/scan_short_dialogue.py --stage 4 --output     # → 方案/
  python scripts/scan_short_dialogue.py --all --output         # 全阶段
"""

import os, re, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = ROOT / "docs" / "story"
PLAN_DIR = ROOT / "方案"

STAGE_DIRS = {
    "0": "0：序章", "1": "1：试探和暧昧", "2": "2：挑逗和接受",
    "3": "3：渐进接触", "4": "4：跨线", "5": "5：享受和掌控",
    "6": "6：放纵", "7": "7：终局", "8": "8：后日谈",
}

MIN_CHAPTER = 187
F_MIN_PERIODS = 2    # 引号内≥此数量。
D_MAX_CHARS = 10     # 对话≤此字数
T_MAX_CHARS = 20     # T型单句≤此字数
T_MIN_COUNT = 3      # T型连续N句


def count_chinese(s: str) -> int:
    n = 0
    for ch in s:
        if ('一' <= ch <= '鿿' or
            ch in '，。！？…—、：；'
                   '“”‘’（）【】《》'):
            n += 1
    return n


def split_by_period(text: str) -> list[str]:
    """按。分割（跳过引号内的。）"""
    sentences = []
    in_quote = False
    seg_start = 0
    for i, ch in enumerate(text):
        if ch in '"“':       # " 或 "
            in_quote = True
        elif ch in '"”':     # " 或 "
            in_quote = False
        elif ch == '。' and not in_quote:  # 。
            seg = text[seg_start:i].strip()
            if seg:
                sentences.append(seg)
            seg_start = i + 1
    if seg_start < len(text):
        seg = text[seg_start:].strip()
        if seg:
            sentences.append(seg)
    return sentences


def scan_file(filepath: Path) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {"id": None, "name": "", "findings": [], "error": str(e)}

    chapter_id = None
    chapter_name = ""
    for line in lines:
        s = line.strip()
        if s.startswith("ID:"):
            try:    chapter_id = int(s.split(":")[1].strip())
            except: chapter_id = s.split(":")[1].strip()
        elif s.startswith("名称:"):  # 名称:
            chapter_name = s.split(":", 1)[1].strip() if ":" in s else ""
        if chapter_id is not None and chapter_name:
            break

    if chapter_id is None:
        return {"id": None, "name": "", "findings": [], "error": "No ID"}
    if isinstance(chapter_id, int) and chapter_id < MIN_CHAPTER:
        return {"id": chapter_id, "name": chapter_name, "findings": [], "skipped": True}

    # 定位字段边界
    markers = {}
    for i, line in enumerate(lines):
        s = line.strip()
        for key in ["情境", "核心"]:  # 情境, 核心
            if s == f"{key}:" or s.startswith(f"{key}:"):
                markers[key] = i
                break

    findings = []

    for field in ["情境", "核心"]:
        if field not in markers:
            continue
        end_key = "核心" if field == "情境" else "章节任务"
        end = markers.get(end_key, markers.get("章节终止条件", len(lines)))
        for i in range(markers[field] + 1, end):
            txt = lines[i].strip()
            if not txt:
                continue

            # --- F & D: 引号内对话（兼容 "" 和 "" 两种引号）---
            for m in re.finditer(r'["“]([^"”]*)["”]', txt):
                content = m.group(1)
                qs, qe = m.start(), m.end()
                cc = count_chinese(content)
                if cc > 50:
                    continue
                pc = content.count('。')

                if pc >= F_MIN_PERIODS:
                    ctx = txt[max(0,qs-25):min(len(txt),qe+25)]
                    findings.append({
                        "type": "F", "chapter": chapter_id, "line": i + 1,
                        "field": field, "quote": content, "context": ctx,
                        "note": f"引号内{pc}个。"
                    })
                elif content.endswith('。') and cc <= D_MAX_CHARS:
                    ctx = txt[max(0,qs-25):min(len(txt),qe+25)]
                    findings.append({
                        "type": "D", "chapter": chapter_id, "line": i + 1,
                        "field": field, "quote": content, "context": ctx,
                        "note": f"≤{D_MAX_CHARS}字以。结尾"
                    })

            # --- T: 叙事短句三连 ---
            sentences = split_by_period(txt)
            j = 0
            while j <= len(sentences) - T_MIN_COUNT:
                w = sentences[j:j + T_MIN_COUNT]
                no_comma = all('，' not in s and '；' not in s for s in w)
                all_short = all(count_chinese(s) <= T_MAX_CHARS for s in w)
                if no_comma and all_short:
                    ctx_start = max(0, len(txt) - sum(len(s)+1 for s in sentences[j:]) - 25)
                    # 重建上下文
                    merged = '。'.join(w) + '。'
                    findings.append({
                        "type": "T", "chapter": chapter_id, "line": i + 1,
                        "field": field, "quote": merged, "context": merged,
                        "note": f"短句{T_MIN_COUNT}连: 无逗号单从句×{T_MIN_COUNT}"
                    })
                    j += T_MIN_COUNT
                else:
                    j += 1

    return {"id": chapter_id, "name": chapter_name, "findings": findings}


def format_report(all_results: list[dict], stage_label: str) -> str:
    out = []
    out.append(f"# 短对话扫描 — {stage_label}  (≥Ch{MIN_CHAPTER})")
    out.append(f"# F=引号内≥{F_MIN_PERIODS}个。 / D=≤{D_MAX_CHARS}字以。结尾 / T=无逗号单从句{T_MIN_COUNT}连(≤{T_MAX_CHARS}字)")
    out.append("")

    total = {"F": 0, "D": 0, "T": 0}
    has_issue = 0
    skipped = 0

    for r in all_results:
        if r.get("skipped"):
            skipped += 1
            continue
        if r.get("error"):
            out.append(f"## !! {r.get('file','?')} — {r['error']}")
            out.append("")
            continue
        if not r.get("findings"):
            continue

        has_issue += 1
        ch_id = r["id"]
        ch_name = r["name"]
        out.append(f"## Ch{ch_id}: {ch_name}")
        out.append("")

        for f in r["findings"]:
            t = f["type"]
            total[t] = total.get(t, 0) + 1
            out.append(f"  章节{ch_id}, L{f['line']} [{t}] {f['note']}")
            out.append(f"    ...{f['context']}...")
            out.append("")
        out.append("")

    scanned = sum(1 for r in all_results if not r.get("skipped") and not r.get("error"))
    summary = (f"# 章节: {has_issue}个有问题 / 扫描{scanned}章(跳过{skipped}) | "
               f"F型{total['F']} / D型{total['D']} / T型{total['T']}")
    out.insert(2, summary)
    out.insert(3, "")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="扫描章节TXT短对话(≥Ch187)")
    parser.add_argument("--stage", type=str, help="阶段编号 0-8")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output", action="store_true")
    args = parser.parse_args()

    if args.all:
        stages = list(STAGE_DIRS.keys())
    elif args.stage and args.stage in STAGE_DIRS:
        stages = [args.stage]
    else:
        parser.print_help()
        return

    for sn in stages:
        sdir = STAGE_DIRS[sn]
        spath = STORY_DIR / sdir
        if not spath.exists():
            print(f"!! 目录不存在: {spath}")
            continue

        print(f"\n{'='*50}")
        print(f"阶段{sn}: {sdir}")
        print(f"{'='*50}")

        txts = sorted(spath.glob("*.TXT"), key=lambda f: f.name)
        all_r = []
        for tf in txts:
            r = scan_file(tf)
            all_r.append(r)
            if r.get("skipped"):
                continue
            fs = r.get("findings", [])
            if fs:
                fc = sum(1 for x in fs if x["type"] == "F")
                dc = sum(1 for x in fs if x["type"] == "D")
                tc = sum(1 for x in fs if x["type"] == "T")
                print(f"  Ch{r['id']:>4}: F={fc} D={dc} T={tc}  {r.get('name','')[:35]}")

        report = format_report(all_r, sdir)

        if args.output:
            os.makedirs(PLAN_DIR, exist_ok=True)
            opath = PLAN_DIR / f"短对话扫描_{sdir}.txt"
            with open(opath, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"  → {opath}")
        else:
            print(report)


if __name__ == "__main__":
    main()
