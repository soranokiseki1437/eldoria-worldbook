# -*- coding: utf-8 -*-
"""
scripts2/execute_stage_splitting.py

执行《临时方案_第二部7000字以上阶段拆分与全局重编号大纲.md》：
1. 一次性读取全部 49 个原始阶段详规文件入内存；
2. 拆分 14 个超长阶段，生成 33 个新阶段详规文件；
3. 顺延重命名 19 个未拆分但编号变动的阶段详规文件（阶段 1~16 保持原状）；
4. 删除 14 个已被拆分的原始文件与 19 个已重命名的旧文件，确保全库物理阶段文件恰好为 68 个；
5. 级联更新第 5 至 14 幕的 00_第X幕大纲与接口.md；
6. 级联更新《第五幕各剧情点时间与时空锚点汇总表.md》；
7. 级联更新《00_第二部宏篇主线总纲与方案管理中枢.md》与《01_宏篇主线剧情总大纲与分幕导航.md》；
8. 修正《临时方案_第二部7000字以上阶段拆分与全局重编号大纲.md》中的文风扫描报警并标记执行完成。
"""

import os
import re
import glob

BASE_DIR = r"方案\第二部\主线与世界扩充方案\分阶段详规"

CN_NUMS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
def int_to_cn(num):
    if num <= 10:
        return CN_NUMS[num]
    elif num < 20:
        return "十" + (CN_NUMS[num % 10] if num % 10 != 0 else "")
    elif num < 100:
        tens = num // 10
        rem = num % 10
        return CN_NUMS[tens] + "十" + (CN_NUMS[rem] if rem != 0 else "")
    return str(num)

