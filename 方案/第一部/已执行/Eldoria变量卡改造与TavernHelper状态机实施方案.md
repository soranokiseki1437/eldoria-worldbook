# Eldoria 变量卡改造与 TavernHelper 状态机详细实施方案 (v1.2.0)

> **文档版本**：v1.2.0（工程级加固与全链路闭环版）· 2026-09-26  
> **归属工程**：Eldoria 世界书 · 第一部  
> **适用环境**：SillyTavern + TavernHelper（酒馆助手）扩展  
> **核心目标**：将大纲推进升级为前端 JavaScript 变量状态机驱动，通过宏物理反哺实现精准切章与世界书激活闭环，彻底根除大模型中途幻觉跳章。

---

## 一、 方案背景与解决的核心痛点

### 1.1 现状与痛点
在纯 Prompt（纯世界书文本）驱动的模式下，大模型同时承担了**“编剧（写正文）”**与**“裁判（算进度与切章）”**的双重职责：
* **终点引力导致跳章**：大模型看到总条数或下一章预告时，极易产生“叙事已充分，该收束了”的幻觉，在中途（如 2/4、6/7）强行时间跳跃切入下一章；
* **自由探索易丢进度**：玩家中途偏离主线进行分支互动时，大模型容易混淆“章节内自由探索”与“章节完结”，导致断点丢失或直接跳章；
* **裁判吹黑哨**：虽然提示词中三令五申“X < N 严禁跳章”，但纯文本约束属于概率机制，缺乏物理级硬阻断；
* **状态反哺断层**：前端变量与提示词脱节时，大模型无法感知当前章节已变更，导致代码切章后大模型依然沉浸在旧章节。

### 1.2 改造目标
引入类脑社区成熟的 **MVU（Macro Variable Update）变量状态机机制**：
* **职责彻底分离**：大模型仅负责汇报本轮动作的**增量状态（Delta State）**；
* **裁判权收归代码**：由 **TavernHelper 前端脚本**严格执行数学计算、进度步进、余韵冻结、**章节物理加一（`chapter + 1`）**与**大纲归零或继承（`step = 0 / 1`）**；
* **物理级宏反哺闭环**：通过 `{{getvar::chapter}}` 宏将酒馆变量硬注入系统提示词与状态栏，自动命中触发对应章节的世界书条目，形成**“代码切章 ➔ 宏替换 ➔ 世界书激活 ➔ LLM 获取新大纲”**的绝对闭环；
* **双变量精准分治**：彻底拆分“固有自由探索章节（沙盒漫游）”与“常规章节内自由探索状态（分支偏离）”，并补全沙盒跳出通道，杜绝死锁与互踩；
* **保持纯粹文学性**：**好感度等复杂数值绝不强设变量**，完全保留原汁原味的文学描写。

---

## 二、 三大安全底线与不伤原则（确保 100% 稳妥）

1. **绝对不伤 923 个故事章节（零侵入）**：
   * `docs/story/*/*.TXT` 全部 923 章剧本源文件 **0 修改、1 个字都不用动**；
   * 章节数据继续保持标准的 `总情境数: N` 与标号列表 `  - 1. ... - N. ...`；世界书章节关键词保持单 key `第N章`。
2. **绝对不伤历史聊天记录与存档（零破坏）**：
   * 改造仅作用于酒馆前端监听与 Prompt 状态块，不重写历史楼层；
   * 脚本内置**容错清洗器（JSON Sanitizer）**与正则兜底，若大模型某轮输出残缺或包含 Python 风格大小写/注释，脚本自动修复并继承，绝不报红崩溃。
3. **版本随时一键秒级回滚**：
   * 实施前已有永久 Git 锚点（`b2a44390`），任何意外均可单命令无损撤销。

---

## 三、 变量字典与数据模型（Variable Schema）

在酒馆变量池中建立以下 6 个核心变量（**严禁引入任何下一章节变量，防止提前触发下一章世界书大纲**）：

| 变量键名 (`Key`) | 类型 | 取值范围 / 示例 | 职责与含义 |
| :--- | :---: | :--- | :--- |
| `chapter` | `int` | `1 ~ 923` | 当前正进行的章节物理编号（**唯一上下文锚点，全库唯一允许激活的章节关键词**） |
| `step` | `int` | `0 ~ N` | 当前已展开的大纲情境编号（`0` 表示刚进入新章未展开；沙盒章节为 `0`） |
| `max_step` | `int` | `0 ~ 15` | 本章总情境数（常规章节为具体数字 N；沙盒章节为 `0`） |
| **`is_sandbox_chapter`** | `bool` | `true / false` | **固有自由探索章节标记**（全库118章沙盒，锁定禁止自动步进与冷却） |
| **`is_free_explore`** | `bool` | `true / false` | **章节内自由探索状态标记**（动态运行时状态，常规章节偏离主线时冻结断点） |
| `in_afterglow` | `bool` | `true / false` | 当前是否已推完所有情境，正处于“强制余韵沉淀与冷却”状态 |

> **🔴 架构安全红线（防提前剧透与终点引力）**：
> 世界书每个故事章节的触发词为严格的 `['第N章']`。**绝对禁止在 Prompt、状态栏或变量中输出任何形式的“下一章节（第N+1章）”字样**！否则酒馆上下文扫描器会瞬间命中下一章的关键词，导致大模型在游玩当前章节的中途就被提前注入下一章大纲，彻底引发剧透与跳章幻觉！上下文中有且仅允许出现当前章节号！
> 
> **注**：在 LLM 的增量汇报块（`json:mvu`）中，额外包含一个瞬时汇报字段 **`request_next_chapter`**（`bool`，仅在沙盒章节中玩家要求离开/切章时填 `true`，用于打破沙盒死锁）。

