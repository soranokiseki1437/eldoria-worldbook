# -*- coding: utf-8 -*-
import re

files = [
    '方案/第一批次_故事1-3章节正文.md',
    '方案/第二批次_故事4-7章节正文.md',
    '方案/第三批次_故事8-10章节正文.md'
]

# Rules for replacing bullet 1 start:
# "午后，" -> "某日午后，"
# "傍晚，" -> "某日傍晚，"
# "清晨，" -> "某日清晨，"
# "黄昏，" -> "某日黄昏，"
# "薄暮中的" -> "某日黄昏，" or "第二天午后，"
# "更衣内帐" -> "第二天午后，更衣内帐" or keep as is? Wait, the user said:
# "全部改成某日午后/某日清晨或第二天午后"

for f in files:
    content = open(f, 'r', encoding='utf-8').read()
    
    # Batch 1
    content = content.replace("  - 午后，光晶矿坑", "  - 某日午后，光晶矿坑")
    content = content.replace("  - 午后，矮人之屋地下", "  - 某日午后，矮人之屋地下")
    content = content.replace("  - 傍晚，心木废墟古堡", "  - 某日傍晚，心木废墟古堡")
    
    # Batch 2
    content = content.replace("  - 清晨，重型锻造区", "  - 某日清晨，重型锻造区")
    content = content.replace("  - 锻造石窟内，水力风箱", "  - 第二天清晨，锻造石窟内，水力风箱")
    content = content.replace("  - 黄昏，薄暮悄然漫过", "  - 某日黄昏，薄暮悄然漫过")
    content = content.replace("  - 薄暮中的兵械室内，长桌", "  - 没过多久，长桌") # wait, or 第二天黄昏?
    content = content.replace("  - 午后，初冬的寒意悄然", "  - 某日午后，初冬的寒意悄然")
    content = content.replace("  - 更衣内帐的门帘后，菲娜", "  - 同一日午后，更衣内帐的门帘后，菲娜")
    content = content.replace("  - 午后，一场冰冷的暴雨", "  - 某日午后，一场冰冷的暴雨")
    content = content.replace("  - 冰冷的暴雨密密麻麻敲击", "  - 暴雨倾盆的午后，冰冷的雨水密密麻麻敲击")
    
    # Batch 3
    content = content.replace("  - 傍晚，夕阳的金辉斜斜", "  - 某日傍晚，夕阳的金辉斜斜")
    content = content.replace("  - 清晨，西侧密林深处", "  - 某日清晨，西侧密林深处")
    content = content.replace("  - 哨棚顶上的通气木缝旁", "  - 同一日清晨，哨棚顶上的通气木缝旁")
    content = content.replace("  - 午后，矮人之屋深处的", "  - 某日午后，矮人之屋深处的")
    content = content.replace("  - 虚掩的门缝外，亚尔缇娜", "  - 同一日午后，虚掩的门缝外，亚尔缇娜")
    
    with open(f, 'w', encoding='utf-8') as out:
        out.write(content)
    print(f"Processed {f}")