# 14 个超长阶段的拆分规划
SPLIT_CONFIGS = [
    # 原阶段 17 (第五幕) -> 新阶段 17, 18
    {
        "orig_act": "05_第五幕_分道巡礼·虚妄的线索",
        "orig_stage_num": 17,
        "splits": [
            {
                "new_stage_num": 17,
                "title": "月牙古泉·遗迹石闸解算与暗影异兽初战",
                "sub_slice": (0, 4), # subs 1~4
                "summary": "雷恩劳拉双人探查月牙泉古遗迹、太古石闸机关解算与暗影异兽初战",
                "deliver": "* **交付状态**：艾德里安暗影心魔经镜湖满月先灵之镜彻底净化，西线探得地窟机兽破闸关键线索；南线黎恩菲娜救助浅滩孤儿，锁定理查德黑帆走私船停泊泊位 ➔ **无缝交接至【[阶段十八：先灵石台·极剑试炼破执与太古秘辛起获详规](阶段十八_先灵石台·极剑试炼破执与太古秘辛起获详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 18,
                "title": "先灵石台·极剑试炼破执与太古秘辛起获",
                "sub_slice": (4, 8), # subs 5~8
                "summary": "月下石台先灵剑影对决、劳拉极剑心性破执、起获教会异化死士先导密函",
                "receive": "* **承接状态**：承接阶段十七，艾德里安与菲重整心智备战地窟机兽；南线黎恩菲娜锁定黑帆走私船底舱坐标；西南线雷恩直面放逐耻辱烙印。",
                "deliver": None
            }
        ]
    },
    # 原阶段 21 (第六幕) -> 新阶段 22, 23
    {
        "orig_act": "06_第六幕_霜雪冬歇·冬日庆典与降临共盟",
        "orig_stage_num": 21,
        "splits": [
            {
                "new_stage_num": 22,
                "title": "深冬留宿·围炉分食麦饼与矮人雪仗打铁日常",
                "sub_slice": (0, 5), # subs 1~5
                "summary": "深冬暴雪连天留宿大本营、大食堂热汤馅饼、矮人打铁拼酒与少女雪仗欢闹",
                "deliver": "* **交付状态**：朱利安在大本营客舍安稳留宿，与同伴经雪仗、后厨洋葱麦糊与矮人打铁拼酒建立深厚烟火羁绊；全员身心在暴雪初冬得到充分休整 ➔ **无缝交接至【[阶段二十三：晨光降临·全营篝火欢歌与冬日降临共盟详规](阶段二十三_晨光降临·全营篝火欢歌与冬日降临共盟详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 23,
                "title": "晨光降临·全营篝火欢歌与冬日降临共盟",
                "sub_slice": (5, 10), # subs 6~10
                "summary": "晨光降临祭典篝火、五族同伴互赠手作信物、朱利安王子正式确立南下战略共识",
                "receive": "* **承接状态**：承接阶段二十二深冬留宿，大本营暴雪初霁，爱丽榭与菲娜备妥防冻草药。",
                "deliver": None
            }
        ]
    },
    # 原阶段 22 (第六幕) -> 新阶段 24, 25
    {
        "orig_act": "06_第六幕_霜雪冬歇·冬日庆典与降临共盟",
        "orig_stage_num": 22,
        "splits": [
            {
                "new_stage_num": 24,
                "title": "隔音长桌·冬日议事复盘与王都商路沙盘推演",
                "sub_slice": (0, 5), # subs 1~4.5 (5 elements)
                "summary": "工坊隔音长桌深度推演、王都各派系贵族实力对账与行商物资配比",
                "deliver": "* **交付状态**：隔音长桌完成王都政局沙盘推演，剖析教会异端审问厅与骑士团派系矛盾，摸清边境伯布鲁诺的自保立场 ➔ **无缝交接至【[阶段二十五：整装待发·战术导力物理伪装与一月大商路总纲详规](阶段二十五_整装待发·战术导力物理伪装与一月大商路总纲详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 25,
                "title": "整装待发·战术导力物理伪装与一月大商路总纲",
                "sub_slice": (5, 11), # subs 5~10 (6 elements)
                "summary": "乔治法林整备耐寒双层遮蔽盒、全队分派假身份文书、开春启程整肃",
                "receive": "* **承接状态**：承接阶段二十四沙盘推演结论，双主角梳理王都地理与记忆切片。",
                "deliver": None
            }
        ]
    },
    # 原阶段 23 (第七幕) -> 新阶段 26, 27, 28
    {
        "orig_act": "07_第七幕_王都商路·繁华市井与暗潮生活流",
        "orig_stage_num": 23,
        "splits": [
            {
                "new_stage_num": 26,
                "title": "南门过闸·王都繁华初涉与金鸢尾老铺寻访",
                "sub_slice": (0, 4), # subs 1~4
                "summary": "车队经白鹿驿道初抵王都南门、平民与骑士阶层反差、落脚金鸢尾街区",
                "deliver": "* **交付状态**：车队顺利通过王都南门关卡，落脚下城平民区，完成市井采风与复式清账，初步摸清水道暗渠与市井物价 ➔ **无缝交接至【[阶段二十七：临街老铺·心木商行盘下与工匠整饬翻新详规](阶段二十七_临街老铺·心木商行盘下与工匠整饬翻新详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 27,
                "title": "临街老铺·心木商行盘下与工匠整饬翻新",
                "sub_slice": (4, 8), # subs 5~8
                "summary": "通过玛格丽特夫人盘下两层旧货栈、乔治哈根连夜修缮柜台排风暗道",
                "receive": "* **承接状态**：承接阶段二十六，通过玛格丽特夫人引荐接洽旧货栈业主。",
                "deliver": "* **交付状态**：成功盘下临河旧货栈作为“心木商行”据点，乔治与哈根连夜加固柜台、修缮排风暗道与临河铁砧工坊，结识巡防队长卢卡斯 ➔ **无缝交接至【[阶段二十八：初次开门·心木香薰走俏与市井眼线暗布详规](阶段二十八_初次开门·心木香薰走俏与市井眼线暗布详规.md)】**。"
            },
            {
                "new_stage_num": 28,
                "title": "初次开门·心木香薰走俏与市井眼线暗布",
                "sub_slice": (8, 13), # subs 9~13
                "summary": "商行开业、北方硬木与草药香薰引爆市井、建立下城平民情报流",
                "receive": "* **承接状态**：承接阶段二十七商行修缮就绪，工匠与店面整饬完毕。",
                "deliver": None
            }
        ]
    },
    # 原阶段 24 (第七幕) -> 新阶段 29, 30
    {
        "orig_act": "07_第七幕_王都商路·繁华市井与暗潮生活流",
        "orig_stage_num": 24,
        "splits": [
            {
                "new_stage_num": 29,
                "title": "百工暗巷·维克托地下工坊寻访与齿轮咬合",
                "sub_slice": (0, 9), # subs 1~9
                "summary": "拜访钟表大师维克托、识破教会对纯铜发条的管制封锁与工匠暗号接头",
                "deliver": "* **交付状态**：玲与艾玛拜访钟表大师维克托地下工坊，结识学徒科林并勘破纯铜发条管制机密；拓印要塞钥匙模型并送别玛格丽特南下商车 ➔ **无缝交接至【[阶段三十：铜齿清音·八音盒核心试音与贵族沙龙入场契机详规](阶段三十_铜齿清音·八音盒核心试音与贵族沙龙入场契机详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 30,
                "title": "铜齿清音·八音盒核心试音与贵族沙龙入场契机",
                "sub_slice": (9, 17), # subs 10~17
                "summary": "纯铜八音盒机芯试制成功、以清越乐音打动名媛、拿到贵族沙龙请柬",
                "receive": "* **承接状态**：承接阶段二十九，维克托地下工坊齿轮模组交割完成。",
                "deliver": None
            }
        ]
    },
    # 原阶段 25 (第七幕) -> 新阶段 31, 32, 33
    {
        "orig_act": "07_第七幕_王都商路·繁华市井与暗潮生活流",
        "orig_stage_num": 25,
        "splits": [
            {
                "new_stage_num": 31,
                "title": "衣香鬓影·金鸢尾沙龙礼仪伪装与名媛茶叙辩锋",
                "sub_slice": (0, 6), # subs 1~6
                "summary": "黎恩菲娜盛装出席贵族沙龙、巧妙应对教会主教与傲慢贵族的试探诘难",
                "deliver": "* **交付状态**：黎恩菲娜盛装出席金鸢尾高级沙龙，在衣香鬓影中机智化解贵族诘难与教会神官试探，成功打入核心贵族社交圈 ➔ **无缝交接至【[阶段三十二：密室长卷·王储忠义派碰头与平民抚恤密账交割详规](阶段三十二_密室长卷·王储忠义派碰头与平民抚恤密账交割详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 32,
                "title": "密室长卷·王储忠义派碰头与平民抚恤密账交割",
                "sub_slice": (6, 13), # subs 7~13
                "summary": "在沙龙侧室与忠义派贵族碰头、核对埃德蒙国王当年的平民抚恤密账卷轴",
                "receive": "* **承接状态**：承接阶段三十一沙龙内圈渗透成功，转入侧室密会。",
                "deliver": "* **交付状态**：在沙龙密室与王储忠义派大臣接头，核对平民抚恤密账卷轴；艾玛截获暗影毒素密信并做出法理反制决断 ➔ **无缝交接至【[阶段三十三：雨夜归途·下城马车伏击反侦察与暗梢斩断详规](阶段三十三_雨夜归途·下城马车伏击反侦察与暗梢斩断详规.md)】**。"
            },
            {
                "new_stage_num": 33,
                "title": "雨夜归途·下城马车伏击反侦察与暗梢斩断",
                "sub_slice": (13, 18), # subs 14~18
                "summary": "沙龙归途遭遇神秘黑衣刺客追踪、小巷断后击溃暗梢安全归栈",
                "receive": "* **承接状态**：承接阶段三十二密账交割完毕，全队冒雨乘马车返回下城。",
                "deliver": None
            }
        ]
    },
    # 原阶段 26 (第七幕) -> 新阶段 34, 35
    {
        "orig_act": "07_第七幕_王都商路·繁华市井与暗潮生活流",
        "orig_stage_num": 26,
        "splits": [
            {
                "new_stage_num": 34,
                "title": "后室托付·商行暗账交割与下城防线留守",
                "sub_slice": (0, 5), # subs 1~5
                "summary": "将心木商行交由玛格丽特心腹掌舵、布下应急撤退密道防线",
                "deliver": "* **交付状态**：将心木商行日常与暗账彻底交由留守心腹掌舵，完善暗渠撤退密道防线；工匠与同伴在炉火前温存道别 ➔ **无缝交接至【[阶段三十五：白鹿启程·商队满载北返与暗潮围城预兆详规](阶段三十五_白鹿启程·商队满载北返与暗潮围城预兆详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 35,
                "title": "白鹿启程·商队满载北返与暗潮围城预兆",
                "sub_slice": (5, 11), # subs 6~11
                "summary": "车队载满稀缺物资金币驶出王都、察觉到边境哨卡调动异常的至暗阴云",
                "receive": "* **承接状态**：承接阶段三十四商行托付妥当，商队整装待发。",
                "deliver": None
            }
        ]
    },
    # 原阶段 29 (第八幕) -> 新阶段 38, 39
    {
        "orig_act": "08_第八幕_血色伏击·至暗大溃败",
        "orig_stage_num": 29,
        "splits": [
            {
                "new_stage_num": 38,
                "title": "血染石桥·生铁巨盾断后与雷恩力竭被俘",
                "sub_slice": (0, 3), # subs 1~3
                "summary": "撤退至石桥隘口、雷恩孤身持重盾卡死隘口阻挡狂潮、力竭被圣殿卫队锁拿入死牢",
                "deliver": "* **交付状态**：雷恩在石桥隘口孤身持盾浴血断后，生铁重盾碎裂力竭被俘，被圣殿卫队押入要塞第七深层水牢 ➔ **无缝交接至【[阶段三十九：暴雨溃退·至暗残部突围与林缘防线收拢详规](阶段三十九_暴雨溃退·至暗残部突围与林缘防线收拢详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 39,
                "title": "暴雨溃退·至暗残部突围与林缘防线收拢",
                "sub_slice": (3, 6), # subs 4~6
                "summary": "黎恩掩护残部冒着滂沱大雨冲出重围、在泥泞荒原边缘稳住防线",
                "receive": "* **承接状态**：承接阶段三十八石桥失守雷恩被俘，主力残部在暴雨泥泞中绝地撤退。",
                "deliver": None
            }
        ]
    },
    # 原阶段 30 (第九幕) -> 新阶段 40, 41, 42
    {
        "orig_act": "09_第九幕_绝境流亡·篝火重铸与艾斯特雷亚之誓",
        "orig_stage_num": 30,
        "splits": [
            {
                "new_stage_num": 40,
                "title": "泥泞长路·荒野伤兵撤退与领民草棚接应",
                "sub_slice": (0, 6), # subs 1~6
                "summary": "撤往旧领荒原、破产领民冒死提供热麦汤与草药、劳拉为伤员包扎",
                "deliver": "* **交付状态**：残部沿泥泞山道撤至艾斯特雷亚旧领，破产领民冒死提供草棚与热汤掩护；劳拉以残刃破除心性执念 ➔ **无缝交接至【[阶段四十一：古堡残垣·祖训石碑摸索与领主责任觉醒详规](阶段四十一_古堡残垣·祖训石碑摸索与领主责任觉醒详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 41,
                "title": "古堡残垣·祖训石碑摸索与领主责任觉醒",
                "sub_slice": (6, 8), # subs 7~8
                "summary": "退守艾斯特雷亚旧领残破庄园、朱利安在先祖墓碑前立誓绝不放弃平民",
                "receive": "* **承接状态**：承接阶段四十伤员在旧领安置，艾德里安重返废弃城堡残垣。",
                "deliver": "* **交付状态**：艾德里安在先祖墓碑与忠仆断骨前立誓，真正觉醒领主守护责任；艾玛与修女完成伤员救治草药调配 ➔ **无缝交接至【[阶段四十二：篝火誓约·全队战损复盘与死牢劫狱誓约缔结详规](阶段四十二_篝火誓约·全队战损复盘与死牢劫狱誓约缔结详规.md)】**。"
            },
            {
                "new_stage_num": 42,
                "title": "篝火誓约·全队战损复盘与死牢劫狱誓约缔结",
                "sub_slice": (8, 11), # subs 9~11
                "summary": "夜幕篝火前黎恩点燃斗志、全员立下不惜代价攻破圣殿死牢救回雷恩的铁誓",
                "receive": "* **承接状态**：承接阶段四十一领主觉醒与草药就绪，全员聚集于地窖围炉。",
                "deliver": None
            }
        ]
    },
    # 原阶段 31 (第九幕) -> 新阶段 43, 44, 45
    {
        "orig_act": "09_第九幕_绝境流亡·篝火重铸与艾斯特雷亚之誓",
        "orig_stage_num": 31,
        "splits": [
            {
                "new_stage_num": 43,
                "title": "界标逼近·圣殿追兵压境与旧领哨卡对峙",
                "sub_slice": (0, 8), # subs 1~8
                "summary": "达米安率重装骑兵追至旧领石界标、双方在风雨中拔剑戒备",
                "deliver": "* **交付状态**：达米安率重装骑兵追逼旧领石界标，双方在风雨哨卡拔剑对峙；营地内部完成物资隐藏 ➔ **无缝交接至【[阶段四十四：大剑当关·黄金罗刹正面霸气一击震慑追兵详规](阶段四十四_大剑当关·黄金罗刹正面霸气一击震慑追兵详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 44,
                "title": "大剑当关·黄金罗刹正面霸气一击震慑追兵",
                "sub_slice": (8, 15), # subs 9~15
                "summary": "劳拉双手大剑斩裂界标青石、凛冽剑气震慑数百追兵不敢逾越",
                "receive": "* **承接状态**：承接阶段四十三对峙剑拔弩张之势，黄金罗刹奥蕾莉亚正面踏出。",
                "deliver": "* **交付状态**：奥蕾莉亚双手大剑斩裂界标青石，霸道剑气正面震慑数百追兵不敢逾越；反派阵营出现内部疑惧裂痕 ➔ **无缝交接至【[阶段四十五：残兵对策·太古古库线索破译与分工整备详规](阶段四十五_残兵对策·太古古库线索破译与分工整备详规.md)】**。"
            },
            {
                "new_stage_num": 45,
                "title": "残兵对策·太古古库线索破译与分工整备",
                "sub_slice": (15, 22), # subs 16~22
                "summary": "逼退追兵后起获先王密藏图纸、凯尔提灯锁定地底太古古库入口",
                "receive": "* **承接状态**：承接阶段四十四逼退追兵，危机暂解。",
                "deliver": None
            }
        ]
    },
    # 原阶段 32 (第九幕) -> 新阶段 46, 47, 48
    {
        "orig_act": "09_第九幕_绝境流亡·篝火重铸与艾斯特雷亚之誓",
        "orig_stage_num": 32,
        "splits": [
            {
                "new_stage_num": 46,
                "title": "太古盲井·古库重力闸门破译与古代矿材启封",
                "sub_slice": (0, 6), # subs 1~6
                "summary": "深入地下千米盲井、凯尔解算太古符文石锁、起获抗酸耐蚀的古代秘银黑钢",
                "deliver": "* **交付状态**：全员深入千米太古盲井，破译重力闸门机关，启封耐酸抗蚀的古代秘银黑钢原石 ➔ **无缝交接至【[阶段四十七：地火炉鸣·矮人地热锻炉点燃与防酸破邪巨剑重铸详规](阶段四十七_地火炉鸣·矮人地热锻炉点燃与防酸破邪巨剑重铸详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 47,
                "title": "地火炉鸣·矮人地热锻炉点燃与防酸破邪巨剑重铸",
                "sub_slice": (6, 12), # subs 7~12
                "summary": "多尔金哈根法林齐上阵、点燃地火锻炉、日夜敲打锻造能劈开死牢生铁重铠的防酸巨剑",
                "receive": "* **承接状态**：承接阶段四十六启封古代黑钢矿材，点燃矮人地热古锻炉。",
                "deliver": "* **交付状态**：多尔金哈根法林齐心锻打千磅铁砧，成功重铸出抗黑酸的破邪巨剑粗胚并完成冷泉初炼 ➔ **无缝交接至【[阶段四十八：试剑淬火·圣光灌注名刃与死牢劫狱战术总推演详规](阶段四十八_试剑淬火·圣光灌注名刃与死牢劫狱战术总推演详规.md)】**。"
            },
            {
                "new_stage_num": 48,
                "title": "试剑淬火·圣光灌注名刃与死牢劫狱战术总推演",
                "sub_slice": (12, 19), # subs 13~19
                "summary": "菲娜注入炽天使圣光完成淬火试剑、全员在沙盘上完成深渊暗河潜入与死牢劫狱推演",
                "receive": "* **承接状态**：承接阶段四十七巨剑粗胚重铸完成，进入最终圣光淬火。",
                "deliver": None
            }
        ]
    },
    # 原阶段 33 (第十幕) -> 新阶段 49, 50
    {
        "orig_act": "10_第十幕_深渊古道·暗河谍影与地底破壁",
        "orig_stage_num": 33,
        "splits": [
            {
                "new_stage_num": 49,
                "title": "逆水盲泉·深渊暗河舟行与钟乳险滩潜渡",
                "sub_slice": (0, 6), # subs 1~6
                "summary": "加尔领航皮筏逆流穿行地下暗河、躲避地底盲眼巨鳄",
                "deliver": "* **交付状态**：加尔领航皮筏逆水潜渡深渊暗河，穿越钟乳险滩并击溃地底盲眼巨蜥突袭，建立中途避风营地 ➔ **无缝交接至【[阶段五十：石闸悬吊·太古泄洪闸卡槽手动破壁通关详规](阶段五十_石闸悬吊·太古泄洪闸卡槽手动破壁通关详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 50,
                "title": "石闸悬吊·太古泄洪闸卡槽手动破壁通关",
                "sub_slice": (6, 12), # subs 7~12
                "summary": "哈根冒险攀爬卡死石闸、生铁手摇绞盘破开通往死牢底层的通道",
                "receive": "* **承接状态**：承接阶段四十九中途营地建立，继续向太古泄洪石闸推进。",
                "deliver": None
            }
        ]
    },
    # 原阶段 34 (第十幕) -> 新阶段 51, 52
    {
        "orig_act": "10_第十幕_深渊古道·暗河谍影与地底破壁",
        "orig_stage_num": 34,
        "splits": [
            {
                "new_stage_num": 51,
                "title": "暗影测绘·特务少女潜行与死牢巡防死角测算",
                "sub_slice": (0, 6), # subs 1~6
                "summary": "菲与亚尔缇娜轻身潜入要塞下层、利用后厨排污湍流绘制精确巡防路线图",
                "deliver": "* **交付状态**：菲与亚尔缇娜轻身潜入要塞下层，利用排污激流掩护精准测绘出巡防死角立体图谱，悬丝送入应急伤药 ➔ **无缝交接至【[阶段五十二：水牢定位·囚室铁窗敲击暗号与雷恩生命确认详规](阶段五十二_水牢定位·囚室铁窗敲击暗号与雷恩生命确认详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 52,
                "title": "水牢定位·囚室铁窗敲击暗号与雷恩生命确认",
                "sub_slice": (6, 13), # subs 7~13
                "summary": "隔着厚重铁条以敲击暗号联络上雷恩、确认重伤状态与典狱长莫尔茨动向",
                "receive": "* **承接状态**：承接阶段五十一管网测绘与送药成功，推进至水牢核心囚室。",
                "deliver": None
            }
        ]
    },
    # 原阶段 35 (第十幕) -> 新阶段 53, 54
    {
        "orig_act": "10_第十幕_深渊古道·暗河谍影与地底破壁",
        "orig_stage_num": 35,
        "splits": [
            {
                "new_stage_num": 53,
                "title": "水磨暗坊·黑市物资对冲与重装机具过卡",
                "sub_slice": (0, 8), # subs 1~8
                "summary": "在下城水磨坊伪装羊毛货运、智斗要塞税官运入攻城破拆绞盘部件",
                "deliver": "* **交付状态**：在下城水磨坊伪装羊毛货运瞒过要塞税卡，成功将攻城破拆绞盘部件与重型机具运抵内线，清剿巡骑内奸 ➔ **无缝交接至【[阶段五十四：方解石室·三件重器就位与死牢决战前夜封盒详规](阶段五十四_方解石室·三件重器就位与死牢决战前夜封盒详规.md)】**。",
                "receive": None
            },
            {
                "new_stage_num": 54,
                "title": "方解石室·三件重器就位与死牢决战前夜封盒",
                "sub_slice": (8, 17), # subs 9~17
                "summary": "将破邪巨剑、导力破壁雷管隐蔽运抵前沿石室、全员完成战前最后整备",
                "receive": "* **承接状态**：承接阶段五十三重型机具过卡，运抵前沿方解石隐蔽石室。",
                "deliver": None
            }
        ]
    }
]

