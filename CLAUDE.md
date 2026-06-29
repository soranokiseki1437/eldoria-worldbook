# CLAUDE.md — 世界书构建与章节增强专用Agent

> **定位**：Eldoria世界书 · 100%对齐俺妹ver1.41格式
> **版本**：v10.3 · 2026-06-29

---

## 一、架构与格式

### 1.1 输出格式

**11字段精简Object格式**（V10.2.0验证可行，V10.3.0巩固）：

```
顶层：entries（Object，keyed by string uid）+ _meta
条目：uid/key/keysecondary/comment/content/constant/
      selective/order/position(整数0/1/4)/depth/group
      无 extensions 膨胀（31字段×434条≈300KB纯浪费）
      无 originalData 冗余（434条完整复制≈400KB纯浪费）
      无 characterFilter（434条空壳纯浪费）
```

> **致命陷阱**：entries 必须是 Object `{"0":{...}}`，绝不可用 Array `[{...}]`——Array导致酒馆拒绝导入。

### 1.2 章节体系

- 302个章节，纯数字编号，线性叙事，无分支
- 9个阶段目录（`docs/story/{0：序章/ ... 8：后日谈/}`）
- 章节key：`['第N章']` — 单key，`selectiveLogic: 0`（OR匹配）
- `{{user}}` = 黎恩·舒华泽（第三人称叙事）

### 1.3 系统条目（照抄俺妹）

| 条目 | 位置 | 说明 |
|:--|:--|:--|
| `章节追踪指令` | pos=4, depth=0, order=999 | 玩家上下文驱动的剧情重构 |
| `游戏状态界面` | pos=4, depth=0, order=998 | `<overall>` 格式模板 |
| `叙述风格指令` | pos=4, depth=1, order=100 | 第三人称+去AI化铁律 |
| `世界时间并行和隐奸` | pos=4, depth=1, order=100 | 时间流动/双视角/隐奸叙事逻辑 |

---

## 二、工作流

### 2.1 标准修改循环

```
Step 0 — 确认范围
  ├── 定位 docs/story/{章节}/{ID}：{名称}.TXT
  └── 检查交叉引用：story_tool.py refs <ID>

Step 1 — 阅读权威源
  ├── 阅读 TXT（唯一权威）
  └── 新增章节：参照 docs/story/_TEMPLATE.TXT

Step 2 — 执行修改
  ├── 编辑TXT文件（key: value格式）
  ├── 新增：cp模板→填充→ID行填小数→renumber_events.py
  ├── 删除：story_tool.py refs <ID>→删TXT→renumber_events.py
  └── 修改：编辑TXT即可，无需renumber

Step 3 — 构建验证
  ├── python scripts/build_eldoria.py           ← 构建JSON
  ├── python scripts/story_tool.py validate     ← 验证TXT
  └── 检查JSON中对应条目的content

Step 4 — 记录
  ├── 重大修改 → git commit
  └── 小修复 → TXT文件内加日期注释
```

### 2.2 章节TXT字段体系

| 字段 | 必填 | 说明 |
|------|:--:|------|
| `ID` | ✅ | 纯数字，新章节填小数插入标记 |
| `名称` | ✅ | 中文，`前半段——后半段` 格式 |
| `NSFW` | ✅ | `是` 或 `否` |
| `性行为等级` | 条件 | 0-10，NSFW=是时必填 |
| `阶段` | 条件 | 8个合法值（序章/…/后日谈） |
| `第三者` | 条件 | 姓名（身份），有第三者时填写 |
| `黎恩知情` | 条件 | 描述黎恩角色 |
| `占有欲确认` | 条件 | NTRS NSFW章节事后描写 |
| `好感影响` | 条件 | `{角色名}: ±{value}`，≤10 |
| `情境` | ✅ | bullet列表，至少3条，第三人称 |
| `核心` | ✅ | 设计意图、叙事位置 |
| `章节核心目标` | 新 | ← `核心` 自动推导（构建脚本填充） |
| `章节任务` | 新 | ← LLM逐章写入TXT，构建脚本直接读取 |
| `章节终止条件` | 新 | ← LLM逐章写入TXT，构建脚本直接读取 |

### 2.3 构建命令

```bash
python scripts/build_eldoria.py              # 构建JSON（自动备份）
python scripts/build_eldoria.py --dry-run    # 仅验证不写盘
python scripts/rebuild_all.py                # build → browser
python scripts/story_tool.py validate        # 验证全部TXT
python scripts/story_tool.py refs <ID>       # 查引用（删前必跑）
python scripts/renumber_events.py            # 全局重编号
python scripts/renumber_events.py --dry-run  # 预览变更
```


---

## 三、叙事与写作规则

### 3.1 叙事人称（照抄俺妹）

- **第三人称**，`{{user}}`（黎恩·舒华泽）为视角焦点
- 始终用"他"或"黎恩"指代{{user}}，不用"我"
- {{user}}不知道的事情不写，保持视角一致性

### 3.2 叙事基调

单线NTRS融合线：**共享时刻 ⇄ 回归时刻**交替推进。
Seraphina永远是强者——共享是双方同意的体验，回归是情感落点。

### 3.3 去AI化写作铁律

