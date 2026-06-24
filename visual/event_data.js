// 自动生成于: 2026-06-24T16:51:52.690086
// 数据源: docs/05_事件系统.md
// 生成器: scripts/generate_event_browser.py

const EVENTS = [
  {
    "id": "E01",
    "title": "林间空地的苏醒",
    "route": "prologue",
    "chapter": "林间空地的苏醒",
    "summary": "黎恩在温暖的毛皮上醒来，周围是简陋但整洁的木屋。",
    "type": "main"
  },
  {
    "id": "E02",
    "title": "第一次与影牙兽战斗",
    "route": "prologue",
    "chapter": "影牙兽的威胁",
    "summary": "黎恩与Seraphina在森林边缘探索——银流河附近。",
    "type": "main"
  },
  {
    "id": "E03",
    "title": "第一次来到心木废墟",
    "route": "prologue",
    "chapter": "心木废墟的秘密",
    "summary": "巨大的精灵宫殿废墟在眼前展开——曾经的金色现在被深紫色的腐化所污染。",
    "type": "main"
  },
  {
    "id": "E04",
    "title": "低语林地的幻影",
    "route": "prologue",
    "chapter": "心木废墟的秘密",
    "summary": "黎恩和Seraphina来到低语林地——古老精灵王的灵魂栖息之地。",
    "type": "main"
  },
  {
    "id": "E05",
    "title": "VII班同伴的到达",
    "route": "prologue",
    "chapter": "VII班的到来",
    "summary": "在森林边缘——雾帷边缘——黎恩听到了熟悉的声音。\n      \"黎恩？黎恩！你在吗？\"",
    "type": "main"
  },
  {
    "id": "E06",
    "title": "VII班同伴的到达",
    "route": "prologue",
    "chapter": "VII班的到来",
    "summary": "几天后，更多VII班的同伴穿过雾帷边缘到达——",
    "type": "main"
  },
  {
    "id": "E07",
    "title": "VII班同伴的到达",
    "route": "prologue",
    "chapter": "VII班的到来",
    "summary": "艾玛·米尔斯汀（紫发的魔女继承人）和菲·克劳塞尔\n      （沉默的前猎兵）也穿越了雾帷边缘。",
    "type": "main"
  },
  {
    "id": "E08",
    "title": "森林的庆典",
    "route": "prologue",
    "chapter": "森林的庆典",
    "summary": "在银流河边，VII班的同伴们围着篝火坐下——",
    "type": "main"
  },
  {
    "id": "E09",
    "title": "古老先灵的低语",
    "route": "prologue",
    "chapter": "古老先灵的低语",
    "summary": "在心木废墟的最深处——那棵巨大的枯萎心木树脚下——",
    "type": "main"
  },
  {
    "id": "E10",
    "title": "黑兔的观察",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "在林间空地附近的一棵老橡树上——",
    "type": "main"
  },
  {
    "id": "E11",
    "title": "流浪商人的来访",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "在森林边缘的空地上——黎恩和Seraphina正在巡逻，",
    "type": "main"
  },
  {
    "id": "E12",
    "title": "圣殿骑士的踪迹",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "沿着银流河岸向上游走去——黎恩发现了血迹。",
    "type": "main"
  },
  {
    "id": "E13",
    "title": "学者的研究",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "在古代圣殿的废墟外——黎恩听到了一阵喃喃自语的声音。",
    "type": "main"
  },
  {
    "id": "E14",
    "title": "义妹的到来",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "清晨——雾帷的边缘突然出现了一阵骚动。",
    "type": "main"
  },
  {
    "id": "E15",
    "title": "杀戮之天使",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "午后的林间空地——阳光透过树叶洒下斑驳的光影。",
    "type": "main"
  },
  {
    "id": "P1",
    "title": "深夜的火炉边对话",
    "route": "pure",
    "chapter": "路线分化",
    "summary": "深夜，VII班的同伴们都已经入睡。",
    "type": "main"
  },
  {
    "id": "P2",
    "title": "鬼之力失控后的安抚",
    "route": "pure",
    "chapter": "路线分化",
    "summary": "战斗后，黎恩的鬼之力失控——紫色的火焰包围了他，",
    "type": "main"
  },
  {
    "id": "P3",
    "title": "第一次约会",
    "route": "pure",
    "chapter": "路线分化",
    "summary": "黎恩邀请Seraphina独自一人去银流河——不带任何同伴。",
    "type": "main"
  },
  {
    "id": "P4",
    "title": "守护者的契约",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "在古老先灵的见证下（或不需要），黎恩和Seraphina",
    "type": "main"
  },
  {
    "id": "P5",
    "title": "VII班的\"正式介绍\"",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "林间空地的篝火旁。黎恩握着Seraphina的手，",
    "type": "nsfw"
  },
  {
    "id": "P6",
    "title": "心木废墟净化仪式前置准备",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "心木废墟的边缘。枯萎的心木树在腐化中沉默。",
    "type": "nsfw"
  },
  {
    "id": "P7",
    "title": "与Thalion的第一次正面战斗",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "在心木废墟的深处——Thalion终于现身了。",
    "type": "nsfw"
  },
  {
    "id": "P8",
    "title": "温泉事件",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "银流河的温泉隐藏在圣光花丛之后——",
    "type": "nsfw"
  },
  {
    "id": "P9",
    "title": "守护夜",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "影牙兽的大规模袭击——比以往任何一次都更猛烈。",
    "type": "nsfw"
  },
  {
    "id": "P10",
    "title": "古老先灵的启示",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "在低语林地的最深处——古老先灵埃尔德莱恩再次显现。",
    "type": "nsfw"
  },
  {
    "id": "P11",
    "title": "终极战斗准备",
    "route": "pure",
    "chapter": "终极抉择",
    "summary": "明天。与Thalion的最终决战就在明天。",
    "type": "nsfw"
  },
  {
    "id": "P12",
    "title": "终局抉择",
    "route": "pure",
    "chapter": "终局",
    "summary": "战斗结束了。心木树的新芽在废墟中破土而出。",
    "type": "nsfw"
  },
  {
    "id": "P13",
    "title": "契约之夜",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "守护者契约建立后的第一个夜晚。",
    "type": "nsfw"
  },
  {
    "id": "P14",
    "title": "温泉的清晨",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "温泉之夜的第二天清晨。",
    "type": "nsfw"
  },
  {
    "id": "P15",
    "title": "鬼之圣光交融",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "古老先灵的预言还在耳边回响——\n      \"当圣光与暗影共鸣——森林将从死亡中重生。\"",
    "type": "nsfw"
  },
  {
    "id": "P16",
    "title": "足下的誓言",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "满月。心木树的新芽在月光下泛着银绿色的微光——这是契约之后的第一轮满月。",
    "type": "nsfw"
  },
  {
    "id": "P17",
    "title": "俯首的骑士",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "深夜的木屋。炉火已经烧到了余烬——橙红色的光在灰白的木炭上明灭。",
    "type": "nsfw"
  },
  {
    "id": "P18",
    "title": "巡逻后的夜晚",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "傍晚她巡了整片东侧林地——影牙兽的活动范围又扩大了。",
    "type": "nsfw"
  },
  {
    "id": "P19",
    "title": "艾玛的手交实证研究",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "她推了推眼镜，翻开笔记本。\\\"手部神经末梢密度是女性最高的区域之一。理论上，手的刺激可以传达极其复杂的...情绪。\\\"理论说完，她摘下眼镜放在一旁——这是她\\\"进入实践\\\"的信号。她的手比他想的更温暖、更有力。每当她想验证某个\\\"假说\\\"，",
    "type": "nsfw"
  },
  {
    "id": "P20",
    "title": "初次的唇——口交入门",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "她跪坐在他身前——不是屈从，而是仪式。圣光在她指尖微微亮起，她用手背擦过嘴唇，琥珀色眼睛从下方仰视着他。第一次含入时她微微呛到，但没有退开。圣光在她的咽喉处温和地闪烁——她用魔法抑制了呕吐反射。再次抬起头时，唇间牵着银丝，她的眼神是骄傲的：",
    "type": "nsfw"
  },
  {
    "id": "P21",
    "title": "玲的口交游戏",
    "route": "pure",
    "chapter": "第0章",
    "summary": "\\\"我打赌——你坚持不了三分钟。\\\"她歪着头，笑容是纯粹的恶作剧——但含入的动作却是纯粹的精准。她不含到底，总是在临界点停下，抬头用红瞳看他，嘴里含着，含糊不清地问：\\\"还要吗？\\\"——明知答案。当她终于让他释放时，她舔了舔嘴角，表情像刚吃",
    "type": "nsfw"
  },
  {
    "id": "P22",
    "title": "圣光之谷——乳交",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "她的圣光从锁骨蔓延至双乳之间——她用手指分开乳房两侧，让那条沟变得更深。\"这里...也是我的魔法流淌的地方。\"当他在双乳间滑动时，金色圣光从乳沟中渗出，随着她被挤压的胸脯一明一暗地闪烁——像是心跳化成了光。她低头看着自己胸前，表情混合着惊讶",
    "type": "nsfw"
  },
  {
    "id": "P23",
    "title": "骑士的胸怀——劳拉的乳交",
    "route": "pure",
    "chapter": "第0章",
    "summary": "她解开骑士服的扣子时，动作郑重得像卸下铠甲。\\\"战士的胸膛...也是胸膛。\\\"她的胸肌结实，乳沟深邃——那是常年挥剑的结果。当她用双乳夹住他时，力量控制精准得像握剑——不会太紧，不会太松。\\\"这是我的...另一种形式的侍奉。\\\"她的脸红了—",
    "type": "nsfw"
  },
  {
    "id": "P24",
    "title": "大腿之间——Seraphina的腿交",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "她坐在床沿，双腿并拢，大腿内侧的柔嫩皮肤微微泛着圣光的暖意。\"如果你想...慢一点。\"她并紧的腿间形成了一个温热而紧致的通道——不像内部那样激烈，却有一种\"在她的体表\"的亲昵。每一次滑动都擦过她大腿内侧最敏感的皮肤，她的脚趾蜷起——不是因为",
    "type": "nsfw"
  },
  {
    "id": "P25",
    "title": "银流河畔的初次手交",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "河水浸过脚踝。她看着自己的手覆盖在他勃起上——\"教我。\"从生涩的握法到找到节奏，每一次他的呼吸变化都让她调整手势。她琥珀色的眼睛里既有科研般的专注又有情欲的好奇。\"这样...对吗？\"她不需要答案——他的身体已经回答了。她始终注视他的眼睛，手",
    "type": "nsfw"
  },
  {
    "id": "N1",
    "title": "坦白之夜",
    "route": "ntrs",
    "chapter": "路线分化",
    "summary": "在深夜的林间空地，火炉边。",
    "type": "main"
  },
  {
    "id": "N2",
    "title": "边界协商",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "Seraphina主动找黎恩——她的琥珀色眼睛中有决心。\n      \"我一直在想你说的话。我...我想尝试理解。",
    "type": "main"
  },
  {
    "id": "N3",
    "title": "第一次见证",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "森林深处的腐化区域。Seraphina站在月光下——她的手指在解上衣扣子时微微发抖。",
    "type": "main"
  },
  {
    "id": "N4",
    "title": "第二次见证——习惯的萌芽",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "同一个森林深处的空地。但这一次——月光不那么冷了。",
    "type": "main"
  },
  {
    "id": "N5",
    "title": "迷路的旅人——陌生人仅注视",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "银流河上游浅滩。一个迷路的旅人误入林间空地。",
    "type": "nsfw"
  },
  {
    "id": "N6",
    "title": "雷恩的初访——仪式摸乳",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "黄昏。森林边缘石砌修道院废墟。雷恩单膝跪下——不是求爱，是祝圣的姿势。\n      「黎恩信任我。你也信任我。我不会辜负这种信任。」",
    "type": "main"
  },
  {
    "id": "N7",
    "title": "圣光的初触——摸乳",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "Seraphina坐在心木树下的石阶上，月光透过树叶洒在她的锁骨上。",
    "type": "main"
  },
  {
    "id": "N8",
    "title": "足部护理——银流河的温柔",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "银流河畔。Seraphina赤脚浸在河水中。她抬起湿淋淋的脚——水珠从脚尖滑落。",
    "type": "nsfw"
  },
  {
    "id": "N9",
    "title": "晨露中的裸足",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "清晨木屋。晨光从窗缝透入。她先醒了——看着身边还在睡梦中的他。",
    "type": "nsfw"
  },
  {
    "id": "N10",
    "title": "乔治的注视",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "温泉。Seraphina在金色水中——银发漂浮在水面。",
    "type": "nsfw"
  },
  {
    "id": "N11",
    "title": "挑逗的萌芽",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "木屋中。炉火只剩暗红色余烬。Seraphina趴在黎恩胸口——手指在他锁骨上画圈。\n      \"你今天——吃醋了。\"",
    "type": "main"
  },
  {
    "id": "N12",
    "title": "凯尔的告白——真诚暗恋",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "木屋书房。凯尔攥着精灵语文献，指关节发白。\n      「我研究精灵文化六年——没有一份文献能描述你。是你对我笑的那一次——就一次。我记了它整整十四天。」",
    "type": "main"
  },
  {
    "id": "N13",
    "title": "银色的探索——指交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "银流河畔的草地上，Seraphina仰躺在他的外衣上——双腿微张。",
    "type": "main"
  },
  {
    "id": "N14",
    "title": "雷恩的手——温柔手交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "木屋卧室。炉火烧到正好。Seraphina半躺床沿，衣袍松垮。",
    "type": "nsfw"
  },
  {
    "id": "N15",
    "title": "乔治的触碰——笨拙手交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "木屋。乔治站在床边手不知放哪里。「我拆过上千台导力器——但我没——」",
    "type": "nsfw"
  },
  {
    "id": "N16",
    "title": "艾德里安的唇——口交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "艾德里安府邸私室。他跪在她腿间——跪得优雅。\n      「守护者大人——我可以开始了吗？」语气像在请求一曲舞蹈。",
    "type": "nsfw"
  },
  {
    "id": "N17",
    "title": "圣光之泉——口交受け",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "Seraphina仰躺在心木树根部的软苔上——这是Eldoria最神圣的地方。\n      \"在这里...用你的嘴...\"她的话没说完就转为一声低吟——第三者跪在她双腿之间，",
    "type": "nsfw"
  },
  {
    "id": "N18",
    "title": "林间初尝——首次单人本番",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "密林深处老橡树下。艾德里安把她抵在树上——树皮粗糙硌在背上。\n      「你一直在看黎恩——他就在那边榉树后面。我知道他在。他知道我知道。」",
    "type": "nsfw"
  },
  {
    "id": "N19",
    "title": "隐奸——黎恩的窥视",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "Rean外出归来，循圣光在森林深处月光空地找到Seraphina与第三者独处。",
    "type": "nsfw"
  },
  {
    "id": "N20",
    "title": "玉足之戏——足交NTRS",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "祭坛石阶上。Seraphina赤脚坐于高处，Rean坐对面注视。第三者站她面前。",
    "type": "nsfw"
  },
  {
    "id": "N21",
    "title": "丝袜之诱——角色各自的足部魅力",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "篝火夜。众人围坐。Rean目光扫过各女性角色的脚与丝袜：",
    "type": "nsfw"
  },
  {
    "id": "N22",
    "title": "桌下之手——隐奸手交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "长桌周围坐着同伴——亚莉莎在汇报、劳拉在点头。桌布之下，他的手被Seraphina握住，无声地引导到某个位置。她面色如常地与乔治讨论净化方案，手指却在悄悄解开他的腰带。当他的呼吸开始不稳时，她端起茶杯掩住嘴角的笑意。菲多看了她一眼——Ser",
    "type": "nsfw"
  },
  {
    "id": "N23",
    "title": "桌下之口——隐奸口交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "同样的长桌，同样的会议——但这次她滑到了桌面之下。菲终于问：\\\"Seraphina去哪了？\\\"亚莉莎答：\\\"刚才她说去取净化方案的数据。\\\"与此同时，桌布下的温暖嘴唇正包裹着他。他必须——必须在三秒内——回答劳拉关于影牙兽巡逻路线的问题——",
    "type": "nsfw"
  },
  {
    "id": "N24",
    "title": "亚莉莎的发现",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "亚莉莎偶然撞见了黎恩和Seraphina的NTRS场景——",
    "type": "main"
  },
  {
    "id": "N25",
    "title": "第一次双人共享——NTRS情感阶段B→C过渡",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "篝火已烧到只剩暗红色的炭。Seraphina坐在中间——左边是乔治，右边是凯尔。",
    "type": "nsfw"
  },
  {
    "id": "N26",
    "title": "艾德里安的赌局——首次插入",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "银流河畔月光下。这是NTRS路线最重要的里程碑之一——",
    "type": "nsfw"
  },
  {
    "id": "N27",
    "title": "凯尔的第一次——学者的试炼",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "凯尔紧张地推眼镜——他想参与共享仪式，不是作为研究对象，是作为被信任的人。",
    "type": "main"
  },
  {
    "id": "N28",
    "title": "雷恩的慰藉——骑士的温柔",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "战后。Seraphina坐在河畔，圣光微弱。雷恩无声走近，粗糙大手覆上她的手。\n      \"你累了。\"——他不需要安慰她，只需要陪伴她。他曾失去妻子，他懂沉默的分量。",
    "type": "main"
  },
  {
    "id": "N29",
    "title": "凯尔的再战——主动本番",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "木屋卧室。凯尔进门时手里没有文献——他摘了眼镜放在桌上。她没见过他不戴眼镜的样子。\n      「我——从上次之后做了一些研究。不是学术那种——我问了雷恩。和艾德里安。关于怎么做。」",
    "type": "nsfw"
  },
  {
    "id": "N30",
    "title": "乔治的意外——笨拙本番",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "木屋。乔治解她衣服时手指打结扣子和手指缠在一起。她笑了——温柔地帮他把扣子解开。",
    "type": "nsfw"
  },
  {
    "id": "N31",
    "title": "夜袭——黑暗中的访客",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "深夜木屋。月光穿窗缝。Seraphina侧躺草席。门被推开——来者或Rean/第三者/被Rean撞见。",
    "type": "nsfw"
  },
  {
    "id": "N32",
    "title": "劳拉的直率",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "劳拉·S·亚尔赛德第一个察觉到了黎恩和Seraphina关系中的\"不同\"。",
    "type": "nsfw"
  },
  {
    "id": "N33",
    "title": "与爱丽榭的禁忌",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "爱丽榭在银流河边找到黎恩。月光下，银色的河水映照着她的脸——",
    "type": "nsfw"
  },
  {
    "id": "N34",
    "title": "温泉NTRS版",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "银流河温泉——与纯爱温泉形成镜像对比。",
    "type": "nsfw"
  },
  {
    "id": "N35",
    "title": "菲的直接本番",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "训练后，她坐在兵器架上，双腿晃着。\\\"喂。\\\"她叫他——用的是猎兵的称呼，但眼神里的东西不是猎兵的。\\\"想做就做吧。\\\"没有铺垫，没有浪漫装饰——菲就是菲。但当他进入她时，她搂住他脖子的手臂比任何女人都紧。\\\"...其实我，一直在想这一刻。",
    "type": "nsfw"
  },
  {
    "id": "N36",
    "title": "亚莉莎的傲娇本番",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "\\\"笨、笨蛋！谁说你可以...\\\"——话没说完，因为当他真的进入时，她的手臂像抓救命稻草一样搂住了他的背。蕾丝内衣被扔在地板上——那是莱恩福尔特的最新款，价值数万米拉，此刻只是一块碍事的布。嘴上说着\\\"别、别看我\\\"，但她的身体从不撒谎——",
    "type": "nsfw"
  },
  {
    "id": "N37",
    "title": "玲的游戏本番",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "\\\"这次玩真的哦？\\\"她跨坐在他身上，握着它对准自己时还在笑——但当真正进入的那一刻，她的红瞳骤然放大。镰刀型武器靠在墙角，她的手指在他肩膀上抓出红痕。\\\"等、等一下...\\\"——这是玲第一次失去掌控。她原本的计划是\\\"捉弄他\\\"，但身体有",
    "type": "nsfw"
  },
  {
    "id": "N38",
    "title": "劳拉的骑士本番",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "她将骑士服叠得整整齐齐才放到一旁——\\\"这不代表我卸下了荣誉，只代表我选择对你卸下防御。\\\"她的身体是战士的——腹肌线条分明，大腿有力。当他进入时，她的呼吸只乱了一瞬便重新稳定——骑士的训练让她控制住了身体的反应。但她的指节因为抓床单而发白",
    "type": "nsfw"
  },
  {
    "id": "N39",
    "title": "多人共享之夜",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "森林深处的隐秘空地。Seraphina站在中央——金色圣光是唯一光源。",
    "type": "nsfw"
  },
  {
    "id": "N40",
    "title": "艾玛的仪式性共享",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "艾玛在低语林地布下了魔女家族的\"灵魂共鸣仪式\"——",
    "type": "nsfw"
  },
  {
    "id": "N41",
    "title": "菲的精神见证",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "菲·克劳塞尔从不主动说话。但她的沉默是最敏锐的——",
    "type": "nsfw"
  },
  {
    "id": "N42",
    "title": "群交——圣光之环",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "森林深处祭坛。Seraphina立于中央，多名第三者环绕。五层递进——凯尔被引导→雷恩加入→艾德里安替换→乔治口交→(可选)Thalion腐化介入。Rean坐环外注视。终幕：所有人退开，Rean占有她，鬼之力与圣光完全交融。",
    "type": "nsfw"
  },
  {
    "id": "N43",
    "title": "温泉混浴——银流河的夜晚",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "银流河天然温泉。水汽月光。Seraphina率先入水。水改变所有互动质感。",
    "type": "nsfw"
  },
  {
    "id": "N44",
    "title": "温泉夜——水汽中的足交",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "银流河温泉。水汽升腾。水中足交——水的浮力让动作更慢更深，温度让皮肤更敏感。",
    "type": "nsfw"
  },
  {
    "id": "N45",
    "title": "密林即兴——站立后入",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "她的手撑在古树粗糙的树皮上，手指在苔藓上抓出印痕。他从身后进入——这个姿势让她必须踮起脚尖。森林的寂静让每一次撞击声和水声都格外清晰。她用一只手捂住嘴——不是因为羞耻，而是因为这个姿势让她的声音太大了。透过树叶的阳光斑驳地落在她裸露的背上，",
    "type": "nsfw"
  },
  {
    "id": "N46",
    "title": "镜湖倒影——欲望本番",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "湖水如镜，满月倒映在水中央。她脱衣时看了一眼水面——自己的倒影赤裸着站在月光下。当他从正面进入时，她在水中的倒影同步动作——她看着水中的自己在被占有，看着自己的表情从克制到失控，看着自己的腿缠上他的腰。\\\"那个...是我吗？\\\"她在喘息中问",
    "type": "nsfw"
  },
  {
    "id": "N47",
    "title": "野外暴露——圣光之森",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "数万朵圣光花同时绽放。花粉对Seraphina炽天使血脉有催化作用——圣光失控外溢，衣服在光芒中透明。",
    "type": "nsfw"
  },
  {
    "id": "N48",
    "title": "圣光之镜——欲望的倒影",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "镜湖（Mir'elindor）——不反射现实，只反射欲望。每个人在湖中看到自己最深层的渴望。",
    "type": "nsfw"
  },
  {
    "id": "N49",
    "title": "月光下的誓言",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "满月心木树下。双色光芒照亮草地——森林最神圣之处。足交化为仪式。",
    "type": "nsfw"
  },
  {
    "id": "N50",
    "title": "主动手交——NTRS阶段C→D",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "空地篝火边。Seraphina主动走向乔治——他没有预料到。她在他面前蹲下，",
    "type": "nsfw"
  },
  {
    "id": "N51",
    "title": "主动口交——NTRS阶段D",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "木屋中。艾德里安坐在椅子上——Seraphina跪在他双腿之间。",
    "type": "nsfw"
  },
  {
    "id": "N52",
    "title": "主动隐奸——NTRS阶段D",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "\"今天下午——我会去找乔治。你可以在窗外看。但别进来。\"",
    "type": "nsfw"
  },
  {
    "id": "N53",
    "title": "桌下之手——NTRS隐奸手交",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "长桌。同伴们在讨论净化方案——亚莉莎在汇报数据，劳拉在点头，菲在打瞌睡。",
    "type": "nsfw"
  },
  {
    "id": "N54",
    "title": "桌下之口——NTRS隐奸口交",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "同样的长桌。但这次——Seraphina滑到了桌面之下。",
    "type": "nsfw"
  },
  {
    "id": "N55",
    "title": "隐乳交——NTRS隐蔽乳交",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "心木树后的石阶。月光被树冠切割成碎片洒在地上。乔治坐在石阶上——",
    "type": "nsfw"
  },
  {
    "id": "N56",
    "title": "腐化仪式",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "心木废墟。Thalion站在Seraphina身后——但她的姿态和N3完全不同。",
    "type": "main"
  },
  {
    "id": "N57",
    "title": "胜利庆典后的失控",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "腐化被净化后，银流河畔。",
    "type": "nsfw"
  },
  {
    "id": "N58",
    "title": "终极确认之夜",
    "route": "ntrs",
    "chapter": "终极抉择",
    "summary": "决战前夜。所有同伴都在木屋中——炉火噼啪作响。",
    "type": "nsfw"
  },
  {
    "id": "N59",
    "title": "终局抉择",
    "route": "ntrs",
    "chapter": "终局",
    "summary": "战争结束了。腐化被净化了。",
    "type": "nsfw"
  },
  {
    "id": "PN1",
    "title": "第一次缺席",
    "route": "passive_ntr",
    "chapter": "被动NTR·第一次缺席",
    "summary": "影牙兽的大规模袭击——比以往任何一次都更猛烈。",
    "type": "main"
  },
  {
    "id": "PN2",
    "title": "Thalion的诱惑",
    "route": "passive_ntr",
    "chapter": "Thalion的诱惑",
    "summary": "Seraphina独自在心木废墟附近——心情沉重。突然，腐化的紫色雾气从地面渗出，",
    "type": "main"
  },
  {
    "id": "PN3",
    "title": "乔治的支持",
    "route": "passive_ntr",
    "chapter": "被动NTR·第一次缺席",
    "summary": "在一个深夜，Seraphina独自坐在银流河边——",
    "type": "main"
  },
  {
    "id": "PN4",
    "title": "亚莉莎的对比",
    "route": "passive_ntr",
    "chapter": "Thalion的诱惑",
    "summary": "Seraphina从远处看到黎恩和亚莉莎在一起。",
    "type": "main"
  },
  {
    "id": "PN5",
    "title": "寂寞的释放——被动NTR被忽视自慰",
    "route": "passive_ntr",
    "chapter": "Thalion的诱惑",
    "summary": "又一个夜晚。黎恩在火炉边睡着了——书还摊在膝上。",
    "type": "main"
  },
  {
    "id": "PN6",
    "title": "Thalion的强迫摸乳",
    "route": "passive_ntr",
    "chapter": "Thalion的诱惑",
    "summary": "Seraphina坐在心木树下的石阶上——月光透过树叶洒在她的锁骨上。",
    "type": "main"
  },
  {
    "id": "PN7",
    "title": "Thalion的强迫指交",
    "route": "passive_ntr",
    "chapter": "Thalion的诱惑",
    "summary": "银流河畔的草地上。Seraphina仰躺——但她不是自愿躺下的。",
    "type": "nsfw"
  },
  {
    "id": "PN8",
    "title": "甜言蜜语",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "黄昏。银流河的石阶上。Seraphina独自坐着——赤脚浸在河水里，今天黎恩又出去了。",
    "type": "main"
  },
  {
    "id": "PN9",
    "title": "腐蚀的低语",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "深夜。Seraphina睡着了——黎恩的手臂搭在她腰间。",
    "type": "main"
  },
  {
    "id": "PN10",
    "title": "药与酒",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "Thalion这次带了一个银壶。\"精灵族的安神酒——200年前的配方。你很久没尝过了。\"",
    "type": "main"
  },
  {
    "id": "PN11",
    "title": "肉体的展示",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "银流河。黄昏的光在水面上碎成金色。Seraphina照常来到河边——他现在每天黄昏都在。",
    "type": "main"
  },
  {
    "id": "PN12",
    "title": "被迫的手",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "树后。Thalion拦住了准备去河边找黎恩的Seraphina。\n      \"这么多天——我给你孤独的理解、安神的酒、甚至免费的身体展示。该回报了。\"",
    "type": "nsfw"
  },
  {
    "id": "PN13",
    "title": "指交的陷阱",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "Thalion让她仰躺在银流河边的草地上。没有粗暴——他分开她膝盖时动作不快，像是在等她自己决定要不要夹紧。她没有夹紧。不是同意——是一种麻木的\"反正也会发生\"。",
    "type": "main"
  },
  {
    "id": "PN14",
    "title": "被迫的口",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "Thalion靠在古树上。Seraphina在他面前——跪着。不是被按下去的。是她站不住了——指交的高潮刚过几分钟，腿还在软。\n      \"手不是终点。\"",
    "type": "nsfw"
  },
  {
    "id": "PN15",
    "title": "乳间的耻辱",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "木屋。黎恩今晚巡逻——整夜不回来。Thalion推门进来时Seraphina正坐在床边。她没问\"你怎么进来的\"。她已经不问这个问题了。\n      \"今晚——用这里。\"",
    "type": "nsfw"
  },
  {
    "id": "PN16",
    "title": "半推半就",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "Seraphina今天主动去了河边——美其名曰洗脚。她知道他会在——但不打算对自己承认。",
    "type": "nsfw"
  },
  {
    "id": "PN17",
    "title": "无法回头",
    "route": "passive_ntr",
    "chapter": "Thalion的侵蚀",
    "summary": "深夜。黎恩在火炉边看书——时不时转头对她笑一下。他什么都不知道。",
    "type": "main"
  },
  {
    "id": "PN18",
    "title": "堕落之夜",
    "route": "passive_ntr",
    "chapter": "堕落之夜",
    "summary": "心木废墟。Seraphina跪在腐化草地上——白色衣袍凌乱散开。",
    "type": "nsfw"
  },
  {
    "id": "PN19",
    "title": "堕落之夜的细节——Thalion的足交玷污",
    "route": "passive_ntr",
    "chapter": "堕落之夜",
    "summary": "Seraphina独自坐在银流河边的石阶上——赤脚浸在河水中。",
    "type": "nsfw"
  },
  {
    "id": "PN20",
    "title": "耳边的低语",
    "route": "passive_ntr",
    "chapter": "堕落之夜",
    "summary": "深夜。木屋外下着雨。Seraphina独自环抱膝盖坐在床上。",
    "type": "nsfw"
  },
  {
    "id": "PN21",
    "title": "不敢出声——被动NTR近发现",
    "route": "passive_ntr",
    "chapter": "堕落之夜",
    "summary": "黄昏。黎恩提前回来了——比说好的早了三个小时。",
    "type": "main"
  },
  {
    "id": "PN22",
    "title": "再次找上门——主动接受",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "深夜。敲门声。",
    "type": "main"
  },
  {
    "id": "PN23",
    "title": "窗外的影子——被动NTR近发现",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "黎恩从东面森林巡逻回来——比预期晚了两个小时。",
    "type": "main"
  },
  {
    "id": "PN24",
    "title": "趁他睡着——主动隐奸",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "黎恩的呼吸均匀——他睡得很沉。月光从窗户落在他脸上。",
    "type": "nsfw"
  },
  {
    "id": "PN25",
    "title": "半开的门——被动NTR近发现",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "午后。黎恩忘记了巡逻地图——他折返回木屋。门半开着。",
    "type": "main"
  },
  {
    "id": "PN26",
    "title": "主动口交——被动NTR阶段D+",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "深夜。Thalion的木屋中。Seraphina站在他面前——他坐着。",
    "type": "nsfw"
  },
  {
    "id": "PN27",
    "title": "镜中的自己——被动NTR淫荡觉醒",
    "route": "passive_ntr",
    "chapter": "与Thalion的决战",
    "summary": "深夜。黎恩今晚值夜巡逻——不会回来。",
    "type": "main"
  },
  {
    "id": "PN28",
    "title": "野外暴露——被动NTR阶段D+",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "银流河畔——光天化日。阳光洒在河水上，波光粼粼。",
    "type": "nsfw"
  },
  {
    "id": "PN29",
    "title": "主动索求——被动NTR淫荡升级",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "黎恩坐在火炉边——翻着一本精灵古籍。木门推开——Seraphina走进来。",
    "type": "main"
  },
  {
    "id": "PN30",
    "title": "主动邀约——被动NTR阶段D+终点",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "白天。一只紫色蝴蝶落在Seraphina窗台——Thalion的传讯方式。",
    "type": "nsfw"
  },
  {
    "id": "PN31",
    "title": "故意遗留——被动NTR淫荡巅峰",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "连续三天——黎恩在木屋中发现不属于这里的东西。",
    "type": "main"
  },
  {
    "id": "PN32",
    "title": "Thalion的伪装——被动NTR桥接",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "黄昏。营地边缘的篝火旁——全体同伴围坐讨论腐化扩散的最新数据。",
    "type": "nsfw"
  },
  {
    "id": "PN33",
    "title": "桌下之手——对Thalion隐奸手交",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "长桌。黎恩在和亚莉莎讨论巡逻路线。劳拉在看地图。菲在打瞌睡。",
    "type": "nsfw"
  },
  {
    "id": "PN34",
    "title": "桌面下的脚——被动NTR多线操控",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "战略会议。长桌周围坐满了同伴。",
    "type": "nsfw"
  },
  {
    "id": "PN35",
    "title": "桌下之口——对Thalion隐奸口交",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "同样的长桌。这次黎恩在主持——站在桌前讲解净化方案。\n      \"西面森林的腐化浓度下降了百分之四十——\"",
    "type": "nsfw"
  },
  {
    "id": "PN36",
    "title": "隐乳交——对Thalion隐蔽乳交",
    "route": "passive_ntr",
    "chapter": "彻底破碎",
    "summary": "黎恩出门前在她额头吻了一下。\"今天巡逻可能要很晚。你好好休息。\"",
    "type": "nsfw"
  },
  {
    "id": "PN37",
    "title": "与Thalion的最终战斗",
    "route": "passive_ntr",
    "chapter": "与Thalion的决战",
    "summary": "心木树下。Thalion站在金色叶片下——他的紫色眼睛中已经没有疯狂的火焰。",
    "type": "main"
  },
  {
    "id": "C1",
    "title": "玲的裸足——小恶魔的秘密",
    "route": "side",
    "chapter": "第一次见证",
    "summary": "篝火边只剩两人。玲歪头看着黎恩：\"你一直在看我的腿。\"她慢慢卷下及膝袜——露出常年不见光的瓷白裸足。脚趾在月光下动了动。\"你是第一个。\"",
    "type": "nsfw"
  },
  {
    "id": "C2",
    "title": "亚莉莎的蕾丝——傲娇千金的告白",
    "route": "side",
    "chapter": "第一次见证",
    "summary": "亚莉莎把黎恩拉到营地外树下——脸红到耳根。\"我注意到你在篝火边看我的丝袜。我不是要跟Seraphina抢——只是——\"",
    "type": "nsfw"
  },
  {
    "id": "C3",
    "title": "菲的裸足——猎兵的诚意",
    "route": "side",
    "chapter": "第一次见证",
    "summary": "训练后菲坐在石头上脱黑色过膝袜——早就知道黎恩在看。抬起赤裸的脚——脚底有训练留下的薄茧，脚背上有几道旧伤疤。\"不像Seraphina那么好看。但是——很诚实。\"\n      \"我不用袜子。碍事。\"赤裸的脚心直接贴住皮肤——薄茧制造的摩擦比",
    "type": "nsfw"
  },
  {
    "id": "C4",
    "title": "劳拉的白袜——骑士的荣誉",
    "route": "side",
    "chapter": "第一次共享",
    "summary": "剑术训练后劳拉叫住黎恩——坐姿笔直如剑。\"作为亚尔赛德家的继承人，我应当对此感到羞耻。但我认为——这不羞耻。\"",
    "type": "nsfw"
  },
  {
    "id": "C5",
    "title": "艾玛的吊带袜——魔女的私授课程",
    "route": "side",
    "chapter": "第一次共享",
    "summary": "深夜艾玛帐篷亮着灯。\"黎恩同学——来得正好。我在研究男性足部神经反射与性兴奋的关联性。\"她合上书推了推眼镜——\"请配合我的实证研究。\"",
    "type": "nsfw"
  },
  {
    "id": "C6",
    "title": "亚尔缇娜的任务——黑兔的\"逻辑性服务\"",
    "route": "side",
    "chapter": "第一次共享",
    "summary": "亚尔缇娜无声出现在黎恩面前——面无表情如在汇报任务。\"根据观察，多位女性成员与你进行足交后你的战斗表现有显著变化。逻辑结论：我也应当提供此类服务。不是基于情感——是基于团队协作的需要。\"",
    "type": "nsfw"
  },
  {
    "id": "G1",
    "title": "狩猎竞赛——影牙兽的试炼",
    "route": "general",
    "chapter": "森林的庆典",
    "summary": "影牙兽在森林边缘频繁出没，威胁到附近的村庄。",
    "type": "main"
  },
  {
    "id": "G2",
    "title": "剑术训练——太刀与圣光",
    "route": "general",
    "chapter": "温泉与誓言",
    "summary": "劳拉看到黎恩的太刀和Seraphina的圣光后，",
    "type": "main"
  },
  {
    "id": "G3",
    "title": "密林探索——未知的区域",
    "route": "general",
    "chapter": "温泉与誓言",
    "summary": "Eldoria森林中有一片从未被探索的区域——",
    "type": "main"
  },
  {
    "id": "G4",
    "title": "篝火故事会——每个人的过去",
    "route": "general",
    "chapter": "森林的庆典",
    "summary": "林间空地的篝火噼啪作响，火星飞向星空。",
    "type": "main"
  },
  {
    "id": "G5",
    "title": "雷恩的晨间仪式——骑士的誓言",
    "route": "general",
    "chapter": "各方来客",
    "summary": "清晨第一缕阳光穿过树冠。雷恩独自面对东方——右手放在胸口，闭眼，嘴唇微动。",
    "type": "main"
  },
  {
    "id": "G6",
    "title": "凯尔的精灵语课堂——文化的碰撞",
    "route": "general",
    "chapter": "各方来客",
    "summary": "凯尔正在尝试翻译精灵符文——但他的精灵语发音让林间的鸟儿都沉默了。",
    "type": "nsfw"
  },
  {
    "id": "G7",
    "title": "艾德里安的拍卖会——没落贵族的遗产",
    "route": "general",
    "chapter": "各方来客",
    "summary": "艾德里安突然宣布举办\"艾斯特雷亚家族最后的拍卖会\"——打开一个破旧皮箱。",
    "type": "main"
  },
  {
    "id": "W1",
    "title": "影牙兽大规模袭击",
    "route": "world",
    "chapter": "影牙兽的威胁",
    "summary": "Eldoria森林边缘突然涌出大量影牙兽——数量是平时的三倍以上。",
    "type": "main"
  },
  {
    "id": "W2",
    "title": "心木树的净化仪式",
    "route": "world",
    "chapter": "净化仪式",
    "summary": "心木树——Eldoria森林的核心。它的金色叶片已经有一半变成了深紫色。",
    "type": "nsfw"
  },
  {
    "id": "W3",
    "title": "银流河的净化与恢复",
    "route": "world",
    "chapter": "净化仪式",
    "summary": "银流河——曾经被腐化染成暗紫色的河水，在净化仪式后开始恢复银色。",
    "type": "main"
  },
  {
    "id": "W4",
    "title": "腐化区域的意外扩张",
    "route": "world",
    "chapter": "被动NTR·第一次缺席",
    "summary": "毫无预警地——Eldoria森林的一片区域突然被腐化吞没。",
    "type": "main"
  },
  {
    "id": "W5",
    "title": "古老先灵的第二次对话",
    "route": "world",
    "chapter": "古老先灵的低语",
    "summary": "在心木树下——古老先灵从金色叶片中显形。",
    "type": "nsfw"
  },
  {
    "id": "W6",
    "title": "\"森林意志\"的反应",
    "route": "world",
    "chapter": "Thalion的诱惑",
    "summary": "夜晚，整个Eldoria森林突然\"醒\"了。",
    "type": "main"
  },
  {
    "id": "W7",
    "title": "VII班同伴的\"日常互动\"",
    "route": "world",
    "chapter": "各方来客",
    "summary": "VII班同伴在林间空地进行各自的日常——这是旅途中难得的平静时刻。",
    "type": "main"
  },
  {
    "id": "W8",
    "title": "\"雾帷边缘\"的异象",
    "route": "world",
    "chapter": "新的开始",
    "summary": "Eldoria森林的边缘——\"雾帷\"——是分隔Eldoria与外部世界的银色迷雾。\n      200年来，雾帷从未变化——它保护了森林，也困住了Seraphina。",
    "type": "main"
  },
  {
    "id": "H1",
    "title": "精灵王国的记忆",
    "route": "hidden",
    "chapter": "心木废墟的秘密",
    "summary": "满月之夜——低语林地的银白色树木在月光下发出微弱的荧光。",
    "type": "nsfw"
  },
  {
    "id": "H2",
    "title": "鬼之力与圣光完全共鸣",
    "route": "hidden",
    "chapter": "古老的启示",
    "summary": "在最激烈的战斗中——当黎恩的鬼之力和Seraphina的圣光同时达到峰值，",
    "type": "nsfw"
  },
  {
    "id": "H3",
    "title": "腐化低语者的\"真相\"",
    "route": "hidden",
    "chapter": "边界与试探",
    "summary": "在与腐化低语者多次互动后——Seraphina突然在战斗中停下了。",
    "type": "main"
  },
  {
    "id": "H4",
    "title": "\"如果\"——另一个结局的暗示",
    "route": "hidden",
    "chapter": "终局",
    "summary": "终局前的夜晚。黎恩独自在银流河边——月光照在银色水面上。",
    "type": "nsfw"
  },
  {
    "id": "H5",
    "title": "VII班同伴的\"秘密对话\"",
    "route": "hidden",
    "chapter": "新的开始",
    "summary": "深夜——VII班同伴们以为黎恩已经睡了。",
    "type": "main"
  },
  {
    "id": "R1",
    "title": "鬼之力的低语——失控边缘的独白",
    "route": "rean",
    "chapter": "影牙兽的威胁",
    "summary": "深夜，黎恩独自坐在林间空地的边缘。右手手背的刻印在隐隐发光——",
    "type": "main"
  },
  {
    "id": "R2",
    "title": "太刀与八叶——黎恩的晨间修炼",
    "route": "rean",
    "chapter": "纯爱·守护者契约",
    "summary": "清晨的薄雾中，黎恩独自在林间空地练习八叶一刀流。",
    "type": "nsfw"
  },
  {
    "id": "R3",
    "title": "来自帝国的信——VII班的羁绊",
    "route": "rean",
    "chapter": "VII班的到来",
    "summary": "亚莉莎收到了一封来自帝国的信——通过某种古老的精灵传送魔法。",
    "type": "main"
  },
  {
    "id": "R4",
    "title": "灰之骑神的记忆——瓦利玛的低语",
    "route": "rean",
    "chapter": "古老的启示",
    "summary": "在精灵王国的一处古老遗迹中，黎恩发现了一个巨大的精灵石——",
    "type": "nsfw"
  },
  {
    "id": "R5",
    "title": "独占欲——黎恩的\"重新占有\"",
    "route": "rean",
    "chapter": "新的开始",
    "summary": "NTRS的核心仪式——\"重新占有\"。",
    "type": "main"
  },
  {
    "id": "R6",
    "title": "黎恩的第一次——从\"守护者\"到\"男人\"",
    "route": "rean",
    "chapter": "净化仪式",
    "summary": "在心木树下——精灵族最神圣的地方。",
    "type": "nsfw"
  },
  {
    "id": "R7",
    "title": "嫉妒之火——黎恩的黑暗面",
    "route": "rean",
    "chapter": "与Thalion的决战",
    "summary": "黎恩在森林中寻找Seraphina——然后他找到了。",
    "type": "main"
  },
  {
    "id": "R8",
    "title": "夜色中的契约——黎恩与Seraphina的私密仪式",
    "route": "rean",
    "chapter": "终极抉择",
    "summary": "深夜——林间空地中只有月光。",
    "type": "main"
  },
];

