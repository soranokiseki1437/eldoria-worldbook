import sys

filepath = r'C:\Users\lx\Desktop\世界书\docs\05_事件系统.md'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the N17 event block
start = content.find('事件: N17 艾德里安的指尖')
if start == -1:
    print('ERROR: Could not find N17 event')
    sys.exit(1)

# Find the end of the event (closing ```)
end = content.find('```', content.find('首次出现', start))
if end == -1:
    print('ERROR: Could not find end of N17 event')
    sys.exit(1)

# Include the closing ```
end = end + 3

old_block = content[start:end]
print('=== OLD BLOCK (first 300 chars) ===')
print(old_block[:300])
print('...')
print()

new_block = '''事件: N17 艾德里安的指尖——从容的探索
 触发条件: ntrs_awakened=100, acceptance>=56, adrian_closeness>=30
    性行为等级: 3（指交·男→女——艾德里安的首次触碰）
 情感阶段: B（从容的对手展示——他不催，所以她主动找上门）

    黎恩知情: 是——黎恩坐窗台上
 第三者: 艾德里安
 情境:
 - 艾德里安的手指让她发出了一声自己从没听过的喘息。她愣了一下，然后没再忍，第二声直接漏出来了
 - 之后艾德里安没有催过，没有暗示、没有眼神、没有"顺便路过"。
 几周过去像什么都没发生。他的耐心就是他的从容。菲娜主动找到黎恩，
 "我去找他。因为他不会催我，所以我才准备好了。"
 - 艾德里安府邸私室。他请她坐下，不是床是椅子。"你需要掌控。坐这里。
 高度刚好。"他跪在她腿间，跪得优雅不像雷恩单膝像在完成某个仪式。
 手指修长灵活先落在她膝盖上，不像雷恩那样停顿三次。
 "我可以吗。"不是请求不是确认，是让她回答她自己。
 菲娜点头
 - 手指缓慢插入——他的节奏和雷恩完全不同。雷恩是郑重翻阅古籍——他是从容翻一页已经知道下一页的内容。
 拇指在外按压时食指在内弯曲，找到阴蒂时没有问对不对只是停了半秒听她吸气声。
 她在高潮的边缘犹豫——他抬眼看她：不用忍。然后把她推过去。一阵酥麻从脊柱窜上后脑，和黎恩的触感不同、但同样让人腿软。
 手指抽出来时沾满了淫水，他低头看了一眼。"你的身体。很诚实。"
 占有欲确认:
 - 结束后她腿还在抖。转向黎恩。"他不一样。雷恩让我安心——他让我失控。"
 黎恩从窗台下来走到她面前，把手指放进她嘴里。"尝一下。混在一起了。"
 她含住，眼睛看着黎恩。是你的和他的。分不清了。
       她松开手指。'和你的混在一起了。'黎恩把她拉近。'分得清吗。'她笑。'分不清。所以才是你的。'
 变量: shared+22, possess+25, acceptance+12, adrian_closeness+15
 核心: 艾德里安指交——和雷恩摸乳形成对照：雷恩停顿三次，艾德里安不用停顿；
 雷恩问不可以，艾德里安让她问自己。从容来自不催促——他自荐后等了数周，
 等到菲娜主动上门。首次出现"让她失控"的第三者类型。'''

# Add yaml fence
yaml_prefix = '```yaml\n'
new_block_full = yaml_prefix + new_block + '\n```'

if old_block == new_block_full:
    print('No changes detected.')
    sys.exit(0)

# Count dashes before and after
old_dashes = old_block.count('——')
new_dashes = new_block_full.count('——')
print(f'Dashes: {old_dashes} -> {new_dashes}')

# Check for euphemism fix
if '进入' in old_block and '插入' in new_block_full:
    # Only report if the 进入 was replaced
    old_has_jinru = '缓慢进入——' in old_block
    new_has_charu = '缓慢插入——' in new_block_full
    if old_has_jinru and new_has_charu:
        print('Euphemism: 手指缓慢进入 -> 手指缓慢插入')

content = content.replace(old_block, new_block_full, 1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done.')
