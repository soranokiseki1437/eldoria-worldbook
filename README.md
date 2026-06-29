# Eldoria — 艾尔多利亚守护者

> **SillyTavern 世界书** · 幽暗奇幻 × 史诗羁绊 × 单线纯爱NTRS融合线
>
> `output/Eldoria_V*.json` → 直接导入即用

---

## 世界观（30秒速览）

| | |
|---|---|
| **场景** | Eldoria 森林 — 200年前被腐化吞噬的精灵王国 |
| **主角** | 黎恩·舒华泽（`{{user}}`）— 灰色骑士，鬼之力持有者 |
| **女主** | Seraphina — 最后的精灵守护者，炽天使血脉，320岁 |
| **反派** | Thalion — 堕落的前守护者，腐化影牙首领 |
| **路线** | 单线纯爱NTRS融合线 — 共享时刻 ⇄ 回归时刻，170事件线性叙事 |
| **驱动** | 好感值系统 — 12角色，0-100，影响对话温度与亲密意愿 |

---

## 项目结构

```
世界书/
├── README.md
├── CLAUDE.md                       # Agent 执行手册
│
├── docs/                           # 权威数据源
│   ├── event/                      # ★ 事件TXT文件（170个，唯一权威）
│   │   ├── 0：序章/       (39)    苏醒→告白→第三者登场
│   │   ├── 1：试探和暧昧/ (24)    坦白→注视→第一次共享
│   │   ├── 2：挑逗和接受/ (12)    主动展示→初次口交
│   │   ├── 3：渐进接触/   (27)    足交→手交→乳交→口交→隐奸
│   │   ├── 4：跨线/       (13)    首次插入→自主选择
│   │   ├── 5：享受和掌控/ (33)    主动设计→多P→轮奸→极限
│   │   ├── 6：放纵/       (19)    主动服务→极限→低语者
│   │   ├── 7：终局/       ( 3)    决战前夜→净化→情书
│   │   └── 8：后日谈/     ( 0)    暂无事件
│   ├── chapter/                     # 始终触发条目+概念文件（6个）
│   ├── character/                   # 角色档案（14角色）
│   ├── creature/                    # 生物设定（11种）
│   ├── location/                    # 地点设定（20处）
│   ├── npc/                         # NPC档案（7人+总览）
│   └── world/                       # 世界观概念
│
├── scripts/                        # 构建与工具
│   ├── event_config.py             # 共享chapter元数据
│   ├── story_tool.py               # 验证 · 列表 · 引用扫描（Rule1-9）
│   ├── renumber_events.py          # 全局重编号引擎（核心）
│   ├── build_eldoria.py            # TXT → 世界书JSON
│   ├── assign_chapters.py          # DEFAULT_CHAPTERS权威数据源
│   ├── update_chapter_map.py       # 章节映射报告
│   ├── rebuild_all.py              # 一键全流程（build→browser）
│   ├── backup_restore.py           # 版本备份管理
│   └── generate_chapter_browser.py   # 直接读TXT → 可视化HTML浏览器
│
├── output/                         # 构建产物（不可手动编辑）
│   └── Eldoria_V*.json
│
├── visual/                         # 可视化
│   ├── 全事件浏览器.html
│   └── event_data.js
│
└── backup/                         # 自动备份
```

---

## 工作流

```
docs/story/{章节}/*.TXT   ← ★ 章节唯一权威源（302个独立文件）
    │
    ├── build_eldoria.py 直接读TXT ──→ output/Eldoria_V*.json
    └── story_tool.py 读TXT ──→ 验证 / 列表 / 引用扫描

rebuild_all.py = build → browser 一键完成
```

### 铁律

| # | 规则 |
|---|------|
| 1 | **TXT文件是唯一权威数据源** — 绝不手动编辑 JSON |
| 2 | **修改流程**：编辑TXT → `python scripts/rebuild_all.py` |
| 3 | **增删移章节**：操作TXT → `python scripts/renumber_events.py` → `rebuild_all.py` |
| 4 | **删前必查引用**：`python scripts/story_tool.py refs <ID>` |
| 5 | **参照 CLAUDE.md** — 所有内容编辑遵循写作铁律 |

### 常用命令

```bash
# 一键全流程重建
python scripts/rebuild_all.py

# 验证全部TXT
python scripts/story_tool.py validate

# 查找章节引用（删前必查）
python scripts/story_tool.py refs <ID>

# 查看章节内容
python scripts/story_tool.py show <ID>

# 重编号（增删移事件后运行）
python scripts/renumber_events.py
python scripts/renumber_events.py --dry-run    # 预览变更

# 章节映射报告
python scripts/update_chapter_map.py

# 备份
python scripts/backup_restore.py backup "说明"
```

---

## 快速开始

1. **阅读** `CLAUDE.md`（了解写作标准与工作流）
2. **导入** `output/Eldoria_V*.json` → SillyTavern World Info
3. **开始对话** — AI 自动读取 `first_mes` 开场

**修改世界书**：定位对应TXT → 编辑 → 构建 → 重新导入

---

## 文档导航

| 你想... | 阅读 |
|---------|------|
| 理解写作标准与工作流 | `CLAUDE.md` |
| 查看角色详情 | `docs/character/` |
| 了解世界观概念 | `docs/world/` |
| 浏览事件 | `visual/全事件浏览器.html` |
| 浏览事件详情 | `visual/全事件浏览器.html` |
| 新增/修改章节 | `docs/story/_TEMPLATE_RULES.md` |

---

*Eldoria 的森林在等待它的守护者。*
