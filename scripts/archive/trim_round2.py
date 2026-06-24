#!/usr/bin/env python3
"""第二轮修剪：uid 50, 51, 153, 156 进一步精简到~1000"""
import re

BUILD = r"C:\Users\lx\Desktop\世界书\scripts\build_eldoria.py"
with open(BUILD, "r", encoding="utf-8") as f:
    bt = f.read()

TRIMMED = {}

# ── uid 50 (S4 夜袭): 1357 → 1000 ──
TRIMMED[50] = (
    "【NSFW事件——夜袭：黑暗中的访客】\n\n"
    "触发条件：深夜时间段, trust_level >= 50, Seraphina独自在木屋中\n\n"
    "场景：深夜，月光穿过木窗缝隙照在草席上。Seraphina侧躺，粉发散落，穿着黑色吊带短裙。\n"
    "圣光在沉睡中自行流转。木门发出一声吱呀——一个人影推门而入。\n"
    "夜袭者可能是：黎恩（占有欲确认）/ 艾德里安（隐奸）/ 乔治（被动NTR）/ Thalion（腐化）。\n\n"
    "分支A. 黎恩夜袭（纯爱/占有欲确认）：\n"
    "黎恩跪在草席旁。触碰她裸露的肩膀——她的身体认出鬼之力频率，圣光自动包裹住他的手指。\n"
    "从颈侧吻起沿锁骨向下。吊带被拉下，手探入裙摆。进入时她在半梦半醒间低吟他的名字。\n"
    "窗外可能有另一个气息——但此刻她的身体只回应鬼之力。\n"
    "→ trust +10, bond +15, possessiveness_intensity +10\n\n"
    "分支B. 第三者夜袭（隐奸）：\n"
    "第三者在黑暗中靠近。Seraphina睁开眼——琥珀色瞳孔找到来人轮廓。她没有尖叫。\n"
    "手在黑暗中抬起——掌心朝上。第三者俯身吻她的手腕内侧，沿手臂到肩头到锁骨。\n"
    "每一寸被触碰的皮肤圣光都在微微颤抖。进入时她咬住手指压抑声音。\n"
    "木屋外——如果黎恩在附近——能听到一切。\n"
    "→ hidden_affair_experience +25, possessiveness_intensity +35\n\n"
    "分支C. 黎恩发现第三者夜袭（被动NTR/转折）：\n"
    "黎恩推开门——月光照在草席上的两人身上。鬼之力爆发。\n"
    "Seraphina惊醒：脸上闪过恐惧和愧疚。\n"
    "→ 愤怒：trust-20, abandonment_count+10 / 接受并对话：trust+5，开启NTRS线\n\n"
    "变量：黎恩夜袭→trust+10 bond+15 / 第三者→hidden+25 intensity+35 / 发现→取决于反应\n"
    "核心：白天伪装被夜色褪去——身体比语言更诚实。人物反应要点：艾德里安→熟练自信/乔治→认真笨拙。"
)

# ── uid 51 (S5 野外暴露): 1425 → 1020 ──
TRIMMED[51] = (
    "【NSFW事件——野外暴露：圣光之森】\n\n"
    "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 60, 探索森林深处时触发\n\n"
    "场景：黎恩和Seraphina踏入从未被探索过的空地。瞬间——数万朵圣光花同时绽放。\n"
    "金色光芒像浪潮扩散。亿万颗花粉升腾悬浮。落在皮肤上温暖如微小火花。\n"
    "Seraphina的呼吸变急——花粉对她的炽天使血脉有特殊催化，让克制的圣光失去控制。\n"
    "金色光芒从皮肤涌出，衣服在圣光中变得透明。\n"
    "「黎恩——这些花——我控制不住——」圣光从她指尖流入他皮肤，与鬼之力形成小型漩涡。\n\n"
    "分支A. 纯爱——只有黎恩：\n"
    "鬼之力与圣光在空气中相融，形成一对翅膀——一半金色一半紫色在两人头顶展开。\n"
    "「两种力量，一对翅膀。」她在花田中央完全融合。\n"
    "→ trust +20, bond +20, 解锁「光之翼」新形态\n\n"
    "分支B. NTRS——第三者被发现：\n"
    "圣光花绽放太强烈——第三者从树后走出，无法移开视线。她转向黎恩——眼中是请求。\n"
    "黎恩点头。花粉像有意识一样围绕三人旋转。风穿过花田——花瓣形成金色漩涡。\n"
    "→ shared_experience_level +20, possessiveness_intensity +25\n\n"
    "分支C. 隐奸——第三者偷窥：\n"
    "黎恩和Seraphina不知道有人在看。第三者看到圣光与鬼之力的每一个漩涡，\n"
    "默默退回森林——带走了一个秘密，可能在之后浮出水面。\n"
    "→ hidden_affair_experience +15\n\n"
    "变量：纯爱→trust+20 bond+20 / NTRS→shared+20 intensity+25 / 隐奸→hidden+15\n"
    "核心：圣光花的绽放不是诱惑——是催化。它不会让人做不想做的事，只会让人无法继续隐藏想做的事。\n"
    "人物要点：第三者可能是艾德里安（被圣光吸引）/乔治（仪器被干扰）/雷恩（直觉引导）——圣光烧尽所有面具。"
)

