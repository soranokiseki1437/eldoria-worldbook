# Eldoria 自由探索持久开关与状态锚点改造方案 (v1.4.0)

> **文档版本**：v1.4.0 · 2026-10-05  
> **适用环境**：SillyTavern + TavernHelper 扩展  
> **核心机制**：前端双态持久开关按钮控制 `is_free_explore`；通过《章节引信与状态锚点》宏直接注入运行状态；《游戏状态界面》保持原貌；《章节追踪指令》由用户自行调整适配。

---

## 一、 系统架构设计

```mermaid
graph TD
    A[玩家点击【自由探索】按钮] -->|状态取反 & 持久存盘| B[酒馆变量: is_free_explore = true]
    B -->|DOM 样式驱动| C[按钮高亮发光: 🍃 自由探索开启]
    B -->|宏展开直通| D[章节引信与状态锚点: 注入 is_free_explore]
    D -->|接收模式状态| E[大模型 LLM (按用户追踪指令行动)]
    E -->|自由探索交互| F[输出正文 & step冻结]
    F -->|状态机消息监听| G{is_free_explore 状态判定}
    G -->|锁定开启| H[强制保持 is_free_explore=true, step 坚决不自增]
    G -->|再次点击关闭| I[恢复 is_free_explore=false, 恢复主线步进]
```

* **双态开关持久性**：按钮状态与聊天会话变量 `is_free_explore` 双向绑定。开启后变量持久保持 `true`，大纲情境编号 `step` 冻结，界面按钮常态高亮发光；再次点击切换为 `false`，取消高亮并恢复主线。
* **防冲刷机制**：状态机消息监听层加入硬锁保护，在开关处于开启状态时，忽略大模型汇报的格式波动，避免变量被意外覆盖。
* **状态锚点直通**：直接在 `docs/chapter/_章节引信与状态锚点.TXT` 的 `<chapter_anchor>` 中加入 `{{getvar::is_free_explore}}` 宏，大模型在上下文顶部即可直接读取当前模式状态。
* **范围边界**：
  * `docs/chapter/_游戏状态界面.TXT` **完全不修改**，保持原有格式与字段不变。
  * `docs/chapter/_章节追踪指令.TXT` **由用户自行编辑优化**，方案内不预设改动。

---

## 二、 TavernHelper 脚本规格（Eldoria_StateMachine_v1.4.0）

### 2.1 按钮配置声明
在脚本配置中增加第 5 个按钮 `自由探索`：

```json
{
  "type": "script",
  "enabled": true,
  "name": "Eldoria_StateMachine_v1.4.0",
  "button": {
    "enabled": true,
    "buttons": [
      { "name": "自由探索", "visible": true },
      { "name": "状态查询", "visible": true },
      { "name": "加载变量", "visible": true },
      { "name": "进入下一章", "visible": true },
      { "name": "初始化变量", "visible": true }
    ]
  },
  "data": {
    "chapter": 59,
    "step": 0,
    "max_step": 0,
    "is_sandbox_chapter": false,
    "is_free_explore": false,
    "in_afterglow": false
  }
}
```

---

### 2.2 脚本核心完整代码