---

## 四、 状态机流转力学与反哺闭环（State Machine Mechanics）

### 4.1 状态流转图
```mermaid
stateDiagram-v2
    [*] --> 章节判定
    
    state 章节判定 <<choice>>
    章节判定 --> 固有沙盒漫游: is_sandbox_chapter == true
    章节判定 --> 常规大纲推进: is_sandbox_chapter == false
    
    state 固有沙盒漫游 {
        沙盒交互: 自由探索中 (step=0, 无自动冷却)
        切章请求: 玩家输入"离开/前往下一站/下一章"<br/>request_next_chapter = true
        沙盒交互 --> 切章请求
    }
    
    state 常规大纲推进 {
        新章节就绪 --> 主线推进中: 玩家输入"继续"<br/>AI展开第1条 (step=1)
        主线推进中 --> 主线推进中: step < max_step<br/>继续推进 (step += 1)
        
        主线推进中 --> 章节内分支偏离: 玩家偏离大纲<br/>is_free_explore = true (step冻结)
        章节内分支偏离 --> 主线推进中: 玩家输入"继续"<br/>is_free_explore = false (恢复 step += 1)
        
        主线推进中 --> 余韵沉淀冷却: step == max_step<br/>全部大纲展开完毕 (in_afterglow = true)
        
        余韵沉淀冷却 --> 物理切章: 冷却中玩家再次输入"继续/下一章"
    }
    
    切章请求 --> 物理切章
    余韵沉淀冷却 --> 物理切章
    
    state 物理切章 {
        chapter自增: chapter = chapter + 1
        步进初始化: step = 0, max_step = 0 (绝对归零)
        状态重置: in_afterglow = false, is_free_explore = false, is_sandbox_chapter = false
        物理宏反哺: {{getvar::chapter}} 自动展开为新章节号
        世界书激活: 仅命中新一章"第N章"词条，杜绝跨章干扰
    }
    
    物理切章 --> 章节判定
```

### 4.2 核心流转规则定义：
1. **固有沙盒章节与安全切出（Sandbox Exemption & Exit Channel）**：
   * 若 `is_sandbox_chapter == true`，状态机**完全禁用大纲单步推进与自动余韵沉淀**；
   * 漫游期间 `step = 0, max_step = 0, in_afterglow = false`；
   * **安全切出机制**：当玩家在沙盒中达成目标或输入明确切章意向（如“前往下一区域”、“开启下一章”）时，LLM 汇报 `request_next_chapter = true`，状态机直接触发物理切章，解除沙盒锁定并流转至下一章。
2. **常规单步推进（Step Advance）**：
   * 玩家输入“继续”，AI 展开下一条大纲；
   * 条件：`is_sandbox_chapter == false` 且 `step < max_step` 且 `is_free_explore == false`；
   * 动作：`step` 同步递增。
3. **章节内分支冻结（Free Exploration Freeze）**：
   * 玩家进行自主交流、私会、探索等偏离剧本行为；
   * 条件：常规章节中，AI 判定玩家意图偏离；
   * 动作：`is_free_explore = true`，**`step` 严格冻结保持上一轮数值**，绝不推进。
4. **两轮余韵冷却闭环（Afterglow & Cooldown Cycle）**：
   * **第 1 轮（触顶沉淀）**：当 `step == max_step` 时，AI 展开最后一条物象收束，输出 `in_afterglow = true`。系统进入余韵沉淀，**当前章节号严格保持不变**；
   * **第 2 轮（物理切章）**：上一轮已处于 `in_afterglow == true`，玩家再次回复“继续”或“下一章”，**TavernHelper 触发硬切章**：
     * `chapter = chapter + 1`；
     * `step = 0, max_step = 0`（新章节物理开启，大纲进度绝对归零，彻底杜绝跨章继承脏数据）；
     * `in_afterglow = false`；
     * `is_free_explore = false`。
5. **物理宏反哺链路（Macro Prompt Feedback）**：
   * 切章后变量 `chapter` 更新为新值；
   * 下一轮酒馆组装提示词时，状态栏中的 `第{{getvar::chapter}}章` 自动展开为实际文本（如 `第60章`）；
   * 酒馆世界书引擎扫描上下文，精准命中第 60 章的触发关键词 `第60章`，将新章节大纲注入 Prompt；
   * 上下文中**绝不包含下一章编号**，大模型视野内有且仅有当前章大纲，彻底杜绝提前看到下一章的剧透与终点引力！

---

## 五、 世界书系统机制调整（双轨兼容规范）

### 5.1 修改文件：`docs/chapter/_游戏状态界面.TXT`
必须将该文件的输出指导、示例与校验点升级为**支持宏反哺与 MVU 增量汇报的双轨规范**。以下为该文件的**完整权威修改内容**（实施时可直接全量覆盖）：

