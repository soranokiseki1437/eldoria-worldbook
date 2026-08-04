# Learnings

## [LRN-20260804-001] correction

**Logged**: 2026-08-04T00:00:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
"自由探索——X" 类章节的重复标题是项目故意设计，不是数据问题。

### Details
对 `_sex_index.txt` 做编号审计时发现 19 个重复标题（如"自由探索——营地的深夜"出现在 Ch609/575/238/165/234 等多个编号、"自由探索——营地的午后"出现在 Ch603/564/174/153/121 等）。用户确认：这些是格式合法的重复命名章节（自由探索章本来就是同名不同号），不属于异常，不应标记为需要修复的数据问题。用标题做编号匹配时，这类条目天然存在歧义（无法从标题唯一确定编号），处理时不应把"重复标题"本身当作缺陷，也不应要求索引去重。

### Suggested Action
审计/修复 sex索引编号时：把"自由探索"系列重复标题视为预期结构；工具（如 `scripts/fix_index_numbering.py`）对这类条目的自动匹配结果需人工复核，不以重复标题为判定错误。

### Metadata
- Source: user_feedback
- Related Files: docs/story/_sex_index.txt, scripts/fix_index_numbering.py
- Tags: sex_index, 标题匹配, 编号审计

---
## [LRN-20260804-002] best_practice

**Logged**: 2026-08-04T02:00:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
重编号后 `_sex_index.txt` 和 `_连续叙事弧线章节总览.md` 会整体脱节（619/841 条 sex 索引编号与标题不匹配、弧详情/阶段表仍是旧编号），可用"以标题为准"批量修复。

### Details
- sex索引：先跑 `scripts/fix_index_numbering.py`（按标题精确匹配重排编号，输出 `_sex_index_numbered.txt`），再手工处理其无法修复的条目：① 非整数编号（如 615.5，脚本正则不匹配会原样保留）；② 拆分章节缺（上/中/下）后缀的条目（需展开为各分部条目）；③ 标题被改名/加引号的条目（如"温泉的不知道你在"→`温泉的"不知道你在"`）。修复后全库校验应达到 0 不匹配。
- 弧总览：弧详情/弧总览/阶段表/非弧判定多为旧编号，而拆分表是新编号（混合状态）。按 `**N** 标题` 从文件系统逐条验证映射，勿用替换脚本整体处理（会双重转换）。阶段表章数须按阶段文件夹实际计数重算（本次 765→799 后阶段边界已变：3:150-271/4:272-395/5:396-559/6:560-680/7:681-700/8:701-799）。
- 拆分行（如"贮藏室的意外"）需以文件系统为准复核，不要轻信拆分表（本次表格本身是正确的，但需验证）。

### Suggested Action
重编号后按上述流程同步两份索引文档，并跑 `rebuild_all.py` 重建。

### Metadata
- Source: conversation
- Related Files: docs/story/_sex_index.txt, docs/story/_连续叙事弧线章节总览.md, scripts/fix_index_numbering.py
- Tags: sex_index, 弧总览, 编号同步, renumbering

---
## [LRN-20260804-003] correction

**Logged**: 2026-08-04T03:00:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
CLAUDE.md 及索引文档不要写死章节数目/章节 ID，引用章节一律用章节名称。

### Details
用户要求：CLAUDE.md 中最好不要包含章节数目和章节 id（如 745章/799章/Ch160 之类），因为每次重编号/新增章节都会过时；如果一定要引用章节，就引用章节名称（如《暮色里的通讯——暖岩石上的意外》）。本次已把 CLAUDE.md 中的 799章、744章、Ch160/167/336-338/494、17弧·63章、Ch491+494 等全部改为标题引用或删除，并把该约定写入 CLAUDE.md §2.4。

### Suggested Action
更新 CLAUDE.md 时保持该约定：版本行只写版本号与日期；不写章节数/条目数/JSON大小；引用章节用《名称》。

### Metadata
- Source: user_feedback
- Related Files: CLAUDE.md
- Tags: CLAUDE.md, 章节引用, 文档约定

---
## [LRN-20260804-004] correction

**Logged**: 2026-08-04T13:30:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
写规则文档本身要遵守文档自己的规则——我用了"写菲娜不是填空格…而是代入她"，恰是文档§4.16禁止的pivot否定结构；用户纠正"既然不是就不用说，只写有用的部分"。

