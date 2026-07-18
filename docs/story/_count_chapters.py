import os, re

stages = {}
for root, dirs, files in os.walk('.'):
    stage = os.path.relpath(root, '.')
    if stage == '.': continue
    chapters = []
    for f in files:
        if not f.endswith('.TXT') or f.startswith('_'): continue
        m = re.match(r'(\d+)', f)
        if not m: continue
        cid = int(m.group(1))
        if cid < 154: continue
        if '自由探索' in f: continue
        chapters.append((cid, f))
    if chapters:
        chapters.sort()
        stages[stage] = chapters

# Print all non-free-exploration chapters for agent allocation
all_chapters = []
for stage in sorted(stages.keys()):
    for cid, fname in stages[stage]:
        all_chapters.append((cid, stage, fname))

all_chapters.sort()

# Proposed agent ranges
agents = [
    ("A", 154, 204),
    ("B", 206, 245),
    ("C", 246, 313),
    ("D", 314, 372),
    ("E", 373, 431),
    ("F", 432, 478),
    ("G", 479, 524),
    ("H", 525, 584),
    ("I", 585, 623),
]

for name, lo, hi in agents:
    chs = [(c,s,f) for c,s,f in all_chapters if lo <= c <= hi]
    ids = [str(c[0]) for c in chs]
    # Get stage info
    stage_set = set(s for _,s,_ in chs)
    print(f"Agent {name} [{lo}-{hi}]: {len(chs)} chapters | stages: {', '.join(sorted(stage_set))}")
    if chs:
        print(f"  First: {chs[0][0]} {chs[0][2][:40]}")
        print(f"  Last:  {chs[-1][0]} {chs[-1][2][:40]}")

print(f"\nTotal: {len(all_chapters)}")
