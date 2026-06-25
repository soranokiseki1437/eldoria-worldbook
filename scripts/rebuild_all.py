#!/usr/bin/env python3
"""
rebuild_all.py — 一键全流程重建

用法:
  python scripts/rebuild_all.py              # assemble → build → browser
  python scripts/rebuild_all.py --validate   # 加上 pre-validate
  python scripts/rebuild_all.py --skip-md    # 跳过assemble（仅build + browser）

等价于:
  python scripts/assemble_md.py
  python scripts/build_eldoria.py
  python scripts/generate_event_browser.py
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
    skip_md = '--skip-md' in sys.argv

    if validate:
        # Pre-validate: advisory only (known PN31 false positives won't block)
        print('[pre-validate] 运行事件验证...')
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, 'event_tool.py'), 'validate'],
            cwd=os.path.dirname(SCRIPTS_DIR)
        )
        if result.returncode != 0:
            print('  ⚠️  验证发现警告（不阻塞构建）')

    if not skip_md:
        run('assemble_md.py')

    run('build_eldoria.py')
    run('generate_event_browser.py')

    print(f'\n{"="*60}')
    print('  ✅ 全流程重建完成')
    print(f'     输出: output/Eldoria_V6.4.0.json')
    print(f'     索引: docs/05_事件系统.md')
    print(f'     浏览器: visual/全事件浏览器.html')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