# 35 个未拆分阶段重编号映射: old_stage_num -> new_stage_num
UNSPLIT_MAPPING = {
    # Act 1 (1~3)
    1: 1, 2: 2, 3: 3,
    # Act 2 (4~7)
    4: 4, 5: 5, 6: 6, 7: 7,
    # Act 3 (8~10)
    8: 8, 9: 9, 10: 10,
    # Act 4 (11~14)
    11: 11, 12: 12, 13: 13, 14: 14,
    # Act 5
    15: 15, 16: 16,
    18: 19, 19: 20,
    # Act 6
    20: 21,
    # Act 8
    27: 36, 28: 37,
    # Act 11
    36: 55, 37: 56, 38: 57,
    # Act 12
    39: 58, 40: 59, 41: 60,
    # Act 13
    42: 61, 43: 62, 44: 63,
    # Act 14
    45: 64, 46: 65, 47: 66, 48: 67, 49: 68
}

def load_all_original_files():
    """将既有 49 个阶段详规文件全部载入内存"""
    cn_to_num = {}
    for i in range(1, 100):
        cn_to_num[int_to_cn(i)] = i

    memory_store = {}
    pattern = os.path.join(BASE_DIR, "*", "阶段*.md")
    for fpath in glob.glob(pattern):
        fname = os.path.basename(fpath)
        m = re.match(r"阶段([一二三四五六七八九十]+)_", fname)
        if not m:
            continue
        cn = m.group(1)
        num = cn_to_num[cn]
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        memory_store[num] = {
            "fpath": fpath,
            "fname": fname,
            "content": content,
            "act_dir": os.path.dirname(fpath)
        }
    return memory_store

