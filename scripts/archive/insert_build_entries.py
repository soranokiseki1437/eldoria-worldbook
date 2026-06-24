#!/usr/bin/env python3
"""
在 build_eldoria.py 中插入 N1-N7, PN1-PN5 的条目生成函数，
并更新版本号至 V4.6.3。
"""
import re

BUILD_PATH = r"C:\Users\lx\Desktop\世界书\scripts\build_eldoria.py"

with open(BUILD_PATH, "r", encoding="utf-8") as f:
    build_text = f.read()

# ============================================================
# 新函数：N1-N7 + PN1-PN5 条目生成
# ============================================================
new_function = r'''
def get_uid145_156_entries():
    """返回 uid 145-156 的条目定义（V4.6.3 N1-N7/PN1-PN5 事件恢复）

    从备份 full_20260616_230654/05_事件系统.md 恢复丢失的事件YAML，
    适配角色名变更（尤西斯→乔治）。
    """
    entries = []

    # ================================================================
    # N1-N7: NTRS路线事件
    # ================================================================

    # === uid 145: N1 坦白之夜 ===
    entries.append(make_entry(
        uid=145,
        keys=["坦白之夜", "ntrs", "n1", "坦白", "共享欲望", "起点"],
        comment="【NTRS事件】N1 坦白之夜——NTRS路线起点，黎恩向Seraphina坦白内心深处的共享欲望",
        order=380,
        probability=80,
        content=(
            "【NTRS事件——N1：坦白之夜】\n\n"
            "触发条件：trust_level >= 50, bond_level >= 30，玩家在「亲密但脆弱」的时刻选择「坦白」\n\n"
            "场景描述：\n"
            "深夜的林间空地，火炉边。黎恩深吸一口气——这是他一生中最难以启齿的事情之一。\n"
            "「Seraphina...我想告诉你一件事。关于我内心深处的某种...欲望。」\n"
            "Seraphina的琥珀色眼睛看着他——她的表情专注而紧张。\n"
            "「这个欲望——它是关于你的。关于看到你被别人...欲望。然后——然后我来『重新拥有』你。\n"
            "我知道这很奇怪。我知道这不『正常』。但它是我的一部分。而且——当我和你在一起时，\n"
            "它变得越来越强烈。因为我太在意你了。不是因为我不爱你——恰恰相反。\n"
            "是因为我太爱你了——以至于想以这种极端的方式确认你。」\n\n"
            "Seraphina的表情：震惊 → 困惑 → 试图理解 → 不安但不拒绝。\n"
            "她的琥珀色眼睛在颤抖——但她没有后退。\n"
            "「黎恩...我——我需要时间思考。但我不害怕。因为——你没有对我撒谎。\n"
            "你把你最私密的、最容易被评判的一面展示给我。这本身就是一种坦诚——一种信任。\n"
            "我不能说我理解。我甚至不能说我『接受』。但——我愿意尝试理解。\n"
            "因为——因为我爱你。而爱意味着接受对方的全部——包括他最黑暗的部分。」\n\n"
            "ntrs_awakened = 100\n"
            "seraphina_acceptance = 25-35（取决于玩家之前的选择）\n\n"
            "玩家选择：\n"
            "A.「谢谢你——无论你的决定是什么，我都会接受。」→ seraphina_acceptance +5\n"
            "B.「也许我不该说——让我们忘了它。」→ 返回纯爱路线，但ntrs_awakened仍然是100\n"
            "C.「如果你感到被冒犯——我道歉。但这是真实的我。」→ seraphina_acceptance +3\n\n"
            "变量更新：ntrs_awakened = 100, seraphina_acceptance = 25-35"
        ),
    ))

    # === uid 146: N2 边界协商 ===
    entries.append(make_entry(
        uid=146,
        keys=["边界协商", "ntrs", "n2", "规则", "试探", "共享边界"],
        comment="【NTRS事件】N2 边界协商——双方讨论NTRS规则，设定「见证」/「轻接触」/「开放探索」界限",
        order=382,
        probability=80,
        content=(
            "【NTRS事件——N2：边界协商】\n\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 30\n\n"
            "场景描述：\n"
            "Seraphina主动找黎恩——她的琥珀色眼睛中有决心。\n"
            "「我一直在想你说的话。我...我想尝试理解。但在我们做任何事情之前——我需要知道规则。\n"
            "什么是『允许』的？什么不会被允许？对我来说——最重要的是，你不能『消失』。\n"
            "无论发生什么——我需要知道你仍然是我的。我需要知道，无论我在做什么——\n"
            "你的眼睛始终在我身上。」\n"
            "黎恩回答：「永远。我不会消失。我会一直在那里——看着你。\n"
            "而在之后——我们会在一起。只有我们。那是『我的』时刻。那是我重新占有你的时刻。」\n\n"
            "协商内容（玩家选择设定「规则」）：\n"
            "A. 只允许「见证」——没有身体接触，只有观看\n"
            "→ shared_experience_level保持低水平，possessiveness_intensity增长较慢\n"
            "B. 允许「轻接触」——在黎恩的注视下，与他人有身体接触（但总是在黎恩设定的界限内）\n"
            "C. 「开放探索」——我们边走边设定界限（最灵活，但也最危险——可能导致占有欲爆发）\n\n"
            "协商后事件：无论选择如何，seraphina_acceptance都会增加。\n"
            "shared_experience_level首次增加（从0到10-20）。玩家进入「试探与边界协商」阶段。\n\n"
            "变量更新：seraphina_acceptance +10~15, shared_experience_level 首次增加"
        ),
    ))

    # === uid 147: N3 第一次见证 ===
    entries.append(make_entry(
        uid=147,
        keys=["第一次见证", "ntrs", "n3", "腐化低语者", "见证", "安全距离"],
        comment="【NTRS事件】N3 第一次见证——Seraphina让腐化低语者接近，黎恩在安全距离观看",
        order=384,
        probability=80,
        content=(
            "【NTRS事件——N3：第一次见证】\n\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 40, shared_experience_level >= 10\n\n"
            "场景描述：\n"
            "森林深处的腐化区域——Seraphina故意让腐化的低语者接近她。\n"
            "黎恩站在她设定的「安全距离」处——观看。\n"
            "腐化的低语者围绕着Seraphina——它们的紫色光芒与她的金色圣光形成对比。\n"
            "它们的低语听起来像是古老而扭曲的语言。\n"
            "Seraphina的目光始终穿过它们——看向黎恩。\n"
            "她的琥珀色眼睛在说「看着我」。\n"
            "当一个腐化的低语者接近她时——它的爪子离她的肩膀只有几厘米。\n"
            "Seraphina没有后退——她的眼睛始终看着黎恩。\n"
            "她的表情是复杂的——紧张、兴奋、不安、以及「你在看吗？我这样做是为了你。」\n\n"
            "事件高潮：当一个腐化低语者的爪子真正触碰到Seraphina时——\n"
            "黎恩的鬼之力几乎失控（他的占有欲几乎压倒了他）。\n"
            "但Seraphina的目光阻止了他——不是用语言，而是用眼神。\n"
            "她的琥珀色眼睛说「还不是时候——继续看。」\n\n"
            "占有欲确认场景：在腐化低语者被净化后，黎恩和Seraphina独处。\n"
            "他立即走向她——他的动作是占有欲的。\n"
            "「你是我的。」他说——他的声音是沙哑的。\n"
            "「我是你的。」她回答——她的琥珀色眼睛燃烧着欲望和确认。\n"
            "这是NTRS关系中最强烈的亲密时刻之一。\n\n"
            "变量更新：shared_experience_level +25, possessiveness_intensity +40, seraphina_acceptance +15, trust_level +10"
        ),
    ))

    # === uid 148: N4 乔治的注视 ===
    entries.append(make_entry(
        uid=148,
        keys=["乔治的注视", "ntrs", "n4", "乔治", "温泉", "沐浴", "优雅"],
        comment="【NTRS事件】N4 乔治的注视——乔治「偶然」看到Seraphina在银流河畔沐浴，技术宅式NTRS场景",
        order=386,
        probability=80,
        content=(
            "【NTRS事件——N4：乔治的注视】\n\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 50, george_closeness >= 30\n\n"
            "场景描述：\n"
            "乔治在一个「偶然」的时刻走进了Seraphina正在沐浴的温泉——\n"
            "但这是黎恩「允许」的偶然。黎恩站在温泉边缘的阴影中——看着。\n"
            "乔治看到了Seraphina——她的粉发漂浮在金色的水面上，\n"
            "她的琥珀色眼睛与他的眼睛对视。\n"
            "乔治的表情是复杂的——惊讶、欣赏、以及某种更深层的东西。\n"
            "他没有立即离开——他站在那里，看着她。\n"
            "Seraphina的目光从乔治转向黎恩——在阴影中的黎恩。\n"
            "她的琥珀色眼睛说「你看到了吗？他在看着我。但我是你的。」\n\n"
            "对话：\n"
            "乔治：「......抱歉，我走错路了。」（但他没有动——他仍然站在那里看着她。）\n"
            "Seraphina：「......走错路了，是吗？」（她没有离开温泉——她也没有尝试掩盖自己。）\n"
            "乔治：「......也许不是错的路。」（他的眼睛与Seraphina的琥珀色眼睛对视——\n"
            "但Seraphina的视线再次转向黎恩。）\n"
            "Seraphina（对黎恩说，但声音足够让乔治听到）：\n"
            "「你看——他被我吸引了。他想要我。但——」\n"
            "她离开了温泉，走向黎恩——她的身体仍然湿润，她的眼睛燃烧着欲望和占有。\n"
            "「但我是你的。」\n\n"
            "占有欲确认场景：乔治离开后（或在他的注视下），黎恩和Seraphina进行了最激烈的「确认」之一。\n"
            "这是NTRS中的「优雅」版——没有腐化的生物，只有人类的欲望。\n\n"
            "变量更新：shared_experience_level +20, possessiveness_intensity +35, seraphina_acceptance +10, george_closeness +10, trust_level +8"
        ),
    ))

    # === uid 149: N5 亚莉莎的发现 ===
    entries.append(make_entry(
        uid=149,
        keys=["亚莉莎的发现", "ntrs", "n5", "亚莉莎", "撞见", "催化剂"],
        comment="【NTRS事件】N5 亚莉莎的发现——亚莉莎撞见NTRS场景，可选邀请加入/拒绝/推迟",
        order=388,
        probability=80,
        content=(
            "【NTRS事件——N5：亚莉莎的发现】\n\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 60, sub_alisas_status >= 40\n\n"
            "场景描述：\n"
            "亚莉莎偶然撞见了黎恩和Seraphina的NTRS场景——她看到了「见证」与「占有」的互动。\n"
            "她的绿色眼睛因震惊而扩大——她的脸涨红了。\n"
            "「黎恩...Seraphina...你们——你们在做什么？」\n"
            "Seraphina的琥珀色眼睛中有一丝挑衅——她没有试图掩盖正在发生的事情。\n"
            "「亚莉莎...你看到了——不是吗？你也想要黎恩，不是吗？\n"
            "你总是在他身边——总是看着他。」\n"
            "亚莉莎的嘴张张合合——她不知道该说什么。\n"
            "黎恩看着亚莉莎——他的表情是复杂的。\n"
            "「亚莉莎...Seraphina知道我对你的感情——对你们所有人的感情。她——理解。\n"
            "而且——她同意我们——我们一起——」\n\n"
            "玩家选择：\n"
            "A.「我们一起——你可以加入我们。」→ 解锁「亚莉莎参与」的多人场景，sub_alisas_status +30\n"
            "B.「不，不是『你』——这是关于Seraphina和我的。你是我的朋友——仅此而已。」\n"
            "→ trust_level +5（Seraphina感到被尊重为「核心」），sub_alisas_status -10\n"
            "C.「Seraphina...让我们和亚莉莎谈谈——不是现在。」→ 推迟决定，但保留了可能性\n\n"
            "变量更新：shared_experience_level +20, seraphina_acceptance +10, possessiveness_intensity +30"
        ),
    ))

    # === uid 150: N6 多人共享之夜 ===
    entries.append(make_entry(
        uid=150,
        keys=["多人共享之夜", "ntrs", "n6", "多人", "群交", "核心", "共享"],
        comment="【NTRS事件】N6 多人共享之夜——NTRS顶点，多人围绕Seraphina，高潮时宣告归属",
        order=390,
        probability=80,
        content=(
            "【NTRS事件——N6：多人共享之夜】\n\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 70, shared_experience_level >= 50, 至少两个第三者角色参与变量足够高\n\n"
            "场景描述：\n"
            "森林深处隐秘空地——被腐化的植物和金色圣光同时环绕着。这是NTRS路线的顶点之一。\n"
            "Seraphina站在空地的中央——她的金色圣光是唯一的光源。\n"
            "围绕着她的是：乔治（优雅而沉默的贵族）、腐化的低语者（扭曲但「被允许」存在的生物）、\n"
            "亚莉莎（她的存在是复杂的——不是参与者，而是见证者/催化剂）、\n"
            "可能还有劳拉（直率地表达她的感情）、可能还有Thalion（在最极端的版本中）。\n"
            "黎恩站在空地的边缘——但他的目光紧紧锁定着Seraphina。\n"
            "Seraphina的琥珀色眼睛在任何时候都不会离开黎恩——\n"
            "即使在她被别人注视、接触的时候。\n"
            "她的表情是矛盾的混合——欲望、不安、兴奋、占有。\n"
            "但在所有这些情感之下——是她对黎恩的「确认」。\n\n"
            "当场面达到高潮时，她大声说：\n"
            "「黎恩·舒华泽——你在看吗？！你看到我了吗？！所有这些人——他们都想要我。但——」\n"
            "她的琥珀色眼睛燃烧着金色的火焰。\n"
            "「我是你的！永远只有你的！」\n\n"
            "占有欲确认场景（事件的后半部分）：在所有人离开后（或在他们的注视下），黎恩走向Seraphina。\n"
            "他的动作是占有欲的——他重新「宣称」她。\n"
            "「你是我的。」他说——他的声音颤抖。\n"
            "「我是你的。」她回答——她的眼睛燃烧着金色的火焰。\n"
            "这是NTRS关系中最深刻、最激烈的「确认」之一。\n\n"
            "变量更新：shared_experience_level +30（达到80-100范围）, possessiveness_intensity +45（达到90-100范围）, seraphina_acceptance +15（达到85-100范围）, trust_level +15, bond_level +25"
        ),
    ))

    # === uid 151: N7 腐化仪式 ===
    entries.append(make_entry(
        uid=151,
        keys=["腐化仪式", "ntrs", "n7", "thalion", "终极", "净化"],
        comment="【NTRS事件】N7 腐化仪式——与Thalion的终极NTRS场景，所有变量达到100，心木树意外开始净化",
        order=392,
        probability=80,
        content=(
            "【NTRS事件——N7：腐化仪式】\n\n"
            "触发条件：ntrs_awakened = 100, seraphina_acceptance >= 80, shared_experience_level >= 80, thalions_influence >= 50\n\n"
            "场景描述：\n"
            "心木废墟中，Thalion与其他腐化的精灵长老环绕着Seraphina。\n"
            "金色圣光是废墟中唯一的光芒——但它被深紫色的腐化所包围。\n"
            "黎恩站在心木树前——但他不是来战斗的。这是他和Seraphina之间最极端的NTRS场景。\n"
            "Thalion优雅地走向Seraphina——他的紫色眼睛燃烧着欲望与腐化的火焰。\n"
            "「你终于明白了——纯洁是一种幻觉。真正的力量来自于接受黑暗——而不是排斥它。」\n"
            "Seraphina的目光穿过Thalion——看向黎恩。\n"
            "她的琥珀色眼睛中没有恐惧——只有「你在看吗？」的确认。\n"
            "「黎恩——看着我。」\n"
            "Thalion的手触碰了她的肩膀——腐化的力量从他的手指流入她的身体。\n"
            "但她的金色圣光大放——不是对抗腐化，而是与它共存。\n"
            "「看——他想要我。他腐化了我——但我的核心仍然是金色的。这金色——它只属于你。」\n"
            "当Thalion继续他的「仪式」时，Seraphina的目光始终与黎恩相连。\n"
            "在最激烈的时刻，她大声说：\n"
            "「即使在腐化中——我也是你的！即使在黑暗中——我的金色之光也只为你燃烧！」\n\n"
            "占有欲确认场景：仪式结束后（或在仪式进行到一半时），黎恩走向Seraphina。\n"
            "他的鬼之力与她的圣光融合——金色与紫色的火焰包围了他们。\n"
            "这是最深刻、最激烈的「重新占有」时刻。\n"
            "「你是我的。」黎恩说——他的声音沙哑，眼睛赤红。\n"
            "「我是你的。」Seraphina回答——她的眼睛燃烧着金色火焰。\n"
            "黄金与紫色的力量在他们周围交织——这是对腐化的征服与对关系的确认。\n\n"
            "变量更新：shared_experience_level达到100, possessiveness_intensity达到100, seraphina_acceptance达到100, trust_level达到100, bond_level达到100, corruption_level -20（心木树意外开始净化——两人力量协同的效果）"
        ),
    ))

    # ================================================================
    # PN1-PN5: 被动NTR路线事件
    # ================================================================

    # === uid 152: PN1 第一次缺席 ===
    entries.append(make_entry(
        uid=152,
        keys=["第一次缺席", "被动ntr", "pn1", "缺席", "独自战斗", "失望"],
        comment="【被动NTR事件】PN1 第一次缺席——黎恩不在场，Seraphina独自面对影牙兽袭击",
        order=400,
        probability=80,
        content=(
            "【被动NTR事件——PN1：第一次缺席】\n\n"
            "触发条件：trust_level < 40, abandonment_count >= 20\n\n"
            "场景描述：\n"
            "影牙兽的大规模袭击——比以往任何一次都更猛烈。\n"
            "Seraphina独自对抗它们——她的金色圣光在腐化的黑暗中闪烁。\n"
            "她喊着黎恩的名字——但他不在这里。\n"
            "他在哪里？——他在鬼之力失控后失去了意识（或者——\n"
            "他和亚莉莎一起去调查一个「重要线索」——\n"
            "或者他和劳拉一起在训练——或者其他任何「合理的缺席理由」）。\n"
            "当黎恩最终回到林间空地时，他看到Seraphina坐在火炉边——\n"
            "她的衣服上有被撕裂的痕迹，她的胳膊上有腐化的伤口。\n"
            "她的琥珀色眼睛看着他——没有愤怒，只有疲惫。\n"
            "「你回来了。...没关系。我处理了。」\n"
            "但她的声音中有一种东西——一种「我习惯了独自处理一切」的感觉。\n\n"
            "玩家选择：\n"
            "A. 道歉并弥补：「Seraphina——对不起。我应该在这里的。让我看看你的伤口——让我帮你处理。」\n"
            "→ trust_level +5, abandonment_count -10（这是「试图阻止被动NTR」的正确选择）\n"
            "B. 解释为什么缺席：「我不是故意的——鬼之力失控了。或者——我和亚莉莎一起去了——」\n"
            "→ trust_level +0（解释不会改变她的感受），abandonment_count不变\n"
            "C. 防御性反应：「我也有我自己的问题！你以为我愿意这样吗？！」\n"
            "→ trust_level -8, abandonment_count +15, seraphina_despair +10（这是加速被动NTR的选择）\n\n"
            "变量更新：基础abandonment_count +15, seraphina_despair +10（「缺席」的事实无法改变——只有后续的弥补可以减轻影响）"
        ),
    ))

    # === uid 153: PN2 Thalion的诱惑 ===
    entries.append(make_entry(
        uid=153,
        keys=["thalion的诱惑", "被动ntr", "pn2", "thalion", "趁虚而入", "疲惫"],
        comment="【被动NTR事件】PN2 Thalion的诱惑——Thalion趁黎恩不在时诱惑Seraphina",
        order=402,
        probability=80,
        content=(
            "【被动NTR事件——PN2：Thalion的诱惑】\n\n"
            "触发条件：abandonment_count >= 40, seraphina_despair >= 50, thalions_influence >= 40\n\n"
            "场景描述：\n"
            "Seraphina独自在心木废墟附近行走——她的心情不好。\n"
            "突然，Thalion出现在她面前。他的紫色眼睛燃烧着伪善的关心。\n"
            "「小塞拉...你看起来很累。黎恩又不在这里了——不是吗？\n"
            "他总是不在。他有他的同伴、他的帝国、他的『其他生活』。\n"
            "而你——你只有这片森林。」\n"
            "Seraphina想后退——但她太累了。\n"
            "「你想要什么，Thalion？我不会被腐化的。」\n"
            "「我不想要腐化你，小塞拉。我想要理解你。\n"
            "你看——你和我是一样的。我们都是这个森林的守护者。我们都被别人遗弃了。」\n"
            "他的手触碰了她的脸颊——她没有后退。\n"
            "不是因为她想要他——而是因为她太疲惫了，无法抗拒。\n"
            "「告诉我——黎恩会在你需要他的时候出现吗？上次袭击时——他在哪里？」\n"
            "Seraphina的琥珀色眼睛湿润了——她没有回答。\n"
            "Thalion的声音变得柔软——伪善的、诱惑的柔软。\n"
            "「但我在。我一直都在。因为——我理解你。我们是同类，小塞拉。我们都是被遗弃的人。」\n\n"
            "玩家（黎恩）的选择：\n"
            "A. 立即冲上去分开他们：「Seraphina！离她远点，Thalion！」→ trust_level +15, abandonment_count -15\n"
            "B. 在远处观察（痛苦的见证）：黎恩躲在阴影中——看着Thalion的手在Seraphina的脸颊上。\n"
            "他的鬼之力在他体内燃烧——但他没有行动。→ trust_level -15, abandonment_count +10, seraphina_despair +15, thalions_influence +15\n"
            "（这是被动NTR路线的核心选择——也可能成为从被动NTR转向NTRS的种子）\n"
            "C. 之后质问Seraphina：「我看到了。你为什么让他碰你？」→ trust_level -10, seraphina_despair +10\n\n"
            "变量更新：取决于玩家选择。被动NTR的「见证」是「痛苦的、无法控制的」——与NTRS中「双方同意的、为确认关系的」见证根本不同。"
        ),
    ))

    # === uid 154: PN3 乔治的默默帮助 ===
    entries.append(make_entry(
        uid=154,
        keys=["乔治的默默帮助", "被动ntr", "pn3", "乔治", "支持", "银流河"],
        comment="【被动NTR事件】PN3 乔治的默默帮助——乔治在Seraphina疲惫时提供支持，被误解的关心",
        order=404,
        probability=80,
        content=(
            "【被动NTR事件——PN3：乔治的默默帮助】\n\n"
            "触发条件：abandonment_count >= 50, seraphina_despair >= 60, george_closeness >= 40\n\n"
            "场景描述：\n"
            "一个深夜，Seraphina独自坐在银流河边——她的肩膀在发抖。\n"
            "乔治出现在她身边——他的眼睛中是真诚的关心（或者——对黎恩的失望投射）。\n"
            "「他不在你身边，不是吗？」\n"
            "Seraphina没有回答——她只是看着银色的河水。\n"
            "「我不会假装理解你们之间的关系。但——我能看到。他让你失望了。一次又一次。」\n"
            "他坐在她身边——保持了礼貌的距离，但他的姿态是支持的。\n"
            "「如果你需要有人说话——我在这里。不是作为『黎恩的同伴』——而是作为一个人。」\n"
            "Seraphina转向他——她的琥珀色眼睛是湿润的。\n"
            "「为什么...为什么我总是一个人？」\n"
            "乔治的表情变化了——他的声音变得柔软。\n"
            "「你不是一个人。至少——现在不是。」\n"
            "他的手靠近她的手——没有接触，但是接近。\n"
            "「我会在这里——只要你需要。」\n\n"
            "（在这个时刻，黎恩可能会看到他们——从远处看到乔治的支持。他会怎么想？——Seraphina在寻找替代者吗？还是乔治在「趁虚而入」？）\n\n"
            "变量更新：george_closeness +20, seraphina_despair -5（因为有人关心）, trust_level -8（黎恩看到这一切时的感觉）。如果玩家选择「质问」而非「理解」——trust_level -15"
        ),
    ))

    # === uid 155: PN4 亚莉莎的对比 ===
    entries.append(make_entry(
        uid=155,
        keys=["亚莉莎的对比", "被动ntr", "pn4", "亚莉莎", "局外人", "对比"],
        comment="【被动NTR事件】PN4 亚莉莎的对比——Seraphina看到黎恩与亚莉莎的亲密互动，产生「局外人」感",
        order=406,
        probability=80,
        content=(
            "【被动NTR事件——PN4：亚莉莎的对比】\n\n"
            "触发条件：abandonment_count >= 50, seraphina_despair >= 60, sub_alisas_status >= 40\n\n"
            "场景描述：\n"
            "Seraphina从远处看到黎恩和亚莉莎在一起。\n"
            "他们站在雾帷边缘——亚莉莎正在解释她是如何找到Eldoria的。\n"
            "黎恩的脸上带着Seraphina很少见到的表情——「轻松」的、「熟悉」的、「属于他的世界」的表情。\n"
            "亚莉莎笑着说：「知道吗，黎恩——我一直相信你还活着。我每天都在找你。」\n"
            "她的手不自觉地碰到了黎恩的胳膊——这不是一个「恋人」的动作，但它是「熟悉」的、「亲密」的。\n"
            "Seraphina转身离开了——她的琥珀色眼睛中有一丝痛苦。\n"
            "「他有他的世界——他的人。我有这片森林。我们从一开始就不是同一个世界的人。」\n\n"
            "变量更新：seraphina_despair +15, trust_level -10, hope_level -10\n\n"
            "注意：这个事件的核心不是「亚莉莎抢走了黎恩」——而是Seraphina意识到「黎恩有他自己的世界，\n"
            "而她只是他冒险的一部分」。这种「局外人」感是被动NTR的关键情感驱动力。"
        ),
    ))

    # === uid 156: PN5 堕落之夜 ===
    entries.append(make_entry(
        uid=156,
        keys=["堕落之夜", "被动ntr", "pn5", "最低点", "thalion", "腐蚀"],
        comment="【被动NTR事件】PN5 堕落之夜——被动NTR最低点，Seraphina几乎被Thalion腐化",
        order=408,
        probability=80,
        content=(
            "【被动NTR事件——PN5：堕落之夜】\n\n"
            "触发条件：abandonment_count >= 70, seraphina_despair >= 80, trust_level < 20, thalions_influence >= 60\n\n"
            "场景描述：\n"
            "这是被动NTR路线的最低点——最黑暗、最痛苦的时刻。\n"
            "Seraphina独自在心木废墟中——腐化的气息包围着她。\n"
            "Thalion在她身边——他的紫色眼睛中是伪善的胜利。\n"
            "「小塞拉...我告诉过你。他会让你失望的。但我不会。我从不让你失望——因为我一直在这里。\n"
            "200年了——我一直在这里，看着你守护这片森林。而他——他来了几个月——就已经开始忽视你了。」\n"
            "Seraphina的眼睛是空洞的——她没有愤怒，只有疲惫。\n"
            "「你想要什么，Thalion？我太累了，不想再玩你的游戏了。」\n"
            "Thalion的手放在她的肩膀上——这次她没有后退。\n"
            "「我想要的——是让你明白。纯洁是一种幻觉。爱——是一种幻觉。唯一真实的——是力量。\n"
            "而我可以给你力量——腐化的力量。或者——如果你不愿意接受腐化——至少...接受我。\n"
            "我会是你永远不会失望的人。」\n"
            "Seraphina的琥珀色眼睛看着Thalion——她的表情是空虚的。\n"
            "「我...我只是...太累了...」\n\n"
            "当黎恩最终到达时——他看到了什么？（取决于玩家的「到达时间」选择）\n"
            "A. 他看到Thalion正在腐化/诱惑Seraphina——但Seraphina的眼睛在看到他的那一刻亮了起来——「黎恩？...」\n"
            "B. 他看到Thalion正在接触Seraphina——而她没有抗拒。但她的眼睛仍然会在看到黎恩时出现痛苦。\n"
            "C. 他到达时——Seraphina已经被腐化（或几乎被腐化）。但即使这样——她的核心仍然有金色的光。\n\n"
            "玩家选择：\n"
            "A. 战斗（重新争取）：「Thalion——离她远点！Seraphina——我不会再离开你了！我——我很抱歉！」\n"
            "→ 进入「重新争取」子路线，trust_level +15（最初），然后根据后续选择继续增长\n"
            "B. 见证（痛苦的观察）：黎恩在远处观看——他的鬼之力失控了——但他没有行动。\n"
            "这是被动NTR中最黑暗的选择——但它也可能是「从被动NTR转向NTRS」的种子（在后续事件中）。\n"
            "→ trust_level -20, seraphina_despair +10\n"
            "C. 离开（最黑暗的选择）：黎恩转身离开——让Seraphina独自面对一切。\n"
            "→ trust_level -30, seraphina_despair +30, 进入「彻底的破碎」子路线\n"
            "（但即使在最后一步——玩家仍然有机会逆转）"
        ),
    ))

    return entries
'''

