"""
插入新事件N35(乔治舔穴)+N35-N68→N36-N69重编号
"""
import re

FILE = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# ============================================================
# Step 1: Renumber N35-N68 → N36-N69 (single pass, word boundary)
# ============================================================
def shift_id(m):
    num = int(m.group(1))
    if 35 <= num <= 68:
        return f'N{num + 1}'
    return m.group(0)

c = re.sub(r'(?<![A-Za-z0-9])N(\d{2})(?!\d)', shift_id, c)
print('✅ Step 1: N35-N68 → N36-N69')

# Fix range labels
c = c.replace('N1-N68', 'N1-N69')
c = c.replace('N01-N68', 'N01-N69')
c = c.replace('68个', '69个')
c = c.replace('68 events', '69 events')
print('✅ Step 1b: Updated range labels + counts')

# ============================================================
# Step 2: Insert new N35 after N34
# ============================================================
new_event = '''### 事件N35：乔治的唇——意外的美味

```yaml
事件: N35 乔治的唇——意外的美味
 触发条件: ntrs_awakened=100, acceptance>=68, george_closeness>=42
    性行为等级: 6（舔穴·男→女——乔治的第一次为她口交）
 情感阶段: C（享受被服务——从被舔到高潮，黎恩提出下一步可能）

    黎恩知情: 是——黎恩邀请乔治，中途回来撞见
 第三者: 乔治
 情境:
 - 黎恩在走廊上截住乔治——"今晚陪陪她。不用我告诉你做什么——她已经知道怎么开始了。"
 乔治推了三次眼镜——这次没问"真的可以吗"。他已经知道了。
 - 木屋。菲娜靠在床头——看到他进来，嘴角弯了一下。不是害羞——是已经想好要干什么。
 "过来。"乔治坐到床边——她倾身靠近，手指先碰他锁骨再滑到胸口。"上次——你喜欢吗。"
 乔治耳朵红了——点头。她解开他的扣子——节奏不紧不慢。手覆上他的腹部，感觉到肌肉跳了一下。
 她低头笑了一声——"你比上次更紧张。""因为——"他推眼镜，"这次没有别人。只有你。"
 - 然后他做了一件她没想到的事。他把她推倒在床上——动作很轻但意图明确。从她的锁骨往下吻——胸、肋、腹——
 然后掰开她的腿。她以为他会用手——上次他就是用手。但他把脸埋进了她腿间。
 舌尖碰到那一点时她腰弹了一下——不是艾德里安那种熟练的从容。是笨拙但认真——每一处都停很久。他的舌头找到她最敏感的位置—
 然后停在那里反复——像修导力装置一样专注。她手指插进他头发——娇喘从喉咙深处溢出来。不是演的。
 - "没想到——"乔治从她腿间抬起头，嘴唇还是湿的——"这么好吃。"
 菲娜用手臂挡住眼睛——脸红了。不是因为被舔——是因为他说这话的时候还在舔嘴唇像刚发现新元素。他低头继续——这次更投入。
 她的娇喘声越来越大——乔治的裤子顶起来了但她没空管。高潮时她腿夹紧他的头——手攥着床单——叫了一声。
 - 门开了。黎恩站在门口。
 画面：菲娜瘫在床上腿还在抖，乔治跪在床边嘴唇湿透裤子撑起帐篷。
 乔治整个人冻结——"我...她...你让我..."黎恩抬手——"我知道。"
 乔治以最快速度穿好衣服退出房间——眼镜歪了。
 占有欲确认:
 - 黎恩走到床边——低头看她。高潮余韵还在她脸上——琥珀色眼睛半睁半闭。
 "好吃。"他重复了一遍乔治的话——语气不是嘲讽是玩味。她用手臂挡住脸——"你听到了多少。""全部。"
 他坐在床沿手指抚过她腿间——还在颤。"他让你到了。"她点头——移开手臂看着他。
 "我在想——"黎恩的手指停在她入口处——"下次。要不要尝试——真的进去。"
 她整个人顿了一下。然后摇头——"不要。不是现在。"他点头——没追问。但她知道他听到了。
 - 那晚躺在他身边闭着眼——脑海里反复回放那句"要不要尝试真的进去"。拒绝是条件反射——但画面留下来
 了。她想了几遍——不是想乔治，不是想艾德里安——是想"不是黎恩的"。那个念头让她心跳快了半拍。
 然后又想到低语者——差点被插入那次——她蜷了一下。怕。可又——
 她翻了个身把脸埋进黎恩胸口。先不想了。
 玩家选择:
 A. 让她自己决定节奏 → trust+25, shared+15
 B. 主动推进"下次可以试试" → possess+30, acceptance+20
 变量: shared+20, possess+25, acceptance+15, george_closeness+20, trust+15, bond+12
 核心: ★乔治第一次舔穴——从指交到口交的递进。笨拙但认真——"这么好吃"的感叹是纯学术惊喜。
 黎恩主动提出"下次尝试真的进入"——首次将插入提上议程。菲娜口头拒绝但内心反复回放画面。
 想到低语者——怕但又想——为后续事件（低语者回访/第一次插入）埋下双重伏笔。
```'''

# Find N34 end
m34 = re.search(r'### 事件N34[：:][^\n]*', c)
n34_start = m34.start()
next_m = re.search(r'\n### 事件N3[6-9]|\n### 事件N[4-9]|\n### [A-Z]阶段|\n## ', c[n34_start+10:])
if next_m:
    insert_pos = n34_start + 10 + next_m.start()
else:
    insert_pos = len(c)

c = c[:insert_pos] + '\n' + new_event + '\n' + c[insert_pos:]
print('✅ Step 2: New N35 inserted after N34')

# ============================================================
# Validation
# ============================================================
events = re.findall(r'### 事件(N\d{2})[：:]', c)
ntrs = sorted(set(e for e in events if e.startswith('N')), key=lambda x: int(x[1:]))
from collections import Counter
dupes = [eid for eid, count in Counter(ntrs).items() if count > 1]
nums = sorted(int(e[1:]) for e in ntrs)
gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in nums]
print(f'📊 {len(ntrs)} events ({ntrs[0]}-{ntrs[-1]})')
print(f'   Dupes: {dupes if dupes else "none"} ✅')
print(f'   Gaps: {gaps if gaps else "none"} ✅')

# Update mapping table
old_mapping = '| N35 | 第二次共享——多低语者强迫口交手交 | 低语者×3 |'
new_mapping = '| N35 | 乔治的唇——意外的美味 | 乔治 |\n| N36 | 第二次共享——多低语者强迫口交手交 | 低语者×3 |'
if old_mapping in c:
    c = c.replace(old_mapping, new_mapping)
    print('✅ Mapping table updated')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)
print('✅ Done.')