def execute_splitting(memory_store):
    print("\n--- 正在拆分 14 个超长阶段，生成 33 个新文件 ---")
    created_files = []
    for cfg in SPLIT_CONFIGS:
        orig_num = cfg["orig_stage_num"]
        orig_data = memory_store[orig_num]
        content = orig_data["content"]
        act_dir = orig_data["act_dir"]

        pos_sec1 = content.find("## 一、")
        pos_sec2 = content.find("## 二、")
        pos_sec3 = content.find("## 三、")

        header = content[:pos_sec1]
        sec1 = content[pos_sec1:pos_sec2]
        sec2 = content[pos_sec2:pos_sec3]
        sec3 = content[pos_sec3:]

        subs = [s for s in re.split(r"(?m)^(?=###\s+)", sec2) if s.strip().startswith("###")]
        sec2_title_m = re.search(r"^(## 二、[^\n]*)", sec2)
        sec2_title = sec2_title_m.group(1) if sec2_title_m else "## 二、 阶段全景长线剧情演进"

        rec_m = re.search(r"(### 1\.[^\n]*\n)(.*?)(?=\n### 2\.|\Z)", sec3, re.DOTALL)
        deliv_m = re.search(r"(### 2\.[^\n]*\n)(.*?)(?=\n### 3\.|\Z)", sec3, re.DOTALL)
        stat_m = re.search(r"(### 3\.[^\n]*\n)(.*)", sec3, re.DOTALL)

        orig_receive_body = rec_m.group(2).strip() if rec_m else ""
        orig_deliver_body = deliv_m.group(2).strip() if deliv_m else ""
        orig_status_body = stat_m.group(2).strip() if stat_m else ""

        # 提取幕名称
        act_name_m = re.search(r"(第[一二三四五六七八九十]+幕[·_][^\n>]+)", header)
        act_name = act_name_m.group(1).replace("_", "·") if act_name_m else cfg["orig_act"]
        act_short = act_name[:act_name.find("·")] if "·" in act_name else act_name[:4]

        bq_lines = [l for l in header.splitlines() if l.startswith(">")]
        bq_text = "\n".join(bq_lines) if bq_lines else f"> **所属母案**：[01_宏篇主线剧情总大纲与分幕导航.md](../../01_宏篇主线剧情总大纲与分幕导航.md) · [00_{cfg['orig_act'][:5]}大纲与接口.md](00_{cfg['orig_act'][:5]}大纲与接口.md)\n> **所属幕次**：{act_name}\n> **叙事模式**：阶段全景长线剧情叙述\n> **文风基准**：纯正日式 RPG 剑与魔法（JRPG Western Fantasy）。"

        for split_info in cfg["splits"]:
            new_stage_num = split_info["new_stage_num"]
            new_cn = int_to_cn(new_stage_num)
            new_title = split_info["title"]
            new_fname = f"阶段{new_cn}_{new_title}详规.md"
            new_fpath = os.path.join(act_dir, new_fname)

            new_header = f"# {act_short}·阶段{new_cn}：{new_title}详规\n\n{bq_text}\n\n---\n\n"

            start_idx, end_idx = split_info["sub_slice"]
            slice_subs = subs[start_idx:end_idx]
            renumbered_subs = []
            for s_idx, sub_text in enumerate(slice_subs, 1):
                renumbered = re.sub(r"^###\s+[\d\.]+\s*(?:\.\s*)?", f"### {s_idx}. ", sub_text)
                renumbered_subs.append(renumbered.strip())
            new_sec2 = f"{sec2_title}\n\n" + "\n\n".join(renumbered_subs) + "\n\n---\n\n"

            rec_content = split_info["receive"] if split_info["receive"] is not None else orig_receive_body
            deliv_content = split_info["deliver"] if split_info["deliver"] is not None else orig_deliver_body

            new_sec3 = f"## 三、 本阶段接口与交接说明\n\n### 1. 承接（上一阶段的终态）\n{rec_content}\n\n### 2. 交付（下一阶段要用的输入）\n{deliv_content}\n\n"
            if orig_status_body:
                new_sec3 += f"### 3. 物件与角色状态变化\n{orig_status_body}\n"

            full_content = new_header + sec1 + "\n\n---\n\n" + new_sec2 + new_sec3
            with open(new_fpath, "w", encoding="utf-8") as out_f:
                out_f.write(full_content)
            created_files.append(new_fpath)
            print(f"  [CREATED] {new_fname} ({len(slice_subs)} subs)")

    return created_files