### Details
重写 _TEMPLATE_RULES.md"人物指纹清单"引言时，我写了"写菲娜不是填空格。要写对她，不是把条目一个个勾上，而是代入她"——这正是该文档§4.16"禁'不是A，是B'pivot结构"要消灭的句式。用户指出：否定掉的"不是…"部分没用就直接删，只留正面指令（"代入菲娜再落笔——结合人物形象、当时心理、情境"）。规则文档的范例措辞必须通过自身禁令。

### Suggested Action
编辑 _TEMPLATE_RULES.md 时先自检新措辞是否踩了该文档自己的禁令：§4.16 否定pivot、句号堆砌、破折号滥用、cliché、碎片句。写肯定句，不写"不是X而是Y"。

### Metadata
- Source: user_feedback
- Related Files: docs/story/_TEMPLATE_RULES.md
- Tags: 否定pivot, 规则文档, 措辞自检

---
## [LRN-20260804-005] correction

**Logged**: 2026-08-04T13:40:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
角色声音/教学示例必须温暖、正面、取自原章节；删禁忌列与负面示例；不用"话少/冷漠"概括角色；清单化自问改代入角色。

### Details
用户对 _TEMPLATE_RULES.md §4.0.3 的连续纠正：① 删除禁忌列与负面示例，只留正面示例；② 卡兹尔示例"还冷漠了一点"要换温暖批；③ 艾玛示例不能只有和卡兹尔的（需覆盖多角色）；④ 黎恩人设从"话少"改为"温柔，幽默，沉稳可靠"，示例配温暖长对话/吐槽/调侃/与菲娜对话（"当然陪，我不会让你一个人面对这种事。""安排是我安排的，吃醋是它自己来的。""我只是没提醒你。""这种事你去问本人啊。"等），删"句号收尾"约束；⑤ 人物指纹清单/在方案应用清单去掉逐项自问，改代入角色（人物形象+当时心理+情境）；⑥ 零容忍缺项仅指菲娜任何阶段都脸红/可爱/甜美，不是每次逐项填满。

### Suggested Action
写角色声音/行为教学示例：从原章节挑温暖完整台词；用正面示例教学，不写"禁止/错误形态"；不用"话少/冷漠"当角色标签；教学清单避免"逐项自问"，教"代入角色推断行为"。

### Metadata
- Source: user_feedback
- Related Files: docs/story/_TEMPLATE_RULES.md
- Tags: 角色声音, 对白温度, 正面示例, 代入角色

---
## [LRN-20260804-006] best_practice

**Logged**: 2026-08-04T13:50:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
规则文档里的示例台词改动，要同步改原章节 TXT 并重建 JSON + validate——否则规则与正文（唯一权威源）脱节。

### Details
改 §4.0.3 速查表台词时，用户要求原章节同步：480"他就把你操了。"→"他就没忍住把我的小宝贝吃干抹净了。"（并把"替她把话说完、语气自然"改成"没好气地说"）；118"安排是我安排的。吃醋是它自己来的。"→逗号版（去句号堆砌）。改完跑 build_eldoria.py + story_tool.py validate。速查表示例是章节台词的引用，措辞/标点必须与原文一致。

### Suggested Action
改 _TEMPLATE_RULES.md 的示例台词后，grep 原章节核对并同步；改过章节 TXT 就执行 build_eldoria.py + story_tool.py validate；commit + push。

### Metadata
- Source: user_feedback
- Related Files: docs/story/5：享受和掌控/480：腐化藤的拘束——和上次一样的姿势.TXT, docs/story/2：挑逗和接受/118：挑逗的萌芽——确认吃醋的表情.TXT
- Tags: 示例同步, 章节TXT, 构建验证

---
## [LRN-20260804-007] correction

**Logged**: 2026-08-04T14:00:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
规则文档不留版本更新记录痕迹——删除"版本：V10.30.x"和"本次更新"脚注，版本历史以 git log 为准。

### Details
用户要求去掉 _TEMPLATE_RULES.md 底部的版本号+本次更新脚注（"不要保留版本更新记录痕迹"）。该文件现只留"模板和规则维护：新增字段类型或写作规则变更时同步更新本文件。"一行。commit message 里带版本号（如 V10.30.5）即可。

### Suggested Action
以后改规则文档不加版本/更新记录脚注；版本号写在 commit message，历史看 git log。

### Metadata
- Source: user_feedback
- Related Files: docs/story/_TEMPLATE_RULES.md
- Tags: 版本脚注, git log, 文档约定

---
