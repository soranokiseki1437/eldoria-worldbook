#!/usr/bin/env python3
"""
rebuild_all.py — 一键全流程重建

用法:
  python scripts/rebuild_all.py              # build → browser
  python scripts/rebuild_all.py --validate   # 加上 pre-validate

等价于:
  python scripts/build_eldoria.py
  python scripts/generate_chapter_browser.py
"""

import sys, os, subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run(script, *args):
    """Run a Python script, exit on failure."""
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, script)] + list(args)
    print(f'\n{"─"*60}')
    print(f'  ▶ {script} {" ".join(args)}')
    print(f'{"─"*60}')
    result = subprocess.run(cmd, cwd=os.path.dirname(SCRIPTS_DIR))
    if result.returncode != 0:
        print(f'\n❌ {script} 失败 (exit {result.returncode})')
        sys.exit(result.returncode)
    return result.returncode


def main():
    validate = '--validate' in sys.argv

    if validate:
        print('[pre-validate] 运行事件验证...')
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, 'story_tool.py'), 'validate'],
            cwd=os.path.dirname(SCRIPTS_DIR)
        )
        if result.returncode != 0:
            print('  ⚠️  验证发现警告（不阻塞构建）')

    run('build_eldoria.py')
    run('generate_chapter_browser.py')

    print(f'\n{"="*60}')
    print('  ✅ 全流程重建完成')
    print(f'     输出: output/Eldoria_V10.4.0.json')
    print(f'     浏览器: visual/全章节浏览器.html')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
