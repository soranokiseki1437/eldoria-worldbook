import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()

details = {
    # === 低语者/群交接受递进 ===
    'N11': ' - 第一次面对低语者。她裸露在它面前时攥紧了黎恩的手——指节发白。低语者失控后她被黎恩抱在怀里还在发抖。不是后悔——是第一次触碰到了"共享"的边界：不是所有人都可控。这个认知让她恐惧，也让她好奇',
    'N36': ' - 三个低语者同时出现。这次是她选的——主动挑战而非被动面对。但当数量超出预期、当嘴里和背后的肉棒同时逼近时，她还是慌了。不是后悔——是"我以为我准备好了但好像还没有"。拼命摇头是信号。黎恩出手的那一刻她松了一口气——不是解脱，是被接住',
    'N43': ' - 四个人。她赤裸站中央——这次不是恐惧不是被迫。是她设计的游戏。她对黎恩伸手——邀请他加入。从第一次被低语者吓得发抖到现在赤身站在三个男人中间伸手请爱人进来，中间隔着的不是距离，是77次选择',
    'N56': ' - 花田。三个人。她被夹在雷恩和乔治中间——叫出声时惊飞了鸟，然后笑了。花田3P和废墟里的轮奸不一样——这里是阳光、花瓣、信任的人。她会笑了。从恐惧到游戏设计者到能在花田里被操得笑出声。这是递进',
    'N74': ' - 催情茶。两个人。但这两个人是黎恩和雷恩——她最信任的。平时最温柔的两个人同时失控，她被夹在中间。不是低语者的恐惧、不是花田的游戏——是被最珍视的人狂暴需要。她在害羞和欲望之间哭了。不是因为痛苦——是因为这两个人同时对她失控。被需要到这种程度，200年来第一次',
    'N75': ' - 五六个低语者。她跪在废墟中央。从第一次面对一只低语者时攥紧黎恩的手发抖，到主动挑战三只但还要黎恩救援，到设计四个人的游戏，到花田里被操笑——现在她独自面对五六只，没有求救。嘴里那根第一个射时她咽下去了。从第一次面对一只低语者时的恐惧到今天咽下第一口的接受，这条线不是堕落，是信任的扩容。她的极限不是身体能承受多少，是心能容纳多少',
}

count = 0
for eid, detail in details.items():
    pattern = r'(### 事件' + eid + r'[：:][^\n]+\n\n```yaml\n)'
    m = re.search(pattern, text)
    if not m: print(f'x {eid}'); continue
    block_start = m.end()
    chunk = text[block_start:]
    end_bt = chunk.find('\n```')
    if end_bt < 0: print(f'x {eid} end'); continue
    block = chunk[:end_bt]
    qj = re.search(r'(\s*情境[：:][^\n]*\n)', block)
    if not qj: print(f'x {eid} qj'); continue
    insert_pos = block_start + qj.end()
    text = text[:insert_pos] + detail + '\n' + text[insert_pos:]
    count += 1
    print(f'+ {eid}')

with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(text)
print(f'Done: {count}/{len(details)}')
