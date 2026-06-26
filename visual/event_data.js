// 自动生成于: 2026-06-26T13:18:28.077034
// 数据源: docs/05_事件系统.md
// 生成器: scripts/generate_event_browser.py

const EVENTS = [
  {
    "id": "E1",
    "title": "林间空地的苏醒",
    "route": "prologue",
    "chapter": "林间空地的苏醒",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E2",
    "title": "第一次与影牙兽战斗",
    "route": "prologue",
    "chapter": "影牙兽的威胁",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E3",
    "title": "心木废墟",
    "route": "prologue",
    "chapter": "影牙兽的威胁",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E4",
    "title": "低语林地的幻影",
    "route": "prologue",
    "chapter": "心木废墟的秘密",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E5",
    "title": "VII班同伴的到达（亚莉莎）",
    "route": "prologue",
    "chapter": "VII班的到来",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E6",
    "title": "VII班同伴的到达（劳拉与乔治）",
    "route": "prologue",
    "chapter": "VII班的到来",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E7",
    "title": "VII班同伴的到达（艾玛与菲）",
    "route": "prologue",
    "chapter": "VII班的到来",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E8",
    "title": "森林的庆典（第一晚）",
    "route": "prologue",
    "chapter": "森林的庆典",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E9",
    "title": "古老先灵的低语（正式登场）",
    "route": "prologue",
    "chapter": "古老先灵的低语",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E10",
    "title": "黑兔的观察（亚尔缇娜登场）",
    "route": "prologue",
    "chapter": "各方来客",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E11",
    "title": "流浪商人的来访（艾德里安登场）",
    "route": "prologue",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E12",
    "title": "圣殿骑士的踪迹（雷恩登场）",
    "route": "prologue",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E13",
    "title": "学者的研究（凯尔登场）",
    "route": "prologue",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E14",
    "title": "义妹的到来（爱丽榭登场）",
    "route": "prologue",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "E15",
    "title": "杀戮之天使（玲登场）",
    "route": "prologue",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P1",
    "title": "深夜的火炉边对话（第一次深度情感交流）",
    "route": "pure",
    "chapter": "影牙兽的威胁",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P2",
    "title": "鬼之力失控后的安抚（关键连接事件）",
    "route": "pure",
    "chapter": "影牙兽的威胁",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P3",
    "title": "银流河畔的告白（第一次约会）",
    "route": "pure",
    "chapter": "心木废墟的秘密",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P4",
    "title": "守护者的契约",
    "route": "pure",
    "chapter": "VII班的到来",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P5",
    "title": "VII班的\"正式介绍\"——Seraphina作为黎恩的恋人",
    "route": "pure",
    "chapter": "VII班的到来",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P6",
    "title": "心木废墟净化仪式前置准备",
    "route": "pure",
    "chapter": "古老先灵的低语",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P7",
    "title": "与Thalion的第一次正面战斗",
    "route": "pure",
    "chapter": "各方来客",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P8",
    "title": "温泉事件（纯爱版本）",
    "route": "pure",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P9",
    "title": "守护夜——并肩作战到黎明",
    "route": "pure",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P10",
    "title": "古老先灵的启示——森林意志与黎恩的作用",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P11",
    "title": "终极战斗准备——与Thalion的最终对质前夕",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P12",
    "title": "终局抉择（纯爱版本）",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "",
    "type": "main"
  },
  {
    "id": "P13",
    "title": "契约之夜——初次的结合",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P14",
    "title": "温泉的清晨（纯爱NSFW）",
    "route": "pure",
    "chapter": "纯爱·守护者契约",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P15",
    "title": "鬼之圣光交融（纯爱NSFW）",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P16",
    "title": "足下的誓言（纯爱NSFW）",
    "route": "pure",
    "chapter": "温泉与誓言",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P17",
    "title": "俯首的骑士（纯爱NSFW）",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P18",
    "title": "巡逻后的夜晚（纯爱NSFW）",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P19",
    "title": "初次的唇——口交入门",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P20",
    "title": "圣光之谷——乳交",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P21",
    "title": "大腿之间——腿交",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "P22",
    "title": "银流河畔的初次手交",
    "route": "pure",
    "chapter": "古老的启示",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N01",
    "title": "坦白之夜——路线分支点",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N02",
    "title": "边界协商",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N03",
    "title": "迷路的旅人——陌生人仅注视",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N04",
    "title": "月光下的自慰——黑丝与星图",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N05",
    "title": "坐骑上的意外——颠簸的缰绳",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N06",
    "title": "足部护理——银流河的温柔",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N07",
    "title": "窗边口交——未知的观众",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N08",
    "title": "篝火边的雷恩",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N09",
    "title": "装睡——角落的骑士",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N10",
    "title": "雷恩的初访——正义的拒绝",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N11",
    "title": "雷恩的同意——从拒绝到触碰",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N12",
    "title": "艾德里安的察觉——从容的入局者",
    "route": "ntrs",
    "chapter": "边界与试探",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N13",
    "title": "乔治的注视——发现吃醋有趣",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N14",
    "title": "凯尔的告白——真诚暗恋",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N15",
    "title": "第一次共享——腐化低语者",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N16",
    "title": "丝袜与内衣——故意的展示",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N17",
    "title": "挑逗的萌芽",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N18",
    "title": "扣穴的代价",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N19",
    "title": "银色的探索——指交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N20",
    "title": "乔治的逃跑——亲密的陷阱",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N21",
    "title": "乔治的同意——笨拙的第一课",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N22",
    "title": "艾德里安的指尖——从容的探索",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N23",
    "title": "圣光之泉——口交受け",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N24",
    "title": "凯尔的第一次——黑丝与滚烫的手心",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N25",
    "title": "凯尔的臣服——足交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N26",
    "title": "乔治的回礼——从按摩到足交",
    "route": "ntrs",
    "chapter": "第一次见证",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N27",
    "title": "玲的口交游戏",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N28",
    "title": "玲的裸足——小恶魔的秘密",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N29",
    "title": "桌下之手——隐奸手交",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N30",
    "title": "菲的裸足——猎兵的诚意",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N31",
    "title": "桌下之口——隐奸口交",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N32",
    "title": "艾玛的手交实证研究",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N33",
    "title": "树后的秘密——第一次给别人打飞机",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N34",
    "title": "第一次双人共享——两只手同时",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N35",
    "title": "艾德里安的扑克——乳的初次",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N36",
    "title": "酒后扑克——第一次给别人口交",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N37",
    "title": "凯尔的乳交——学术实践",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N38",
    "title": "酒后之夜——黎恩的指使",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N39",
    "title": "凯尔的再战——从乳到口",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N40",
    "title": "黎恩的安排——让她和乔治独处",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N41",
    "title": "凯尔的山洞——采样与被困",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N42",
    "title": "装睡的代价——黎恩的恶作剧",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N43",
    "title": "全身被舔——中途离场的眼泪",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N44",
    "title": "不准再丢下我",
    "route": "ntrs",
    "chapter": "第一次共享",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N45",
    "title": "乔治的唇——意外的美味",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N46",
    "title": "被干软之后的提问",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N47",
    "title": "白丝与初吻——雷恩的沦陷",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N48",
    "title": "第二次共享——多低语者强迫口交手交",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N49",
    "title": "温柔的疗愈——她选了凯尔",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N50",
    "title": "凯尔的清晨——黑丝与第一次插入",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N51",
    "title": "翌日——两个人",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N52",
    "title": "走廊的绯红——凯尔不敢看她",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N53",
    "title": "犹豫——不要，好痛",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N54",
    "title": "桌下——吞下去的选择",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N55",
    "title": "黎恩的提议——再给他一次机会",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N56",
    "title": "早晨的喂奶——不痛了",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N57",
    "title": "雷恩的稳重，她选的第二次",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N58",
    "title": "弯腰的弧度——乔治的笔掉了",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N59",
    "title": "开裆连裤袜——弯腰的盛宴",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N60",
    "title": "试衣——镜前的另一个人",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N61",
    "title": "图纸与门缝——她设计的隐奸",
    "route": "ntrs",
    "chapter": "多人共享之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N62",
    "title": "打开的门",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N63",
    "title": "劳拉的直率——月光下的乳交",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N64",
    "title": "姐妹的足——爱丽榭与菲娜的联合足交",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N65",
    "title": "艾德里安的从容——浪子的本番",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N66",
    "title": "重新填满——谁的更爽",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N67",
    "title": "亚莉莎的蕾丝——傲娇的告白",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N68",
    "title": "她的游戏——黎恩也参与",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N69",
    "title": "劳拉的白袜——鬼之力的释放",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N70",
    "title": "艾玛的传送门——远程口交与足交",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N71",
    "title": "草药咖啡——拘束与内射",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N72",
    "title": "菲的早晨——沉默的口交",
    "route": "ntrs",
    "chapter": "被动NTR·第一次缺席",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N73",
    "title": "醉诱——扶她回屋之后",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N74",
    "title": "温泉——菲娜的羞辱游戏",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N75",
    "title": "密林巡逻——树后内射",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N76",
    "title": "菲的早晨——口交叫醒服务",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N77",
    "title": "镜湖——亡妻的幻影",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N78",
    "title": "镜湖倒影——幻影中的内射",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N79",
    "title": "胜利庆典后的3P",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N80",
    "title": "温泉晕厥——事后告知",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N81",
    "title": "艾玛的吊带袜——魔女的私授课程",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N82",
    "title": "亚莉莎的换装——催情熏香中的傲娇本番",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N83",
    "title": "野外失控——花田轮奸",
    "route": "ntrs",
    "chapter": "Thalion的诱惑",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N84",
    "title": "亚尔缇娜的任务——逻辑性服务",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N85",
    "title": "欲望之镜——镜湖倒影",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N86",
    "title": "玲的游戏本番",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N87",
    "title": "主动手交——服务第三者",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N88",
    "title": "艾德里安的舌——反向服务",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N89",
    "title": "雷恩的克制——足交的圣殿骑士",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N90",
    "title": "劳拉的骑士本番",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N91",
    "title": "雷恩的跪礼——圣殿骑士的口",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N92",
    "title": "第一次自己决定",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N93",
    "title": "凯尔的独白——窗外的归来",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N94",
    "title": "凯尔的观摩——黎恩的归来本番",
    "route": "ntrs",
    "chapter": "堕落之夜",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N95",
    "title": "主动口交——老手的从容",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N96",
    "title": "桌下之手——隐奸手交",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N97",
    "title": "桌下之口——隐奸口交",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N98",
    "title": "凯尔的邀请——河边的先斩后奏",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N99",
    "title": "乔治的测试——导力震动棒",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N100",
    "title": "腐化迷雾——半梦半醒的交叉",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N101",
    "title": "黑暗中的乳交——她不让开灯",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N102",
    "title": "催情茶——两个人的轮奸",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N103",
    "title": "低语者的轮奸——D阶段极限",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N104",
    "title": "洗干净的回归",
    "route": "ntrs",
    "chapter": "彻底破碎",
    "summary": "",
    "type": "main"
  },
  {
    "id": "N105",
    "title": "她的情书——独属于两人的完整性爱",
    "route": "ntrs",
    "chapter": "净化仪式",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "N106",
    "title": "终局抉择",
    "route": "ntrs",
    "chapter": "净化仪式",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN1",
    "title": "第一次缺席",
    "route": "passive_ntr",
    "chapter": "终极抉择",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN2",
    "title": "Thalion的诱惑（圣光被压制——无法反抗）",
    "route": "passive_ntr",
    "chapter": "终极抉择",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN3",
    "title": "乔治的支持（被误解的关心）",
    "route": "passive_ntr",
    "chapter": "终极抉择",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN4",
    "title": "亚莉莎的对比（\"她一直在他身边\"）",
    "route": "passive_ntr",
    "chapter": "终极抉择",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN5",
    "title": "寂寞的释放——被动NTR被忽视自慰",
    "route": "passive_ntr",
    "chapter": "终极抉择",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN6",
    "title": "Thalion的强迫摸乳",
    "route": "passive_ntr",
    "chapter": "终局",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN7",
    "title": "Thalion的强迫指交",
    "route": "passive_ntr",
    "chapter": "终局",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN8",
    "title": "甜言蜜语",
    "route": "passive_ntr",
    "chapter": "终局",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN9",
    "title": "腐蚀的低语",
    "route": "passive_ntr",
    "chapter": "终局",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN10",
    "title": "药与酒",
    "route": "passive_ntr",
    "chapter": "终局",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN11",
    "title": "肉体的展示",
    "route": "passive_ntr",
    "chapter": "终局",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN12",
    "title": "被迫的手",
    "route": "passive_ntr",
    "chapter": "新的开始",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN13",
    "title": "指交的陷阱",
    "route": "passive_ntr",
    "chapter": "新的开始",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN14",
    "title": "被迫的口",
    "route": "passive_ntr",
    "chapter": "新的开始",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN15",
    "title": "乳间的耻辱",
    "route": "passive_ntr",
    "chapter": "新的开始",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN16",
    "title": "半推半就",
    "route": "passive_ntr",
    "chapter": "新的开始",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN17",
    "title": "无法回头",
    "route": "passive_ntr",
    "chapter": "新的开始",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN18",
    "title": "堕落之夜（被动NTR的最低点——Thalion插入）",
    "route": "passive_ntr",
    "chapter": "第25章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN19",
    "title": "堕落之夜的细节——Thalion的足交玷污",
    "route": "passive_ntr",
    "chapter": "第25章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN20",
    "title": "耳边的低语",
    "route": "passive_ntr",
    "chapter": "第25章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN21",
    "title": "不敢出声——被动NTR近发现",
    "route": "passive_ntr",
    "chapter": "第25章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN22",
    "title": "再次找上门——主动接受",
    "route": "passive_ntr",
    "chapter": "第26章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN23",
    "title": "窗外的影子——被动NTR近发现",
    "route": "passive_ntr",
    "chapter": "第26章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN24",
    "title": "趁他睡着——主动隐奸",
    "route": "passive_ntr",
    "chapter": "第26章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN25",
    "title": "半开的门——被动NTR近发现",
    "route": "passive_ntr",
    "chapter": "第26章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN26",
    "title": "主动口交——被动NTR阶段D+",
    "route": "passive_ntr",
    "chapter": "第27章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN27",
    "title": "镜中的自己——被动NTR淫荡觉醒",
    "route": "passive_ntr",
    "chapter": "第27章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN28",
    "title": "野外暴露——被动NTR阶段D+",
    "route": "passive_ntr",
    "chapter": "第27章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN29",
    "title": "主动索求——被动NTR淫荡升级",
    "route": "passive_ntr",
    "chapter": "第27章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN30",
    "title": "主动邀约——被动NTR阶段D+终点",
    "route": "passive_ntr",
    "chapter": "第28章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN31",
    "title": "故意遗留——被动NTR淫荡巅峰",
    "route": "passive_ntr",
    "chapter": "第28章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN32",
    "title": "Thalion的伪装——被动NTR桥接",
    "route": "passive_ntr",
    "chapter": "第28章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "PN33",
    "title": "桌下之手（被动NTR）——对Thalion隐奸手交",
    "route": "passive_ntr",
    "chapter": "第28章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN34",
    "title": "桌面下的脚——被动NTR多线操控",
    "route": "passive_ntr",
    "chapter": "第29章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN35",
    "title": "桌下之口（被动NTR）——对Thalion隐奸口交",
    "route": "passive_ntr",
    "chapter": "第29章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN36",
    "title": "隐乳交（被动NTR）——对Thalion隐蔽乳交",
    "route": "passive_ntr",
    "chapter": "第29章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "PN37",
    "title": "与Thalion的最终战斗（被动NTR版本）",
    "route": "passive_ntr",
    "chapter": "第30章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W1",
    "title": "影牙兽大规模袭击",
    "route": "world",
    "chapter": "林间空地的苏醒",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W2",
    "title": "心木树的净化仪式",
    "route": "world",
    "chapter": "心木废墟的秘密",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W3",
    "title": "银流河的净化与恢复",
    "route": "world",
    "chapter": "森林的庆典",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W4",
    "title": "腐化区域的意外扩张",
    "route": "world",
    "chapter": "古老先灵的低语",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W5",
    "title": "古老先灵的第二次对话",
    "route": "world",
    "chapter": "各方来客",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W6",
    "title": "\"森林意志\"的反应",
    "route": "world",
    "chapter": "路线分化",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W7",
    "title": "VII班同伴的\"日常互动\"",
    "route": "world",
    "chapter": "纯爱·守护者契约",
    "summary": "",
    "type": "main"
  },
  {
    "id": "W8",
    "title": "\"雾帷边缘\"的异象",
    "route": "world",
    "chapter": "温泉与誓言",
    "summary": "",
    "type": "main"
  },
  {
    "id": "H1",
    "title": "精灵王国的记忆",
    "route": "hidden",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "H2",
    "title": "鬼之力与圣光完全共鸣",
    "route": "hidden",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "H3",
    "title": "\"如果\"——另一个结局的暗示",
    "route": "hidden",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "H4",
    "title": "VII班同伴的\"秘密对话\"",
    "route": "hidden",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G1",
    "title": "狩猎竞赛——影牙兽的试炼",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G2",
    "title": "剑术训练——太刀与圣光",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G3",
    "title": "密林探索——未知的区域",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G4",
    "title": "篝火故事会——每个人的过去",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G5",
    "title": "雷恩的晨间仪式——骑士的誓言",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G6",
    "title": "凯尔的精灵语课堂——文化的碰撞",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "G7",
    "title": "艾德里安的拍卖会——没落贵族的遗产",
    "route": "general",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "R1",
    "title": "鬼之力的低语——失控边缘的独白",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "R2",
    "title": "太刀与八叶——黎恩的晨间修炼",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "R3",
    "title": "来自帝国的信——VII班的羁绊",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "R4",
    "title": "灰之骑神的记忆——瓦利玛的低语",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "R5",
    "title": "独占欲——黎恩的\"重新占有\"",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "R6",
    "title": "黎恩的第一次——从\"守护者\"到\"男人\"",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "nsfw"
  },
  {
    "id": "R7",
    "title": "嫉妒之火——黎恩的黑暗面",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
  {
    "id": "R8",
    "title": "夜色中的契约——黎恩与Seraphina的私密仪式",
    "route": "rean",
    "chapter": "第99章",
    "summary": "",
    "type": "main"
  },
];

const CHAPTERS = [
  {
    "num": 1,
    "name": "林间空地的苏醒",
    "phase": "prologue",
    "count": 2
  },
  {
    "num": 2,
    "name": "影牙兽的威胁",
    "phase": "prologue",
    "count": 4
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
    "count": 5
  },
  {
    "num": 5,
    "name": "森林的庆典",
    "phase": "prologue",
    "count": 2
  },
  {
    "num": 6,
    "name": "古老先灵的低语",
    "phase": "prologue",
    "count": 3
  },
  {
    "num": 7,
    "name": "各方来客",
    "phase": "prologue",
    "count": 3
  },
  {
    "num": 8,
    "name": "路线分化",
    "phase": "prologue",
    "count": 8
  },
  {
    "num": 9,
    "name": "纯爱·守护者契约",
    "phase": "pure",
    "count": 5
  },
  {
    "num": 10,
    "name": "温泉与誓言",
    "phase": "pure",
    "count": 4
  },
  {
    "num": 11,
    "name": "古老的启示",
    "phase": "pure",
    "count": 6
  },
  {
    "num": 12,
    "name": "边界与试探",
    "phase": "ntrs",
    "count": 12
  },
  {
    "num": 13,
    "name": "第一次见证",
    "phase": "ntrs",
    "count": 14
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
    "count": 17
  },
  {
    "num": 16,
    "name": "被动NTR·第一次缺席",
    "phase": "passive",
    "count": 11
  },
  {
    "num": 17,
    "name": "Thalion的诱惑",
    "phase": "passive",
    "count": 11
  },
  {
    "num": 18,
    "name": "堕落之夜",
    "phase": "passive",
    "count": 11
  },
  {
    "num": 19,
    "name": "彻底破碎",
    "phase": "passive",
    "count": 10
  },
  {
    "num": 20,
    "name": "净化仪式",
    "phase": "passive",
    "count": 2
  },
  {
    "num": 22,
    "name": "终极抉择",
    "phase": "finale",
    "count": 5
  },
  {
    "num": 23,
    "name": "终局",
    "phase": "finale",
    "count": 6
  },
  {
    "num": 24,
    "name": "新的开始",
    "phase": "finale",
    "count": 6
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
