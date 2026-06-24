with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# N47: full rewrite
old_n47_header = '### 事件N47：欲望之镜'
i = c.find(old_n47_header)
ys = c.find('```yaml', i)
ye = c.find('```', ys+7)

new_n47_yaml = '''事件: N47 欲望之镜——镜湖倒影
    触发: ntrs_awakened=100, exploration>=45, 镜湖
    性行为: 9+（插入·镜湖倒影·雷恩+凯尔同时）
    情感: C→D（三重视线——她在倒影中看到自己被两个人占有）
    黎恩知情: 是——在对岸同时看到真实和倒影
    第三者: 雷恩+凯尔
    情境:
      - 镜湖水面如镜。菲娜在湖岸被雷恩从正面进入——凯尔在身后覆上来。
        湖面倒影里她看到自己被两个人同时占有——不是恐惧是好奇。
        原来我的身体可以同时容纳两种节奏
      - 黎恩在对岸——看着真实的她和倒影中的她同时被进入。
        她透过倒影与他对视——他在看我。我在看我自己。我们都在看同一件事
      - 结束后湖面平息。她涉水走向黎恩——在倒影里看到自己走向他。抬头——
        你在镜子里看到什么？看到你回来。她靠进他怀里——
        湖面现在只映着月光和两个人
    占有欲确认:
      - 她抬头——你看到的不是幻想。是真的。我回来了。
    变量: shared+30, possess+25, acceptance+15, trust+15
    核心: 三重视线——黎恩看她，她看倒影，倒影中她看黎恩。不是湖的魔法是镜面的物理，折射的是欲望。'''

c = c[:ys+7] + '\n' + new_n47_yaml + '\n' + c[ye:]

# N48: fix format
old_n48 = '    第三者 触发: ntrs_awakened=100, acceptance>=60, shared>=52'
new_n48 = '    第三者: 乔治\n    触发: ntrs_awakened=100, acceptance>=60, shared>=52'
c = c.replace(old_n48, new_n48)

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)
print('N47 rewritten, N48 fixed')