def execute_renumbering(memory_store):
    print("\n--- 正在顺延重命名 19 个未拆分但编号变动的阶段文件 ---")
    renamed_files = []
    for old_num, new_num in UNSPLIT_MAPPING.items():
        if old_num == new_num:
            continue
        old_cn = int_to_cn(old_num)
        new_cn = int_to_cn(new_num)
        old_data = memory_store[old_num]
        content = old_data["content"]
        orig_fpath = old_data["fpath"]
        fname = old_data["fname"]
        dirpath = old_data["act_dir"]

        new_fname = fname.replace(f"阶段{old_cn}_", f"阶段{new_cn}_")
        new_fpath = os.path.join(dirpath, new_fname)

        # 更新标题行
        content = re.sub(rf"# (第[一二三四五六七八九十]+幕·)?阶段{old_cn}[：:]", rf"# \g<1>阶段{new_cn}：", content)

        with open(new_fpath, "w", encoding="utf-8") as out_f:
            out_f.write(content)
        renamed_files.append((orig_fpath, new_fpath))
        print(f"  [RENAMED] {fname} -> {new_fname}")

    return renamed_files

def cleanup_old_files(memory_store):
    print("\n--- 正在删除 14 个已被拆分与 19 个已重命名的旧文件 ---")
    deleted_count = 0
    # 1. 14 个拆分的原文件
    for cfg in SPLIT_CONFIGS:
        orig_num = cfg["orig_stage_num"]
        fpath = memory_store[orig_num]["fpath"]
        if os.path.exists(fpath):
            os.remove(fpath)
            deleted_count += 1
            print(f"  [DELETED SPLIT ORIG] {os.path.basename(fpath)}")

    # 2. 19 个被重命名的原文件
    for old_num, new_num in UNSPLIT_MAPPING.items():
        if old_num != new_num:
            fpath = memory_store[old_num]["fpath"]
            if os.path.exists(fpath):
                os.remove(fpath)
                deleted_count += 1
                print(f"  [DELETED RENAMED ORIG] {os.path.basename(fpath)}")

    print(f"清理完成，共删除 {deleted_count} 个旧文件。")

