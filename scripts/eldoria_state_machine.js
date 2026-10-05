// ====================================================================
// Eldoria 状态机引擎 v1.4.0 (防历史重放连环切章加固版 + 自由探索持久开关)
// 特性：
// 1. 【进房防重放加固】：严格物理闭锁，历史消息渲染绝不触发状态机，杜绝进房连跳切章
// 2. 【自由探索持久开关】：双态按钮高亮变色、防AI冲刷锁
// 3. 【精准末尾守卫】：严格仅允许当前最新一条有效消息触发切章与步进
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
            is_fina_alone: extractBool('is_fina_alone'),
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

/**
 * 跨端弹窗通知（强制顶部居中 toast-top-center，避免手机底栏与软键盘遮挡）
 */
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
// 1. 开关按钮外观渲染器与按钮事件监听 (配合 TavernHelper getButtonEvent 使用)
// --------------------------------------------------------------------

/**
 * 动态刷新自由探索按钮外观（高亮/发光/文案切换）
 */
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
    // 🔘 按钮一：【自由探索】双态切换开关
    eventOn(getButtonEvent('自由探索'), async () => {
        try {
            const vars = getEldoriaVars();
            const currentState = (vars.is_free_explore === true || vars.is_free_explore === 'true');
            const nextState = !currentState;

            await updateEldoriaVars({ is_free_explore: nextState });
            updateExploreButtonUI(nextState);

            if (nextState) {
                notifyEldoria('success', '【自由探索模式已锁定开启】<br/>只要不再次点击按钮，当前状态将持续保持为 true。<br/>大纲进度已冻结，尽情与同伴交流/探索。', 'Eldoria 模式切换');
            } else {
                notifyEldoria('info', '【已恢复主线推进模式】<br/>大纲锁定已解除，将恢复主线推进。', 'Eldoria 模式切换');
            }
        } catch (err) {
            console.error('[Eldoria-Button] 切换自由探索模式失败:', err);
            notifyEldoria('error', '模式切换异常: ' + (err.message || err));
        }
    });

    // 🔘 按钮二：【状态查询】（弹出 Toastr 卡片查看当前进度）
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

    // 🔘 按钮三：【加载变量】（一键扫描近期楼层，自动提取并同步最新 mvu 变量）
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
            const isFinaAlone = (foundData.is_fina_alone !== undefined)
                ? (foundData.is_fina_alone === true || foundData.is_fina_alone === 'true')
                : (currentVars.is_fina_alone === true || currentVars.is_fina_alone === 'true');

            const newVars = {
                chapter: parsedChapter,
                step: parsedStep,
                max_step: parsedMax,
                is_sandbox_chapter: !!foundData.is_sandbox_chapter,
                is_free_explore: lockedFreeExplore,
                is_fina_alone: isFinaAlone,
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
            console.log(`[Eldoria-Button] >>> 成功从第 ${foundMsgIdx + 1} 楼加载变量:`, newVars);
        } catch (err) {
            console.error('[Eldoria-Button] 加载变量失败:', err);
            notifyEldoria('error', '加载变量失败: ' + (err.message || err), 'Eldoria 状态机');
        }
    });

    // 🔘 按钮四：【进入下一章】（手动确认物理切章）
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
                is_fina_alone: false,
                in_afterglow: false
            });

            updateExploreButtonUI(false);
            notifyEldoria('success', `已成功流转至第 ${nextChapter} 章！世界书已切换。`, 'Eldoria 状态机');
            console.log(`[Eldoria-Button] >>> 手动切章成功: 第 ${nextChapter} 章`);
        } catch (err) {
            console.error('[Eldoria-Button] 手动切章失败:', err);
            notifyEldoria('error', '切章失败: ' + (err.message || err), 'Eldoria 状态机');
        }
    });

    // 🔘 按钮五：【初始化变量】（一键弹窗设定章节，初始化核心变量）
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
                is_fina_alone: false,
                in_afterglow: false
            });

            updateExploreButtonUI(false);
            notifyEldoria('success', `变量池已成功初始化至第 ${chapterNum} 章！<br/>各状态已归零重置。`, 'Eldoria 状态机');
            console.log(`[Eldoria-Button] 变量池初始化完成: 第 ${chapterNum} 章`);
        } catch (err) {
            console.error('[Eldoria-Button] 初始化变量失败:', err);
            notifyEldoria('error', '初始化变量出现异常: ' + (err.message || err), 'Eldoria 状态机');
        }
    });
}


