#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/scan_viridia_diseases.py — 第二部（维里迪亚王国篇）专属文风、词汇与病灶雷达

与第一部（scripts/scan_narrative_diseases.py）物理隔离。
专门防御：
1. [古风/仙侠/修真黑名单]：碎银、官道、演兵场、路引、四合院、中军大帐、千斤闸、剑意、身法、划拳、品茶、烽火等。
2. [中式传统度量衡]：斤、两、尺、寸、丈、里（如“三寸”、“半尺”、“数十里”、“重达千斤”）。
3. [跨体系残留字段]：非白名单字段、未定义系统参数。
4. [翻译腔长定语堆叠与括号英文]：如“高石围墙方庭合院式高级驿舍（Courtyard Coaching Inn）”。
5. [章节元数据字段规范]：主要人物字段必须存在，必须严格符合 9 字段白名单。
"""

import os
import sys
import glob
import re
import argparse

# 导入第二部配置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
try:
    import story2_config as config
except ImportError:
    from scripts2 import story2_config as config

try:
    from scan_classical_inversions import check_line_inversions
except ImportError:
    from scripts2.scan_classical_inversions import check_line_inversions

# ═══════════════════════════════════════════════════════════
# 黑名单词库定义
# ═══════════════════════════════════════════════════════════

# 1. 古风/武侠/仙侠/东方修真黑名单
WUXIA_FORBIDDEN_WORDS = [
    '碎银', '碎银粒', '散碎银两', '粗银块', '粗银条', '粗银', '一两银', '两银', '铜板', '铜钱', '文钱', '银票', '宝钞', '飞钱', '盘缠', '细软',
    '火耗', '耗羡', '铸造火耗', '贴水', '重铸贴水', '折算贴水', '石券', '大石券', '拱券', '券顶',
    '税吏', '恶吏', '酷吏',
    '液压', '铣削', '铣制', '进刀角度', '公差', '气焊',
    '高碳钢', '低碳钢', '高锡青铜', '铍青铜', '高抗冲', '屈服强度', '主轴模数', '齿轮模数', '分度圆', '气动换向阀', '碱性中和', '引力坍缩', '引力迟滞力场',
    '老子', '老夫', '小崽子', '吃不住猛水', '撑门石', '倒卷翻天', '夹生石头', '别脱扣',
    '官署', '长官官署', '官衙', '府衙', '官道', '十里官道', '官卡', '哨卡公堂', '车马店', '大车店', '古道', '驿路长亭', '凉亭', '北地',
    '演兵场', '校场点将台', '路引', '文牒', '通关文牒', '行商文牒', '通行文牒', '四合院', '厢房', '正房', '中军大帐', '帅帐', '千斤闸', '雕花木旗', '木旗',
    '千斤', '划拳', '行酒令', '掷骰盅', '品茶', '刮茶沫', '奉茶', '包子', '馒头', '卤肉', '酱牛肉',
    '剑意', '剑意共振', '万剑归宗', '身法', '轻灵身法', '水上漂', '烽火', '烽火台', '驿亭',
    '掌柜', '店小二', '伙计', '客栈', '修真', '内力', '真气', '浊气', '轻功', '暗度陈仓', '瞒天过海',
    '兵荒马乱', '江湖', '武林', '宗门', '演武场', '地宫', '洞府', '打坐', '吐纳',
    '周天', '真元', '大能', '高人', '尊者', '仙躯', '神识', '神魂', '神仙', '仙人', '大罗神仙', '大罗',
    '四肢百骸', '气海', '精关', '丹田', '气机', '气力', '灵气', '飞剑', '遁光', '储物袋',
    '本座', '名门闺秀', '闺秀', '药膳', '调息', '古篆', '敕印', '门楣', '门槛', '女当家', '大当家',
    # 空间构件与日常器物
    '长案', '案头', '书案', '案台', '桐油', '茶盏', '一盏茶', '盖碗', '通条', '圆几', '茶几', '小几', '条几', '凭几', '几案', '木几',
    # 禽鸟/武侠轻功意象与古风比喻
    '紫燕', '飞燕', '如燕', '轻如燕', '游龙', '游龙身法', '惊鸿',
    # 东方器物、瓷器与修真容器
    '白瓷', '青瓷', '青花瓷瓶', '白瓷药盒', '瓷盒', '瓷瓶', '瓷罐', '玉瓶', '玉盒', '玉佩', '锦囊', '药丸', '灵丹', '丹药',
    # 东方市井与话本谦称、长工市井差事及体制古风
    '草民', '老朽', '小女子', '奴家', '恩师', '同袍', '袍泽', '军伍同袍', '战友', '活计', '细致活计', '手头的活计',
    '小的', '做牛做马', '求大人恩典', '招供', '画押', '领罚', '侍奉', '伺候', '服侍', '奴婢',
    '名誉名节', '贞节', '妇道', '清白受损', '恶少', '强占良妇', '勾栏侍妾',
    '矮人部族', '矮人部落', '矮人氏族', '矮人王国',
    # 中世纪欧洲社科历史教材生硬专词（JRPG置换为领地/封地/庄园/教产）
    '采邑', '免税采邑', '采邑私兵', '采邑贵族', '矿山采邑',
    # 国术武侠动作与发力黑话
    '坐马', '下盘', '扎稳下盘', '马步', '沉腰', '沉腰坐马', '沉腰立马', '直取要害',
    '覆鳞如钩', '如钩', '反关节擒拿', '柔劲', '如灵蛇', '灵蛇出洞', '身形如游蛇', '游蛇', '汉白玉', '汉白玉台阶', '寒光乍现',
    # 东方/近现代非中世纪兵器与古风兵刃服饰
    '马刀', '战刀', '开山重斧', '横戟', '长戟', '钢戟', '战戟', '铁戟', '双戟', '方天画戟', '长戈',
    '战袍', '外袍', '锦袍', '青衫', '白衫', '宽袍大袖', '前襟', '衣襟',
    # 东方江湖熟语与绿林口吻
    '过命', '过命交情', '过命的交情', '剑客', '大侠', '游侠儿', '草莽', '同道中人',
    # 中式古风地理关卡与中式建筑构件（严格杜绝中式院落、窗棂构件）
    '窗棂', '木格窗', '雕花', '雕花木格窗', '雕花木窗', '雕花木旗', '木窗棂', '轩窗', '小轩窗', '隔扇', '影壁', '照壁', '雕梁', '雕梁画栋', '飞檐', '斗拱',
    # 武侠动作与招式黑话（严禁直接套用武侠打斗）
    '飞掠', '凌空飞掠', '错步', '滑步', '面门', '死穴', '命门', '战端', '战端收束', '微风劲', '气劲', '护体罡气',
    '剑芒', '刀芒', '杀招', '出招', '招式', '过招', '杀气腾腾', '暴起发难', '发难',
    # 玄幻仙侠玄学描写
    '虚覆', '指尖虚覆', '通体莹白', '交融流转', '流转不息', '流转', '通透温润', '本源之力', '空间织锦', '虚空微澜', '心眼探阵', '探阵', '阵眼', '法印',
    # 古风文言虚词、副词与动词
    '顷刻', '瞬息', '半晌', '未几', '旋即', '蓦地', '骤然', '些许', '良久', '过了良久', '沉吟', '沉吟良久', '尽数', '全数',
    '徐徐', '悠悠', '赫然', '步入', '踏足', '敛息', '阖眸', '残影', '轻启', '虚抚', '微蹙', '凭栏',
    '轻步上前', '轻步走去', '指节微白', '指节发白', '行至', '移步', '趋步', '踱步至', '正襟危坐',
    # 古风颜色与声效套话
    '赤红', '墨色', '素白', '黛色', '青丝', '云鬓', '吱呀', '打了个转',
    # 假雅伪古风复合偏正与江湖公文词（日轻绝无）
    '故土林海', '林海', '趁手', '趁手的', '趁手的工具', '过命', '方略', '定计', '筹谋', '交代方略', '桑梓',
    # 中式古代官制与衙门职官称谓（西幻日轻杜绝）
    '枢密院', '掌印', '掌印夫人', '女掌印', '掌印人', '夤夜', '夙夜',
    # 隐性古风漂移灰色词
    '快意', '沉缓', '天光', '眼帘', '眼睫', '指掌', '退散', '清冷如冰', '冷若冰霜', '此番',
    # 评书武侠夸张强调动词（日轻西幻使用自然停下/悄然松开/忍住/咽下）
    '生生咬碎', '生生止住', '生生止', '生生停', '生生刹', '生生忍', '生生咽', '生生憋', '生生压', '生生吞', '生生打断', '生生掐', '生生逼', '硬生生',
    '落入眼中', '尽收眼底', '莫要', '做贼心虚', '不疑有他', '晴空霹雳', '雷霆炸响',
    # 中式传统历法与时间概念（西幻世界观禁词，替换为沉眠季末期/晨光降临祭前夕/年轮交替之际）
    '岁末', '除夕',
    # 东方朝廷、深闱与微服出巡
    '微服', '微服私访', '微服出巡', '深宫', '内闱', '大内', '深闱',
    # 东方古风发饰首饰与挂件饰品（菲娜为粉色长发及腰，杜绝中式发簪与流苏）
    '木簪', '玉簪', '发簪', '簪子', '发钗', '步摇', '金簪', '流苏',
    # 言情与武侠装逼套句/动作与中式器具
    '踏碎积雪', '踏碎薄霜', '踏碎晨霜', '拂袖', '拂袖而去', '拍案而起', '怒目圆睁', '半盏', '象牙折扇',
    # 古代世俗行军词汇（日轻西幻使用整备启程/出发/车队开动）
    '拔营', '开拔', '拔营起寨', '大军开拔', '大军拔营'
]

# 1.1 评书话本与说书人套话黑名单（彻底拔除中式说书腔调与土俗俚语）
STORYTELLING_FORBIDDEN_WORDS = [
    '话音未落', '果不其然', '只见', '说时迟那时快', '殊不知', '岂料',
    '暗道一声', '心下大骇', '按捺不住', '不由得', '且说', '按下不表',
    '这厢', '那厢', '暴喝一声', '心生一计',
    # 中式市井土俗俚语与绿林男性称呼
    '手脚麻利', '倒爷', '老浪子', '老乡', '擦屁股', '泥腿子',
    '汉子', '壮汉', '粗汉', '大汉', '莽汉', '老汉', '铁兄弟',
    # 中式话本与评书引语腔调（严禁“XX道：”说书人句式）
    '分析道', '解释道', '蹙眉道', '叹道', '轻叹道'
]

# 1.1.1 中式市井方言、土俗口语与破坏沉浸感虚词黑名单（彻底杜绝将JRPG西幻写成中式胡同市井或茶馆话本）
FOLK_SLANG_FORBIDDEN_WORDS = [
    # 时间与经历类中式方言虚词（日轻JRPG汉化使用“自从/从小/自幼/如今/关键关头/未曾料到”）
    '自打', '打小', '现如今', '这当口', '节骨眼', '哪曾想', '落难',
    # 状态与突发类中式方言词（日轻西幻使用“猝不及防/突然间/动作利落/心生疑窦/毫无异状/无论如何”）
    '冷不丁', '麻利', '好端端', '横竖', '撂挑子', '嚼舌根',
    # 市井交际与评书套话（日轻西幻使用“出面解围/从中调解/筹备/拍手招呼大家/空之女神/店主/侍者/同袍”）
    '打圆场', '大声张罗', '张罗起来', '打量了一番', '不打紧', '老天爷', '吃干抹净', '旧部',
    # 中式市井俗称（日轻西幻统一使用“那孩子/小姑娘/少女”）
    '丫头', '野丫头'
]

# 1.2 古风言情与假文雅修辞黑名单（彻底杜绝古偶文风）
ROMANCE_ANCIENT_CLICHES = [
    '微嗔', '薄怒', '莞尔', '掩面', '颔首', '轻颔', '蹙起', '美目', '秋波', '蛾眉', '娇躯',
    '眼眸', '双眸', '美眸', '寒眸', '凤眸', '眸光', '微凉', '柔荑', '玉手', '纤手', '檀口', '樱唇', '皓齿', '贝齿',
    '香腮', '俏脸', '天鹅颈', '雪乳', '玉峰', '酥胸', '玉足', '秀足',
    '蹙眉', '蹙额', '紧蹙',
    '皮肉', '生疼', '化作一滩春水'
]

# 1.3 现代公文报告与作战通报套话（消灭会议纪要与总结通报）
BUREAUCRATIC_FORBIDDEN_WORDS = [
    '清剿完毕', '战斗收束', '梳理顺畅', '收束完毕', '开展', '落实',
    '达成共识', '正式敲定', '平静说出', '明确敲定', '逐项核对', '逐项核验', '言明', '坦言自己',
    '核心骨干',
    # 现代社会学与阶级标签（西幻RPG世界观禁词，替换为市井平民/普通领民/粗暴水手等实体身份）
    '底层平民', '社会底层', '底层海员', '底层水手', '底层劳工', '底层民众', '底层阶级', '底层阶层', '底层人'
]

# 1.4 中式古代朝堂/公案判词/古风小生戏腔黑名单（彻底杜绝古偶公案与中式文言戏腔台词）
COURT_ANCIENT_CLICHES = [
    '万万不可', '这是何意', '何出此言', '不可造次', '万死不辞',
    '越俎代庖', '此人乃是', '自有王法', '微臣', '老臣', '末将', '卑职', '臣等',
    '启奏', '圣裁', '圣躬', '皇恩', '叩首', '成何体统', '休得无礼', '休要多言',
    '纳命来', '手底下见真章', '国祚延绵', '移驾', '代掌国政', '神智偶有迷乱',
    '舍身相护', '救命大恩', '大恩永世不忘', '未曾料想', '不知死活',
    '后会有期', '不吝赐教', '赐教', '实不相瞒',
    # 古风小生腔调、中式公案苦情腔、江湖话本与泛化“老XX”偏正词
    '逼仄', '幽深', '残命', '纵是', '爬也要', '玉石俱焚', '草芥', '视血肉为草芥',
    '申冤', '伸冤', '含冤', '沉冤昭雪', '天理何在', '作恶多端', '苍天有眼',
    '老谋深算', '老骨头', '老团长', '老仆', '老狐狸', '老将', '老泪', '老泪纵横', '老泪长叹', '老骨头糊涂', '老脸',
    '老匹夫', '老朽', '老汉', '老者', '老道'
]

# 1.4.1 古风小生/江湖游侠自称“在下”正则（精确排除在下城区/在下水道/在下层/正在下雨等方位空间与天气词）
ZAIXIA_PRONOUN_PATTERN = re.compile(
    r'(?:[“"「，,、\s]|^)在下(?!([城层方底面落降雨雪水游行脚滑跌沉坡位道渠盲井榻线端颌颚]))'
)

# 1.5 连续四字短语连缀正则（中式四字律动检测，连缀3个及以上4字结构硬拦截）
CADENCE_4_CHAR_PATTERN = re.compile(
    r'(?:^|[，,、])([一-龥]{4})[，,、]([一-龥]{4})[，,、]([一-龥]{4})(?:[，,、。！？\s]|$)'
)

# 2. 中式传统度量衡与文言计时正则（允许“里格/公顷/公里/厘米/分贝”等，但严禁传统中国市制单位与古风“载”）
# 匹配：一尺、数尺、三寸、数十斤、数里、五里、千斤、数万石、数斗、两百载、数载等
CHINESE_UNIT_PATTERN = re.compile(
    r'(?<![公公分厘纳毫百千])(?<![a-zA-Z0-9])'
    r'([一二三四五六七八九十百千万数几两半0-9]+(斤|两|尺|寸|丈|里|斗|载)|[一二三四五六七八九十百千万数几两半]+石(?!头|块|壁|缝|阶|门|桥|柱|洞|窟|殿|板|匠|泉|栏|雕|像|山|屋|亭|椅|凳|盒|碑|碗|壶|锅|盆|锁|槽|栏|道|路|崖|砾|质|材|构|体|晶))'
    r'(?![米克分厘寸升格])'
)

# 3. 跨体系污染词与非白名单词汇
PART1_CONTAMINATION_WORDS = [
    '战术隐蔽',
    '爱意值',
    '隐秘事件',
    '背德事件',
    '落红', '淫靡', '淫水', '浪叫', '肉刃', '牝穴', '娇喘',
    '花径', '花心', '甬道', '蜜道', '阳精', '元阳', '精元', '龙根', '阳物', '昂扬', '破身', '破瓜', '失身'
]

# 4. 恶性翻译腔与括号英文堆叠正则（如：方庭合院式高级驿舍（Courtyard Coaching Inn））
TRANSLATIONESE_PATTERN = re.compile(r'[\u4e00-\u9fa5]{6,}（[A-Za-z\s]+）')

# 5. 设定档案（docs2/）元叙事与破坏第四面墙禁词（设定库必须作为独立完整故事书写，严禁出现第X部或括号轨迹世界）
META_PART_PATTERN = re.compile(r'第[一二三四五六七八九十0-9]+部')
META_OTHER_PATTERN = re.compile(r'(上一部|下一部|第一季|第二季|第三季|留给第三部|第三部伏笔|轨迹世界|轨迹系列)')

# 6. 教廷与圣殿概念混淆/混搭禁词库（防止神权教廷与武装修会概念滑丝，严禁不存在的神殿）
CHURCH_TEMPLAR_CONFUSION_WORDS = [
    '圣殿修道院', '教廷骑士', '教会骑士', '教廷审判骑士', '教会审判骑士',
    '圣殿大教堂', '教廷要塞', '教廷大要塞', '圣殿主教', '圣殿神官',
    '圣殿司铎', '圣殿秘库', '圣殿工坊', '神殿', '晨光神殿', '圣殿神殿'
]

# 7. 世俗军队与骑士降阶黑名单词库（严禁将受封圣殿骑士降阶为世俗散兵老兵/长官）
SECULAR_MILITARY_FORBIDDEN_WORDS = [
    '老兵', '退伍老兵', '大头兵', '军官', '长官', '老长官', '长官大人', '守将', '武将', '退伍军人',
    '军纪', '军令', '军备', '守军', '驻军', '军情', '军需', '军饷', '军法', '军规', '治军', '青年将领', '全军', '兵卒', '军卒', '边境军卒',
    '随军司铎', '拔营', '开拔', '拔营起寨', '大军开拔', '大军拔营',
    '士兵', '步兵', '大头兵'
]

# 7.1 网文元叙事与破坏第四面墙出戏代称（大纲、正文与设定档案严禁使用“主角团/主角们/主角方”，一律使用“众人/大家/全员/队伍/黎恩一行”）
META_JARGON_FORBIDDEN_WORDS = [
    '主角团', '主角们', '主角方', '反派方', '反派们'
]

# 7.2 角色对白与正文剧作破壁元叙事正则（严禁在对白台词中出现“第X幕/阶段/章/部”等剧作与大纲元编号）
CHINESE_DIALOGUE_PATTERN = re.compile(r'[“「]([^”」]+)[”」]')
ASCII_DIALOGUE_PATTERN = re.compile(r'(?:[：:说应问答喝道笑骂吼喊呼怒叹冷笑]\s*)"([^"]+)"')
META_BREAKING_TERMS_PATTERN = re.compile(r'(第[一二三四五六七八九十百0-9]+[幕阶段]|第[一二三四五六七八九十百0-9]+章(?!第?[一二三四五六七八九十0-9]+[款条则卷编])|上一幕|下一幕|前一幕|后一幕|上个阶段|下个阶段|本幕|本阶段|剧本|编剧|伏笔)')

# 8. 否定式元叙述与自卫性辩解正则（严禁在正文中通过否定别家流派来进行描写，严禁出现“没有摆出...武侠/流氓/客栈/戾气/无赖相”等）
DEFENSIVE_META_PATTERN = re.compile(
    r'(没有|并未|绝非|不是|毫无).{0,10}(武侠|仙侠|修真|轻功|市井流氓|横肉暴徒|客栈|戾气|无赖相|江湖)'
)

# 9. 现实地球地理打破沉浸感黑名单词库（第二部本土为晨光大陆Luminas，异界为塞姆利亚大陆Zemuria，严禁现实地球地理名词）
REAL_EARTH_GEO_WORDS = [
    '欧陆', '欧洲'
]

# 10. 要塞泛用与要塞军权违规词库（【要塞】全书唯一专属特指【圣殿大要塞】具体据点，严禁将要塞泛化为政体或造词'要塞军权'）
FORTRESS_MISUSE_WORDS = [
    '要塞军权', '大要塞军权', '要塞军', '要塞方', '要塞势力', '军事要塞', '地方要塞',
    '要塞骑士团', '要塞大团长', '要塞驻军',
    '要塞防资', '要塞特权', '要塞司法权', '要塞受挫', '要塞巡骑', '要塞铁骑', '要塞武装', '要塞守备铁骑', '大门要塞'
]

# 10.1 要塞作为施动主语正则（【要塞】是纯物理据点，严禁作为行动主体/施动主语，必须使用“圣殿骑士团/誓约骑士/铁誓骑队”）
FORTRESS_ACTIVE_SUBJECT_PATTERN = re.compile(
    r'(?:圣殿)?要塞(?:更会|会|将|企图|意图|决定|出动|派遣|大举|下达|调动|发兵|派兵|围剿|进犯|查扣|抓捕)'
)

# 11. 中式古风关卡与关隘专属禁词库（全书严禁中式“关隘/关口”，必须使用正向实体【维里迪亚大门】、边防大门、边防哨卡或边境哨所）
GATE_PASS_FORBIDDEN_WORDS = [
    '关隘', '关口', '维里迪亚关隘', '入关', '出关'
]

# 12. 中式古典家具专属禁词正则（严禁各类明清几案坐具，西幻统一使用长木桌/小圆桌/边桌/靠背椅/木凳）
CHINESE_FURNITURE_PATTERN = re.compile(
    r'([圆茶木石竹玉方矮条琉]几|小[圆木茶]几|矮茶几|几案|案台|长案|案头|书案|屏风|绣墩|罗汉床|凭几(?![个十百千万株条本双只门瓶把张片辆口群峰面道位枚粒根朵块件步载天分里尺寸丈包盒袋碗杯人名位]))'
)

# 13. 中医中药性味与温养滋补修辞正则（严禁将西幻料理草药写成中医药膳煲汤）
TCM_HERBAL_PATTERN = re.compile(
    r'(温润(?:接骨木|草药|药根|药性|浓汤|高汤|药膳|热汽|药香|之效|茶水)|药膳|滋补|生津|温补|调息|培元|固本|气血两虚|行气活血)'
)

def is_blacklist_definition_line(line):
    """判断某一行是否属于黑名单、规则定义、替换表或版本日志"""
    stripped = line.strip()
    # 规则替换表格或带叉号的黑名单列举
    if stripped.startswith('|') and ('严禁' in stripped or '替换' in stripped or '红线' in stripped or '东方' in stripped or '古风' in stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in ['×', '* ×', '- ×', '× ', '【严禁', '严禁', '拔除', '清除']):
        return True
    if '词汇对照与置换规范表' in stripped or '红线词库' in stripped:
        return True
    return False

def audit_file(filepath):
    """审计单个文件的文风与规范问题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    text = "".join(lines)

    fname = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, config.PROJECT_DIR)
    findings = []

    is_index_file = fname.startswith('_')
    is_character_card = 'docs2/character' in rel_path.replace('\\', '/')
    is_guide_or_plan = '方案/第二部' in rel_path.replace('\\', '/') or 'SKILL' in fname or 'skills' in rel_path or (is_index_file and fname.endswith('.md'))

    in_blacklist_table = False
    in_interface_section = False
    in_code_block = False

    # 按行检查，精准定位并过滤黑名单定义行
    for line_idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # 检测代码块状态
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 检测表格状态
        if stripped.startswith('|'):
            if '严禁' in stripped or '禁用' in stripped or '替换' in stripped or '红线' in stripped or '黑名单' in stripped or '误区' in stripped:
                in_blacklist_table = True
                continue
            if in_blacklist_table:
                # 处于黑名单对照表格内，跳过此行扫描
                continue
        else:
            in_blacklist_table = False

        if stripped.startswith(('## 三、', '### 2. 后置交付输出', '### 1. 前置输入承接')) or '接口与交接' in stripped or '本阶段接口' in stripped:
            in_interface_section = True
        elif stripped.startswith(('## 一、', '## 二、')):
            in_interface_section = False

        if is_guide_or_plan:
            if any(stripped.startswith(p) for p in ['×', '* ×', '- ×', '× ', '【严禁', '严禁', '拔除', '清除', '丢弃', '抛弃']):
                continue
            if '词汇对照与置换规范表' in stripped or '红线词库' in stripped:
                continue

        # 目录树行跳过古风禁词检测（如 README 目录树中引用历史或外部文件名）
        if stripped.startswith(('├', '└', '│')):
            continue

        # 规则说明或禁令行跳过
        if any(stripped.startswith(p) for p in ['- 禁', '* 禁', '【禁', '禁止']):
            continue

        # 1. 检查武侠/古风禁词
        for word in WUXIA_FORBIDDEN_WORDS:
            if word in line:
                if any(k in line for k in ['拔除', '清除', '严禁', '黑名单', '红线', '置换', '替换', '绝对禁止', '杜绝', '丢弃', '抛弃', '禁止']):
                    continue
                if word == '老夫' and '老夫老妻' in line:
                    continue
                if word == '长戈' and '戈德弗里' in line:
                    continue
                if word == '木旗' and '木旗杆' in line:
                    continue
                if word == '贴水' and any(water in line for water in ['贴水滑', '贴水面', '紧贴水', '贴着水']):
                    continue
                if word == '小的' and any(adj in line for adj in ['大小', '掌心大', '巴掌大', '最小', '狭小', '微小', '细小', '矮小', '幼小', '小巧', '小小', '老小', '那么小', '这么小', '年纪小', '年龄小', '从小到大']):
                    continue
                if word == '古道' and ('第十幕' in line or '10_第十幕' in line):
                    continue
                findings.append(('【古风/武侠禁词】', f"行 {line_idx}: 发现 '{word}' -> {line.strip()[:60]}"))

        # 1.1 检查非西幻中式器皿“瓷”字禁令（带瓷皆错：骨瓷/细瓷/粗瓷/瓷盘/瓷杯/瓷碟/陶瓷等全量硬拦截，西幻一律使用银制/陶制/玻璃/木制）
        if '瓷' in line:
            if not any(k in line for k in ['拔除', '清除', '严禁', '黑名单', '红线', '置换', '替换', '绝对禁止', '杜绝', '丢弃', '抛弃', '禁止', '规避', '绝缘']):
                findings.append(('【非西幻器皿/瓷字违规】', f"行 {line_idx}: 严禁出现带'瓷'字器皿 -> {line.strip()[:60]}"))

        # 1.2 检查中式古代坐卧具“榻”字禁令（带榻皆错：床榻/同榻/木榻/卧榻/病榻/软榻等全量硬拦截，西幻一律使用床/大床/木床/长椅）
        if '榻' in line:
            if not any(k in line for k in ['拔除', '清除', '严禁', '黑名单', '红线', '置换', '替换', '绝对禁止', '杜绝', '丢弃', '抛弃', '禁止', '规避', '绝缘']):
                findings.append(('【中式家具/榻字违规】', f"行 {line_idx}: 严禁出现带'榻'字中式坐卧具 -> {line.strip()[:60]}"))

        # 1.3 检查中式古典家具“几/案/屏风/绣墩”禁令
        m_furn = CHINESE_FURNITURE_PATTERN.search(line)
        if m_furn:
            if not any(k in line for k in ['拔除', '清除', '严禁', '黑名单', '红线', '置换', '替换', '绝对禁止', '杜绝', '丢弃', '抛弃', '禁止', '规避', '绝缘']):
                findings.append(('【中式家具/几案违规】', f"行 {line_idx}: 严禁出现中式古典家具 '{m_furn.group(0)}'（西幻一律使用长木桌/小圆桌/边桌/靠背椅/木凳） -> {line.strip()[:60]}"))

        # 1.4 检查中医中药性味/修真温养修辞禁令
        m_tcm = TCM_HERBAL_PATTERN.search(line)
        if m_tcm:
            if not any(k in line for k in ['拔除', '清除', '严禁', '黑名单', '红线', '置换', '替换', '绝对禁止', '杜绝', '丢弃', '抛弃', '禁止', '规避', '绝缘']):
                findings.append(('【中医药膳/性味修辞违规】', f"行 {line_idx}: 严禁使用中医药膳/温补玄虚修辞 '{m_tcm.group(0)}'（西幻日轻草药直接客观描写） -> {line.strip()[:60]}"))

        # 1.5 检查文言倒装句式与动词介词结构（调用 check_line_inversions）
        inversion_issues = check_line_inversions(line, line_idx)
        for itype, idesc in inversion_issues:
            findings.append((itype, idesc))

        # 2. 检查传统中式度量衡
        for m in CHINESE_UNIT_PATTERN.finditer(line):
            unit_str = m.group(1)
            # 排除常用非度量与公制词汇
            if any(ok in line for ok in ['心里', '屋里', '手里', '怀里', '眼里', '公里', '里格', '海里', '拔除', '清除', '严禁']):
                continue
            findings.append(('【中式度量衡】', f"行 {line_idx}: 发现 '{unit_str}' -> {line.strip()[:60]}"))

        # 3. 检查第一部字段/内容污染（角色卡保留自身生理设定，但在其他卡片、章节、方案中严格禁止）
        for pw in PART1_CONTAMINATION_WORDS:
            if pw in line:
                if (is_character_card or 'NSFW' in rel_path) and pw in ['蜜穴', '娇喘']:
                    continue
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范']):
                    continue
                findings.append(('【第一部字段/内容污染】', f"行 {line_idx}: 发现 '{pw}' -> {line.strip()[:60]}"))

        # 4. 检查 docs2/ 设定档案中的元叙事/第X部违规（档案必须作为独立完整故事书写）
        if 'docs2' in rel_path.replace('\\', '/') and filepath.endswith('.TXT'):
            m_part = META_PART_PATTERN.search(line)
            if m_part:
                findings.append(('【设定档案元叙事违规】', f"行 {line_idx}: 档案设定必须作为独立故事书写，严禁特意提及分部 '{m_part.group(0)}' -> {line.strip()[:60]}"))
            m_other = META_OTHER_PATTERN.search(line)
            if m_other:
                findings.append(('【设定档案元叙事违规】', f"行 {line_idx}: 档案设定严禁出现元叙事词汇 '{m_other.group(0)}' -> {line.strip()[:60]}"))

        # 5. 检查教廷与圣殿概念混搭违规（严禁神权与修会概念混用）
        for cw in CHURCH_TEMPLAR_CONFUSION_WORDS:
            if cw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆']):
                    continue
                findings.append(('【教廷/圣殿概念混淆】', f"行 {line_idx}: 发现混淆词 '{cw}' -> {line.strip()[:60]}"))

        # 6. 检查世俗军队与降阶称谓违规（方案与正文章节中严禁将誓约骑士写为老兵/大头兵/世俗军队/长官）
        if is_guide_or_plan or ('story' in rel_path.lower() and filepath.endswith('.TXT')):
            for smw in SECULAR_MILITARY_FORBIDDEN_WORDS:
                if smw in line:
                    if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                        continue
                    findings.append(('【世俗军队/降阶称谓违规】', f"行 {line_idx}: 方案与章节严禁使用世俗军队降阶词 '{smw}' -> {line.strip()[:60]}"))

        # 6.1 检查网文元叙事与出戏代称（方案、大纲、详规与正文中严禁使用“主角团”，一律使用“众人/大家/全员/队伍/黎恩一行”）
        for mjw in META_JARGON_FORBIDDEN_WORDS:
            if mjw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    continue
                findings.append(('【元叙事出戏违规】', f"行 {line_idx}: 严禁使用网文剧作元叙事代称 '{mjw}'！方案与正文一律置换为'众人'、'大家'、'全员'、'队伍'或'黎恩一行' -> {line.strip()[:60]}"))

        # 6.2 检查角色台词/对白破壁元叙事（严禁在角色对白“...”或「...」中出现“第X幕/阶段/章”等剧作元编号）
        dialogues = [m.group(1) for m in CHINESE_DIALOGUE_PATTERN.finditer(line)]
        dialogues.extend([m.group(1) for m in ASCII_DIALOGUE_PATTERN.finditer(line)])
        for quote_text in dialogues:
            m_term = META_BREAKING_TERMS_PATTERN.search(quote_text)
            if m_term:
                if not any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '违规']):
                    findings.append(('【角色台词破壁元叙事违规】', f"行 {line_idx}: 严禁角色在对白台词中口吐剧作工程元编号 '{m_term.group(0)}'！台词必须转换为'先前/两个月前/前些天'等沉浸式时空指示词 -> {line.strip()[:60]}"))

        # 针对具体小说正文（story/中的TXT章节），全篇一律不得出现幕次/阶段编号等元叙事
        if 'story' in rel_path.lower() and filepath.endswith('.TXT'):
            m_story_meta = META_BREAKING_TERMS_PATTERN.search(line)
            if m_story_meta:
                findings.append(('【小说正文破壁元叙事违规】', f"行 {line_idx}: 小说正文中严禁出现剧作元叙事词汇 '{m_story_meta.group(0)}' -> {line.strip()[:60]}"))

        # 7. 检查否定式元叙述与防守性辩解（严禁正文出现“没有...武侠/流氓/客栈/戾气”等）
        m_def = DEFENSIVE_META_PATTERN.search(line)
        if m_def:
            if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '自卫性']):
                continue
            findings.append(('【否定式元叙述/防守性辩解】', f"行 {line_idx}: 发现防守性否定元叙述 '{m_def.group(0)}' -> {line.strip()[:60]}"))

        # 8. 检查现实地球地理违规（严禁在第二部中出现欧陆/欧洲，必须使用架空“晨光大陆”或日式西幻）
        for geo in REAL_EARTH_GEO_WORDS:
            if geo in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '打破沉浸感']):
                    continue
                findings.append(('【现实地球地理违规】', f"行 {line_idx}: 发现现实地球地理词 '{geo}'（请置换为'晨光大陆'或'日式西幻'） -> {line.strip()[:60]}"))

        # 9. 检查评书话本与说书人套话
        for stw in STORYTELLING_FORBIDDEN_WORDS:
            if stw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    continue
                findings.append(('【评书话本套话】', f"行 {line_idx}: 发现评书说书人套话 '{stw}' -> {line.strip()[:60]}"))

        # 9.1 检查中式市井方言、土俗口语与破坏沉浸感虚词（读者视角出戏硬拦截）
        for fsw in FOLK_SLANG_FORBIDDEN_WORDS:
            if fsw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '违规']):
                    continue
                findings.append(('【市井方言出戏违规】', f"行 {line_idx}: 发现严重破坏西幻/JRPG沉浸感的中式市井方言虚词 '{fsw}'！请置换为清澈的日轻JRPG散句（如自从/突然/动作利落/如今/出面解围） -> {line.strip()[:60]}"))

        # 10. 检查古风言情与假文雅修辞
        for rac in ROMANCE_ANCIENT_CLICHES:
            if rac in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    continue
                findings.append(('【古偶假文雅套话】', f"行 {line_idx}: 发现古言假文雅修辞 '{rac}' -> {line.strip()[:60]}"))

        # 11. 检查现代公文与作战通报套话
        for bfw in BUREAUCRATIC_FORBIDDEN_WORDS:
            if bfw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    continue
                findings.append(('【公文通报腔违规】', f"行 {line_idx}: 发现现代公文/作战通报词 '{bfw}' -> {line.strip()[:60]}"))

        # 11.1 检查中式古代朝堂/公案判词/古风小生戏腔（彻底杜绝古偶公案与中式文言戏腔台词）
        for cac in COURT_ANCIENT_CLICHES:
            if cac in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '违规红线']):
                    continue
                findings.append(('【古风小生/朝堂文言戏腔违规】', f"行 {line_idx}: 发现中式朝堂/公案戏腔 '{cac}' -> {line.strip()[:60]}"))

        m_zx = ZAIXIA_PRONOUN_PATTERN.search(line)
        if m_zx:
            if not any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '违规红线']):
                findings.append(('【古风小生自称违规】', f"行 {line_idx}: 发现古风小生/江湖自称 '在下' -> {line.strip()[:60]}"))

        # 12. 检查连续四字短语连缀病灶（中式四字律动检测，仅在章节情境与详规演进中检测）
        if 'story' in rel_path.lower() or '分阶段详规' in rel_path:
            # 过滤掉标题、角色列表行
            if not any(stripped.startswith(p) for p in ['ID:', '名称:', '主要人物:', '阶段:', '路线:', '核心:', '规划规模:']):
                m_cadence = CADENCE_4_CHAR_PATTERN.search(line)
                if m_cadence:
                    findings.append(('【四字连缀话本病灶】', f"行 {line_idx}: 检测到连续四字短语连缀 '{m_cadence.group(0).strip('，,、')}'，句式严重话本化！请使用长短舒展的轻小说现代句式。"))

        # 12.1 检查分阶段详规正文是否残留提纲骨架标记（统一标准为100%连续小说级全景长叙述散文）
        if '分阶段详规' in rel_path and not os.path.basename(rel_path).startswith('00_'):
            if any(line.strip().startswith(p) for p in ['* **剧情路线**', '* **主要人物**', '* **核心意图**', '* **时序情境推进**']):
                findings.append(('【详规提纲骨架残留违规】', f"行 {line_idx}: 分阶段详规正文必须 100% 展开为小说级连续全景长叙述散文，严禁残留提纲标签 '{line.strip()[:30]}'！"))
            elif re.match(r'^\s*-\s*[0-9]+\.\s*\*\*', line):
                findings.append(('【详规列表条目残留违规】', f"行 {line_idx}: 分阶段详规正文必须 100% 展开为小说级连续全景长叙述散文，严禁使用列表条目切片 '{line.strip()[:30]}'！"))

        # 13. 角色装备与人设常识防御断言（覆盖 docs2/story 章节与方案分阶段详规，按分句细粒度检测避免群像误判）
        if ('story' in rel_path.lower() and filepath.endswith('.TXT')) or '分阶段详规' in rel_path:
            clauses = re.split(r'[；;。！？\n]', line)
            for clause in clauses:
                if not clause.strip():
                    continue
                # 菲武器常识校验（双枪剑，非纯刀剑，非纯短铳）
                if ('菲' in clause or '克劳塞尔' in clause) and '菲娜' not in clause and '索菲亚' not in clause:
                    for blade_word in ['收刀', '刀刃', '刀鞘', '长刀', '短刀', '太刀']:
                        if blade_word in clause and '黎恩' not in clause:
                            if not any(k in clause for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止']):
                                findings.append(('【角色武器常识违规】', f"行 {line_idx}: 菲专属武器为双枪剑（Gunblade），装配枪套与钢丝，严禁使用“{blade_word}”等纯刀剑描述！ -> {clause.strip()[:60]}"))
                    for gun_word in ['短铳', '火铳', '燧发枪', '手枪', '刺刀短铳']:
                        if gun_word in clause:
                            if not any(k in clause for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止']):
                                findings.append(('【角色武器契约违规】', f"行 {line_idx}: 菲官方武器为双枪剑（Gunblade），兼具斩击与射击，严禁使用“{gun_word}”等单纯火器描述！ -> {clause.strip()[:60]}"))
                # 爱丽榭能力与武器常识校验（营地料理与生活支柱，非魔法师，绝无法杖）
                if '爱丽榭' in clause or '舒华泽' in clause:
                    for mage_word in ['法杖', '魔杖', '魔导杖', '收起法杖', '拿出法杖', '握紧法杖']:
                        if mage_word in clause and '艾玛' not in clause:
                            if not any(k in clause for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止']):
                                findings.append(('【角色人设能力违规】', f"行 {line_idx}: 爱丽榭为营地生活料理支柱非魔法师，绝无法杖“{mage_word}”！ -> {clause.strip()[:60]}"))
                # 菲娜施法与武器常识校验（双手祈祷式纯圣光，绝无短杖）
                if '菲娜' in clause or 'Seraphina' in clause:
                    for wand_word in ['短杖', '银质短杖', '魔杖', '权杖']:
                        if wand_word in clause and '艾玛' not in clause and '克莱门特' not in clause and '罗恩' not in clause:
                            if not any(k in clause for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止']):
                                findings.append(('【角色装备契约违规】', f"行 {line_idx}: 菲娜施法为双手祈祷式纯圣光，绝无手持“{wand_word}”！ -> {clause.strip()[:60]}"))
                    if '两百年前的守护者' in clause:
                        findings.append(('【角色人设辈分冲突】', f"行 {line_idx}: 菲娜本人即为320岁亲历两百年腐化之唯一守护者，严禁将其作为后辈描写！ -> {clause.strip()[:60]}"))
                    if '金发' in clause or '金色长发' in clause or '一头金发' in clause:
                        findings.append(('【角色人设发色冲突】', f"行 {line_idx}: 菲娜设定为及腰粉色长发（CHR_D2_01），严禁描写为金发！ -> {clause.strip()[:60]}"))
                # 雷恩装备常识校验
                if '雷恩' in clause:
                    for renn_err in ['晨光之盾', '制式圣剑']:
                        if renn_err in clause:
                            findings.append(('【角色设定常识违规】', f"行 {line_idx}: 雷恩十四年前已被夺剑废黜，使用朴素生铁重盾与旧长剑，严禁使用“{renn_err}”！ -> {clause.strip()[:60]}"))

        # 14. 检查要塞泛用、非法造词与施动主语违规
        for fmw in FORTRESS_MISUSE_WORDS:
            if fmw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    continue
                findings.append(('【要塞泛用/非法造词违规】', f"行 {line_idx}: 发现 '{fmw}'（【要塞】全书唯一专属特指【圣殿大要塞】具体据点，严禁泛化造词，请置换为'圣殿骑士团/圣殿大团长'等） -> {line.strip()[:60]}"))

        m_fortress_subj = FORTRESS_ACTIVE_SUBJECT_PATTERN.search(line)
        if m_fortress_subj:
            if not any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                findings.append(('【要塞拟人化/施动主语违规】', f"行 {line_idx}: 发现将地理据点作为施动主体 '{m_fortress_subj.group(0)}'！【要塞】是纯物理据点，无法发起行动，施动主体必须使用【圣殿骑士团】、【铁誓骑队】或【誓约骑士】！ -> {line.strip()[:60]}"))

        # 15. 检查中式古风关卡与关隘专属违规
        for gpw in GATE_PASS_FORBIDDEN_WORDS:
            if gpw in line:
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    continue
                if gpw == '入关' and re.search(r'(?:[进迈深切陷转])入关|入关(?:[键注头联系闭押卡门]|节|怀)', line):
                    continue
                if gpw == '出关' and re.search(r'(?:[走突杀脱解迈冲带])出关|出关(?:[卡隘口键头门]|闭)', line):
                    continue
                findings.append(('【中式古风关隘违规】', f"行 {line_idx}: 发现禁词 '{gpw}'（全书严禁中式关隘，请置换为'维里迪亚大门'、'边境大门'或'边防哨所/哨卡'） -> {line.strip()[:60]}"))

        # 16. 检查正文/情境叙事中的元叙事出戏、现代网络词汇、分镜术语与身份标签作主语
        # 针对 docs2/story/ 正文及分阶段详规中的情境叙事段落（排除大纲接口文件）
        is_story_or_scenario = ('story' in rel_path.lower() and filepath.endswith('.TXT')) or ('分阶段详规' in rel_path and not fname.startswith(('00_', '临时方案')))
        if is_story_or_scenario:
            # 16.1 幕级剧作元叙事破坏第四面墙（严禁在正文细节描写中将“第X幕/第X部”作为时间或事件状语）
            if not in_interface_section and not stripped.startswith(('#', '>', '|', '**', '- 前盘', '- 中盘', '- 后盘', '- 承接', '- 所属', '本阶段为', '本阶段聚焦', '本阶段承接')):
                m_meta_act = re.search(r'第[一二三四五六七八九十0-9]+[幕部期]', line)
                if m_meta_act and not any(k in line for k in [
                    '所属方案', '所属幕次', '上一幕', '下一幕', '接口', '导航', '前置', '后置', '对接', '转出', '衔接', '大纲', '【第',
                    '收官状态', '外部态势', '终局承接', '高维跨界', '核心意图', '核心瓶颈', '平原领主', '预设核心', '行会垄断', '环境与局势',
                    '承接点', '规划规模', '剧情路线', '主要人物', '核心主题', '挫折与瓶颈', '核心破局', '承接第八幕', '转入地底潜行',
                    '第十二幕全幕', '第二部三大终局', '向第三部引渡', '为第三部跨位面', '第二部圆满闭合', '贯穿至第'
                ]):
                    findings.append(('【叙事出戏/元叙事违规】', f"行 {line_idx}: 正文情境描写中严禁出现剧作分幕划分 '{m_meta_act.group(0)}'，破坏第四面墙！请置换为原生态时间词（如'当初'、'数月前'等） -> {line.strip()[:60]}"))

            # 16.2 现代网络梗、网文套话与出戏词汇
            for buzz in ['降维', '暴风吐槽', '吐槽模式', '心声吐槽', '护短模式', '护犊子']:
                if buzz in line and not any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝']):
                    findings.append(('【叙事出戏/网络梗违规】', f"行 {line_idx}: 发现现代网络流行语/出戏词汇 '{buzz}'，严重破坏架空西幻沉浸感！ -> {line.strip()[:60]}"))

            # 16.3 分镜指令词作为动作主语前缀
            m_camera = re.match(r'^\s*-\s*(?:慢镜头|镜头(?:切向|切至|聚焦|慢放|反打|捕捉|横移|由|自|横扫|定格|推近|拉远|特写))', line)
            if m_camera:
                findings.append(('【分镜术语入侵叙事】', f"行 {line_idx}: 严禁在情境叙事中将分镜指令作为动作前缀 '{m_camera.group(0).strip('- ')}'！请直接描写角色的物理动作或客观环境。 -> {line.strip()[:60]}"))

            # 16.4 旁白身份标签作主语
            m_tag = re.search(r'(?:^|[-*#\s：:])(?:精灵少女|紫发少女|黑发青年|金发少女|银发青年|前骑士|天才少女|女剑士)[^，。、\n]*[，。]', line)
            if m_tag and not any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '外貌', '身躯']):
                findings.append(('【旁白身份标签作主语】', f"行 {line_idx}: 旁白必须直呼其名，严禁使用身份标签作主语 '{m_tag.group(0).strip()}'！ -> {line.strip()[:60]}"))

        # 17. 检查文言介词倒装句式（如“裹以”、“覆以”、“饰以”、“佐以”等动词+以，以及“之以”句式）
        inversion_issues = check_line_inversions(line, line_idx)
        if inversion_issues:
            findings.extend(inversion_issues)


    # 5. 章节文件专属检查（针对 docs2/story/ 下的非索引 TXT）
    if 'story' in filepath.lower() and filepath.endswith('.TXT') and not is_index_file:
        if '主要人物:' not in text and '主要人物：' not in text:
            findings.append(('【缺少主要人物字段】', "第二部章节必须显式声明 '主要人物: 角色1, 角色2'"))

    return rel_path, findings

def scan_all(include_archive=False):
    """全量扫描第二部方案库与设定库"""
    print("=" * 60)
    print(" 维里迪亚王国篇（第二部）专属文风与病灶透视雷达")
    print(" 监控目标：docs2/ 设定库、方案/第二部/ 方案库、docs2/story/ 章节库")
    print("=" * 60)

    target_files = []

    # 1. docs2/ 所有的 TXT 文件
    if os.path.exists(config.DOCS2_DIR):
        target_files.extend(glob.glob(os.path.join(config.DOCS2_DIR, '**', '*.TXT'), recursive=True))

    # 2. 方案/第二部/ 所有的 MD 文件（默认排除历史归档 已执行/）
    if os.path.exists(config.SCHEME2_DIR):
        all_mds = glob.glob(os.path.join(config.SCHEME2_DIR, '**', '*.md'), recursive=True)
        for md_path in all_mds:
            if not include_archive and ('已执行' in md_path or 'NSFW' in md_path):
                continue
            target_files.append(md_path)

    total = len(target_files)
    issues_count = 0
    problem_files = []

    for fpath in sorted(target_files):
        rel_path, issues = audit_file(fpath)
        if issues:
            issues_count += len(issues)
            problem_files.append((rel_path, issues))

    print(f"\n扫描完成：共检查 {total} 个文件，发现 {issues_count} 处异常。")

    if not problem_files:
        print("\n[OK] 恭喜！第二部所有活跃设定与方案文件纯度 100%，无任何古风、中式度量衡或第一部字段污染！")
        return 0
    else:
        print("\n" + "!" * 60)
        print(" 发现以下文件存在文风或字段病灶，需立即修复：")
        print("!" * 60)
        for rpath, issues in problem_files:
            print(f"\n文件: {rpath}")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="第二部专属文风与病灶透视雷达")
    parser.add_argument('--file', type=str, help="扫描指定文件")
    args = parser.parse_args()

    if args.file:
        rpath, issues = audit_file(os.path.abspath(args.file))
        if issues:
            print(f"文件 {rpath} 发现 {len(issues)} 处问题：")
            for itype, idesc in issues:
                print(f"  - {itype} {idesc}")
            sys.exit(1)
        else:
            print(f"文件 {rpath} 纯度 100%，无违规项。")
            sys.exit(0)
    else:
        sys.exit(scan_all())
