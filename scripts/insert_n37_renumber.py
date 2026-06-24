"""
插入新事件N37(凯尔·第一次人类插入)+N37-N69→N38-N70重编号
"""
import re

FILE = 'C:/Users/lx/Desktop/世界书/docs/05_事件系统.md'
with open(FILE, 'r', encoding='utf-8') as f:
    c = f.read()

# Step 1: Renumber N37-N69 → N38-N70
def shift_id(m):
    num = int(m.group(1))
    if 37 <= num <= 69:
        return f'N{num + 1}'
    return m.group(0)

c = re.sub(r'(?<![A-Za-z0-9])N(\d{2})(?!\d)', shift_id, c)
print('✅ Step 1: N37-N69 → N38-N70')

c = c.replace('N1-N69', 'N1-N70')
c = c.replace('69个', '70个')
c = c.replace('69 events', '70 events')
print('✅ Step 1b: Range labels + counts')

# Step 2: Insert new N37 after N36
new_event = '''### 事件N37：凯尔的清晨——黑丝与第一次插入

```yaml
事件: N37 凯尔的清晨——黑丝与第一次插入
 触发条件: ntrs_awakened=100, acceptance>=75, kael_closeness>=50, 清晨时段
    性行为等级: 9（插入·第一次被黎恩以外的人进入——凯尔）
 情感阶段: C（第一次人类插入——痛但跨过了，只有黎恩能真正满足她）

    黎恩知情: 是——黎恩全程在窗外观看
 第三者: 凯尔
 情境:
 - 低语者那次之后菲娜平静了几天。她知道自己可以喊停——黎恩会出手。但她也知道一件事没变：
 那句"要不要尝试真的进去"还在她脑子里。不是怕了——是准备好了。不是准备好享受。是准备好面对。
 她找到黎恩——"凯尔。"他只说了这两个字。他懂了。
 - 清晨。菲娜穿着黑丝袜推开凯尔的房门——他还在睡，眼镜放在床头。她跪到床边——
 丝袜摩擦地面的声音让他动了动睫毛。她低头含住他——隔着内裤。凯尔惊醒——深蓝眼睛对上她的琥珀色。
 "菲——"她没让他说完。拉开内裤——直接含进去。他在她嘴里硬起来——手指插进自己头发里。
 "这是——现在是早上——"她松口——唇间牵着银丝。"嗯。早上。"
 - 凯尔看到了黑丝。他的目光从她的嘴唇移到腿——丝袜在晨光里泛着微光。他伸手碰她小腿——
 指尖沿丝袜纹路往上滑。然后他低头——嘴唇贴上黑丝，从膝盖内侧一路往上。她听见他吸了一口气——
 丝袜的气息混着她的体温。不是变态——是像在研究一种很久以前就想触碰的材质。她伸手按住他后脑。
 "可以了。进来。"
 - 他进入时她指甲陷进了他肩膀——不是因为舒服。痛。不是撕裂的痛——是陌生的痛。黎恩之外的人。
 不一样的角度、不一样的尺寸——和黎恩给她的满胀感完全不同。凯尔停住了——"疼吗？"她咬着嘴唇——
 点了头。但手没从他肩上松开。"继续。慢一点。"
 他慢了——慢到几乎停下来。她闭着眼睛——感觉到的不是快感，是"不是黎恩的"。每一次摩擦都在提醒她。
 但她能承受。不是崩溃——只是不舒服。她睁开眼——窗户方向。黎恩站在外面。灰色眼睛与她对视。
 她没移开——看着他，让凯尔在自己体内抽送。他的视角：黑丝包裹的小腿架在凯尔肩上，她的脸因为不适微微皱着——
 但她的眼睛在看他。不是求助——是确认。你看。我做到了。
 - 凯尔释放时她轻轻抚了他的背——"很好。"不是假话——他真的很好。温柔、克制、每一下都在问她。
 只是她的身体还没准备好接受别人的形状。她穿回黑丝——腿间有他的痕迹和她的不适应。
 占有欲确认:
 - 回到木屋。黎恩已经在门口——她直接把自己塞进他怀里。他没问——把她抱起来放倒在床上。
 接下来的一次不是温柔——是她要的那种。满胀、猛烈、完全吻合。她在他身下高潮时叫得比任何一次都响——
 不是表演——是真的需要。只有黎恩能填满的角度。只有黎恩。
 事后她趴在他胸口——腿还在他腿上。"疼。"她轻声说。"不是你的。是他的。"
 黎恩手指穿过她发丝——"以后还要吗。"她沉默了一会儿。"不知道。但这次——我跨过去了。"
 他收紧手臂——"我看到了。全部。你一直在看我。"她抬头——"因为是你让我去的。所以我每次闭眼——都睁开找你。"
 变量: shared+28, possess+50, acceptance+20, kael_closeness+25, trust+20, bond+15, first_insertion_marker+1
 核心: ★第一次被黎恩以外的人进入——选择了凯尔。体验并不好——痛、不舒服、陌生的形状——但她跨过去了。
 黑丝是给凯尔的礼物也是给黎恩的画面。全程窗外对视——她不是在和他做，是在为黎恩做。
 结束后找黎恩疯狂做——确认：只有黎恩的身体与她完全吻合。首插不是享乐的顶点，是仪式性的跨越。
```'''

# Find N36 end
m36 = re.search(r'### 事件N36[：:][^\n]*', c)
n36_start = m36.start()
next_m = re.search(r'\n### 事件N3[89]|\n### 事件N[4-9]|\n### [A-Z]阶段|\n## ', c[n36_start+10:])
if next_m:
    insert_pos = n36_start + 10 + next_m.start()
else:
    insert_pos = len(c)

c = c[:insert_pos] + '\n' + new_event + '\n' + c[insert_pos:]
print('✅ Step 2: New N37 inserted after N36')

# Validation
events = re.findall(r'### 事件(N\d{2})[：:]', c)
ntrs = sorted(set(e for e in events if e.startswith('N')), key=lambda x: int(x[1:]))
from collections import Counter
dupes = [eid for eid, count in Counter(ntrs).items() if count > 1]
nums = sorted(int(e[1:]) for e in ntrs)
gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in nums]
print(f'📊 {len(ntrs)} events ({ntrs[0]}-{ntrs[-1]})')
print(f'   Dupes: {dupes if dupes else "none"} ✅')
print(f'   Gaps: {gaps if gaps else "none"} ✅')

# Update mapping table - need to insert N37 entry before N38
old = '| N38 | 半开的门——隐奸游戏 | 乔治 |'
new = '| N37 | 凯尔的清晨——黑丝与第一次插入 | 凯尔 |\n| N38 | 半开的门——隐奸游戏 | 乔治 |'
if old in c:
    c = c.replace(old, new)
    print('✅ Mapping table updated')
else:
    print('⚠ Mapping entry not found, checking...')
    # Try to find the mapping section
    for line in c.split('\n'):
        if 'N38' in line and '半开' in line:
            print(f'  Found: {line.strip()}')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(c)
print('✅ Done.')