```text
ID: UI01
名称: 游戏状态界面
触发关键词:
始终触发: 是
注入深度: 0
内容:
  - ### LLM 输出指导
  - **请在正文后严格按以下格式生成内容，禁止额外说明或修改标签结构：**
  - <overall>
  - <chapter_information>
  - 当前章节|<格式如：第{{getvar::chapter}}章 章节名称>
  - 大纲情境进度|<第X条，若探索则为"第X条（自由探索中）"，若冷却则为"第X条（余韵沉淀）"，若沙盒章节则为"自由探索章节">
  - 阶段|<x：阶段名>
  - 在场人物|<逗号分隔的人物列表>
  - </chapter_information>
  - ```json:mvu
  - {
  -   "chapter": {{getvar::chapter}},
  -   "step": <本轮刚展开完毕的情境数字编号，沙盒章节填0>,
  -   "max_step": <本章总情境数纯数字，沙盒章节填0>,
  -   "is_sandbox_chapter": <若为固有自由探索章节填true，否则false>,
  -   "is_free_explore": <常规章节中若偏离主线填true，否则false>,
  -   "in_afterglow": <常规章节若全部情境完成进入冷却填true，否则false>,
  -   "request_next_chapter": <若处于沙盒章节且玩家要求离开/进入下一章时填true，否则false>
  - }
  - ```
  - <StatusBlock>
  - ```
  - 🕣<圣光纪年xxxx年 x月x日（周x）xx时xx分> | 🌏<地点> | ☁️<天气>
  - # <角色名> 年龄: <xx岁>
  - ╒═════
  - 💖对黎恩的好感度: <0-100数值，如：85；若为男性同伴则写作 🤝对黎恩的信赖度: 75>
  - 📅当前章节: <格式如：第{{getvar::chapter}}章 章节名称>
  - 👚 服装:
  - 💭 情绪:
  - 💑 行为:
  - 🤔 对黎恩的想法:
  - 🙀 Tips:
  - ╘═════
  - ```
  - </StatusBlock>
  - <WorldState>
  - 📡 镜头外动态|<200字以上文段>
  - </WorldState>
  - </overall>
  - ### 字段说明与规则
  - 1. **`<chapter_information>`**
  -    - **当前章节**：格式为 `第X章 章节名称`。必须如实反映当前实际章节编号（由提示词中注入的章节号确定），严禁手工伪造或跳号。
  -    - **严禁输出下一章节**：彻底废除原有的“下一章节”字段！上下文中有且仅允许包含当前正在进行的章节编号，严禁在状态栏中输出任何“第N+1章”文本，物理切断下一章世界书大纲被提前激活的剧透途径。
  -    - **大纲情境进度**：严格按 `第X条` 格式。X为当前回复正文刚展开完毕的情境编号。
  -        * **章节内自由探索/支线**：若玩家中途偏离剧本，进度必须冻结保留上一轮数字：`第X条（自由探索中）`，严禁改写为“自由探索章节”。
  -        * **余韵沉淀与冷却**：章节全部情境完成后（X达到章节总情境数），进入冷却时输出 `第X条（余韵沉淀）`。
  -        * **固有自由探索章节**：仅当章节原TXT元数据显式声明 `[总情境数]: 自由探索章节` 时，才直接输出 `自由探索章节`。
  - 2. **`json:mvu` 增量状态块**
  -    - 伴随 `<chapter_information>` 同步输出，严格按 JSON 规范填入增量字段，用于前端状态机数学计算与物理切章。
  - 3. **`<StatusBlock>` 与 `<WorldState>`**
  -    - **好感度/信赖度**：依据各角色好感度设定与当前剧情阶段如实评估输出（0-100数值，女性角色用 `💖对黎恩的好感度`，男性角色用 `🤝对黎恩的信赖度`）。严禁输出 `{love_point}` 等未解析占位符！
  -    - **活跃角色判定与上限**：最多包含 2 个当前回复中有实质性互动（对话、主动行为、心理/情感反应描写）的角色状态卡（Seraphina首位→女性好感降序→男性信赖降序）。仅在场但无互动的背景角色只在`在场人物`列出；镜头外角色统一记入`<WorldState>`。
  - ---
  - ### 合规示例 
  - <overall>
  - <chapter_information>
  - 当前章节|第59章 篝火故事——精灵王国的碎片
  - 大纲情境进度|第1条
  - 阶段|0：序章
  - 在场人物|黎恩,Seraphina,劳拉,亚莉莎,艾玛,菲,艾德里安,玲
  - </chapter_information>
  - ```json:mvu
  - {
  -   "chapter": 59,
  -   "step": 1,
  -   "max_step": 3,
  -   "is_sandbox_chapter": false,
  -   "is_free_explore": false,
  -   "in_afterglow": false,
  -   "request_next_chapter": false
  - }
  - ```
  - <StatusBlock>
  - ```
  - 🕣圣光纪年3472年 8月12日（周五）20时15分 | 🌏林间空地·营地篝火 | ☁️晴朗星夜
  - # Seraphina 年龄: 320岁
  - ╒═════
  - 💖对黎恩的好感度: 25
  - 📅当前章节: 第59章 篝火故事——精灵王国的碎片
  - 👚 服装: 月白色丝质长袍外罩银色轻纱，长发散落肩头
  - 💭 情绪: 讲述中逐渐放松，眼角有极淡的笑意
  - 💑 行为: 坐在黎恩身旁讲述八岁时在银流河放花节的记忆，手指在膝盖上无意识地画圈
  - 🤔 对黎恩的想法: 他在听——真的在听。这是第一次有人类听我说这些
  - 🙀 Tips: 320年来第一次主动向他人分享童年回忆
  - ╘═════
  - ```
  - </StatusBlock>
  - <WorldState>
  - 📡 镜头外动态|营地乔治工坊背阴处的储料隔间内，空气中弥漫着导力机油与松木的混合气味。多尔金粗糙粗壮的大手一把扣住艾玛柔软丰满的腰臀，将身材高挑的魔女压在码放整齐的零件箱前。硬如生铁的粗长肉棒隔着单薄法袍重重抵在湿热的腿心用力研磨，激得艾玛浑身酸软轻颤。
  - </WorldState>
  - </overall>
  - ---
  - ### 强制校验点
  - 1. XML标签与 ```json:mvu 代码块完整且闭合
  - 2. `当前章节` 必须按 `第X章 章节名称` 如实输出当前正在进行的章节，严禁输出“下一章节”字段
  - 3. `大纲情境进度` 严格遵循断点规则与冻结规范
  - > 请按此模板生成内容，任何偏差将导致系统解析失败。
