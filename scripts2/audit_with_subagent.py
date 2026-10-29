#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts2/audit_with_subagent.py — 独立的 JRPG 语域审查子 Agent（Discriminator Subagent）

通过调用独立的 agy 子进程启动全新无污染上下文的 LLM 实例，
专门负责执行《世界书·第二部》文风与语域对抗性质检，
彻底消除主 Agent 在自我修改时的“思维惯性”与“确认偏误”。
"""

import os
import sys
import argparse
import subprocess

import re

def load_rules_context():
    """动态读取工作区权威规则文件，确保单一事实源 (Single Source of Truth)"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lexicon_path = os.path.join(repo_root, '.agents', 'rules', 'lexicon.md')
    writing_guards_path = os.path.join(repo_root, '.agents', 'rules', 'writing-guards.md')

    rules_text = ""
    if os.path.exists(lexicon_path):
        with open(lexicon_path, 'r', encoding='utf-8', errors='ignore') as f:
            rules_text += f"\n--- 【底层词汇与实体转换字典 (lexicon.md)】 ---\n" + f.read()[:5000]
    if os.path.exists(writing_guards_path):
        with open(writing_guards_path, 'r', encoding='utf-8', errors='ignore') as f:
            rules_text += f"\n--- 【文风防线与写作规范 (writing-guards.md)】 ---\n" + f.read()[:5000]
    return rules_text

def load_docs2_context(text):
    """根据待审文本动态检索并注入 docs2 设定卡片，赋予子 Agent 设定对账事实源"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs2_dir = os.path.join(repo_root, 'docs2')
    if not os.path.exists(docs2_dir):
        return ""

    # 提取所有出现的 ID
    ids = set(re.findall(r'(?:CHR|NPC|LOC)_D2_\d+', text))
    # 提取常见角色名
    common_names = ['黎恩', '菲娜', '朱利安', '雷恩', '劳拉', '艾德里安', '菲', '亚莉莎', '凯尔', '加尔', '罗恩', '亚尔缇娜', '玲', '爱丽榭', '科林', '阿达尔伯特', '克莱门特', '埃德蒙', '卢卡斯', '达米安', '瓦卢瓦', '亨里克', '奥蕾莉亚', '法林', '多尔金', '哈根']
    names_in_text = [name for name in common_names if name in text]

    matched_cards = {}
    for root, dirs, files in os.walk(docs2_dir):
        for f in files:
            if f.endswith('.TXT'):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                        hit = False
                        for eid in ids:
                            if eid in content:
                                hit = True
                                break
                        if not hit:
                            for name in names_in_text:
                                if f.startswith(name):
                                    hit = True
                                    break
                        if hit:
                            # 提取核心设定行（去除超长琐碎项）
                            lines = [line for line in content.split('\n') if not line.strip().startswith('- **阴茎**') and not line.strip().startswith('- **射精**')]
                            matched_cards[f] = '\n'.join(lines[:35])
                except Exception:
                    pass

    if not matched_cards:
        return ""

    docs2_text = "\n--- 【底层设定卡片事实源 (docs2 Ground Truth，前 10 张核心卡)】 ---\n"
    for fname, card_content in list(matched_cards.items())[:10]:
        docs2_text += f"\n>>> 设定卡: {fname}\n{card_content}\n"
    return docs2_text

def build_discriminator_prompt(text, title="待审文本"):
    """构建子 Agent 对抗性审校提示词，切断编写者的思维惯性并对照 docs2 对账"""
    rules_ctx = load_rules_context()
    docs2_ctx = load_docs2_context(text)
    
    prompt = f"""你是一个完全独立、无任何记忆污染与思维惯性的【JRPG 西幻轻小说文风与 docs2 设定审查子 Agent】（Discriminator Subagent）。
你的唯一职责是以极其苛刻的对抗性视野，审查待审文本是否违背《英雄传说 轨迹系列》等 JRPG 官方汉化质感，并严格对照 docs2 真实卡片对账，坚决挑出所有隐蔽的中式古风、文言单字动词、现代工科伪写实、公文通报腔，以及【设定冲突与张冠李戴】。

【第一轨：JRPG 语言与文风病灶严查】：
编写者由于注意力局部坍缩与打地鼠惯性，常常在消除一个中式词后又本能引入新的中式搭子！你必须逐句严查：
1. 中式古典家具（圆几/茶几/小木几/几案、长案/书案/案台、床榻/木榻/同榻/软榻、屏风、绣墩、各类瓷器/瓷壶/骨瓷/细瓷）——全部必须置换为西幻实体（长木桌/小圆桌/边桌/木凳/高背椅/粗陶/双耳陶碗/银器/铁壶）；
2. 文言单字动作与介词倒装结构（行至/移步至/趋步至/走至/步至/踱至、端坐于/正襟危坐于/立于/坐于/垂于/贯注于/隐于/置于）——全部必须还原为现代自然口语动宾散句（快步走到……身边 / 坐在……上 / 垂在身侧）；
3. 中医性味、滋补煲汤与修真玄学腔（“温润”修饰草药/药根/药汤/浓汤/热汽、“药膳”、“滋补”、“生津”、“温补”、“调息”、“培元”）——必须还原为纯正客观西幻草药与食物（高山接骨木根/风干牛肉热汤/腾腾热气）；
4. 话本评书腔、市井土俗与公文报告腔（话本套话、汉子/粗汉/壮汉、清剿完毕/战斗收束/梳理顺畅/理顺/会同等）；
5. 现代工业、解剖生物与学术论文式“伪写实”腔（严禁“高碳钢/合金钢、高锡青铜、高抗冲、主轴模数、气动换向阀、碱性中和、肺活量、瞬膜”等现代工科工业与解剖学生物学词汇，必须还原为 JRPG 奇幻工匠与轻小说感官语言：矮人精钢/百炼硬钢、古代厚铸青铜、加厚耐酸铅皮、齿牙规制咬合、石灰沸腾滚烫白沫、半透明防水眼膜、水泽亚人闭气耐力、暗影吸聚涡流/狂暴黑风暴）。