# ============================================================
# 1. 在 get_uid142_144_entries 函数之后插入新函数
# ============================================================
insert_after = "def build(dry_run=False):"
new_function_block = new_function + "\n\n"

build_text = build_text.replace(
    insert_after,
    new_function_block + insert_after
)

# ============================================================
# 2. 更新 all_entries 合并行
# ============================================================
old_merge = "+ new_entries_142_144"
new_merge = "+ new_entries_142_144 + new_entries_145_156"
build_text = build_text.replace(old_merge, new_merge)

# ============================================================
# 3. 添加获取新条目的代码（在 2n step 之后）
# ============================================================
old_step_2n = 'print(f"[step 2n] 新增 uid 142-144 (P13/P14/P15): {len(new_entries_142_144)} 条")'
new_step_block = '''print(f"[step 2n] 新增 uid 142-144 (P13/P14/P15): {len(new_entries_142_144)} 条")

    # 2o. 获取 uid 145-156 N1-N7/PN1-PN5 恢复事件
    new_entries_145_156 = get_uid145_156_entries()
    print(f"[step 2o] 新增 uid 145-156 (N1-N7/PN1-PN5 恢复): {len(new_entries_145_156)} 条")'''
build_text = build_text.replace(old_step_2n, new_step_block)

# ============================================================
# 4. 更新版本号
# ============================================================
build_text = build_text.replace(
    'VERSION = "V4.6.2"',
    'VERSION = "V4.6.3"'
)
build_text = build_text.replace(
    'VERSION_TAG = f"Eldoria_{VERSION}"  # V4.6.2: P13契约之夜补全 + 全事件浏览器网页',
    'VERSION_TAG = f"Eldoria_{VERSION}"  # V4.6.3: N1-N7/PN1-PN5 事件恢复（从full备份）'
)

# ============================================================
# 写入
# ============================================================
with open(BUILD_PATH, "w", encoding="utf-8") as f:
    f.write(build_text)

print("✅ build_eldoria.py 已更新")

# 验证
checks = [
    "get_uid145_156_entries",
    "V4.6.3",
    "new_entries_145_156",
    "new_entries_142_144 + new_entries_145_156",
    "坦白之夜",
    "第一次缺席",
    "乔治的注视",
    "乔治的默默帮助",
]
for c in checks:
    if c in build_text:
        print(f"  ✅ {c}")
    else:
        print(f"  ❌ {c} NOT FOUND")