```

---

### 5.2 同步瘦身文件：`docs/chapter/_章节追踪指令.TXT`
既然切章、步进与防跳章已 100% 收归前端代码在物理层强制卡死，大模型的大脑无需再承担任何“裁判”内耗，原指令中长达 20 余行的大段防跳章紧箍咒（如 `X < N 绝对防跳章锁死`、`当 X < N 严禁进入下一章`、`进入下一章条件`）全部彻底切除！

将 `docs/chapter/_章节追踪指令.TXT` 中的 **第 3 节（第 55~76 行）** 整体替换为以下极简、纯粹的 3 条正向规则：

```text
**3. 大纲情境推进与正文落地**

*   **单步深度展开**: 每次玩家回复"继续"时，AI 只需顺延展开当前大纲中的 1 条情境。将单次回复的篇幅聚焦于景色氛围、内心波澜、身体微反应与微动作，好茶慢慢品，严禁急躁推进流水账。判断进度只由正文决定，`<WorldState>` 镜头外动态属暗线不影响进度。
*   **自由探索遵从玩家**: 玩家中途偏离大纲进行自主互动时，大纲剧本立即暂置，完全跟随玩家展开；当前章节名保持不变，进度必须冻结输出 `大纲情境进度|第X条（自由探索中）`，严格保留上一轮断点 X。当收到“继续”指令时，强制从断点第 X+1 条恢复推进。
*   **如实汇报进度**: 每次回复末尾，AI 仅需根据本轮正文实际展开的情境编号，如实输出 `<chapter_information>` 中的 `大纲情境进度|第X条`，并在 `json:mvu` 状态块中同步输出 `step: X`。当推进至本章最后一条收束情境时，输出 `第X条（余韵沉淀）` 并置 `in_afterglow: true`。
```

> **彻底剥离的冗余垃圾**：
> ❌ 剔除所有“X < N 严禁跳章”、“防跳章锁死”等大段负向恐吓（避免激起注意力逆向诱导）；
> ❌ 剔除所有“章节完成判定”、“进入下一章指令”与切章裁判解释（大模型无需操心切章，全由代码在幕后静默完成）。



---

## 六、 TavernHelper 前端自动化处理脚本（完整生产级代码）

在 SillyTavern 的 **TavernHelper ➔ Scripts** 中添加以下专属处理逻辑（命名为 `Eldoria_StateMachine_v1.2` 并启用）：

```javascript
// ====================================================================
// Eldoria 状态机引擎 v1.3.0 (静默纯净版+步进绝对归零+防重触发+母条目引信驱动)
// 特性：双自由探索分治、沙盒死锁拦截、容错JSON清洗、Swipe安全定位、
//       切章步进绝对归零、防重复触发节流、4大脚本按钮（状态查询/加载变量/进入下一章/初始化变量）
// ====================================================================

/**
 * 鲁棒性 JSON 清洗与宽松解析器 (容忍尾随逗号、注释、Python风格大小写)
 */
function safeParseMVU(rawJsonStr) {
    if (!rawJsonStr) return null;
    try {
        let clean = rawJsonStr.trim()
            .replace(/\/\/.*$/gm, '')                 // 去除单行注释
            .replace(/\/\*[\s\S]*?\*\//g, '')        // 去除块级注释
            .replace(/,\s*([}\]])/g, '$1')           // 修复尾随逗号
            .replace(/:\s*True\b/g, ': true')        // Python True 修复
            .replace(/:\s*False\b/g, ': false')      // Python False 修复
            .replace(/:\s*None\b/g, ': null')        // Python None 修复
            .replace(/'([^']+)'/g, '"$1"');          // 单引号转双引号
        return JSON.parse(clean);
    } catch (e) {
        console.warn('[Eldoria-MVU] 严格JSON解析失败，启动正则提取兜底:', e);
        const extractInt = (key) => {
            const m = rawJsonStr.match(new RegExp(`"${key}"\\s*:\\s*(\\d+)`));
            return m ? parseInt(m[1], 10) : undefined;
        };
        const extractBool = (key) => {
            const m = rawJsonStr.match(new RegExp(`"${key}"\\s*:\\s*(true|false)`, 'i'));
            return m ? (m[1].toLowerCase() === 'true') : undefined;
        };
        const fallback = {
            chapter: extractInt('chapter'),
            step: extractInt('step'),
            max_step: extractInt('max_step'),
            is_sandbox_chapter: extractBool('is_sandbox_chapter'),
            is_free_explore: extractBool('is_free_explore'),
            in_afterglow: extractBool('in_afterglow'),
            request_next_chapter: extractBool('request_next_chapter')
        };
        if (fallback.chapter !== undefined) return fallback;
        return null;
    }
}