// --------------------------------------------------------------------
// 2. 会话生命周期守护（核心加固：杜绝进房/切会话批量重绘历史楼层时连环切章）
// --------------------------------------------------------------------
let isChatReady = false;
let lastProcessedFingerprint = '';

function markCurrentChatAsReady() {
    try {
        const context = (typeof SillyTavern !== 'undefined' && SillyTavern.getContext) 
            ? SillyTavern.getContext() 
            : (typeof getContext === 'function' ? getContext() : null);
        if (context && context.chat && context.chat.length > 0) {
            const lastMsg = context.chat[context.chat.length - 1];
            if (lastMsg) {
                // 🔴 核心锁：进入房间完毕后，直接将原本就存在的最末楼层登记为“已处理”，绝不允许历史完结楼层再切章！
                lastProcessedFingerprint = `${context.chat.length - 1}_${lastMsg.swipe_id || 0}_${(lastMsg.mes || '').length}`;
            }
        }
        isChatReady = true;
        const vars = getEldoriaVars();
        updateExploreButtonUI(vars.is_free_explore === true || vars.is_free_explore === 'true');
    } catch (e) {
        console.warn('[Eldoria-Lifecycle] markCurrentChatAsReady 异常:', e);
    }
}

// 监听会话完成与切换事件
const chatCompletedEvent = (typeof tavern_events !== 'undefined' && tavern_events.CHAT_COMPLETED)
    ? tavern_events.CHAT_COMPLETED
    : 'chat_completed';

const chatChangedEvent = (typeof tavern_events !== 'undefined' && tavern_events.CHAT_CHANGED)
    ? tavern_events.CHAT_CHANGED
    : 'chat_changed';

if (typeof eventOn === 'function') {
    eventOn(chatCompletedEvent, () => {
        setTimeout(markCurrentChatAsReady, 300);
    });
    eventOn(chatChangedEvent, () => {
        // 切换对话时立即闭锁，拒绝处理历史消息批量重绘
        isChatReady = false;
    });
} else if (typeof eventSource !== 'undefined' && eventSource.on) {
    eventSource.on(chatCompletedEvent, () => {
        setTimeout(markCurrentChatAsReady, 300);
    });
    eventSource.on(chatChangedEvent, () => {
        isChatReady = false;
    });
}

// 兜底定时器：若特定宿主环境未抛出 chatCompletedEvent，进房 1.2 秒后自动就绪
setTimeout(markCurrentChatAsReady, 1200);


