import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# Helper: find event by title, locate its 情境 first bullet, insert line before it
def insert_cause_before_first_bullet(event_title_slug, cause_line):
    global c
    # Find the event header
    pattern = r'(### 事件' + re.escape(event_title_slug) + r'[^\n]*\n.*?情境:\n)(\s*- )'
    m = re.search(pattern, c, re.DOTALL)
    if not m:
        print(f'  WARNING: pattern not found for {event_title_slug}')
        # Try broader: just find the header, then find 情境 near it
        header_pat = r'### 事件' + re.escape(event_title_slug)
        hm = re.search(header_pat, c)
        if hm:
            # Find next 情境 after this header
            after_header = c[hm.start():]
            ctx = re.search(r'(情境:\n)(\s*- )', after_header)
            if ctx:
                idx = hm.start() + ctx.start()
                prefix = c[:idx + len(ctx.group(1))]
                suffix = c[idx + len(ctx.group(1)):]
                c = prefix + cause_line + '\n' + suffix
                print(f'  OK (broad match): {event_title_slug}')
                return
        print(f'  FAILED: {event_title_slug}')
        return

    idx = m.start()
    prefix = c[:idx + len(m.group(1))]
    suffix = c[idx + len(m.group(1)):]
    c = prefix + cause_line + '\n' + suffix
    print(f'  OK: {event_title_slug}')

# N21
insert_cause_before_first_bullet(
    'N21：桌下之手——隐奸手交',
    '      - N19树后隐蔽游戏让菲娜发现"假装没人知道"比"有人看"更刺激。她找到黎恩——'
    '"下次——公共场合。"长桌会议是最好的舞台：同伴环绕、表面正经、桌下失控'
)

# N22
insert_cause_before_first_bullet(
    'N22：菲的裸足——猎兵的诚意',
    '      - 菲从玲那里听说了篝火边的事。猎兵不绕弯——训练后直接问黎恩："听说你喜欢脚。"'
    '黎恩没否认。她点头——脱了靴子。不是勾引是诚意：想看就看。不像菲娜精致——但很诚实'
)

# N19 (now between N22 and N23)
insert_cause_before_first_bullet(
    'N19：树后的秘密——打飞机与口交',
    '      - N18.6足崇拜之后凯尔看菲娜脚的眼神变了——像在看一本还想继续翻的书。'
    '菲娜和黎恩商量后决定试试隐蔽场景——"假装偷情"。凯尔是唯一会当真以为这是秘密的人'
)

# N23
insert_cause_before_first_bullet(
    'N23：桌下之口——隐奸口交',
    '      - N21手交成功后菲娜胆子更大了——桌下手是前菜。这次她钻到桌子下面：'
    '在同伴环绕中让黎恩保持扑克脸比任何直接刺激都更让她兴奋'
)

# N24
insert_cause_before_first_bullet(
    'N24：第一次双人共享',
    '      - N18.5/N18.6之后凯尔和乔治都已是"自己人"——一个从摸黑丝学会靠近、一个从足崇拜学会主动。'
    '菲娜想试同时处理两人。"他们两个——我都信任。不会失控。"'
)

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

print('\nAll causes inserted OK')