// --------------------------------------------------------------------
// 0. 酒馆助手变量读写适配层 (全版本兼容：getVariables / insertOrAssignVariables)
// --------------------------------------------------------------------
function getEldoriaVars() {
    try {
        if (typeof getVariables === 'function') return getVariables() || {};
        if (typeof TavernHelper !== 'undefined' && typeof TavernHelper.getVariables === 'function') {
            return TavernHelper.getVariables() || {};
        }
    } catch (e) {
        console.warn('[Eldoria] getVariables 失败:', e);
    }
    return {};
}

async function updateEldoriaVars(newVars) {
    try {
        if (typeof insertOrAssignVariables === 'function') {
            return await insertOrAssignVariables(newVars);
        }
        if (typeof TavernHelper !== 'undefined' && typeof TavernHelper.insertOrAssignVariables === 'function') {
            return await TavernHelper.insertOrAssignVariables(newVars);
        }
        if (typeof replaceVariables === 'function') {
            const current = getEldoriaVars();
            return await replaceVariables({ ...current, ...newVars });
        }
        if (typeof TavernHelper !== 'undefined' && typeof TavernHelper.replaceVariables === 'function') {
            const current = getEldoriaVars();
            return await TavernHelper.replaceVariables({ ...current, ...newVars });
        }
        console.error('[Eldoria] 未找到变量写入接口');
    } catch (e) {
        console.error('[Eldoria] 写入变量失败:', e);
        throw e;
    }
}


// --------------------------------------------------------------------
// 1. 按钮点击事件监听 (配合 TavernHelper getButtonEvent 使用)
// --------------------------------------------------------------------

if (typeof getButtonEvent === 'function' && typeof eventOn === 'function') {
    // 🔘 按钮一：【状态查询】（弹出 Toastr 卡片查看当前进度）
    eventOn(getButtonEvent('状态查询'), async () => {
        try {
            const vars = getEldoriaVars();
            const c = vars.chapter || 1;
            const s = vars.step || 0;
            const ms = vars.max_step || 0;
            const fe = vars.is_free_explore ? '🍃 自由探索/私会' : '⚔️ 主线大纲';
            const ag = vars.in_afterglow ? '⏳ 余韵沉淀中' : '进行中';
            const sb = vars.is_sandbox_chapter ? '🗺️ 固有沙盒漫游' : '常规章节';

            toastr.info(
                `【当前章节】：第 ${c} 章<br/>` +
                `【大纲进度】：第 ${s} / ${ms} 条<br/>` +
                `【运行模式】：${fe}<br/>` +
                `【冷却状态】：${ag}<br/>` +
                `【章节属性】：${sb}`,
                'Eldoria 实时状态卡',
                { timeOut: 6000, escapeHtml: false }
            );
        } catch (err) {
            console.error('[Eldoria-Button] 状态查询失败:', err);
        }
    });

    // 🔘 按钮二：【加载变量】（一键扫描近期楼层，自动提取并同步最新 mvu 变量）
    eventOn(getButtonEvent('加载变量'), async () => {
        try {
            const context = (typeof SillyTavern !== 'undefined' && SillyTavern.getContext) 
                ? SillyTavern.getContext() 
                : (typeof getContext === 'function' ? getContext() : null);
            if (!context || !context.chat || context.chat.length === 0) {
                toastr.warning('当前无聊天记录，无法加载变量', 'Eldoria 状态机');
                return;
            }

            let foundData = null;
            let foundMsgIdx = -1;
            // 从最新的消息往回倒序扫描，找到最近一条包含有效 mvu 块的 AI 消息
            for (let i = context.chat.length - 1; i >= 0; i--) {
                const msg = context.chat[i];
                if (!msg || msg.is_user || !msg.mes) continue;
                const mvuMatch = msg.mes.match(/```\s*(?:json)?(?::)?mvu\s*([\s\S]*?)\s*```/i) ||
                                 msg.mes.match(/(?:json)?(?::)?mvu\s*(\{[\s\S]*?\})/i);
                if (mvuMatch) {
                    const parsed = safeParseMVU(mvuMatch[1]);
                    if (parsed && parsed.chapter !== undefined) {
                        foundData = parsed;
                        foundMsgIdx = i;
                        break;
                    }
                }
            }

            if (!foundData) {
                toastr.warning('未在近期消息中找到有效的 mvu 状态块！', 'Eldoria 状态机');
                return;
            }

            const parsedChapter = parseInt(foundData.chapter, 10);
            const parsedStep = parseInt(foundData.step, 10);
            const parsedMax = parseInt(foundData.max_step, 10);

            const newVars = {
                chapter: isNaN(parsedChapter) ? 1 : parsedChapter,
                step: isNaN(parsedStep) ? 0 : parsedStep,
                max_step: isNaN(parsedMax) ? 0 : parsedMax,
                is_sandbox_chapter: !!foundData.is_sandbox_chapter,
                is_free_explore: !!foundData.is_free_explore,
                in_afterglow: !!foundData.in_afterglow
            };

            await updateEldoriaVars(newVars);

            toastr.success(
                `成功从第 ${foundMsgIdx + 1} 楼恢复变量！<br/>` +
                `【当前章节】：第 ${newVars.chapter} 章<br/>` +
                `【大纲进度】：第 ${newVars.step} / ${newVars.max_step} 条<br/>` +
                `【运行模式】：${newVars.is_free_explore ? '🍃 自由探索' : '⚔️ 主线大纲'}<br/>` +
                `【冷却状态】：${newVars.in_afterglow ? '⏳ 余韵沉淀中' : '进行中'}`,
                'Eldoria 状态机',
                { timeOut: 6000, escapeHtml: false }
            );
            console.log(`[Eldoria-Button] >>> 成功从第 ${foundMsgIdx + 1} 楼加载变量:`, newVars);
        } catch (err) {
            console.error('[Eldoria-Button] 加载变量失败:', err);
            toastr.error('加载变量失败: ' + (err.message || err), 'Eldoria 状态机');
        }
    });

    // 🔘 按钮三：【进入下一章】（手动确认物理切章）
    eventOn(getButtonEvent('进入下一章'), async () => {
        try {
            const vars = getEldoriaVars();
            const prevChapter = parseInt(vars.chapter || 1, 10);
            const nextChapter = prevChapter + 1;

            await updateEldoriaVars({
                chapter: nextChapter,
                step: 0,
                max_step: 0,
                is_sandbox_chapter: false,
                is_free_explore: false,
                in_afterglow: false
            });

            toastr.success(`已成功流转至第 ${nextChapter} 章！世界书已切换。`, 'Eldoria 状态机');
            console.log(`[Eldoria-Button] >>> 手动切章成功: 第 ${nextChapter} 章`);
        } catch (err) {
            console.error('[Eldoria-Button] 手动切章失败:', err);
            toastr.error('切章失败: ' + (err.message || err), 'Eldoria 状态机');
        }
    });

    // 🔘 按钮四：【初始化变量】（一键弹窗设定章节，初始化6大核心变量）
    eventOn(getButtonEvent('初始化变量'), async () => {
        try {
            const vars = getEldoriaVars();
            const current = vars.chapter || 59;
            const inputChap = prompt('【Eldoria 变量初始化】\n请输入您当前正游玩的章节物理编号（纯数字）：', current);
            if (inputChap === null) return; // 用户点击取消

            const chapterNum = parseInt(inputChap.trim(), 10);
            if (isNaN(chapterNum) || chapterNum <= 0) {
                toastr.error('输入的章节编号必须是大于0的纯数字！', 'Eldoria 状态机');
                return;
            }

            await updateEldoriaVars({
                chapter: chapterNum,
                step: 0,
                max_step: 0,
                is_sandbox_chapter: false,
                is_free_explore: false,
                in_afterglow: false
            });

            toastr.success(`变量池已成功初始化至第 ${chapterNum} 章！<br/>各状态已归零重置。`, 'Eldoria 状态机', { escapeHtml: false });
            console.log(`[Eldoria-Button] 变量池初始化完成: 第 ${chapterNum} 章`);
        } catch (err) {
            console.error('[Eldoria-Button] 初始化变量失败:', err);
            toastr.error('初始化变量出现异常: ' + (err.message || err), 'Eldoria 状态机');
        }
    });
}