```javascript
// ====================================================================
// Eldoria 状态机引擎 v1.4.0 (自由探索双态持久开关版)
// ====================================================================

/**
 * 鲁棒性 JSON 清洗与宽松解析器
 */
function safeParseMVU(rawJsonStr) {
    if (!rawJsonStr) return null;
    try {
        let clean = rawJsonStr.trim()
            .replace(/\/\/.*$/gm, '')
            .replace(/\/\*[\s\S]*?\*\//g, '')
            .replace(/,\s*([}\]])/g, '$1')
            .replace(/:\s*True\b/g, ': true')
            .replace(/:\s*False\b/g, ': false')
            .replace(/:\s*None\b/g, ': null')
            .replace(/'([^']+)'/g, '"$1"');
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
// 0. 变量读写适配层
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

function notifyEldoria(type, message, title = 'Eldoria 状态机') {
    try {
        if (typeof toastr !== 'undefined' && typeof toastr[type] === 'function') {
            toastr[type](message, title, {
                timeOut: 6000,
                escapeHtml: false,
                positionClass: 'toast-top-center'
            });
            return;
        }
    } catch (e) {
        console.warn('[Eldoria-Notify] toastr 调用异常:', e);
    }
    try {
        const plainMsg = message.replace(/<br\s*\/?>/gi, '\n');
        alert(`【${title}】\n${plainMsg}`);
    } catch (_) {}
}

// --------------------------------------------------------------------
// 1. 开关按钮外观渲染器与按钮事件监听
// --------------------------------------------------------------------
function updateExploreButtonUI(isActive) {
    try {
        const buttons = document.querySelectorAll('.tavern_helper_btn, button');
        for (const btn of buttons) {
            const txt = btn.innerText || '';
            if (txt.includes('自由探索') || txt.includes('主线推进') || txt.includes('推进剧情')) {
                if (isActive) {
                    btn.innerHTML = '🍃 自由探索 [开启]';
                    btn.style.setProperty('background', '#2e7d32', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('box-shadow', '0 0 10px rgba(76, 175, 80, 0.85)', 'important');
                    btn.style.setProperty('border', '1px solid #81c784', 'important');
                    btn.title = '当前处于自由探索模式（大纲冻结）。点击切换为主线推进';
                } else {
                    btn.innerHTML = '⚔️ 推进主线 [常态]';
                    btn.style.removeProperty('background');
                    btn.style.removeProperty('color');
                    btn.style.removeProperty('box-shadow');
                    btn.style.removeProperty('border');
                    btn.title = '当前处于主线推进模式。点击切换为自由探索模式';
                }
            }
        }
    } catch (e) {
        console.warn('[Eldoria-Toggle] 更新按钮外观失败:', e);
    }
}

if (typeof getButtonEvent === 'function' && typeof eventOn === 'function') {
    // 🔘 按钮：【自由探索】双态切换
    eventOn(getButtonEvent('自由探索'), async () => {
        try {
            const vars = getEldoriaVars();
            const currentState = (vars.is_free_explore === true || vars.is_free_explore === 'true');
            const nextState = !currentState;

            await updateEldoriaVars({ is_free_explore: nextState });
            updateExploreButtonUI(nextState);

            if (nextState) {
                notifyEldoria('success', '【自由探索模式已锁定开启】<br/>大纲进度保持冻结，完全顺应自由互动。再次点击按钮切回主线。', 'Eldoria 模式切换');
            } else {
                notifyEldoria('info', '【已切回主线推进模式】<br/>大纲锁定已解除，将恢复主线推进。', 'Eldoria 模式切换');
            }
        } catch (err) {
            console.error('[Eldoria-Button] 切换自由探索模式失败:', err);
            notifyEldoria('error', '模式切换异常: ' + (err.message || err));
        }
    });

    // 🔘 按钮：【状态查询】
    eventOn(getButtonEvent('状态查询'), async () => {
        try {
            const vars = getEldoriaVars();
            const c = vars.chapter || 1;
            const s = vars.step || 0;
            const ms = vars.max_step || 0;
            const fe = (vars.is_free_explore === true || vars.is_free_explore === 'true') ? '🍃 自由探索 (已锁定)' : '⚔️ 主线大纲推进';
            const sb = vars.is_sandbox_chapter ? '🗺️ 固有沙盒漫游' : '常规章节';

            notifyEldoria(
                'info',
                `【当前章节】：第 ${c} 章<br/>` +
                `【大纲进度】：第 ${s} / ${ms} 条<br/>` +
                `【运行模式】：${fe}<br/>` +
                `【章节属性】：${sb}`,
                'Eldoria 实时状态卡'
            );
        } catch (err) {
            console.error('[Eldoria-Button] 状态查询失败:', err);
        }
    });

    // 🔘 按钮：【加载变量】
    eventOn(getButtonEvent('加载变量'), async () => {
        try {
            const context = (typeof SillyTavern !== 'undefined' && SillyTavern.getContext) 
                ? SillyTavern.getContext() 
                : (typeof getContext === 'function' ? getContext() : null);
            if (!context || !context.chat || context.chat.length === 0) {
                notifyEldoria('warning', '当前无聊天记录，无法加载变量', 'Eldoria 状态机');
                return;
            }

            let foundData = null;
            let foundMsgIdx = -1;
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
                notifyEldoria('warning', '未在近期消息中找到有效的 mvu 状态块！', 'Eldoria 状态机');
                return;
            }

            let parsedChapter = parseInt(foundData.chapter, 10);
            let parsedStep = parseInt(foundData.step, 10);
            let parsedMax = parseInt(foundData.max_step, 10);
            parsedChapter = isNaN(parsedChapter) ? 1 : parsedChapter;
            parsedStep = isNaN(parsedStep) ? 0 : parsedStep;
            parsedMax = isNaN(parsedMax) ? 0 : parsedMax;

            if (!foundData.is_sandbox_chapter && !foundData.is_free_explore && parsedMax > 0 && parsedStep >= parsedMax) {
                parsedChapter += 1;
                parsedStep = 0;
                parsedMax = 0;
            }

            const currentVars = getEldoriaVars();
            const lockedFreeExplore = (currentVars.is_free_explore === true || currentVars.is_free_explore === 'true');

            const newVars = {
                chapter: parsedChapter,
                step: parsedStep,
                max_step: parsedMax,
                is_sandbox_chapter: !!foundData.is_sandbox_chapter,
                is_free_explore: lockedFreeExplore,
                in_afterglow: false
            };

            await updateEldoriaVars(newVars);
            updateExploreButtonUI(newVars.is_free_explore);

            notifyEldoria(
                'success',
                `成功从第 ${foundMsgIdx + 1} 楼恢复变量！<br/>` +
                `【当前章节】：第 ${newVars.chapter} 章<br/>` +
                `【大纲进度】：第 ${newVars.step} / ${newVars.max_step} 条<br/>` +
                `【运行模式】：${newVars.is_free_explore ? '🍃 自由探索' : '⚔️ 主线大纲'}`,
                'Eldoria 状态机'
            );
        } catch (err) {
            console.error('[Eldoria-Button] 加载变量失败:', err);
            notifyEldoria('error', '加载变量失败: ' + (err.message || err));
        }
    });

    // 🔘 按钮：【进入下一章】
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

            updateExploreButtonUI(false);
            notifyEldoria('success', `已成功流转至第 ${nextChapter} 章！大纲进度归零重置。`, 'Eldoria 状态机');
        } catch (err) {
            console.error('[Eldoria-Button] 手动切章失败:', err);
            notifyEldoria('error', '切章失败: ' + (err.message || err));
        }
    });

    // 🔘 按钮：【初始化变量】
    eventOn(getButtonEvent('初始化变量'), async () => {
        try {
            const vars = getEldoriaVars();
            const current = vars.chapter || 59;
            const inputChap = prompt('【Eldoria 变量初始化】\n请输入您当前正游玩的章节物理编号（纯数字）：', current);
            if (inputChap === null) return;

            const chapterNum = parseInt(inputChap.trim(), 10);
            if (isNaN(chapterNum) || chapterNum <= 0) {
                notifyEldoria('error', '输入的章节编号必须是大于0的纯数字！', 'Eldoria 状态机');
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

            updateExploreButtonUI(false);
            notifyEldoria('success', `变量池已成功初始化至第 ${chapterNum} 章！各状态已归零重置。`, 'Eldoria 状态机');
        } catch (err) {
            console.error('[Eldoria-Button] 初始化变量失败:', err);
            notifyEldoria('error', '初始化变量出现异常: ' + (err.message || err));
        }
    });
}

// 会话加载或切换时自动同步按钮样式
const chatLoadedEvent = (typeof tavern_events !== 'undefined' && tavern_events.CHAT_COMPLETED)
    ? tavern_events.CHAT_COMPLETED
    : 'chat_completed';

if (typeof eventOn === 'function') {
    eventOn(chatLoadedEvent, () => {
        setTimeout(() => {
            const vars = getEldoriaVars();
            updateExploreButtonUI(vars.is_free_explore === true || vars.is_free_explore === 'true');
        }, 500);
    });
}

// --------------------------------------------------------------------
// 2. 消息生成监听与状态步进处理
// --------------------------------------------------------------------
let lastProcessedFingerprint = '';

async function onEldoriaMessageRendered(messageId) {
    try {
        const context = (typeof SillyTavern !== 'undefined' && SillyTavern.getContext) 
            ? SillyTavern.getContext() 
            : (typeof getContext === 'function' ? getContext() : null);
        if (!context || !context.chat || context.chat.length === 0) return;

        const chat = context.chat;
        const msgIdx = (typeof messageId === 'number' && messageId >= 0 && messageId < chat.length) 
            ? messageId 
            : (chat.length - 1);
        const lastMsg = chat[msgIdx];
        if (!lastMsg || lastMsg.is_user) return;

        const currentFingerprint = `${msgIdx}_${lastMsg.swipe_id || 0}_${(lastMsg.mes || '').length}`;
        if (currentFingerprint === lastProcessedFingerprint) {
            return;
        }

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

        const vars = getEldoriaVars();
        let currentChapter = parseInt(vars.chapter || aiData.chapter || 1, 10);
        let wasSandbox = (vars.is_sandbox_chapter === true || vars.is_sandbox_chapter === 'true' || vars.is_sandbox_chapter === 1);

        // 按钮锁优先防冲刷逻辑
        const isManuallyLocked = (vars.is_free_explore === true || vars.is_free_explore === 'true');
        const effectiveFreeExplore = isManuallyLocked ? true : !!aiData.is_free_explore;

        // 判定 A：固有沙盒章节处理与跳出
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
                updateExploreButtonUI(false);
                notifyEldoria('success', `离开自由探索区域，正式进入第 ${currentChapter} 章！`, 'Eldoria 状态机');
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
            return;
        }

        // 判定 B：常规章节大纲触顶即时物理切章（自由探索锁定期间禁用自动切章）
        const parsedStep = parseInt(aiData.step, 10);
        const parsedMax = parseInt(aiData.max_step, 10);

        const isChapterCompleted = !effectiveFreeExplore && (
            (!isNaN(parsedMax) && parsedMax > 0 && !isNaN(parsedStep) && parsedStep >= parsedMax) ||
            aiData.in_afterglow === true
        );

        if (isChapterCompleted) {
            const finishedChapter = currentChapter;
            currentChapter += 1;
            
            await updateEldoriaVars({
                chapter: currentChapter,
                step: 0,
                max_step: 0,
                is_sandbox_chapter: false,
                is_free_explore: false,
                in_afterglow: false
            });
            
            updateExploreButtonUI(false);
            notifyEldoria('success', `第 ${finishedChapter} 章圆满完结（进度 ${parsedStep}/${parsedMax}）！已自动流转至第 ${currentChapter} 章`, 'Eldoria 状态机');
            return;
        }

        // 判定 C：大纲单步推进或自由探索步进冻结
        const preservedStep = vars.step !== undefined ? parseInt(vars.step, 10) : 0;
        const finalStep = effectiveFreeExplore ? preservedStep : (isNaN(parsedStep) ? 0 : parsedStep);

        await updateEldoriaVars({
            chapter: currentChapter,
            step: finalStep,
            max_step: isNaN(parsedMax) ? 0 : parsedMax,
            is_sandbox_chapter: false,
            is_free_explore: effectiveFreeExplore,
            in_afterglow: false
        });

        updateExploreButtonUI(effectiveFreeExplore);

    } catch (err) {
        console.error('[Eldoria-MVU] 运行出错:', err);
    }
}

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

## 三、 世界书系统文件更新

### 3.1 `docs/chapter/_章节引信与状态锚点.TXT`

将当前运行的模式变量 `{{getvar::is_free_explore}}` 注入到 `<chapter_anchor>` 块中，使上下文顶部的状态锚点能够同时宣告模式状态：

```text
ID: CH00
名称: 章节引信与状态锚点
触发关键词:
始终触发: 是
注入深度: 0
顺序: 1000
防止进一步递归: 否
内容:
<chapter_anchor>
当前主线剧情锁定章节：第{{getvar::chapter}}章
当前大纲情境步进阶段：第{{getvar::step}}条
当前自由探索模式状态：{{getvar::is_free_explore}}
</chapter_anchor>
```

> **说明**：
> * `docs/chapter/_游戏状态界面.TXT` **完全不作改动**，保持原汁原味。
> * `docs/chapter/_章节追踪指令.TXT` **由用户自行编辑重构**，只需在你的指令中引用 `当前自由探索模式状态` 或 `is_free_explore` 进行分支指导即可。

---

## 四、 实施作业流程

1. **更新状态锚点源文件**：
   * 将第三节规格写入本地 `docs/chapter/_章节引信与状态锚点.TXT`；
2. **构建世界书产物**：
   * 执行 `python scripts/build_eldoria.py`；
   * 确保格式校验通过并更新 `output/Eldoria_V10.31.0.json`。
3. **输出新版脚本产物**：
   * 同步更新 `scripts/eldoria_state_machine.js`；
   * 生成并导出 `output/酒馆助手脚本-Eldoria_StateMachine_v1.4.0.json`。
4. **酒馆配置**：
   * 重新导入世界书 JSON 文件；
   * 在 TavernHelper 扩展中导入 `Eldoria_StateMachine_v1.4.0` 脚本。
