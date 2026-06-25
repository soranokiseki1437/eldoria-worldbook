# Eldoria — 艾尔多利亚守护者

> **SillyTavern 世界书** · 幽暗奇幻 × 史诗羁绊 × 三线叙事
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
| **路线** | 纯爱 · NTRS（共享型） · 被动NTR（破碎型） |
| **驱动** | 变量系统 — 玩家选择自然分支，路线间自由转换 |

---

## 项目结构

```
世界书/
├── README.md
├── CLAUDE.md                       # Agent 执行手册
│
├── docs/                           # 权威数据源
│   ├── event/                      # ★ 事件TXT文件（203个，唯一权威）
│   │   ├── E/   (15) 阶段零共通
│   │   ├── P/   (22) 纯爱路线
│   │   ├── N/   (104) NTRS路线
│   │   ├── PN/  (37) 被动NTR路线
│   │   ├── W/   ( 8) 世界事件
│   │   ├── H/   ( 4) 隐藏事件
│   │   ├── G/   ( 7) 通用SFW
│   │   └── R/   ( 8) 黎恩专属
│   ├── 00_方案总览.md               # 世界观 · 三线架构 · 设计哲学
│   ├── 01_角色档案.md               # 全部角色详细档案
│   ├── 02_世界观设定.md             # 地点 · 历史 · 魔法体系
│   ├── 03_变量系统.md               # 变量定义 · 阈值 · 触发条件
│   ├── 04_关系阶段.md               # 三线关系阶段与行为指南
│   ├── 05_事件系统.md               # 事件索引（生成产物，8.6KB）
│   ├── 06_条目规划与格式.md          # 条目格式 · 关键词规范
│   ├── 07_最终执行指令.md            # 构建指令 · 输出规范
│   └── 08_事件格式标准.md            # TXT格式标准
│
├── scripts/                        # 构建与工具
│   ├── event_config.py             # 共享prefix元数据
│   ├── event_tool.py               # 验证 · 列表 · 引用扫描
│   ├── renumber_events.py          # 批量重编号 + 交叉引用更新
│   ├── assemble_md.py              # TXT → 05MD索引（零硬编码）
│   ├── build_eldoria.py            # TXT → 世界书JSON（306条目）
│   ├── assign_chapters.py          # DEFAULT_CHAPTERS数据源
│   ├── update_chapter_map.py       # 章节映射报告
│   ├── rebuild_all.py              # 一键全流程（assemble→build→browser）
│   ├── backup_restore.py           # 版本备份管理
│   └── generate_event_browser.py   # TXT → 可视化HTML浏览器
│
├── output/                         # 构建产物（不可手动编辑）
│   └── Eldoria_V*.json
│
├── visual/                         # 可视化
│   ├── 全事件浏览器.html
│   └── 剧情时间线可视化.html
│
└── backup/                         # 自动备份
```

---

## 工作流

```
docs/event/{prefix}/*.TXT   ← ★ 事件唯一权威源（193个独立文件）
    │
    ├── build_eldoria.py 直接读TXT ──→ output/Eldoria_V*.json
    ├── assemble_md.py 读TXT ──→ docs/05_事件系统.md（索引）
    └── event_tool.py 读TXT ──→ 验证 / 列表 / 引用扫描

rebuild_all.py = assemble → build → browser 一键完成
```

**V6.5 关键变化**：事件正文从单体MD迁移至独立TXT文件。MD退为轻量索引。

### 铁律

| # | 规则 |
|---|------|
| 1 | **TXT文件是唯一权威数据源** — 绝不手动编辑 JSON |
| 2 | **修改流程**：编辑TXT → `python scripts/rebuild_all.py` |
| 3 | **删前必查引用**：`python scripts/event_tool.py refs <ID>` |
| 4 | **参照 CLAUDE.md** — 所有内容编辑遵循写作铁律 |

### 常用命令

```bash
# 一键全流程重建
python scripts/rebuild_all.py

# 验证全部TXT
python scripts/event_tool.py validate

# 查找事件引用（删前必查）
python scripts/event_tool.py refs <ID>

# 重编号（填补空缺）
python scripts/renumber_events.py <prefix>

# 章节映射报告
python scripts/update_chapter_map.py

# 备份
python scripts/backup_restore.py backup "说明"
```

---

## 快速开始

1. **阅读** `docs/00_方案总览.md`（5分钟了解世界观与三线架构）
2. **导入** `output/Eldoria_V*.json` → SillyTavern World Info
3. **开始对话** — AI 自动读取 `first_mes` 开场

**修改世界书**：定位对应分md → 编辑 → 构建 → 重新导入

---

## 文档导航

| 你想... | 阅读 |
|---------|------|
| 理解世界观与路线设计 | `docs/00_方案总览.md` |
| 查看角色详情 | `docs/01_角色档案.md` |
| 了解变量与触发条件 | `docs/03_变量系统.md` |
| 查看所有事件 | `docs/05_事件系统.md` |
| 新增/修改事件 | `docs/08_事件格式标准.md` → `docs/05_事件系统.md` |
| 理解条目格式 | `docs/06_条目规划与格式.md` |
| 执行构建与部署 | `docs/07_最终执行指令.md` |
| 编辑NSFW内容 | `CLAUDE.md`（写作标准+禁令） |

---

*Eldoria 的森林在等待它的守护者。*