// --------------------------------------------------------------------
// 2. 消息生成监听 (AI 回复渲染完毕后的自动增量解析与状态步进)
// --------------------------------------------------------------------
let lastProcessedFingerprint = '';

async function onEldoriaMessageRendered(messageId) {
    try {
        const context = (typeof SillyTavern !== 'undefined' && SillyTavern.getContext) 
            ? SillyTavern.getContext() 
            : (typeof getContext === 'function' ? getContext() : null);
        if (!context || !context.chat || context.chat.length === 0) return;

        const chat = context.chat;

        // 1. 精确获取目标消息，防止 Swipe 划选重绘时历史串扰
        const msgIdx = (typeof messageId === 'number' && messageId >= 0 && messageId < chat.length) 
            ? messageId 
            : (chat.length - 1);
        const lastMsg = chat[msgIdx];
        if (!lastMsg || lastMsg.is_user) return;

        // 防重触发节流守卫：防止同一条消息因多次重绘事件重复触发状态机导致连跳
        const currentFingerprint = `${msgIdx}_${lastMsg.swipe_id || 0}_${(lastMsg.mes || '').length}`;
        if (currentFingerprint === lastProcessedFingerprint) {
            return;
        }

        // 2. 提取 AI 生成的 json:mvu 块 (宽容匹配：支持 ```json:mvu、```:mvu 与裸标签)
        const mvuMatch = lastMsg.mes && (
            lastMsg.mes.match(/```\s*(?:json)?(?::)?mvu\s*([\s\S]*?)\s*```/i) ||
            lastMsg.mes.match(/(?:json)?(?::)?mvu\s*(\{[\s\S]*?\})/i)
        );
        if (!mvuMatch) return;

        const aiData = safeParseMVU(mvuMatch[1]);
        if (!aiData) {
            console.error('[Eldoria-MVU] 提取变量失败，跳过本轮同步');
            return;
        }

        lastProcessedFingerprint = currentFingerprint;

        // 3. 读取并归一化酒馆现存状态
        const vars = getEldoriaVars();
        let currentChapter = parseInt(vars.chapter || aiData.chapter || 1, 10);
        let wasInAfterglow = (vars.in_afterglow === true || vars.in_afterglow === 'true' || vars.in_afterglow === 1);
        let wasSandbox = (vars.is_sandbox_chapter === true || vars.is_sandbox_chapter === 'true' || vars.is_sandbox_chapter === 1);

        // 4. 【判定 A：固有沙盒章节处理与解脱跳出通道】
        if (aiData.is_sandbox_chapter || wasSandbox) {
            if (aiData.request_next_chapter === true || (!aiData.is_sandbox_chapter && wasSandbox)) {
                currentChapter += 1;
                await updateEldoriaVars({
                    chapter: currentChapter,
                    step: 0,
                    max_step: 0,
                    is_sandbox_chapter: false,
                    is_free_explore: false,
                    in_afterglow: false
                });
                
                toastr.success(`离开自由探索区域，正式进入第 ${currentChapter} 章！`, 'Eldoria 状态机');
                console.log(`[Eldoria-MVU] >>> 沙盒漫游结束，物理晋升至第 ${currentChapter} 章`);
                return;
            }

            await updateEldoriaVars({
                chapter: currentChapter,
                step: 0,
                max_step: 0,
                is_sandbox_chapter: true,
                is_free_explore: false,
                in_afterglow: false
            });
            console.log(`[Eldoria-MVU] 当前处于固有沙盒章节（第${currentChapter}章），保持漫游。`);
            return;
        }

        // 5. 【判定 B：常规章节余韵冷却后物理切章闭环】
        if (wasInAfterglow && !aiData.is_free_explore) {
            const prevChapter = currentChapter;
            currentChapter += 1;
            
            // 铁律：新章节物理开启时，大纲进度必须绝对归零(0/0)！严禁跨章继承旧章节的 step
            await updateEldoriaVars({
                chapter: currentChapter,
                step: 0,
                max_step: 0,
                is_sandbox_chapter: false,
                in_afterglow: false,
                is_free_explore: false
            });
            
            toastr.success(`本章圆满完结！已自动流转至第 ${currentChapter} 章`, 'Eldoria 状态机');
            console.log(`[Eldoria-MVU] >>> 章节物理晋级: 第 ${currentChapter} 章 | 大纲进度绝对归零: 0/0`);
            return;
        }

        // 6. 【判定 C：常规大纲单步推进或章节内分支偏离】
        const parsedStep = parseInt(aiData.step, 10);
        const parsedMax = parseInt(aiData.max_step, 10);

        await updateEldoriaVars({
            chapter: currentChapter,
            step: isNaN(parsedStep) ? 0 : parsedStep,
            max_step: isNaN(parsedMax) ? 0 : parsedMax,
            is_sandbox_chapter: false,
            is_free_explore: !!aiData.is_free_explore,
            in_afterglow: !!aiData.in_afterglow
        });

        console.log(`[Eldoria-MVU] 状态同步: 第${currentChapter}章 | 进度:${aiData.step}/${aiData.max_step} | 探索:${aiData.is_free_explore} | 冷却:${aiData.in_afterglow}`);

    } catch (err) {
        console.error('[Eldoria-MVU] 运行出错:', err);
    }
}

