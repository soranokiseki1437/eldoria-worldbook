import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()

# N23: merge duplicate hand-reaching bullets
text = text.replace(
    ' - 她端着茶杯的左手纹丝不动。桌面上的讨论还在继续，她用全副精力压制喉咙里那声闷哼\n'
    ' - 她的手在桌下伸出去又缩回来，深呼吸了两次，第三次才碰到他的拉链。桌面上她端着茶杯的手纹丝不动',
    ' - 她的手在桌下伸出去又缩回来，深呼吸了两次，第三次才碰到他的拉链。桌面上的讨论还在继续，她端着茶杯的左手纹丝不动，全副精力压在喉咙里'
)

# N37: remove duplicate "他进入时她指甲陷进他肩膀——痛" (my injection already covers first-time pain)
text = text.replace(
    ' - 他进入时她指甲陷进他肩膀——痛。陌生的痛。黎恩之外的人——不一样的角度、不一样的尺寸。\n',
    ''
)

# N66: remove duplicate opening moments (keep the best one)
# Remove bullet 3 (weaker duplicate)
text = text.replace(
    ' - 黎恩进门时她回头看他——嘴角有精液。"你回来了。"语气和说"晚饭好了"一样。然后笑了笑\n',
    ''
)
# Remove bullet 4 (weaker duplicate)
text = text.replace(
    ' - 黎恩进门时她正在凯尔身上——回头看他。嘴角有精液。"你回来了。"语气平静，但耳尖是红的——不是羞耻，是被爱的温度\n',
    ''
)

# N67: remove duplicate countdown bullet
text = text.replace(
    ' - 巷子里。蹲下去之前在心里倒数了三秒——每次都这样。已经是老手了，但每次"开始"的前三秒心跳还是会快到喉咙口\n',
    ''
)
# N67: fix 喉结 again
text = text.replace(
    '菲娜从巷口出来——喉结动了一下，咽下去了。',
    '菲娜从巷口出来——喉咙轻轻动了一下，咽下去了。'
)

# N66: keep the merged "回头+含鸡巴+睫毛颤" version as best
# Check it exists, if not add it back
if '黎恩进门时她回了头——嘴里还含着凯尔' not in text:
    print('WARNING: N66 best version missing')

with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('Dedup done')
