#!/usr/bin/env python3
"""统计187章以后的章节字数分布"""
import os
import re

story_dir = "docs/story"
chapters = []

for root, dirs, files in os.walk(story_dir):
    for f in files:
        if not f.endswith('.TXT'):
            continue
        if f.startswith('_'):
            continue
        m = re.match(r'^(\d+(?:\.\d+)?)：', f)
        if not m:
            continue
        ch_id = m.group(1)
        try:
            ch_num = float(ch_id)
        except ValueError:
            continue
        if ch_num < 187:
            continue

        filepath = os.path.join(root, f)
        with open(filepath, 'r', encoding='utf-8') as fh:
            content = fh.read()

        chinese_chars = len(re.findall(r'[一-鿿]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        word_count = chinese_chars + english_words

        chapters.append({
            'id': ch_id,
            'num': ch_num,
            'file': f,
            'stage': os.path.basename(root),
            'word_count': word_count,
        })

chapters.sort(key=lambda x: x['num'])

print(f"=== 187章以后章节字数统计 ===")
print(f"总章节数: {len(chapters)}")
print(f"章节范围: {chapters[0]['id']} - {chapters[-1]['id']}")
print()

word_counts = [c['word_count'] for c in chapters]
word_counts.sort()
print(f"=== 字数分布 ===")
print(f"最小值: {word_counts[0]}")
print(f"最大值: {word_counts[-1]}")
print(f"中位数: {word_counts[len(word_counts)//2]}")
print(f"平均值: {sum(word_counts)//len(word_counts):.0f}")

def percentile(data, p):
    k = (len(data) - 1) * p / 100
    f = int(k)
    c = k - f
    if f + 1 < len(data):
        return data[f] + c * (data[f+1] - data[f])
    return data[f]

for p in [10, 25, 50, 75, 90, 95, 99]:
    print(f"P{p}: {percentile(word_counts, p):.0f}")

print()

buckets = [
    (0, 500, "0-500"),
    (500, 1000, "500-1000"),
    (1000, 1500, "1000-1500"),
    (1500, 2000, "1500-2000"),
    (2000, 2500, "2000-2500"),
    (2500, 3000, "2500-3000"),
    (3000, 4000, "3000-4000"),
    (4000, 5000, "4000-5000"),
    (5000, 7000, "5000-7000"),
    (7000, 10000, "7000-10000"),
    (10000, 999999, "10000+"),
]

print(f"=== 字数区间分布 ===")
for lo, hi, label in buckets:
    count = sum(1 for w in word_counts if lo <= w < hi)
    pct = count / len(word_counts) * 100
    bar = '█' * int(pct / 2)
    print(f"{label:>12}: {count:>4}章 ({pct:5.1f}%) {bar}")

print()

print(f"=== 最长的30章 ===")
top = sorted(chapters, key=lambda x: x['word_count'], reverse=True)[:30]
for i, c in enumerate(top):
    print(f"  {i+1:>2}. Ch{c['id']:>6} [{c['stage']}] {c['word_count']:>6}字 — {c['file'][:80]}")

print()

print(f"=== 最短的20章 ===")
bottom = sorted(chapters, key=lambda x: x['word_count'])[:20]
for i, c in enumerate(bottom):
    print(f"  {i+1:>2}. Ch{c['id']:>6} [{c['stage']}] {c['word_count']:>6}字 — {c['file'][:80]}")
