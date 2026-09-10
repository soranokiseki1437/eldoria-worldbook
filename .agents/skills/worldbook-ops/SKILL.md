---
name: worldbook-ops
description: 世界书工程运维、自动化构建与全库一致性检查技能。当需要执行一键全流程重建、TXT语法验证、全局重编号、依赖引用检查与异常排错时使用。
---

# 世界书工程运维与构建技能 (WorldBook Ops)

> 本技能定义了世界书全流程构建、重编号、一致性校验与快照备份的标准工程流水线。

---

## 一、 核心流水线规范

### 1. 标准修改后的构建与验证管线 (Pipeline A)
无论进行了章节新增、内容精修还是状态栏更新，完成修改后必须依次执行：

```bash
# 步骤 1：验证所有 TXT 文件语法与必填字段（包含情境规范、TC3纯物象提示等）
python scripts/story_tool.py validate

# 步骤 2：若涉及新增地点或生物/怪物，核实 docs/location/_地点总览.TXT 或 docs/creature/_怪物与生物总览.TXT 是否已同步更新对应档案

# 步骤 3：执行全库一致性审计（编号匹配/命名/sex索引/弧总览）
python scripts/check_consistency.py

# 步骤 4：一键全流程生成（构建 JSON + 编译 HTML 章节浏览器）
python scripts/rebuild_all.py
```


### 2. 章节增删移与重编号流水线 (Pipeline B)
涉及调整章节顺序、插入章节或删除章节时，严格遵循以下顺序：

```bash
# 步骤 1：【删前必查】若涉及删除章节，必须先扫描是否有其他章节对其引用
python scripts/story_tool.py refs <章节ID>

# 步骤 2：对 TXT 执行全局自动重编号引擎
python scripts/renumber_events.py

# 步骤 3：执行重编号后的级联更新与索引增补（铁律）
# ① 更新 docs/story/_连续叙事弧线章节总览.md（平移全部受影响的弧线引用、更新各阶段章数、首尾章及总章数统计）
# ② 更新 docs/story/_sex_index.txt（平移已有编号，且必须将新增章节的性行为标签收录进对应分类、更新分类计数，删除章节相应剔除）
python scripts/post_renumber_updates.py

# 步骤 4：方案文档闭环同步（铁律）
# 方案中已写成 TXT 落地的章节直接彻底删除，更新剩余方案的排期锚点，严禁记录修改痕迹，完成即删干净。

# 步骤 5：重新构建浏览器并检查索引漂移警告
python scripts/generate_chapter_browser.py

# 步骤 6：运行全量一致性审计（必须 100% 绿灯）
python scripts/check_consistency.py

# 步骤 7：运行最终全流程构建
python scripts/rebuild_all.py
```

### 3. 版本快照备份管理 (Pipeline C)
进行大范围批次修改或结构重组前，必须先行创建快照：

```bash
# 创建快照
python scripts/backup_restore.py backup "快照说明_YYYYMMDD"

# 查看现有快照列表
python scripts/backup_restore.py list
```

---

## 二、 异常排错与踩坑手册

遇到构建告警、一致性失败或编号漂移时，查阅：
- [troubleshooting.md](file:///home/nanhu2/comfyui/%E4%B8%96%E7%95%8C%E4%B9%A6/.agents/skills/worldbook-ops/references/troubleshooting.md)（含自由探索同名判定、重编号脱节修复、盲区排查）
- 历史深度记录直接检索：`grep -rn "<关键字>" .learnings/LEARNINGS.md`
