import glob, re

banned_words = [
    '轻步', '肉刃', '肉棒', '肉茎', '昂扬', '甬道', '花径', '花心', '白浊', '深喉', '深射',
    '双乳', '雪乳', '乳沟', '胸脯', '解衣', '解甲', '温存', '避人耳目', '夹磨', '破身',
    '服侍', '侍奉', '伺候', '抽吸', '水渍', '浪子', '胯下', '全数', '尽数', '嗓音微哑',
    '微哑', '招供', '窗棂', '推拉', '惊惶', '惊恐', '恐慌', '恐惧', '吓得', '吓了一跳',
    '大受惊吓', '提到了嗓子眼', '心跳如擂鼓', '雷鼓', '死死', '哆嗦', '发抖', '颤抖',
    '受困被迫', '被迫', '被动承受', '怯生生', '浑身一僵', '长老', '近卫骑士', '狙击枪',
    '心爱的', '恋人', '未婚妻', '年轻剑士',
    '战袍', '军歌', '将士', '气血', '顽石', '火塘', '推拿', '穴位', '丹田', '经脉',
    '氅', '软榻', '酡红', '啼泣', '春景', '春色', '领命', '残阳如血', '烛台', '蜡泪'
]

character_setting_rules = [
    ('爱丽榭蓝发', r'爱丽榭.*?蓝发|蓝发.*?爱丽榭'),
    ('亚尔缇娜黑发', r'亚尔缇娜.*?黑发|黑发.*?亚尔缇娜'),
    ('艾德里安近卫骑士', r'艾德里安（近卫骑士）'),
]

files = sorted(glob.glob('方案/*批次*章节正文.md'))
total_chapters = 0
all_passed = True

for path in files:
    print('====================================')
    print('Testing file:', path)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    
    # 1. check banned words
    found = []
    for w in banned_words:
        matches = list(re.finditer(re.escape(w), content))
        if matches:
            found.append((w, len(matches)))
    if found:
        print('  [FAIL] Banned words found:', found)
        all_passed = False
    else:
        print('  [PASS] Zero banned words & character setting errors!')
    
    # 2. check character setting rules regex
    setting_fails = []
    for rule_name, rule_regex in character_setting_rules:
        matches = list(re.finditer(rule_regex, content))
        if matches:
            setting_fails.append((rule_name, len(matches)))
    if setting_fails:
        print('  [FAIL] Character setting violations:', setting_fails)
        all_passed = False
    
    # 3. check #### 正文
    if '#### 正文' in content:
        print('  [FAIL] Found #### 正文!')
        all_passed = False
    else:
        print('  [PASS] Zero #### 正文!')

    # 4. check chapters
    pattern = r'```text\s*\n(ID:.*?)\n```'
    blocks = re.findall(pattern, content, re.DOTALL)
    for b in blocks:
        total_chapters += 1
        cid_m = re.search(r'ID:\s*([\d\.]+)', b)
        if not cid_m:
            continue
        cid = cid_m.group(1)
        name = re.search(r'名称:\s*([^\n]+)', b).group(1)
        third = re.search(r'第三者:\s*([^\n]+)', b).group(1)
        
        # opening
        m_scene = re.search(r'情境:\s*\n\s*-\s*([^\n]+)', b)
        first_line = m_scene.group(1) if m_scene else ''
        
        # check time prefix
        if not re.match(r'^(某日|第二天|同一)', first_line):
            print(f'  [FAIL OPENING TIME] {cid}: {first_line[:20]}')
            all_passed = False
        
        # check core
        m_core = re.search(r'核心:\s*([^\n]+)', b)
        core_text = m_core.group(1) if m_core else ''
        if '“' in core_text or '”' in core_text:
            print(f'  [FAIL CORE DIALOGUE] {cid}: {core_text}')
            all_passed = False
            
        # check termination condition 3
        m_terms = re.findall(r'-\s*([^\n]+)', re.search(r'章节终止条件:(.*?)$', b, re.DOTALL).group(1))
        if len(m_terms) >= 3:
            term3 = m_terms[2]
            # verify no quotes or direct character speech
            if '“' in term3 or '”' in term3:
                print(f'  [FAIL TERM3 DIALOGUE] {cid}: {term3}')
                all_passed = False
        
        # count characters in 情境
        scene_content = re.search(r'情境:(.*?)(?=核心:)', b, re.DOTALL).group(1)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', scene_content))
        print(f'  [OK] {cid:5} | {chinese_chars:3d} 汉字 | {third:15} | {name[:22]:22} | 开头: {first_line[:14]}')

print('====================================')
print(f'Total inspected chapters: {total_chapters}')
if all_passed:
    print('ALL BATCHES PASSED 100% INSPECTION!')
else:
    print('SOME CHECKS FAILED!')
