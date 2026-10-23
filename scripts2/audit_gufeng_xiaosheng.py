# -*- coding: utf-8 -*-
"""
audit_gufeng_xiaosheng.py
用于深度排查第二部（全十四幕详规与主线方案）中潜藏的古风小生、江湖武侠、古言茶馆与公案戏腔词汇
"""

import os
import re

TARGET_DIR = r"d:\Siegfried\世界书\方案\第二部\主线与世界扩充方案\分阶段详规"

# 潜在古风小生/江湖武侠/茶馆戏腔特征词
GUFENG_SUSPECTS = [
    # 称谓与自称
    r'小生', r'兄台', r'仁兄', r'贤弟', r'后生', r'小可', r'鄙人', r'不才', r'晚生',
    r'老朽', r'老夫', r'拙荆', r'贱内', r'舍弟', r'舍妹', r'愚兄', r'诸兄',
    r'姑娘(?![，,。！？“”"、\s])', r'小女子', r'少侠', r'女侠', r'大侠', r'游侠儿',
    r'这厮', r'那厮', r'狂徒', r'泼皮', r'草莽', r'贼子', r'逆贼', r'乱臣贼子',
    # 寒暄礼数与江湖客套
    r'抱拳', r'拱手', r'作揖', r'长揖', r'折扇', r'轻摇折扇', r'抚须', r'捻须', r'捋须',
    r'负手', r'负手而立', r'拂袖', r'甩袖', r'袖袍', r'撩袍',
    r'久仰', r'如雷贯耳', r'幸会', r'借一步', r'承让', r'后会有期', r'贻笑大方',
    r'敢问', r'请教', r'赐教', r'讨教', r'冒昧叨扰', r'叨扰', r'见笑', r'让各位见笑',
    r'劳烦', r'烦劳', r'打扰各位', r'借光', r'借过',
    # 评书说书与话本台词
    r'愿闻其详', r'洗耳恭听', r'所言极是', r'言之有理', r'非也', r'实不相瞒', r'说来话长',
    r'且慢', r'且住', r'何方神圣', r'来者何人', r'好大的口气', r'休想', r'休得', r'休要',
    r'找死', r'活得不耐烦', r'多行不义', r'大难临头', r'朗声', r'仰天大笑',
    r'朗声笑道', r'沉声喝道', r'厉声喝道',
    # 其他中式市井/古文句式
    r'不知尊驾', r'尊驾', r'阁下留步', r'借一步说话', r'留步',
    r'这等', r'此等', r'彼时', r'尔等', r'汝等'
]

compiled_patterns = [(p, re.compile(p)) for p in GUFENG_SUSPECTS]

def run_audit():
    total_files = 0
    total_findings = 0
    results = {}

    for root, _, files in os.walk(TARGET_DIR):
        for f in files:
            if not f.endswith('.md'):
                continue
            total_files += 1
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, TARGET_DIR)
            
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
                
            for idx, line in enumerate(lines, 1):
                # 排除规则说明行、黑名单定义行
                if any(k in line for k in ['不要', '拔除', '清除', '严禁', '黑名单', '禁止', '规范', '置换', '替换', '防呆', '杜绝', '违规红线', '杜绝“']):
                    continue
                # 排除表格表头
                if line.strip().startswith('| **文风') or line.strip().startswith('| **词汇'):
                    continue
                
                for raw_pat, pat in compiled_patterns:
                    m = pat.search(line)
                    if m:
                        matched = m.group(0)
                        # 白名单过滤
                        if matched == '袖袍' and '宽大' in line:
                            pass
                        if rel not in results:
                            results[rel] = []
                        results[rel].append((idx, matched, line.strip()[:100]))
                        total_findings += 1

    print(f"扫描完毕: 遍历 {total_files} 个文件，发现 {total_findings} 处潜在古风小生/话本嫌疑。")
    print("=" * 80)
    for rel, findings in sorted(results.items()):
        print(f"\n文件: {rel}")
        for lnum, matched, snippet in findings:
            print(f"  行 {lnum} [{matched}]: {snippet}")

if __name__ == '__main__':
    run_audit()