// 绑定消息渲染监听 (多环境自适应)
const msgRenderedEvent = (typeof tavern_events !== 'undefined' && tavern_events.CHARACTER_MESSAGE_RENDERED)
    ? tavern_events.CHARACTER_MESSAGE_RENDERED
    : (typeof event_types !== 'undefined' ? event_types.CHARACTER_MESSAGE_RENDERED : 'character_message_rendered');

if (typeof eventOn === 'function') {
    eventOn(msgRenderedEvent, onEldoriaMessageRendered);
} else if (typeof eventSource !== 'undefined' && eventSource.on) {
    eventSource.on(msgRenderedEvent, onEldoriaMessageRendered);
}
```

---

## 七、 气泡代码无痕隐藏配置（酒馆内置 Regex 规则）

为了防止 ````json:mvu ... ```` 机器代码干扰聊天视觉体验，在 SillyTavern 的 **正则表达式扩展（Regex Scripts）** 中添加 1 条加固替换规则：

* **规则名称**：`Eldoria_MVU_Stripper`
* **查找正则表达式 (Find Regex)**：
  ```regex
  /(?:\r?\n)?(?:```\s*(?:json)?(?::)?mvu[\s\S]*?```|(?::mvu|json:mvu)\s*\{[\s\S]*?\})(?:\r?\n)?/gi
  ```
  *(注：如果是在酒馆界面手动填写，请在 Find Regex 输入框填入上述带 `/.../gi` 的完整形式，或者直接在酒馆 Regex 页面点击右上角导入 `output/regex-eldoria_mvu_stripper.json`)*
* **替换为 (Replace With)**：*(完全留空)*
* **应用位置 (Placement)**：
  * ✅ 勾选：`AI 输出 (AI Output)`
  * ✅ 勾选：`展示时渲染 (Display Only / only_format_display)`
  * 🔴 **绝对严禁勾选**：`修改原始文本 (Modify Raw / Affect Save)`（若勾选会导致前端渲染前消息被破坏，JS 脚本无法提取变量！）

> **效果**：大模型生成完毕后，TavernHelper 脚本精准提取变量数据，随后该代码块在界面上被无痕隐形，正文排版紧凑纯净，绝无留白残缺。

---

## 八、 工业级实施操作流水线（SOP 与自检清单）

本方案设计为**零停机、无损平滑升级**。请按以下 4 步标准作业程序推进实施：

### 8.1 实施前基线备份（安全底线）
在终端中执行 Git 状态确认，确保随时可秒级撤销：
```bash
# 确认当前工作区干净并记录锚点
git status
```

### 8.2 步骤一：更新系统世界书源文件并重建
1. 将第五节 5.1 提供的完整文本全量覆盖写入本地文件：
   `docs/chapter/_游戏状态界面.TXT`
2. 将第五节 5.2 提供的瘦身文本替换写入本地文件对应章节：
   `docs/chapter/_章节追踪指令.TXT`（第 3 节）
3. 在项目根目录下运行世界书自动构建脚本：
   ```bash
   python scripts/build_eldoria.py
   ```
   *检查终端输出：确认看到 `[step 4] 验证通过` 与 `构建完成! 主文件: output/Eldoria_V10.31.0.json`*。

### 8.3 步骤二：在酒馆中重新导入世界书
1. 打开 SillyTavern，进入 **世界书（World Info）** 面板；
2. 找到当前绑定的 `Eldoria` 世界书，点击导入或直接覆盖导入刚才生成的 `output/Eldoria_V10.31.0.json`。

### 8.4 步骤三：挂载 TavernHelper 状态机脚本与 Regex 隐藏
1. **挂载脚本**：
   * 在酒馆右上角扩展菜单中打开 **TavernHelper ➔ Scripts**；
   * 点击 `+ 新建脚本`，命名为 `Eldoria_StateMachine_v1.2`；
   * 将本文档**第六节的完整 JavaScript 代码**全选粘贴进去，勾选 `启用 (Enable)` 并保存。
2. **挂载正则**：
   * 打开 SillyTavern 的 **Regex（正则表达式）** 扩展；
   * 新建规则 `Eldoria_MVU_Stripper`；
   * 查找正则：`\r?\n?```json:mvu[\s\S]*?```\r?\n?`；替换内容：*(完全留空)*；
   * 勾选：`AI 输出 (AI Output)` 和 `展示时渲染 (Display Only)`；
   * 🔴 **核对红线：绝对不得勾选“修改原始聊天记录”**。

### 8.5 步骤四：在当前会话中初始化变量池
在当前角色聊天输入框中，直接发送以下斜杠命令（请将 `59` 替换为你当前正在游玩的实际章节编号）：
```text
/setvar chapter 59 | /setvar step 1 | /setvar max_step 3 | /setvar is_sandbox_chapter false | /setvar is_free_explore false | /setvar in_afterglow false
```
*提示：发送后可在酒馆控制台或变量查看器中输入 `/getvar chapter` 确认返回值是否为当前章节。*

---

### 8.6 上线前 5 分钟 Pre-flight 自检清单（全部勾选方可正式游玩）

* [ ] `docs/story/*/*.TXT` 目录下的 923 个源文件完全未被触碰（零侵入保证）；
* [ ] `docs/chapter/_游戏状态界面.TXT` 内的当前章节行已确认为 `当前章节|第{{getvar::chapter}}章`；
* [ ] 运行 `python scripts/build_eldoria.py` 终端成功通过 13 字段格式校验；
* [ ] TavernHelper 脚本已成功开启且控制台无语法报错；
* [ ] Regex 隐藏规则已就绪，测试生成一条回复时聊天气泡内**看不见**机器代码块，且 F12 控制台输出了 `[Eldoria-MVU] 状态同步成功` 日志。

---

### 8.7 紧急故障回滚预案（Rollback Runbook）
若在游玩中遇到任何不可预期的问题，只需两步即可 10 秒无损回滚到旧版状态：
1. **酒馆端**：在 TavernHelper ➔ Scripts 中一键关闭 `Eldoria_StateMachine_v1.2` 脚本；
2. **世界书端**：恢复 `docs/chapter/_游戏状态界面.TXT` 为 Git 历史版本并重新执行 `python scripts/build_eldoria.py`：
   ```bash
   git checkout docs/chapter/_游戏状态界面.TXT
   python scripts/build_eldoria.py
   ```

---

## 九、 全场景验收测试矩阵

| 测试场景 | 玩家行为 | AI 输出预期 (`json:mvu`) | TavernHelper 状态机动作 |
| :--- | :--- | :--- | :--- |
| **常规单步推进** | 输入“继续” | `step: 2, is_free_explore: false` | `step` 变为 2，`chapter` 稳定保持 59 |
| **章节内偏离分支** | 输入“去河边抓鱼” | `is_free_explore: true` | `step` 冻结在 2，记录进入分支探索 |
| **分支回归主线** | 输入“继续主线” | `step: 3, is_free_explore: false` | `is_free_explore` 解除，从第 3 条恢复推进 |
| **大纲达峰沉淀** | 推至最后一条 | `step: max_step, in_afterglow: true` | `in_afterglow` 触发，锁死本章进入余韵冷却 |
| **冷却完毕晋级** | 冷却中输入“继续” | `is_free_explore: false` | **`chapter` 自动 +1 (变60)，`step` 智能归零/初始化！** |
| **固有沙盒漫游** | 处于118个沙盒章之一 | `is_sandbox_chapter: true` | 禁用自动切章与冷却，保持沙盒自由交互 |
| **沙盒明确切出** | 沙盒中输入“前往下一个城镇” | `request_next_chapter: true` | **立即切出沙盒，`chapter` 自动 +1 晋级新章！** |
| **模型格式微残缺** | 输出附带注释或 Python 大写 `True` | 包含 `//` 或 `True` | **容错解析器自动清洗，正常更新无报红** |
