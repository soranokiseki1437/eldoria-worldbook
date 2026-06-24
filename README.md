# Eldoria — 艾尔多利亚守护者

> SillyTavern 世界书（Worldbook）项目 | 版本见 `scripts/build_eldoria.py` VERSION
>
> 幽暗奇幻 x 史诗感 x 个人羁绊 — 三线叙事架构的交互式角色扮演世界

---

## 一、项目概述

**Eldoria** 是一款为 [SillyTavern](https://github.com/SillyTavern/SillyTavern) 平台设计的完整世界书。项目以闪之轨迹主角 **黎恩·舒华泽** 穿越至濒死的精灵魔法森林 **Eldoria** 为背景，围绕黎恩与精灵守护者 **Seraphina** 之间复杂的情感羁绊展开叙事。

核心创新：**三条叙事路线共存**——纯爱、NTRS（共享型NTR）、被动NTR——由变量系统驱动，根据玩家选择自然分支，路线间可自由转换。

**最终产物**：`output/Eldoria_V*.json` — 可直接导入 SillyTavern 的完整角色卡+世界书 JSON。

---

## 二、核心设定速览

| 要素 | 内容 |
|------|------|
| **世界观** | Eldoria 森林 — 200年前被腐化吞噬的精灵王国，圣光与腐化对抗 |
| **主角** | 黎恩·舒华泽（{{user}}）— 灰色骑士，鬼之力持有者 |
| **女主** | Seraphina — 最后的精灵守护者，炽天使血脉，320岁 |
| **反派** | Thalion — 堕落的前守护者，影牙首领 |
| **路线** | 纯爱 / NTRS（共享） / 被动NTR（破碎） |
| **变量** | 信任度、绝望度、Thalion影响力、腐化等级等，详见 `docs/03_变量系统.md` |

---

## 三、项目结构

```
世界书/
├── README.md                       # 本文件
├── CLAUDE.md                       # Agent 执行手册
├── docs/                           # ★ 权威数据源
│   ├── 00_方案总览.md               # 世界观、三线架构、设计哲学
│   ├── 00_工作流与版本管理.md        # 版本历史、构建流程
│   ├── 01_角色档案.md               # 所有角色详细档案
│   ├── 02_世界观设定.md             # 地点、历史、魔法体系
│   ├── 03_变量系统.md               # 变量定义、阈值、触发条件
│   ├── 04_关系阶段.md               # 三线关系阶段与行为指南
│   ├── 05_事件系统.md               # ★ 全部事件定义（权威事件源）
│   ├── 06_条目规划与格式.md          # 条目格式规范、关键词设计
│   ├── 07_最终执行指令.md            # 构建指令与输出规范
│   └── 08_事件格式标准.md            # 事件YAML格式统一标准
├── scripts/                        # 构建与工具
│   ├── build_eldoria.py            # JSON构建脚本（★ 核心）
│   ├── backup_restore.py           # 版本备份管理
│   ├── generate_event_browser.py   # 可视化网页生成器
│   └── ...                         # 其他工具脚本
├── output/                         # 构建输出
│   └── Eldoria_V*.json             # 最终产物（不可手动编辑）
├── visual/                         # 可视化
│   ├── 全事件浏览器.html            # 交互式事件浏览器
│   └── 剧情时间线可视化.html        # 剧情时间线
└── backup/                         # 备份目录
```

---

## 四、工作流

```
分 md 文档（权威源）→ build_eldoria.py（构建）→ Eldoria_V*.json（产物）
                         │
                         └── generate_event_browser.py → visual/*.html（可视化）
```

**核心规则**：
1. **分 md 是唯一权威数据源**，永远不要手动编辑 JSON
2. 修改流程：编辑分 md → 运行 `python scripts/build_eldoria.py` → 验证
3. 构建前建议备份：`python scripts/backup_restore.py backup "说明"`
4. 事件数量、章节分配等统计数据以 `docs/05_事件系统.md` 为准

---

## 五、快速开始

1. 阅读 `docs/00_方案总览.md` 了解世界观与三线架构（5分钟）
2. 将 `output/Eldoria_V*.json` 导入 SillyTavern World Info
3. 开始对话 — AI 将自动读取 first_mes 开场

**修改世界书**：找到对应分 md → 编辑 → `python scripts/build_eldoria.py` → 重新导入

---

## 六、维护原则

- **不重复信息**：事件数、章节名、版本号等动态数据以权威源文件为准，本文档不冗余列出
- **先读后改**：修改前阅读目标文件及其交叉引用
- **构建验证**：每次修改后运行 `--validate` 确保无错误
- **去AI化**：所有内容编辑遵循 CLAUDE.md 中的写作铁律

---

*Eldoria 森林在等待它的守护者。*
