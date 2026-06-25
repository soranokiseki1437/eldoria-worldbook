import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    text = f.read()

details = {
    # === 早期：嘴笨，只会基本含吐 ===
    'N29': ' - 她的舌头不知道该放哪。给黎恩口交时舌头有自己的记忆，给这个人没有。只能嘴唇裹紧、头上下动——最基本的吞吐。牙齿不小心刮到龟头时艾德里安的腹肌抽了一下，她赶紧松开嘴，用舌尖碰了碰刮到的地方——无声的对不起',
    'N32': ' - 这次她学会了用舌面在龟头底部平扫——上次发现那里最敏感。但还不敢舔别处。嘴在动的时候手只能握着根部不动——手和嘴还没学会同时做两件事',

    # === 中期：舌头灵活，手开始配合 ===
    'N35': ' - 她蹲下去之前往手心吐了点口水——从艾玛那里学的，润滑会让手和嘴的配合更顺。先用舌尖在龟头边缘画了一圈，等他呼吸乱了才含进去。舌头在嘴里不是平躺着——会卷，会在肉棒进出的时候用舌面裹住它。右手握着根部配合嘴的节奏——嘴里进的时候手退，嘴里退的时候手进',
    'N43': ' - 她跪在艾德里安面前给他口交时左手也没闲着——手指在乔治的肉棒上做着完全不同的节奏。嘴在一个人身上，手在另一个人身上，两个节奏互不干扰。她发现自己的舌头现在可以在含住的时候独立做小动作了——舌尖顶着龟头下方那个凹陷处，同时嘴唇还在上下动',

    # === 后期：舔蛋，手口协调，老手从容 ===
    'N64': ' - 她不只是含。舌头沿着龟头边缘慢慢绕圈，然后从顶端一路舔到根部——再往下。嘴唇松开肉棒，舌尖碰到囊袋的时候雷恩的呼吸断了。她抬头看了他一眼——你这里没被人碰过。然后把蛋蛋含进嘴里，手同时握着肉棒上下套弄。嘴和手各管一处，节奏不同但配合得像练了上百次',
    'N67': ' - 巷子里三分钟。她的舌头比嘴唇更忙——舔、卷、点、压，每一下都在不同的位置。含到深处时喉咙能放松到吞下整个龟头，退出来时舌尖还在马眼上勾一下。右手握根部控制深度，左手托囊袋——手指轻轻揉捏。三分钟不是因为她急，是因为他知道她能做到。她做到了',
    'N69': ' - 桌下只有她一个人——手口并用。舌头灵活得不像是200年前那个连接吻都不会的精灵。舌尖快速弹动龟头系带的同时手指在根部打圈，然后突然一口吞到底——喉咙的肌肉学会了主动吞咽而不是被动接受。艾德里安在桌上写的字从报告变成了鬼画符',
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
