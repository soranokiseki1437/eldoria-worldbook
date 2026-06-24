"""Clean all NTRS events: remove 圣光/腐化神棍描述 + 删事件编号互引"""
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c = f.read()

# ===== 1. Event number cross-references =====
# N58: "和N11一样" / "呼应N11"
c = c.replace(
    '- 事后：趴胸口不说话。手指在他锁骨画圈——和N11一样但没笑。这是她身体写给他的信',
    '- 事后：趴胸口不说话。手指在他锁骨画圈——但没笑。这是她身体写给他的信')
c = c.replace(
    '呼应N11（手指画圈）——起点是"吃醋有趣"，终点是"我从未选过别人"。',
    '手指画圈从起点到终点——从"吃醋有趣"到"我从未选过别人"。')

# N53: "不是N22（她为黎恩服务）"
c = c.replace(
    '不是N22（她为黎恩服务）——是她为第三者服务黎恩旁观。游戏升级。',
    '不是她为黎恩服务——是她为第三者服务黎恩旁观。游戏升级。')

# N54: "比N53更进一步"
c = c.replace(
    '- 比N53更进一步——口交比手交更亲密更禁忌。她从容到可以在桌下含一个男人而桌面没人发现',
    '- 比手交更进一步——口交更亲密更禁忌。她从容到可以在桌下含一个男人而桌面没人发现')

# N19: "和N3的紧张寻求确认判若两人"
c = c.replace(
    '没看树的方向没做手势——和N3的紧张寻求确认判若两人',
    '没看树的方向没做手势——和最初时的紧张寻求确认判若两人')

# ===== 2. 圣光/腐化神棍描述 in NTRS events =====
# N7: 圣光从指尖乳尖渗出
c = c.replace(
    '圣光从指尖乳尖渗出形成金色雾。她克制呻吟腿想并拢却被膝盖分开。',
    '她克制呻吟腿想并拢却被膝盖分开。')

# H3: 圣光/腐化 rewrites
c = c.replace(
    '- 先灵的声音穿过腐化：守护者...你的圣光...会净化我们...但我们需要...触碰...需要...释放...',
    '- 先灵破碎的声音从紫色光芒中传来：守护者...我们需要...触碰...需要...释放...')
c = c.replace(
    '- 不是仪式——是轮奸。口交手交阴道插入同时进行。低语者不是温柔的不是礼貌的——是200年被腐化压抑后的爆发。她在他们中间——被填满每一处',
    '- 不是仪式——是轮奸。口交手交阴道插入同时进行。低语者不是温柔的不是礼貌的——是200年被囚禁压抑后的爆发。她在他们中间——被填满每一处')
c = c.replace(
    '- 但她的圣光没灭——反而更亮。不是因为享受——是因为她在用身体承受腐化。这是一种比剑更古老的净化方式',
    '- 但她没有退缩——不是因为享受是因为她在用身体承受。这是一种比剑更古老的方式')
c = c.replace(
    '- 结束后低语者一个接一个倒下——紫色光芒变金色。不是在被净化——是在被看见。菲娜躺在中间——头发散乱满身精液和汗水——但嘴角在笑。扶我起来——腿没力气了',
    '- 结束后低语者一个接一个倒下——紫色光芒褪为金色。菲娜躺在中间——头发散乱满身精液和汗水——但嘴角在笑。扶我起来——腿没力气了')

# N42: unpolished event - remove 圣光
c = c.replace(
    '情境: 森林深处祭坛。Seraphina立于中央，多名第三者环绕。五层递进——凯尔被引导→雷恩加入→艾德里安替换→乔治口交→(可选)Thalion腐化介入。Rean坐环外注视。终幕：所有人退开，Rean占有她，鬼之力与圣光完全交融。',
    '情境: 森林深处祭坛。菲娜立于中央多名第三者环绕。五层递进——凯尔被引导→雷恩加入→艾德里安替换→乔治口交→(可选)Thalion介入。黎恩坐环外注视。终幕：所有人退开黎恩占有她。')

# N47: already polished but title and 圣光花 keep - it's a plant name, not force description
# Check if "圣光花" needs to stay...
# The user said "圣光和腐化等神棍描述" - 圣光花 is a flower, not mystical force. Keep.

# ===== 3. Check for 腐化 in H3 core =====
c = c.replace(
    '黎恩差点失控但忍住了因为她说了可以。保留精灵身份揭示——低语者是200年前被Thalion欺骗的精灵平民。',
    '黎恩差点失控但忍住了因为她说了可以。低语者是200年前被Thalion欺骗的精灵平民。')

# ===== 4. N58 "圣光花开满河岸" in N59 - keep? It's environmental, not sex scene.
# Let's keep environmental references for now, focus on sex scene 神棍

with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('NTRS events cleaned')

# Verify: re-read and check
with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    c2 = f.read()

# Check remaining violations
import re
for pat, label in [
    (r'(和|与|比|呼应|不是|从).{,6}[NPC]\d{1,3}(.{,10}(?:一样|相反|更进一步|判若两人|服务|观看))', '编号互引'),
    (r'圣光(?!花|之|的初|之泉|之环|之森|之镜)', '圣光(非常规组合)'),
]:
    matches = list(re.finditer(pat, c2))
    if matches:
        print(f'\n{label} 残留 ({len(matches)}处):')
        for m in matches[:20]:
            # get line number
            ln = c2[:m.start()].count('\n') + 1
            print(f'  L{ln}: ...{m.group()[:60]}...')
    else:
        print(f'\n{label}: 已清除')
