#!/usr/bin/env python3
"""统计每个章节TXT的字符数，输出到output目录并打印分析摘要。

Usage:
    python scripts/chapter_char_count.py          # 输出TXT + 终端摘要
    python scripts/chapter_char_count.py --json   # 同时输出JSON
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = ROOT / "docs" / "story"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 阶段目录映射（按编号排序）
STAGE_ORDER = [
    "0：序章", "1：试探和暧昧", "2：挑逗和接受", "3：渐进接触",
    "4：跨线", "5：享受和掌控", "6：放纵", "7：终局", "8：后日谈"
]


def parse_chapter_id(filename: str) -> int:
    """从文件名提取章节编号，如 '001：林间空地的苏醒——陌生的森林.TXT' → 1"""
    m = re.match(r"^(\d+)", filename)
    return int(m.group(1)) if m else 0


def get_stage_name(filepath: Path) -> str:
    """从文件路径提取阶段名"""
    # filepath 形如 docs/story/0：序章/001：xxx.TXT
    return filepath.parent.name


def count_chars(filepath: Path) -> int:
    """读取文件并返回字符数（UTF-8，不含BOM）"""
    try:
        text = filepath.read_text(encoding="utf-8-sig")
        return len(text)
    except Exception as e:
        print(f"  ⚠ 读取失败: {filepath.name} — {e}", file=sys.stderr)
        return 0


def main():
    want_json = "--json" in sys.argv

    # 收集所有章节TXT（排除_TEMPLATE.TXT和任何下划线开头的文件）
    chapters = []
    for stage_dir_name in STAGE_ORDER:
        stage_path = STORY_DIR / stage_dir_name
        if not stage_path.is_dir():
            continue
        for txt_file in sorted(stage_path.glob("*.TXT")):
            if txt_file.name.startswith("_"):
                continue
            ch_id = parse_chapter_id(txt_file.name)
            char_count = count_chars(txt_file)
            chapters.append({
                "id": ch_id,
                "filename": txt_file.name,
                "stage": stage_dir_name,
                "path": str(txt_file.relative_to(ROOT)),
                "chars": char_count,
            })

    # 按章节ID排序
    chapters.sort(key=lambda c: c["id"])

    total_chars = sum(c["chars"] for c in chapters)
    n = len(chapters)

    # ── 统计分位数 ──
    char_counts = sorted(c["chars"] for c in chapters)
    avg = total_chars / n if n else 0

    def percentile(sorted_vals, p):
        """p in 0..100"""
        if not sorted_vals:
            return 0
        k = (len(sorted_vals) - 1) * p / 100
        f = int(k)
        c = k - f
        if f + 1 < len(sorted_vals):
            return sorted_vals[f] + c * (sorted_vals[f + 1] - sorted_vals[f])
        return sorted_vals[f]

    p10 = percentile(char_counts, 10)
    p25 = percentile(char_counts, 25)
    p50 = percentile(char_counts, 50)
    p75 = percentile(char_counts, 75)
    p90 = percentile(char_counts, 90)
    p95 = percentile(char_counts, 95)
    p99 = percentile(char_counts, 99)

    # ── 阶段统计 ──
    stage_stats = defaultdict(lambda: {"count": 0, "total_chars": 0, "chapters": []})
    for c in chapters:
        st = stage_stats[c["stage"]]
        st["count"] += 1
        st["total_chars"] += c["chars"]
        st["chapters"].append(c)

    # ── 输出TXT ──
    txt_path = OUTPUT_DIR / "chapter_char_count.txt"
    lines = []
    lines.append("=" * 78)
    lines.append("  世界书 · 章节字符数统计")
    lines.append(f"  总章节数: {n}  |  总字符数: {total_chars:,}  |  平均: {avg:,.0f}")
    lines.append("=" * 78)
    lines.append("")
    lines.append("─" * 78)
    lines.append(f"  分位数分析")
    lines.append("─" * 78)
    lines.append(f"  P10  {p10:>8,.0f}     P75  {p75:>8,.0f}")
    lines.append(f"  P25  {p25:>8,.0f}     P90  {p90:>8,.0f}")
    lines.append(f"  P50  {p50:>8,.0f}     P95  {p95:>8,.0f}")
    lines.append(f"  Avg  {avg:>8,.0f}     P99  {p99:>8,.0f}")
    lines.append("")
    lines.append(f"  最短: #{char_counts[0]:,}字  |  最长: #{char_counts[-1]:,}字")
    lines.append("")

    # 阶段汇总
    lines.append("─" * 78)
    lines.append(f"  {'阶段':<16} {'章数':>5}  {'总字符':>10}  {'平均':>8}  {'占比':>7}")
    lines.append("─" * 78)
    for sn in STAGE_ORDER:
        st = stage_stats.get(sn)
        if st:
            pct = st["total_chars"] / total_chars * 100 if total_chars else 0
            avg_s = st["total_chars"] / st["count"] if st["count"] else 0
            lines.append(f"  {sn:<16} {st['count']:>5}  {st['total_chars']:>10,}  {avg_s:>8,.0f}  {pct:>6.1f}%")
    lines.append("─" * 78)
    lines.append(f"  {'合计':<16} {n:>5}  {total_chars:>10,}  {avg:>8,.0f}  {'100.0%':>7}")
    lines.append("")

    # 章节明细
    lines.append("─" * 78)
    lines.append(f"  {'章节':<6} {'字符数':>8}  {'阶段':<16} {'文件名'}")
    lines.append("─" * 78)
    for c in chapters:
        lines.append(f"  Ch{c['id']:<3}  {c['chars']:>8,}  {c['stage']:<16} {c['filename']}")

    # Top 30 最长章节
    lines.append("")
    lines.append("─" * 78)
    lines.append("  Top 30 最长章节（可能需要拆分）")
    lines.append("─" * 78)
    top30 = sorted(chapters, key=lambda c: c["chars"], reverse=True)[:30]
    for i, c in enumerate(top30, 1):
        over_avg = c["chars"] / avg if avg else 1
        lines.append(f"  #{i:>2}  Ch{c['id']:<4} {c['chars']:>8,}字  ({over_avg:.1f}×平均值)  [{c['stage']}]  {c['filename']}")

    txt_content = "\n".join(lines) + "\n"
    txt_path.write_text(txt_content, encoding="utf-8")
    print(f"✅ TXT 已写入: {txt_path}")

    # ── 可选JSON ──
    if want_json:
        json_path = OUTPUT_DIR / "chapter_char_count.json"
        json_data = {
            "total_chapters": n,
            "total_chars": total_chars,
            "average": round(avg, 1),
            "percentiles": {
                "p10": round(p10, 1), "p25": round(p25, 1), "p50": round(p50, 1),
                "p75": round(p75, 1), "p90": round(p90, 1), "p95": round(p95, 1), "p99": round(p99, 1),
            },
            "min": {"chapter": chapters[0]["id"], "chars": char_counts[0]},
            "max": {"chapter": chapters[-1]["id"], "chars": char_counts[-1]},
            "stage_summary": {},
            "chapters": chapters,
        }
        for sn in STAGE_ORDER:
            st = stage_stats.get(sn)
            if st:
                json_data["stage_summary"][sn] = {
                    "count": st["count"],
                    "total_chars": st["total_chars"],
                    "average": round(st["total_chars"] / st["count"], 1),
                }
        json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ JSON 已写入: {json_path}")

    # ── 终端摘要 ──
    print()
    print(f"📊 分析摘要 — {n}章 · {total_chars:,}字 · 平均{avg:,.0f}字/章")
    print(f"   分布: P10={p10:,.0f}  P25={p25:,.0f}  P50={p50:,.0f}  P75={p75:,.0f}  P90={p90:,.0f}  P95={p95:,.0f}  P99={p99:,.0f}")

    # 长章节阈值建议：> P90 或 > 2×平均值
    long_threshold = max(p90, avg * 2)
    long_chapters = [c for c in chapters if c["chars"] > long_threshold]
    print(f"\n⚠  过长候选 (> {long_threshold:,.0f}字, P90或2×Avg较大者): {len(long_chapters)}章")
    if long_chapters:
        for c in sorted(long_chapters, key=lambda c: c["chars"], reverse=True):
            print(f"   Ch{c['id']:<4} {c['chars']:>8,}字  [{c['stage']}]  {c['filename']}")

    # 按阶段的过长分布
    print(f"\n📈 阶段分布（过长候选按阶段）:")
    for sn in STAGE_ORDER:
        st = stage_stats.get(sn)
        if not st:
            continue
        long_in_stage = [c for c in st["chapters"] if c["chars"] > long_threshold]
        avg_s = st["total_chars"] / st["count"]
        flag = f" ⚠ {len(long_in_stage)}章过长" if long_in_stage else ""
        print(f"   {sn}: {st['count']}章 · 平均{avg_s:,.0f}字 · 最长Ch{max(st['chapters'],key=lambda c:c['chars'])['id']}({max(c['chars']for c in st['chapters']):,}字){flag}")


if __name__ == "__main__":
    main()
