file_01 = r'd:\Siegfried\世界书\方案\第二部\主线与世界扩充方案\前十幕大调查工作区\01_全量设定卡基准白名单与地理时空总表.md'

with open(file_01, 'r', encoding='utf-8') as fp:
    c = fp.read()

replaces = [
    ('会议厅 | `LOC_D2_04`', '会议厅 | `LOC_D2_42`'),
    ('艾斯特雷亚别邸 | `LOC_D2_26`', '艾斯特雷亚别邸 | `LOC_D2_04`'),
    ('镜湖 | `LOC_D2_28`', '镜湖 | `MAG_D2_05`'),
    ('南部沼泽 | `LOC_D2_09`', '南部沼泽 | `LOC_D2_07`'),
    ('边境猎屋 | `LOC_D2_27`', '边境猎屋 | `LOC_D2_09`'),
    ('隐士石泉 | `LOC_D2_42`', '隐士石泉 | `LOC_D2_38`'),
    ('天线观测台 | `LOC_D2_38`', '天线观测台 | `LOC_D2_26`'),
    ('边境机房 | `LOC_D2_45`', '边境机房 | `LOC_D2_27`'),
    ('帝都图书馆 | 跨界 |', '帝都图书馆 | `LOC_D2_28` |'),
]

for old, new in replaces:
    if old in c:
        c = c.replace(old, new)
        print(f'Replaced: {old} -> {new}')
    else:
        print(f'NOT FOUND: {old}')

with open(file_01, 'w', encoding='utf-8') as fp:
    fp.write(c)

print('Done writing 01!')