# ── uid 153 (PN2 Thalion诱惑): 1344 → 980 ──
TRIMMED[153] = (
    "【被动NTR事件——PN2：Thalion的诱惑】\n\n"
    "触发条件：abandonment_count >= 40, seraphina_despair >= 50, thalions_influence >= 40\n\n"
    "场景：Seraphina独自在心木废墟附近——心情低落。Thalion突然出现。\n"
    "「小塞拉...你看起来很累。黎恩又不在这里了——不是吗？\n"
    "他总是不在。他有他的同伴、他的帝国、他的『其他生活』。而你——你只有这片森林。」\n"
    "Seraphina想后退——但她太累了。「你想要什么，Thalion？我不会被腐化的。」\n"
    "「我不想要腐化你。我想要理解你。你看——我们都是这个森林的守护者。我们都被遗弃了。」\n"
    "他的手触碰她的脸颊——她没有后退。不是想要他，是太疲惫了。\n"
    "「告诉我——黎恩会在你需要他的时候出现吗？」她的琥珀色眼睛湿润了——没有回答。\n"
    "「但我在。我一直都在。因为——我理解你。我们是同类，小塞拉。」\n\n"
    "玩家（黎恩）的选择：\n"
    "A. 立即冲上去分开他们：「Seraphina！离她远点，Thalion！」→ trust+15, abandonment_count-15\n"
    "B. 在远处观察（痛苦的见证）：黎恩躲在阴影中——看着Thalion的手在她脸颊上。\n"
    "鬼之力燃烧——没有行动。→ trust-15, abandonment_count+10, seraphina_despair+15, thalions_influence+15\n"
    "（被动NTR核心选择——也可能成为转向NTRS的种子）\n"
    "C. 之后质问：「我看到了。你为什么让他碰你？」→ trust-10, seraphina_despair+10\n"
    "她疲惫地回答：「我只是...太累了。」\n\n"
    "变量：取决于选择。被动NTR的「见证」是痛苦的、无法控制的——与NTRS中双方同意的见证根本不同。\n"
    "核心性格要点：Seraphina在此刻不是「软弱」——是疲惫。她200年来独自守护的疲惫在这一刻被Thalion精准抓住。"
)

# ── uid 156 (PN5 堕落之夜): 1460 → 1040 ──
TRIMMED[156] = (
    "【被动NTR事件——PN5：堕落之夜】\n\n"
    "触发条件：abandonment_count >= 70, seraphina_despair >= 80, trust_level < 20, thalions_influence >= 60\n\n"
    "场景：被动NTR路线最低点——最黑暗的时刻。\n"
    "Seraphina独自在心木废墟中——腐化气息包围。Thalion在她身边。\n"
    "「小塞拉...我告诉过你。他会让你失望的。但我不会——200年来我一直在这里。\n"
    "而他——来了几个月——就已经开始忽视你了。」\n"
    "Seraphina的眼睛空洞——没有愤怒，只有疲惫。\n"
    "「你想要什么，Thalion？我太累了。」\n"
    "他的手放在她肩膀上——这次她没有后退。\n"
    "「我想要的——是让你明白。纯洁是幻觉。爱是幻觉。唯一真实的是力量。而我可以给你力量。\n"
    "或者——如果你不愿意接受腐化——至少...接受我。我会是你永远不会失望的人。」\n"
    "她的琥珀色眼睛看着他——表情空虚。「我...我只是...太累了...」\n\n"
    "当黎恩到达时——他看到什么？\n"
    "A. Thalion在腐化/诱惑她——但她的眼睛在看到黎恩的那一刻亮了起来：「黎恩？...」\n"
    "B. Thalion在接触她——她没有抗拒。但眼睛仍然会在看到黎恩时浮现痛苦。\n"
    "C. 她已被腐化或几乎腐化——但即使这样，核心仍然有金色光芒。\n\n"
    "玩家选择：\n"
    "A. 战斗（重新争取）：「Thalion——离她远点！我不会再离开你了！我很抱歉！」\n"
    "→ trust+15，进入「重新争取」子路线\n"
    "B. 见证（痛苦的观察）：远处观看——鬼之力失控但没有行动。被动NTR最黑暗选择——也可能是转向NTRS的种子。\n"
    "→ trust-20, seraphina_despair+10\n"
    "C. 离开（最黑暗的选择）：转身离开让她独自面对。→ trust-30, seraphina_despair+30，进入「彻底破碎」\n"
    "（但即使在最后一步——玩家仍然有机会逆转）\n\n"
    "变量：取决于选择。Seraphina的核心——即使在最黑暗时刻——保留了尊严和选择的可能性。\n"
    "关键情感：这不是「被拯救」的场景——她在最低点时仍保留了说「不」的能力。这是被动NTR与纯粹凌辱的本质区别。"
)

# ============================================================
def find_and_replace_entry(build_text, uid, new_content):
    pattern = rf'(# === uid {uid}:.*?===\s*\n\s*entries\.append\(make_entry\(\s*\n\s*uid={uid},.*?content=\(\s*\n)(.*?)(\n\s*\),)'
    match = re.search(pattern, build_text, re.DOTALL)
    if not match:
        return build_text, False
    new_lines = []
    for line in new_content.split('\n'):
        escaped = line.replace('\\', '\\\\').replace('"', '\\"')
        new_lines.append(f'            "{escaped}\\n"')
    new_content_str = '\n'.join(new_lines)
    old = match.group(0)
    new = match.group(1) + new_content_str + match.group(3)
    return build_text.replace(old, new, 1), True

for uid, new_content in TRIMMED.items():
    bt, ok = find_and_replace_entry(bt, uid, new_content)
    print(f"  {'✅' if ok else '❌'} uid={uid}")

with open(BUILD, "w", encoding="utf-8") as f:
    f.write(bt)
print(f"\n完成: {len(bt)} 字符")
