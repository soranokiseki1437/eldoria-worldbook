#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Reference Text Search Utility
通用参考文献全文检索工具：支持跨参考库按关键词、发言人、上下文窗口动态提取原始文本片段。
"""

import os, sys, re, argparse, random

# 默认指向技能内部的 references 目录
DEFAULT_VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../references'))

def scan_markdown_files(root_dir):
    md_files = []
    if not os.path.exists(root_dir):
        return []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith('.md'):
                md_files.append(os.path.join(dirpath, f))
    return sorted(md_files)

def get_vault_toc(vault_dir):
    """提取全部参考剧本的章节标题与事件大纲索引，供 LLM 全景式审阅"""
    files = scan_markdown_files(vault_dir)
    toc_tree = {}
    for fpath in files:
        rel_path = os.path.relpath(fpath, vault_dir)
        headings = []
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f, 1):
                    # 匹配 #, ##, ### 以及带重点符号的事件行
                    m = re.match(r'^(?:>\s*⚡\s*)?(#{1,3}\s+.+)', line.strip())
                    if m:
                        headings.append((idx, m.group(1).strip()))
        except Exception:
            continue
        if headings:
            toc_tree[rel_path] = headings
    return toc_tree

def search_text(vault_dir, query=None, speaker=None, context_lines=4, limit=5):
    files = scan_markdown_files(vault_dir)
    results = []

    for fpath in files:
        rel_path = os.path.relpath(fpath, vault_dir)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            continue

        for idx, line in enumerate(lines):
            # 过滤发言人
            if speaker and f"**{speaker}**" not in line and f"*{speaker}" not in line and f"[{speaker}]" not in line:
                continue

            # 匹配关键词
            matched = False
            if not query:
                matched = True if speaker else False
            else:
                if query in line:
                    matched = True

            if matched:
                start_l = max(0, idx - context_lines)
                end_l = min(len(lines), idx + context_lines + 1)
                snippet = "".join(lines[start_l:end_l]).strip()

                results.append({
                    'file': rel_path,
                    'line': idx + 1,
                    'query': query,
                    'snippet': snippet
                })

                if len(results) >= limit:
                    return results

    return results

def main():
    parser = argparse.ArgumentParser(description="Scenario Reference Vault - Explorer & Reading Assistant")
    parser.add_argument('-t', '--toc', action='store_true', help="查看全部参考剧本的宏观章节大纲与事件目录树")
    parser.add_argument('-q', '--query', type=str, help="按关键词快速定位文本出现位置")
    parser.add_argument('-s', '--speaker', type=str, help="按发言人名称筛选台词")
    parser.add_argument('-d', '--dir', type=str, default=DEFAULT_VAULT_ROOT, help="参考文本根目录路径")
    parser.add_argument('-c', '--context', type=int, default=4, help="上下文辐射行数 (默认 4 行)")
    parser.add_argument('-n', '--limit', type=int, default=5, help="返回结果上限 (默认 5 条)")

    args = parser.parse_args()

    if args.toc:
        toc_tree = get_vault_toc(args.dir)
        print("======================================================================")
        print("  📚 参考剧本库宏观事件与章节大纲目录 (Scenario Event TOC)")
        print("  供 LLM 全景式阅读感知各篇章的冲突类型，指导精读定位")
        print("======================================================================\n")
        for fpath, headings in toc_tree.items():
            print(f"📖 【{fpath}】")
            for line_no, h in headings:
                indent = "  " * (h.count('#') - 1)
                clean_h = re.sub(r'^#+\s*', '', h)
                print(f"  {indent}• (L{line_no:04d}) {clean_h}")
            print()
        return

    if not args.query and not args.speaker:
        parser.print_help()
        print("\n提示示例:")
        print("  1. 查看剧本事件总览: python3 search_vault.py --toc")
        print("  2. 定点检索关键词:   python3 search_vault.py -q '不能全都怪我' -c 3")
        return

    results = search_text(
        vault_dir=args.dir,
        query=args.query,
        speaker=args.speaker,
        context_lines=args.context,
        limit=args.limit
    )

    print(f"=== 检索完成: 关键词='{args.query or ''}' | 角色='{args.speaker or ''}' | 找到 {len(results)} 条 ===")
    for i, r in enumerate(results, 1):
        print(f"\n--- [片段 {i}] {r['file']} (第 {r['line']} 行) ---")
        print(r['snippet'])
        print("-" * 60)

if __name__ == '__main__':
    main()