| # | 禁令 | 说明 |
|---|------|------|
| 1 | 不写"成本"表述 | 禁用优化/提升/降低/节省/高效/低成本 |
| 2 | 不括号堆砌 | 补充解释直接写进正文 |
| 3 | 不列函数/变量名 | 叙事文本不出现变量名罗列 |
| 4 | 不写空泛结尾 | 禁用"为...支撑""奠定...基础" |
| 5 | 不做未证实声明 | 适用项目书写作逻辑 |
| 6 | 不反复"看黎恩确认" | 共享时刻聚焦体验，回归时刻才看黎恩 |
| 7 | 不反复"微笑/平静/掌控" | Seraphina随阶段演进有变化有波动 |
| 8 | 不用"不是…是…"句式 | 直接写肯定句 |
| 9 | 不写元叙事标记 | 版本变更记git，不入TXT |
| 10 | 不后挂解释 | 修饰融入动词——"轻轻贴上" |
| 11 | 功能性对话可概述 | 保留承载性格或弦外之音的对话 |

### 3.4 NSFW规则

- 直接词汇：肉棒/小穴/口交/乳交/插入/射精
- 禁不良气味（体臭/骚味）——足部气味例外
- 禁魔法灯光秀（圣光/鬼之力流转）
- Seraphina永远是强者内核
- `<overall>`格式详见 `docs/chapter/_游戏状态界面.TXT`

---

## 四、核心设计原则

1. **黎恩永远是黎恩**：灰色骑士内核，`{{user}}`=黎恩
2. **Seraphina永远是Seraphina**：守护者的优雅与孤独
3. **共享 ≠ 背叛**：双方自愿，共享后回归彼此
4. **共享时刻 ⇄ 回归时刻**：两条线交替推进
5. **章节TXT是唯一权威源**：绝不手动编辑JSON

---

## 五、文档依赖链

```
docs/story/{章节}/*.TXT     ← ★ 章节唯一权威源
├── _TEMPLATE.TXT            ← 新章节模板
├── chapter/                 ← 系统指令+概念文件
│   ├── _章节追踪指令.TXT    ← 玩家上下文驱动的重构流程
│   ├── _游戏状态界面.TXT    ← <overall>格式模板
│   ├── _叙述风格指令.TXT    ← 第三人称叙事+去AI化
│   └── _世界时间并行和隐奸.TXT ← 时间流动/双视角/隐奸逻辑
├── character/               ← 角色档案
├── world/                   ← 世界观概念
├── magic/                   ← 魔法体系
├── creature/                ← 生物设定
├── location/                ← 地点设定
├── npc/                     ← NPC档案
├── affection/               ← 好感度分级
scripts/
├── build_eldoria.py         ← TXT→世界书JSON（逐字段对齐俺妹格式）
├── story_tool.py            ← 验证/列表/查看/引用扫描
├── renumber_events.py       ← 全局重编号引擎
├── generate_chapter_browser.py ← 全章节浏览器生成器(V5.0 角色×阶段分类)
└── rebuild_all.py           ← 一键重建(build→browser)
开场白.txt                   ← 首个消息（含<overall>状态块）
output/Eldoria_V10.3.0.json  ← 派生产物，不可手动编辑
visual/全章节浏览器.html      ← 章节浏览器（角色×阶段分类筛选）
```

---

## 六、V10.3 变更记录（2026-06-29）

**当日变更汇总**：

### A. JSON瘦身（3.9MB→1.3MB，-67%）+ 导入修复
| # | 变更 | 说明 |
|---|------|------|
| 1 | **43字段→11字段** | 砍掉extensions(31字段)/characterFilter/originalData，验证V10.2.0的9字段可行后增至11字段 |
| 2 | **entries保持Object** | Array→Object是本次导入失败的根因，已修复并写入铁律 |
| 3 | **去掉extensions/originalData/characterFilter** | 434条×31字段extensions+434条originalData复制+434个空characterFilter=~700KB纯浪费 |
| 4 | **参考文件瘦身** | 俺妹参考987KB→412KB(-58%)，原版备份于同目录 |

### B. 角色特征一致性修复
| # | 变更 | 说明 |
|---|------|------|
| 5 | **乔治不戴眼镜** | 23个章节"推眼镜"→"摸后脑勺"，ch224"眼镜上的轻吻"→"帽檐下的轻吻" |
| 6 | **凯尔ch166** | "推鼻梁上已经不存在的眼镜"→"推眼镜"（档案明写戴细框眼镜） |
| 7 | **黎恩发色瞳色** | `_人物总览`"灰发灰眼"→"黑发青紫瞳"（对齐角色档案） |

### C. 系统条目调整
| # | 变更 | 说明 |
|---|------|------|
| 8 | **世界时间并行** | pos=0 depth=4 → pos=4 depth=1（与叙述风格指令同级，对齐俺妹文风层） |

### D. 章节浏览器V5.0
| # | 变更 | 说明 |
|---|------|------|
| 9 | **角色×章节分类** | 第三者字段 + 好感影响 + 标题 三层OR提取，精准匹配主角 |
| 10 | **去路线标签** | 删除NTRS/纯爱/被动NTR/共通标签，仅保留NSFW/SFW+行为类型 |
| 11 | **改名** | 全事件浏览器→全章节浏览器，V4.7.1→V5.0 |

**当前状态**：434条目·302章节·9阶段·12角色·构建通过·11字段精简Object格式·JSON 1.3MB

---

*Eldoria的森林在等待真正敢于深入的讲述者。开始工作。*
