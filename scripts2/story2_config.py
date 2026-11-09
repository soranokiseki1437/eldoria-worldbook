# -*- coding: utf-8 -*-
"""
scripts2/story2_config.py — 第二部（维里迪亚王国篇）专属系统元数据与配置

与第一部（Eldoria 营地篇 scripts/story_config.py）完全物理隔离，互不干扰。
集中管理第二部：
1. 路径配置（docs2, 方案/第二部, build2）
2. 幕次定义（第一幕至第十幕）
"""

import os

# ═══════════════════════════════════════════════════════════
# 基础路径配置
# ═══════════════════════════════════════════════════════════

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS2_DIR = os.path.join(PROJECT_DIR, 'docs2')
DOCS2_STORY_DIR = os.path.join(DOCS2_DIR, 'story')
SCHEME2_DIR = os.path.join(PROJECT_DIR, '方案', '第二部')
BUILD2_DIR = os.path.join(PROJECT_DIR, 'build2')

# ═══════════════════════════════════════════════════════════
# 第二部十幕架构定义
# ═══════════════════════════════════════════════════════════

ACTS = [
    '第一幕',
    '第二幕',
    '第三幕',
    '第四幕',
    '第五幕',
    '第六幕',
    '第七幕',
    '第八幕',
    '第九幕',
    '第十幕',
]


