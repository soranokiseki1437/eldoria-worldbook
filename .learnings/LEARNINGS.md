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
## [LRN-20260804-008] best_practice

**Logged**: 2026-08-04T11:21:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Agent 启动器安全分类模型持续不可用时反复重试无效，应尽快回退为在主线自己执行机械性任务。

### Details
本次派两个 agent 做大修：sex_index agent 正常启动并交付；弧总览 agent 因分类器"temporarily unavailable"连续失败 5 次（约 3 分钟）。继续重试浪费约 3 分钟，最终回退为主线自己用 Python 脚本完成（弧总览是机械性结构交换，脚本处理比 Edit 精确匹配更稳，结果与预期一致）。该故障是 harness 侧暂时性故障，与任务内容无关；只读操作不受影响。

### Suggested Action
Agent 启动报 `temporarily unavailable` 时：最多重试 1-2 次即回退；机械性/结构化任务直接在主线做（Python 脚本交换块，避免引号/空白不匹配）；等待期间可先做只读调查。

### Metadata
- Source: conversation
- Tags: agent, 分类器, 回退策略

---
## [LRN-20260804-009] best_practice

**Logged**: 2026-08-04T11:21:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
本仓库存在并发会话时，其 `git add -A` + commit 会把我的未提交改动扫进无关提交；每完成一项独立改动就应按文件单独提交，避免成果被 sweep 进 message 不符的提交。

### Details
本次会话期间另一进程在并发提交：`384b9a37`(V10.30.5) 把 agent 已完成但未提交的 `_sex_index.txt` 去重结果、`_连续叙事弧线章节总览.md` 的既有改动、`_TEMPLATE_RULES.md` 一并提交，commit message 只描述 RULES 改动，与实际内容不符；随后又提交 `bfa47ec4`(learnings)。另外 `git push` 可能超时（本次 2 分钟 timeout 后需重试确认）。

### Suggested Action
在本仓库：每完成一个文件就 `git add <具体文件>` + commit + push，不用 `git add -A`；push 超时后用 `git status -sb` 确认是否真正到达 origin，未到则重试。

### Metadata
- Source: conversation
- Related Files: docs/story/_sex_index.txt, docs/story/_连续叙事弧线章节总览.md
- Tags: git, 并发会话, 提交策略
- See Also: LRN-20260804-002

---
## [LRN-20260804-010] best_practice

**Logged**: 2026-08-04T11:21:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
`_连续叙事弧线章节总览.md` 的弧总览表与弧详情小节必须严格按起始章节号升序（标题自述"按章节顺序排列"）；本次发现 421→425 排在 441→443 之后属乱序，已重排并同步重编弧N号。

### Details
弧8(421→425 艾玛×卡兹尔)被排在弧7(441→443 劳拉)之后，违反文件自身声明。修正：交换两段并重编"弧N"（总览表+详情标题），其余章节引用经 check_consistency 验证 0 错误。弧N 号全仓库无外部引用，重编安全。注意 check_consistency.py 只校验引用是否匹配文件系统，并不校验弧序。

### Suggested Action
新增/调整弧时保持起始章升序；建议给 check_consistency.py 增加弧序校验（见 FEAT-20260804-001）。

### Metadata
- Source: conversation
- Related Files: docs/story/_连续叙事弧线章节总览.md
- Tags: 弧总览, 弧序, 章节顺序
- See Also: LRN-20260804-002

---
## [LRN-20260804-008] correction

**Logged**: 2026-08-04T15:00:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
事后余韵/回归时刻：黎恩关切先于分析，菲娜忐忑+坚定、对白有来有回——我优化672时把黎恩写成冷静蹲下分析（"你流出来的蜜液，可能带着圣光净化的气息"）、菲娜平淡回应，被用户判定"没改好"并重写。

### Details
用户重写示范：黎恩紧张地跑到菲娜面前、抱着她说"菲娜！你还好吗？不用怕了，有我在"，圣光分析用"说起来"轻轻带出；菲娜回到他怀里松了口气、反过来安抚他"我好好的黎恩，有你在我不怕哦"；她提出决意时是忐忑+坚定的复合情绪（"如果那里可以让他们解脱...那我...那下次可以试试"），声音轻、带犹豫，说完接甜美落点"嗯呐~"；占有欲确认删掉重复情境的场景描述（"事后黎恩蹲在她面前，她低头看蜜液"），直接进决意对话。

### Suggested Action
写事后/回归时刻：① 黎恩先关切后分析，身体接触在前，不是观察者；② 菲娜提出决意是忐忑+坚定的混合，带犹豫和甜美落点；③ 回归对白有来有回（黎恩怕她受伤→菲娜安抚他）；④ 占有欲确认直接写决意/占有对话，不重述情境。已将①②③并入 _TEMPLATE_RULES.md §8.5.2 关切先于分析 / §4.6 事后余韵铁律5-6，④并入§3.1占有欲确认字段说明。

### Metadata
- Source: user_feedback
- Related Files: docs/story/6：放纵/672：腿间的净化——低语者的解脱.TXT, docs/story/_TEMPLATE_RULES.md
- Tags: 事后余韵, 回归时刻, 黎恩关切, 忐忑坚定, 占有欲确认

---