def update_act5_anchor_table():
    """更新第五幕各剧情点时间与时空锚点汇总表.md"""
    fpath = os.path.join(BASE_DIR, "05_第五幕_分道巡礼·虚妄的线索", "第五幕各剧情点时间与时空锚点汇总表.md")
    if not os.path.exists(fpath):
        return
    with open(fpath, "r", encoding="utf-8") as f:
        c = f.read()

    # 替换关联母案链接
    c = c.replace("阶段十七_先灵映照与极剑破执·暗影机兽与月下石台详规.md", "阶段十七_月牙古泉·遗迹石闸解算与暗影异兽初战详规.md)\n> - [阶段十八_先灵石台·极剑试炼破执与太古秘辛起获详规.md](阶段十八_先灵石台·极剑试炼破执与太古秘辛起获详规.md")
    c = c.replace("阶段十八_机巧穿轴与白鹰立信·货栈暗账与信义放行详规.md", "阶段十九_机巧穿轴与白鹰立信·货栈暗账与信义放行详规.md")
    c = c.replace("阶段十九_公秤仲裁与晨雾归林·复式商战与粮道大捷详规.md", "阶段二十_公秤仲裁与晨雾归林·复式商战与粮道大捷详规.md")

    # 替换章节标题
    # 阶段十七拆分为 阶段十七 (1~4) 和 阶段十八 (5~8 -> 1~4)
    old_sec17_hdr = "## 阶段十七：先灵映照与极剑破执·暗影机兽与月下石台（8个剧情点）"
    new_sec17_hdr = "## 阶段十七：月牙古泉·遗迹石闸解算与暗影异兽初战（4个剧情点）"
    new_sec18_hdr = "## 阶段十八：先灵石台·极剑试炼破执与太古秘辛起获（4个剧情点）"

    if old_sec17_hdr in c:
        pos17 = c.find(old_sec17_hdr)
        pos18 = c.find("## 阶段十八：")
        sec17_content = c[pos17:pos18]

        # 分割剧情点
        p_split = sec17_content.find("## 剧情点 5：")
        part1 = sec17_content[:p_split].replace(old_sec17_hdr, new_sec17_hdr)
        part2 = sec17_content[p_split:]
        # 将剧情点 5~8 重新编号为 1~4
        part2 = part2.replace("## 剧情点 5：", f"{new_sec18_hdr}\n\n## 剧情点 1：")
        part2 = part2.replace("## 剧情点 6：", "## 剧情点 2：")
        part2 = part2.replace("## 剧情点 7：", "## 剧情点 3：")
        part2 = part2.replace("## 剧情点 8：", "## 剧情点 4：")

        c = c[:pos17] + part1 + part2 + c[pos18:]

    # 原阶段十八 -> 阶段十九，原阶段十九 -> 阶段二十
    c = c.replace("## 阶段十九：公秤仲裁与晨雾归林·复式商战与粮道大捷", "## 阶段二十：公秤仲裁与晨雾归林·复式商战与粮道大捷")
    c = c.replace("## 阶段十八：机巧穿轴与白鹰立信·货栈暗账与信义放行", "## 阶段十九：机巧穿轴与白鹰立信·货栈暗账与信义放行")

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(c)
    print("  [UPDATED] 第五幕各剧情点时间与时空锚点汇总表.md")

