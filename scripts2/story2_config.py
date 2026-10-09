# -*- coding: utf-8 -*-
"""
scripts2/story2_config.py — 第二部（维里迪亚王国篇）专属系统元数据与配置

与第一部（Eldoria 营地篇 scripts/story_config.py）完全物理隔离，互不干扰。
集中管理第二部：
1. 路径配置（docs2, 方案/第二部, docs2/story, build2）
2. 章节元数据模式规范（标准 9 字段白名单强约束）
3. 幕次定义（第一幕至第十幕）
"""

import os
from collections import OrderedDict

# ═══════════════════════════════════════════════════════════
# 基础路径配置
# ═══════════════════════════════════════════════════════════

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS2_DIR = os.path.join(PROJECT_DIR, 'docs2')
DOCS2_STORY_DIR = os.path.join(DOCS2_DIR, 'story')
SCHEME2_DIR = os.path.join(PROJECT_DIR, '方案', '第二部')
BUILD2_DIR = os.path.join(PROJECT_DIR, 'build2')

# ═══════════════════════════════════════════════════════════
# 第二部章节元数据 Schema 规范
# ═══════════════════════════════════════════════════════════

# 必须包含的元数据字段
REQUIRED_CHAPTER_FIELDS = [
    'ID',
    '名称',
    'NSFW',
    '性行为等级',
    '黎恩知情',
    '主要人物',
    '总情境数',
    '情境',
    '核心',
]

# 可选字段（第二部无多余可选字段）
OPTIONAL_CHAPTER_FIELDS = []

# 非白名单非法字段防御集合（内部防御拦截）
FORBIDDEN_CHAPTER_FIELDS = [
    '阶段',
    '路线',
    '好感影响',
    '第三者',
    '占有欲确认',
    '战术隐蔽',
    '爱意值',
    '隐秘事件',
    '背德事件',
    '章节任务',
    '章节终止条件',
]

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

