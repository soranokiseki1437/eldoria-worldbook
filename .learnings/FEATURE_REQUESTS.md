# Feature Requests

## [FEAT-20260804-001] check_consistency_add_sexindex_dedup_and_arc_order

**Logged**: 2026-08-04T11:21:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Requested Capability
`scripts/check_consistency.py` 目前无法发现三类问题：① sex索引同一分类内的精确重复行；② 未分类段的陈旧条目（已在其他分类归类却仍留在未分类）；③ 弧总览/弧详情的乱序（不校验弧序）。

### User Context
本次大修 `_sex_index.txt` 时发现 55 条精确重复行（如 247凯尔的山洞×3、559矿道的深处（下）×4）、未分类段 10 条全部已在其他分类归类却仍残留；`_连续叙事弧线章节总览.md` 存在 421→425 排在 441→443 之后的乱序。这些在 `check_consistency.py --quiet` 全绿的情况下依然存在，说明该校验器对"行级正确但结构错误"的场景是盲区。

### Complexity Estimate
medium

### Suggested Implementation
- [5] sex索引检查项增加：
  - 每个分类内 `(编号, 标题)` 去重检测，重复即 fail（附行号）；
  - 未分类段的条目若出现在其他分类，即 fail 提示"已归类仍留未分类"。
- [6] 弧总览检查项增加：
  - 弧总览表各行按起始章节号严格升序校验；
  - 弧详情小节顺序/起始章与弧总览表一一对应校验。
- 保留现有"编号↔标题与文件系统匹配"检查不变。

### Metadata
- Frequency: recurring（重编号/新增章节后反复出现同类问题）
- Related Features: scripts/check_consistency.py 现有第[5][6]项
- See Also: LRN-20260804-013

---