def update_outline_files():
    """更新第 5 至 14 幕的 00_第X幕大纲与接口.md"""
    print("\n--- 正在更新第 5 至 14 幕的 00 大纲与接口文件 ---")

    # 幕元数据规划规模与导航配置
    act_meta = {
        5: {"start": 15, "end": 20, "count": 6, "prev": (4, 14), "next": (6, 21)},
        6: {"start": 21, "end": 25, "count": 5, "prev": (5, 20), "next": (7, 26)},
        7: {"start": 26, "end": 35, "count": 10, "prev": (6, 25), "next": (8, 36)},
        8: {"start": 36, "end": 39, "count": 4, "prev": (7, 35), "next": (9, 40)},
        9: {"start": 40, "end": 48, "count": 9, "prev": (8, 39), "next": (10, 49)},
        10: {"start": 49, "end": 54, "count": 6, "prev": (9, 48), "next": (11, 55)},
        11: {"start": 55, "end": 57, "count": 3, "prev": (10, 54), "next": (12, 58)},
        12: {"start": 58, "end": 60, "count": 3, "prev": (11, 57), "next": (13, 61)},
        13: {"start": 61, "end": 63, "count": 3, "prev": (12, 60), "next": (14, 64)},
        14: {"start": 64, "end": 68, "count": 5, "prev": (13, 63), "next": None},
    }

    act_dirs = sorted([d for d in glob.glob(os.path.join(BASE_DIR, "*")) if os.path.isdir(d)])
    for act_num in range(5, 15):
        ad = act_dirs[act_num - 1]
        of = glob.glob(os.path.join(ad, "00_*.md"))[0]
        with open(of, "r", encoding="utf-8") as f:
            c = f.read()

        meta = act_meta[act_num]
        s_cn = int_to_cn(meta["start"])
        e_cn = int_to_cn(meta["end"])
        cnt = meta["count"]

        # 更新规划规模
        c = re.sub(r"规划规模\*\*：涵盖阶段[^\n，]+[（(]共[^\n）)]+[)）]", f"规划规模**：涵盖阶段{s_cn}至阶段{e_cn}（共 {cnt} 个阶段）", c)

        # 更新前后导航
        if meta["prev"]:
            p_act, p_st = meta["prev"]
            c = re.sub(rf"上一幕：\[00_第{int_to_cn(p_act)}幕[^\n]*·阶段[一二三四五六七八九十]+", f"上一幕：[00_第{int_to_cn(p_act)}幕大纲与接口.md](../{act_dirs[p_act-1][-15:]}/00_第{int_to_cn(p_act)}幕大纲与接口.md)（第{int_to_cn(p_act)}幕···阶段{int_to_cn(p_st)}", c)
        if meta["next"]:
            n_act, n_st = meta["next"]
            c = re.sub(rf"下一幕：\[00_第{int_to_cn(n_act)}幕[^\n]*·阶段[一二三四五六七八九十]+", f"下一幕：[00_第{int_to_cn(n_act)}幕大纲与接口.md](../{act_dirs[n_act-1][-15:]}/00_第{int_to_cn(n_act)}幕大纲与接口.md)（第{int_to_cn(n_act)}幕···阶段{int_to_cn(n_st)}", c)

        # 扫描本幕下现有的所有阶段文件，重新生成表格
        stage_files = sorted(glob.glob(os.path.join(ad, "阶段*.md")))
        table_rows = [
            "| 阶段 | 阶段主题 | 核心长线演进要点 | 详规链接 |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for sf in stage_files:
            sf_name = os.path.basename(sf)
            m = re.match(r"阶段([一二三四五六七八九十]+)_(.*?)详规\.md", sf_name)
            if not m:
                continue
            st_cn = m.group(1)
            st_theme = m.group(2)
            
            # 读取该阶段文件提取 summary
            with open(sf, "r", encoding="utf-8") as s_in:
                s_c = s_in.read()
            # 提取小节标题作为演进要点概览
            sec2_m = re.search(r"## 二、[^\n]*\n(.*?)(?=\n## 三、|\Z)", s_c, re.DOTALL)
            summary_points = []
            if sec2_m:
                sub_titles = re.findall(r"^###\s+\d+\.\s*(.*?)$", sec2_m.group(1), re.M)
                summary_points = sub_titles[:5]
            summary_str = "；".join(summary_points) if summary_points else st_theme
            table_rows.append(f"| **阶段{st_cn}** | **{st_theme}** | 涵盖关键演进：{summary_str} | [阶段{st_cn}详规]({sf_name}) |")

        new_table_str = "\n".join(table_rows)
        # 替换已有表格
        c = re.sub(r"(\| 阶段 \| 阶段主题 \|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|.*\|\n*)+)", new_table_str + "\n", c)

        with open(of, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"  [UPDATED] {os.path.basename(of)} ({len(stage_files)} 阶段)")

def update_master_documents():
    """更新 00 与 01 顶层母案"""
    print("\n--- 正在更新顶层母案 00 与 01 ---")

    # 1. 00_第二部宏篇主线总纲与方案管理中枢.md
    p00 = r"方案\第二部\主线与世界扩充方案\00_第二部宏篇主线总纲与方案管理中枢.md"
    if os.path.exists(p00):
        with open(p00, "r", encoding="utf-8") as f:
            c00 = f.read()

        c00 = c00.replace("十四幕四十四阶段", "十四幕六十八阶段")
        c00 = c00.replace("十四幕四十九阶段", "十四幕六十八阶段")
        c00 = c00.replace("49 个阶段", "68 个阶段")

        # 更新十四幕宏篇演进全景总表中的包含阶段
        stage_ranges = {
            "第五幕": "阶段十五 ~ 二十",
            "第六幕": "阶段二十一 ~ 二十五",
            "第七幕": "阶段二十六 ~ 三十五",
            "第八幕": "阶段三十六 ~ 三十九",
            "第九幕": "阶段四十 ~ 四十八",
            "第十幕": "阶段四十九 ~ 五十四",
            "第十一幕": "阶段五十五 ~ 五十七",
            "第十二幕": "阶段五十八 ~ 六十",
            "第十三幕": "阶段六十一 ~ 六十三",
            "第十四幕": "阶段六十四 ~ 六十八",
        }
        for act_name, r_str in stage_ranges.items():
            c00 = re.sub(rf"(\| \*\*{act_name}\*\* \| [^|]+ \| )阶段[一二三四五六七八九十 ~]+( \|)", rf"\g<1>{r_str}\g<2>", c00)

        with open(p00, "w", encoding="utf-8") as f:
            f.write(c00)
        print("  [UPDATED] 00_第二部宏篇主线总纲与方案管理中枢.md")

    # 2. 01_宏篇主线剧情总大纲与分幕导航.md
    p01 = r"方案\第二部\主线与世界扩充方案\01_宏篇主线剧情总大纲与分幕导航.md"
    if os.path.exists(p01):
        with open(p01, "r", encoding="utf-8") as f:
            c01 = f.read()

        c01 = c01.replace("十四幕四十四阶段", "十四幕六十八阶段")
        c01 = c01.replace("十四幕四十九阶段", "十四幕六十八阶段")
        c01 = c01.replace("四十九阶段导航", "六十八阶段导航")

        with open(p01, "w", encoding="utf-8") as f:
            f.write(c01)
        print("  [UPDATED] 01_宏篇主线剧情总大纲与分幕导航.md")

def update_temp_plan():
    """修正临时方案中的文风禁词报警并标记执行完成"""
    p_temp = r"方案\第二部\主线与世界扩充方案\临时方案_第二部7000字以上阶段拆分与全局重编号大纲.md"
    if os.path.exists(p_temp):
        with open(p_temp, "r", encoding="utf-8") as f:
            ct = f.read()

        # 消除 scan_viridia_diseases 报出的 5 个违规词
        ct = ct.replace("拆分门槛", "拆分基准线")
        ct = ct.replace("铜音流转", "铜齿清音")
        ct = ct.replace("王储旧部", "王储忠义派")
        
        # 标记执行完成
        if "已执行落地" not in ct:
            ct = ct.replace(
                "方案性质**：临时规划与重构方案（供审阅与决策定锚，未对既有原始阶段文件执行物理修改）",
                "方案性质**：规划与重构方案（✅ 已于 2026-11-20 正式执行物理落地完成）"
            )

        with open(p_temp, "w", encoding="utf-8") as f:
            f.write(ct)
        print("  [UPDATED] 临时方案_第二部7000字以上阶段拆分与全局重编号大纲.md")

def main():
    print("=" * 60)
    print(" 执行方案：第二部 7,000 字以上阶段拆分与全局重编号")
    print("=" * 60)

    # 1. 载入原始数据
    memory_store = load_all_original_files()
    print(f"成功将全书 {len(memory_store)} 个原始阶段详规载入内存。")

    # 2. 拆分 14 个文件生成 33 个新文件
    created_files = execute_splitting(memory_store)

    # 3. 顺延重命名 19 个未拆分文件
    renamed_files = execute_renumbering(memory_store)

    # 4. 删除旧文件
    cleanup_old_files(memory_store)

    # 5. 更新第五幕时空锚点表
    update_act5_anchor_table()

    # 6. 更新第 5 至 14 幕的 00 大纲文件
    update_outline_files()

    # 7. 更新母案 00 与 01
    update_master_documents()

    # 8. 更新临时方案本身
    update_temp_plan()

    # 9. 最终数量核验
    all_stages = glob.glob(os.path.join(BASE_DIR, "*", "阶段*.md"))
    print("\n" + "=" * 60)
    print(f" 全局执行完成！当前全书阶段详规文件总数: {len(all_stages)} 个（预期 68 个）")
    print("=" * 60)

if __name__ == "__main__":
    main()
