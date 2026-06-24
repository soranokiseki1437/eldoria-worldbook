with open('docs/05_事件系统.md', 'r', encoding='utf-8') as f:
    content = f.read()

def apply_by_header(content, header, new_yaml):
    idx = content.find(header)
    if idx < 0: return content, False
    ys = content.find('```yaml', idx)
    if ys < 0: return content, False
    ye = content.find('```', ys + 7)
    if ye < 0: return content, False
    return content[:ys+7] + '\n' + new_yaml + '\n' + content[ye:], True

n3_yaml = '''  事件: N3 第一次共享——腐化低语者
    触发条件: ntrs_awakened=100, acceptance>=32, shared>=8
    性行为等级: 3（裸露+摸乳+舔乳+阴茎蹭触·无插入）
    情感阶段: A（为黎恩勉强配合——但失控了）
    黎恩知情: 是——黎恩在场
    第三者: 腐化低语者（非人）
    情境:
      - 森林深处腐化区域。两人商量后决定拿不认识的低语者尝试，菲娜裸露吸引低语者
      - 低语者一开始只是盯着看，随后胯下勃起——暗紫色粗大阴茎从袍下顶出。
        爪子覆上乳房揉捏，低头舔舐乳头，舌比人类长一截在两个乳尖间来回
      - 逐渐疯狂——从背后压上，勃起的肉棒蹭菲娜大腿内侧和下身，往上顶找入口。
        菲娜被吓坏，黎恩鬼之力出手劈飞低语者
      - 菲娜蹲在地上双臂抱胸腿在发抖。自责没做好
    占有欲确认:
      - 黎恩抱住发抖的菲娜擦去她身上低语者残留。确认你是我的——庆幸她没受伤。
        她回应我是你的，没闭眼——怕一闭眼又看到画面
    变量: shared+25, possess+35, acceptance+15, trust+15, bond+8
    核心: 第一次共享就失控——对方越界。但黎恩出手了。确认了即使出事他最在意她。
    排序备注: 移至A阶段末尾（N12之后），作为A阶段尺度最大事件。'''

n4_yaml = '''  事件: N4 第二次共享——多低语者强迫口交手交
    触发条件: ntrs_awakened=100, acceptance>=38, shared>=12, N3已触发
    性行为等级: 6（口交+手交+阴茎蹭触·差点插入）
    情感阶段: A→B过渡（尺度暴增——多个低语者同时，黎恩出手前差点被插入）
    黎恩知情: 是——黎恩在场
    第三者: 三个腐化低语者
    情境:
      - 同腐化区域。菲娜和黎恩商量后再试。三个低语者出现强行把菲娜按跪在地上——
        一个把肉棒塞进她手里，一个捏着她下巴往嘴里捅，第三个从背后蹭她臀部。
        嘴里那根越捅越深她干呕，背后那根从臀缝滑到腿间龟头顶在入口开始往里挤。
        菲娜被吓坏拼命摇头，黎恩全力出手劈飞三个低语者。
        她趴在地上咳嗽嘴角挂着唾液和先走汁，哭了——不是因为痛，是因为差点
    占有欲确认:
      - 黎恩把她捞进怀里她攥着他的衣服哭了很久。他擦她嘴角吻她额头，
        手覆上她胸口感受心跳平稳。你是我的。我是你的。——她声音还在抖
    变量: shared+30, possess+40, acceptance+12, trust+20, bond+10
    核心: 比N3更失控——多个低语者同时口交手交双线程差点被插入。黎恩再次出手。
      事后先让她心跳平稳下来而非仪式性确认。
    排序备注: 移至B~C阶段。'''

content, ok = apply_by_header(content, '### 事件N3：第一次见证（腐化低语者）', n3_yaml)
print('N3:', 'OK' if ok else 'FAIL')
content, ok = apply_by_header(content, '### 事件N4：第二次见证——习惯的萌芽（NTRS情感阶段A→B过渡）', n4_yaml)
print('N4:', 'OK' if ok else 'FAIL')

with open('docs/05_事件系统.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