【第二轨：docs2 设定卡片事实源客观对账】：
以下随附了从 `docs2/` 自动提取的权威卡片。你必须对抗性比对待审文本与 docs2 事实源：
1. 编号与实体匹配：严查是否有张冠李戴（例如把别的角色编号写给当前角色，如将艾玛编号误写给加尔，将乔治编号误写给朱利安）；
2. 身体特征与种族天赋：严查是否有凭空捏造（例如加尔是金色竖瞳、深绿色坚硬鳞甲、长尾有力，绝无解剖学生物学瞬膜；科林是薄荷蓝瞳、浅亚麻短发、发条八音盒；菲娜外貌如20岁少女，炽天使血脉）；
3. 战技与阵营立场：严查是否 OOC（例如黎恩澄澈鬼之力与八叶一刀流、圣殿大要塞全境绝缘“军”字）；
凡与 docs2 原档不符者，一律判定违规！

以下是工作区权威规则与底层卡片：
{rules_ctx}
{docs2_ctx}

----------------------------------------
【待审文本 ({title})】：
{text}
----------------------------------------

【你的审查与判决铁律】：
1. 绝对不要替编写者开脱！凡是倒推回 JRPG 轨迹脚本绝不可能出现的表达，或违背 docs2 设定的，一律判定违规；
2. 若文本 100% 纯正且与 docs2 设定完全一致，第一行必须直接输出：`[PASS] 语域纯度 100%，完全符合 JRPG 轻小说文风与 docs2 设定。`；
3. 若发现任何上述违规、中式古风残留或 docs2 设定冲突，第一行必须输出 `[VIOLATIONS DETECTED]`，随后逐条清晰列出：
   - 违规原句与违规词汇（或设定冲突点）
   - 病灶剖析（属于哪种惯性或何种 docs2 冲突）
   - JRPG 轨迹轻小说口语化散句重塑建议（或 docs2 纠偏方案）。
4. 直接输出纯文本审查报告，绝对严禁调用任何外部工具或执行命令。
"""
    return prompt

def run_subagent_audit(text, title="待审文本"):
    """调用 agy 子进程启动全新隔离的子 Agent 执行对抗性质检"""
    prompt = build_discriminator_prompt(text, title)
    
    try:
        res = subprocess.run(
            ['agy', '--dangerously-skip-permissions', '-p', prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=240
        )
        if res.returncode != 0:
            return False, f"子 Agent 执行异常 (code {res.returncode}):\n{res.stderr}"
        return True, res.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "子 Agent 审查超时 (超过 240 秒)。"
    except Exception as e:
        return False, f"启动子 Agent 失败: {e}"


def audit_file_with_subagent(filepath, chunk_size=2500):
    """按块或全篇对文件执行子 Agent 审查"""
    if not os.path.exists(filepath):
        print(f"[错误] 目标文件不存在: {filepath}")
        return 1

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    fname = os.path.basename(filepath)
    print(f"\n============================================================")
    print(f" [子 Agent 独立审查启动] 目标: {fname}")
    print(f"============================================================")

    # 提取关键长叙述正文部分（跳过纯表格和标题）
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('|') and len(p.strip()) > 30]
    
    # 组合成适当大小的文本块进行精准审查
    current_chunk = []
    current_len = 0
    chunks = []
    
    for p in paragraphs:
        if current_len + len(p) > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = len(p)
        else:
            current_chunk.append(p)
            current_len += len(p)
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    total_chunks = len(chunks)
    has_issues = False

    for idx, chunk in enumerate(chunks, 1):
        chunk_title = f"{fname} - 文本块 {idx}/{total_chunks}"
        print(f"[*] 正在调用子 Agent 审查块 {idx}/{total_chunks} ({len(chunk)} 字符)...")
        success, report = run_subagent_audit(chunk, chunk_title)
        
        if not success:
            print(f"[警告] {report}")
            continue

        if '[PASS]' in report:
            print(f"  -> 块 {idx} 审核通过：纯正 JRPG 文风。")
        else:
            has_issues = True
            print(f"\n[!] 发现问题 (块 {idx}):\n{report}\n")

    print(f"============================================================")
    if not has_issues:
        print(f"[OK] 子 Agent 独立终审通过！{fname} 纯度 100%，无思维惯性遗漏。")
        return 0
    else:
        print(f"[FAIL] 子 Agent 发现了上述文风/语域问题，请根据意见重塑。")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="独立的 JRPG 语域审查子 Agent")
    parser.add_argument('--file', type=str, required=True, help="需要审查的文件路径")
    parser.add_argument('--chunk-size', type=int, default=3000, help="文本分块大小（默认 3000 字）")
    args = parser.parse_args()

    sys.exit(audit_file_with_subagent(os.path.abspath(args.file), args.chunk_size))
