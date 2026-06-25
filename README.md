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
├── docs/                           # ★ 权威数据源（不可跳过）
│   ├── 00_方案总览.md               # 世界观 · 三线架构 · 设计哲学
│   ├── 01_角色档案.md               # 全部角色详细档案
│   ├── 02_世界观设定.md             # 地点 · 历史 · 魔法体系
│   ├── 03_变量系统.md               # 变量定义 · 阈值 · 触发条件
│   ├── 04_关系阶段.md               # 三线关系阶段与行为指南
│   ├── 05_事件系统.md               # ★ 全部事件定义（166个，权威源）
│   ├── 06_条目规划与格式.md          # 条目格式 · 关键词规范
│   ├── 07_最终执行指令.md            # 构建指令 · 输出规范
│   └── 08_事件格式标准.md            # YAML格式统一标准
│
├── scripts/                        # 构建与工具
│   ├── build_eldoria.py            # ★ JSON构建（V6.0: 零硬编码，全MD驱动）
│   ├── event_tool.py               # 事件CRUD + 4规则验证
│   ├── update_chapter_map.py       # 章节映射表自动生成
│   ├── insert_and_renumber.py      # 插入事件 + 级联重编号
│   ├── backup_restore.py           # 版本备份管理
│   └── generate_event_browser.py   # 可视化网页生成
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
分 md（权威源）
    │
    └── build_eldoria.py ──→ output/Eldoria_V*.json
                │
                └── generate_event_browser.py ──→ visual/*.html
```

**V6.0 关键变化**：事件条目由MD自动驱动。新增/修改事件**只需改MD文件**，无需再手动编辑 `build_eldoria.py`。

### 铁律

| # | 规则 |
|---|------|
| 1 | **分md是唯一权威数据源** — 绝不手动编辑 JSON |
| 2 | **修改流程**：编辑分md → `python scripts/build_eldoria.py` → 验证 |
| 3 | **构建前备份**：`python scripts/backup_restore.py backup "说明"` |
| 4 | **参照 CLAUDE.md** — 所有内容编辑遵循写作铁律 |

### 常用命令

```bash
# 构建
python scripts/build_eldoria.py

# 验证
python scripts/build_eldoria.py --validate
python scripts/event_tool.py validate "docs/05_事件系统.md"

# 新增/重排事件后更新章节映射
python scripts/update_chapter_map.py

# 备份
python scripts/backup_restore.py backup "修改说明"
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
