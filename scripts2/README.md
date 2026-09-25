# scripts2/ — 第二部（维里迪亚王国篇）专属工具与脚本区

> **架构原则**：
> 1. **物理隔离与互不干扰**：完全独立于第一部工具区（`scripts/`）。第一部的构建、验证和自动化完全不受第二部影响；第二部的扫描和工具专属于 `docs2/`、`方案/第二部/` 和 `docs2/story/`。
> 2. **借鉴而不重蹈覆辙**：继承第一部优秀架构经验（统一元数据、严格自动化校验、防 AI 机械化病灶），但全面拔除第一部的古风修仙词汇和 NSFW 隐秘/隐奸体系。
> 3. **纯正 JRPG 风格守门人**：杜绝东方武侠仙侠、中式传统度量衡以及恶性翻译腔长定语堆叠。

---

## 核心工具清单

| 脚本文件 | 核心职责 | 对应/借鉴的第一部脚本 |
| :--- | :--- | :--- |
| `story2_config.py` | 第二部系统共享元数据（路径、字段 Schema、幕次阶段、叙事路线） | `scripts/story_config.py` |
| `scan_viridia_diseases.py` | 第二部文风雷达：古风禁词、中式度量衡、NSFW 字段污染、翻译腔堆叠 | `scripts/scan_narrative_diseases.py` |
| `check_viridia_consistency.py` | 第二部实体卡片（地点、NPC、生物）与章节 Schema 全面一致性检测 | `scripts/check_consistency.py` |
| `story2_tool.py` | 第二部章节脚手架与管理工具（自动插入 `主要人物`，杜绝 `战术隐蔽`） | `scripts/story_tool.py` |

---

## 常用命令指南

### 1. 扫描文风与病灶（古风/度量衡/NSFW污染）
```bash
# 全量扫描 docs2/ 与 方案/第二部/
python3 scripts2/scan_viridia_diseases.py

# 扫描单个文件
python3 scripts2/scan_viridia_diseases.py --file docs2/location/白鹿大驿馆.TXT
```

### 2. 检查全库一致性与卡片完整性
```bash
# 检查 docs2/ 实体卡片 ID、名称、必填字段与未来 docs2/story/ 章节规范
python3 scripts2/check_viridia_consistency.py
```

### 3. 创建第二部规范章节脚手架
```bash
# 生成符合 JRPG 规范的标准章节（包含主要人物，无战术隐蔽，无NSFW字段）
python3 scripts2/story2_tool.py new \
  --id "引-1" \
  --title "残区的反扑——东侧的沼地" \
  --stage "第一幕·阶段一：引入与故土远征启程" \
  --route "双线交汇" \
  --characters "雷恩, 菲, 菲娜, 黎恩" \
  --core "腐化退去不等于腐化消失，残区在无人处反扑..." \
  --task "东部巡逻线遭残区影牙兽残余袭击..."
```

---

## 第二部章节 Schema 铁律

```text
ID: {编号}
名称: {前半段}——{后半段}
阶段: {第一幕至第五幕对应阶段}
路线: {艾德里安线 / 雷恩线 / 双线交汇 / 帝国侧支线 / 营地联动支线}
主要人物: [{角色1}, {角色2}, ...]
情境:
  - 1. ...
  - 2. ...
  - 3. ...
  - 4. ...
核心: ...
章节任务: ...
章节终止条件:
  - 1. {纯物象化终止条件1}
  - 2. {纯物象化终止条件2}
  - 3. {纯物象化终止条件3}
```

* **严格禁止字段**：`战术隐蔽`（根据用户指示彻底移除）、`爱意值`、`隐秘事件`、`背德事件`、`NSFW`。