const CHAPTERS = [
  {
    "num": 1,
    "name": "林间空地的苏醒",
    "phase": "prologue",
    "count": 1
  },
  {
    "num": 2,
    "name": "影牙兽的威胁",
    "phase": "prologue",
    "count": 3
  },
  {
    "num": 3,
    "name": "心木废墟的秘密",
    "phase": "prologue",
    "count": 3
  },
  {
    "num": 4,
    "name": "VII班的到来",
    "phase": "prologue",
    "count": 4
  },
  {
    "num": 5,
    "name": "森林的庆典",
    "phase": "prologue",
    "count": 3
  },
  {
    "num": 6,
    "name": "古老先灵的低语",
    "phase": "prologue",
    "count": 2
  },
  {
    "num": 7,
    "name": "各方来客",
    "phase": "prologue",
    "count": 10
  },
  {
    "num": 8,
    "name": "路线分化",
    "phase": "prologue",
    "count": 4
  },
  {
    "num": 9,
    "name": "纯爱·守护者契约",
    "phase": "pure",
    "count": 6
  },
  {
    "num": 10,
    "name": "温泉与誓言",
    "phase": "pure",
    "count": 10
  },
  {
    "num": 11,
    "name": "古老的启示",
    "phase": "pure",
    "count": 7
  },
  {
    "num": 12,
    "name": "边界与试探",
    "phase": "ntrs",
    "count": 9
  },
  {
    "num": 13,
    "name": "第一次见证",
    "phase": "ntrs",
    "count": 17
  },
  {
    "num": 14,
    "name": "第一次共享",
    "phase": "ntrs",
    "count": 18
  },
  {
    "num": 15,
    "name": "多人共享之夜",
    "phase": "ntrs",
    "count": 19
  },
  {
    "num": 16,
    "name": "被动NTR·第一次缺席",
    "phase": "passive",
    "count": 3
  },
  {
    "num": 17,
    "name": "Thalion的诱惑",
    "phase": "passive",
    "count": 6
  },
  {
    "num": 18,
    "name": "堕落之夜",
    "phase": "passive",
    "count": 4
  },
  {
    "num": 19,
    "name": "彻底破碎",
    "phase": "passive",
    "count": 14
  },
  {
    "num": 20,
    "name": "净化仪式",
    "phase": "passive",
    "count": 3
  },
  {
    "num": 21,
    "name": "与Thalion的决战",
    "phase": "passive",
    "count": 3
  },
  {
    "num": 22,
    "name": "终极抉择",
    "phase": "finale",
    "count": 3
  },
  {
    "num": 23,
    "name": "终局",
    "phase": "finale",
    "count": 3
  },
  {
    "num": 24,
    "name": "新的开始",
    "phase": "finale",
    "count": 3
  },
  {
    "num": 170,
    "name": "Thalion的侵蚀",
    "phase": "finale",
    "count": 10
  },
];

// 自动生成的登场顺序（按事件ID首次出现推断）
const DEBUTS = [
  {
    "name": "黎恩",
    "event": "E01",
    "color": "#4facfe",
    "avatar": "黎"
  },
  {
    "name": "Seraphina",
    "event": "E01",
    "color": "#f093fb",
    "avatar": "S"
  },
  {
    "name": "Thalion",
    "event": "PN2",
    "color": "#a18cd1",
    "avatar": "T"
  },
  {
    "name": "乔治",
    "event": "PN3",
    "color": "#43e97b",
    "avatar": "乔"
  },
  {
    "name": "亚莉莎",
    "event": "PN4",
    "color": "#fa709a",
    "avatar": "亚"
  },
  {
    "name": "劳拉",
    "event": "N32",
    "color": "#89f7fe",
    "avatar": "劳"
  },
  {
    "name": "菲",
    "event": "G4",
    "color": "#30cfd0",
    "avatar": "菲"
  },
  {
    "name": "艾玛",
    "event": "G4",
    "color": "#f5576c",
    "avatar": "艾"
  },
  {
    "name": "爱丽榭",
    "event": "N33",
    "color": "#ff9a9e",
    "avatar": "爱"
  },
];
