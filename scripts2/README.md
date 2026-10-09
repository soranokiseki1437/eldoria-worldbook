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
| `story2_tool.py` | 第二部章节脚手架与管理工具（生成标准 9 字段结构与一致性校验） | `scripts/story_tool.py` |

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

### 3. 校验章节合规性（文风雷达 + 9 字段 Schema）
```bash
# 校验单个章节文件（validate 与 lint 别名均可）
python scripts2/story2_tool.py lint --file "docs2/story/第一幕/001：泥沼残兽——青石初芽.TXT"

# 全量校验 docs2/story/ 下所有章节
python scripts2/story2_tool.py validate
```

### 4. 创建第二部规范章节脚手架
```bash
# 生成符合 JRPG 规范的标准章节（9 字段白名单）
python scripts2/story2_tool.py new \
  --id "001" \
  --title "泥沼残兽——青石初芽" \
  --act "第一幕" \
  --characters "雷恩, 菲, 黎恩, 菲娜, 艾玛" \
  --core "战后余波清剿与心木生命复苏。以冷兵器战术肃清残存魔兽，随后在石台举行心木播种，黎恩与菲娜共同唤醒沉睡两百年的新芽。"
```

---

## 第二部章节 Schema 铁律（9 字段白名单）

```text
ID: {编号，三位数字}
名称: {前半段}——{后半段}
NSFW: {是 或 否}
性行为等级: {0-10 —— 仅NSFW章节填写，非NSFW留空}
黎恩知情: {描述 —— 不适用则留空}
主要人物: {角色1}, {角色2}, ...
总情境数: {N}
情境:
  - 1. ...
  - 2. ...
  - 3. ...
  - {N}. {第N条情境：余韵物象收束（呼吸/环境音/微光/场景暂停），作为全章闭合节点}
核心: {1~2句话，禁止破折号，禁止AI元评价，禁止剧透后续章节}
```

