"""
插入新事件N33(凯尔山洞)+N33-N67→N34-N68重新编号
单次pass正则，词边界保护。先移后插策略。
"""
import re

FILE = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# ============================================================
# Step 1: Renumber N33-N67 → N34-N68 (single pass, word boundary)
# ============================================================
def shift_id(m):
    num = int(m.group(1))
    if 33 <= num <= 67:
        return f'N{num + 1}'
    return m.group(0)

# Pattern: N followed by exactly 2 digits, with word boundary protection
# (?<![A-Za-z0-9]) prevents matching PN33, AN33, etc.
# (?!\d) prevents matching N334 (not that we have those)
c = re.sub(r'(?<![A-Za-z0-9])N(\d{2})(?!\d)', shift_id, c)
print('✅ Step 1: N33-N67 → N34-N68')

# Fix the range in mapping table header and any N1-N67 → N1-N68
c = c.replace('N1-N67', 'N1-N68')
c = c.replace('N01-N67', 'N01-N68')
c = c.replace('NTRS路线事件（N1-N67）', 'NTRS路线事件（N1-N68）')
# Update event count: 67个 → 68个
c = c.replace('NTRS路线事件（N1-N68）: 67个', 'NTRS路线事件（N1-N68）: 68个')
# Also check for other count references
c = c.replace('67 events', '68 events')
c = c.replace('67个', '68个')  # in NTRS context
print('✅ Step 1b: Updated range labels + counts')

# ============================================================
# Step 2: Insert new N33 after N32
# ============================================================
new_event = '''### 事件N33：凯尔的山洞——采样与被困

```yaml
事件: N33 凯尔的山洞——采样与被困
 触发条件: ntrs_awakened=100, acceptance>=70, kael_closeness>=45, 凯尔采集任务
    性行为等级: 7（接吻+相互手交指交+外阴摩擦·差一点插入——边缘性行为）
 情感阶段: B→C（凯尔从口到边缘——她守住了底线但给了一道缝）

    黎恩知情: 是——黎恩知情但不在场（事后最嫉妒的一次）
 第三者: 凯尔
 情境:
 - 凯尔在早餐时推了四次眼镜——东侧山洞的矿石样本对净化研究至关重要，但最近有魔兽出没的痕迹。
 一个人去不安全。黎恩看了菲娜一眼。她放下杯子——"我陪他去。"
 出发前黎恩在门口拉住她——手指穿过她指缝。"我不在的时候——不能进去。"
 菲娜脸红到耳根。"谁会进去！"甩开他的手——走出去时脚步比平时快了半拍。
 - 山洞比她想的更深。凯尔举着导力灯蹲在岩壁前——真的在工作。锤子敲下晶簇时碎光四溅——
 他推眼镜的角度和紧张时一模一样，但这次是专注。学者在自己的领域里有另一种从容。
 暴雨毫无征兆地砸下来——洞口在几分钟内变成水帘，出不去了。
 - 衣服湿透贴在身上。两人对视一眼——同时别开。篝火生起来后各自拧干外衣挂在石头上。
 凯尔摘了湿眼镜——没了镜片遮挡的深蓝眼睛让菲娜多看了一眼。他也在看她——锁骨、腰线、腿。
 不是偷看——是山洞太小。她没遮——因为他不是第一次看她的身体。但这次黎恩不在。
 凯尔走过来——脚步比任何时候都轻。他低头碰了她的嘴唇。没问。没推眼镜。没抖。
 菲娜没有推开。她站在篝火的光里让他吻——心跳快得不像掌控者。不是因为他吻得好——
 是因为她没想过要躲。他之前碰过她的胸她的性器——但从没吻过。这是最不该给别人的东西。
 - 吻变深后她的手在他手里——他的手在她腿间。互相。不是教与学——是两个人都在摸索。
 他的手指在她体内弯曲——角度已经不需要她纠正了。她的手指圈着他——脉搏在掌心下跳得快而轻。
 山洞里只有篝火噼啪和两个人压低的呼吸。
 - 他翻身压上来时呼吸全乱——性器抵在她腿间。龟头碰到入口——她伸手按住他胸口。
 "不能。答应过他的。"凯尔停住——深蓝眼睛里有雾但不是愤怒。手肘撑在她两侧。不动了。
 她看见他眼睛里的雾没散——不是不失望，是不敢说。沉默了两秒。然后她手指从自己腹上划过——
 "到这里。外面。"
 他的龟头沿外阴滑动——碾过那一点但不进去。最窄的门缝。她攥着他上臂指甲陷进去——
 不是因为痛，是因为"差一点"。他在她肚子上释放——液体温热地溅在皮肤上。
 他低头看着——推了推不存在的眼镜。"我差点——""差点。"她伸手指擦了一点——
 "但你停了。在我让你停的时候。"
 - 暴雨停后走出山洞——头发还没干。凯尔抱着矿石样本走在她旁边，嘴角压不住。
 占有欲确认:
 - 回到木屋。黎恩坐在桌旁——一眼就看出来了。不是看凯尔——凯尔低着头快步走过去了。是看她。
 头发没干。衣领没翻好。黎恩站起来——"发生了什么。"
 她的脸从脖子红到额头——不是羞愧，是不知道怎么开口让他不吃醋。
 她说了。山洞、暴雨、吻、手、手指、差点——"然后我让他在这里。"手指划过小腹。
 黎恩沉默了五秒——她见过他生气吃醋，没见过这种沉默。
 她伸手碰他脸——"我没让他进去。不是因为答应你。是因为——那个是你的。"
 黎恩把她拉到床上——那晚他占有的方式不一样。不是温柔，不是确认，是刻印。
 事后他手指停在她小腹上——"这里。他碰过的地方。"她点头。他低头吻了那个位置——"现在是我的了。"
 玩家选择:
 A. 让她全程自主应对 → trust+20, shared+15
 B. 事后详细追问每一处细节 → possess+30, bond+10
 变量: shared+22, possess+40, acceptance+10, kael_closeness+20, trust+18, bond+15, jealousy_marker+1
 核心: ★黎恩第一次不在场——从"参与注视"到"事后被告知"。第一次接吻——凯尔主动、菲娜没躲。
 手乳口都做过但从没吻过——嘴唇比性器更私密。外阴摩擦是到达过的最接近插入的距离——守住底线但给了一道缝。
 黎恩嫉妒的方式不是愤怒——是刻印覆盖。
```'''