// --------------------------------------------------------------------
// 3. 消息生成监听 (AI 回复渲染完毕后的自动增量解析与状态步进)
// --------------------------------------------------------------------
async function onEldoriaMessageRendered(messageId) {
    try {
        // 🔴 铁律防线一：进房加载历史记录期间，全局物理闭锁，严禁触发状态机！
        if (!isChatReady) {
            return;
        }

        const context = (typeof SillyTavern !== 'undefined' && SillyTavern.getContext) 
            ? SillyTavern.getContext() 
            : (typeof getContext === 'function' ? getContext() : null);
        if (!context || !context.chat || context.chat.length === 0) return;

        const chat = context.chat;

        // 🔴 铁律防线二：严格只允许当前会话的“绝对最新一条楼层”触发状态机！任何历史楼层重绘直接无视！
        const msgIdx = (typeof messageId === 'number' && messageId >= 0 && messageId < chat.length) 
            ? messageId 
            : (chat.length - 1);
        if (msgIdx !== chat.length - 1) {
            return;
        }

        const lastMsg = chat[msgIdx];
        if (!lastMsg || lastMsg.is_user) return;

        // 防重触发节流守卫
        const currentFingerprint = `${msgIdx}_${lastMsg.swipe_id || 0}_${(lastMsg.mes || '').length}`;
        if (currentFingerprint === lastProcessedFingerprint) {
            return;
        }

        // 提取 AI 生成的 json:mvu 块
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

        // 读取现存变量
        const vars = getEldoriaVars();
        let currentChapter = parseInt(vars.chapter || aiData.chapter || 1, 10);
        let wasSandbox = (vars.is_sandbox_chapter === true || vars.is_sandbox_chapter === 'true' || vars.is_sandbox_chapter === 1);

        // 按钮锁优先防冲刷逻辑
        const isManuallyLocked = (vars.is_free_explore === true || vars.is_free_explore === 'true');
        const effectiveFreeExplore = isManuallyLocked ? true : !!aiData.is_free_explore;

        const effectiveFinaAlone = (aiData.is_fina_alone !== undefined) 
            ? (aiData.is_fina_alone === true || aiData.is_fina_alone === 'true') 
            : (vars.is_fina_alone === true || vars.is_fina_alone === 'true');

        // 判定 A：固有沙盒章节处理与解脱跳出通道
        if (aiData.is_sandbox_chapter || wasSandbox) {
            if (aiData.request_next_chapter === true || (!aiData.is_sandbox_chapter && wasSandbox)) {
                currentChapter += 1;
                await updateEldoriaVars({
                    chapter: currentChapter,
                    step: 0,
                    max_step: 0,
                    is_sandbox_chapter: false,
                    is_free_explore: false,
                    is_fina_alone: false,
                    in_afterglow: false
                });
                updateExploreButtonUI(false);
                notifyEldoria('success', `离开自由探索区域，正式进入第 ${currentChapter} 章！`, 'Eldoria 状态机');
                console.log(`[Eldoria-MVU] >>> 沙盒漫游结束，物理晋升至第 ${currentChapter} 章`);
                return;
            }

            await updateEldoriaVars({
                chapter: currentChapter,
                step: 0,
                max_step: 0,
                is_sandbox_chapter: true,
                is_free_explore: false,
                is_fina_alone: effectiveFinaAlone,
                in_afterglow: false
            });
            console.log(`[Eldoria-MVU] 当前处于固有沙盒章节（第${currentChapter}章），保持漫游。`);
            return;
        }

        // 判定 B：常规章节大纲推满，立即物理切章（自由探索锁定期间严禁切章）
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
                is_fina_alone: false,
                in_afterglow: false
            });
            
            updateExploreButtonUI(false);
            notifyEldoria('success', `第 ${finishedChapter} 章圆满完结（进度 ${parsedStep}/${parsedMax}）！已自动流转至第 ${currentChapter} 章`, 'Eldoria 状态机');
            console.log(`[Eldoria-MVU] >>> 第 ${finishedChapter} 章大纲触顶(${parsedStep}/${parsedMax})，立即物理晋级: 第 ${currentChapter} 章 | 大纲进度绝对归零: 0/0`);
            return;
        }

        // 判定 C：常规大纲单步推进或自由探索步进冻结
        const preservedStep = vars.step !== undefined ? parseInt(vars.step, 10) : 0;
        const finalStep = effectiveFreeExplore ? preservedStep : (isNaN(parsedStep) ? 0 : parsedStep);

        await updateEldoriaVars({
            chapter: currentChapter,
            step: finalStep,
            max_step: isNaN(parsedMax) ? 0 : parsedMax,
            is_sandbox_chapter: false,
            is_free_explore: effectiveFreeExplore,
            is_fina_alone: effectiveFinaAlone,
            in_afterglow: false
        });

        updateExploreButtonUI(effectiveFreeExplore);
        console.log(`[Eldoria-MVU] 状态同步: 第${currentChapter}章 | 进度:${finalStep}/${parsedMax} | 探索:${effectiveFreeExplore}`);

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
