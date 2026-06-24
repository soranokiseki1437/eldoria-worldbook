import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

# === N21: add cause before first bullet ===
# Find: 情境:\n      - 长桌会议——菲娜坐黎恩旁假装看净化地图
old = '      - 长桌会议——菲娜坐黎恩旁假装看净化地图'
new = '''      - N19树后隐蔽游戏让菲娜发现"假装没人知道"比"有人看"更刺激。她找到黎恩——
        "下次——公共场合。"长桌会议是最好的舞台：同伴环绕、表面正经、桌下失控
      - 长桌会议——菲娜坐黎恩旁假装看净化地图'''
assert old in c, 'N21 pattern not found'
c = c.replace(old, new, 1)
print('N21 cause OK')

# === N22: add cause before first bullet ===
old = '      - 训练后菲坐石头脱过膝袜——早知道黎恩在看。抬赤裸脚——脚底薄茧脚背旧伤疤。不像菲娜好看——但很诚实'
new = '''      - 菲从玲那里听说了篝火边的事。猎兵不绕弯——训练后直接问黎恩："听说你喜欢脚。"
        黎恩没否认。她点头——脱了靴子。不是勾引是诚意：想看就看。不像菲娜精致——但很诚实
      - 训练后菲坐石头脱过膝袜——早知道黎恩在看。抬赤裸脚——脚底薄茧脚背旧伤疤。不像菲娜好看——但很诚实'''
assert old in c, 'N22 pattern not found'
c = c.replace(old, new, 1)
print('N22 cause OK')

# === N19: add cause before first bullet ===
old = '      - 密林深处。菲娜和黎恩商量后决定试试隐蔽场景。凯尔被叫到指定树下——'
new = '''      - N18.6足崇拜之后凯尔看菲娜脚的眼神变了——像在看一本还想继续翻的书。
        菲娜和黎恩商量后决定试试隐蔽场景——'假装偷情'。凯尔被叫到指定树下——'''
assert old in c, 'N19 pattern not found'
c = c.replace(old, new, 1)
print('N19 cause OK')

# === N23: add cause before first bullet ===
old = '      - 同样长桌会议——这次她滑到桌面下。菲问菲娜去哪了亚莉莎答去取数据。'
new = '''      - N21手交成功后菲娜胆子更大了——桌下手是前菜。这次她想要更多：
        在同伴环绕中让黎恩保持扑克脸比任何直接刺激都更让她兴奋。
      - 同样长桌会议——这次她滑到桌面下。菲问菲娜去哪了亚莉莎答去取数据。'''
assert old in c, 'N23 pattern not found'
c = c.replace(old, new, 1)
print('N23 cause OK')

# === N24: add cause before first bullet ===
old = '      - 篝火暗红余烬。菲娜坐中间——左边乔治右边凯尔。两人都紧张——'
new = '''      - N18.5/N18.6之后凯尔和乔治都已是"自己人"——一个从摸黑丝学会靠近、一个从足崇拜学会主动。
        菲娜想试同时处理两人。"他们两个——我都信任。不会失控。"黎恩点头。
      - 篝火暗红余烬。菲娜坐中间——左边乔治右边凯尔。两人都紧张——'''
assert old in c, 'N24 pattern not found'
c = c.replace(old, new, 1)
print('N24 cause OK')

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(c)

print('All cause bridges added OK')