# Find end of N32
m32 = re.search(r'### 事件N32[：:][^\n]*', c)
n32_start = m32.start()
# Find start of next event after N32
next_m = re.search(r'\n### 事件N3[4-9]|\n### 事件N[4-9]|\n### [A-Z]阶段|\n## ', c[n32_start+10:])
if next_m:
    insert_pos = n32_start + 10 + next_m.start()
else:
    insert_pos = len(c)

# Insert with proper spacing
c = c[:insert_pos] + '\n' + new_event + '\n' + c[insert_pos:]
print('✅ Step 2: New N33 inserted after N32')

# ============================================================
# Step 3: Validation
# ============================================================
# Count events
events = re.findall(r'### 事件(N\d{2})[：:]', c)
ntrs = sorted(set(e for e in events if e.startswith('N')), key=lambda x: int(x[1:]))
print(f'\n📊 NTRS events: {len(ntrs)} ({ntrs[0]}-{ntrs[-1]})')

# Check for duplicates
from collections import Counter
dupes = [eid for eid, count in Counter(ntrs).items() if count > 1]
if dupes:
    print(f'❌ DUPLICATES: {dupes}')
else:
    print('✅ No duplicates')

# Check for gaps
nums = sorted(int(e[1:]) for e in ntrs)
expected = list(range(nums[0], nums[-1] + 1))
gaps = [n for n in expected if n not in nums]
if gaps:
    print(f'❌ GAPS: N{gaps}')
else:
    print('✅ No gaps in sequence')

# Check for old IDs (N33-N67 should not appear as event IDs anymore)
old_ids_still_present = []
for old_id in [f'N{i}' for i in range(33, 68)]:
    pattern = re.compile(rf'(?<![A-Za-z0-9]){old_id}(?!\d)')
    if pattern.search(c):
        # Check if it's a legitimate reference (not an event ID)
        old_ids_still_present.append(old_id)
if old_ids_still_present:
    print(f'⚠️  Old IDs still present: {old_ids_still_present[:10]}...')
else:
    print('✅ Old IDs fully shifted')

# ============================================================
# Write
# ============================================================
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)
print('\n✅ All done. File updated.')
