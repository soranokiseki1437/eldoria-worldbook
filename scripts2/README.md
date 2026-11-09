# scripts2/ — 第二部（维里迪亚王国篇）专属工具与脚本区

> **架构原则**：
> 1. **物理隔离与互不干扰**：完全独立于第一部工具区（`scripts/`）。第一部的构建、验证和自动化完全不受第二部影响；第二部的扫描和工具专属于 `docs2/` 与 `方案/第二部/`。
> 2. **纯正 JRPG 风格守门人**：杜绝东方武侠仙侠、中式传统度量衡以及恶性翻译腔长定语堆叠。

---

## 核心工具清单

| 脚本文件 | 核心职责 | 对应/借鉴的第一部脚本 |
| :--- | :--- | :--- |
| `story2_config.py` | 第二部系统共享元数据（路径、幕次阶段） | `scripts/story_config.py` |
| `scan_viridia_diseases.py` | 第二部文风雷达：古风禁词、中式度量衡、NSFW 字段污染、翻译腔堆叠 | `scripts/scan_narrative_diseases.py` |
| `check_viridia_consistency.py` | 第二部实体卡片（地点、NPC、生物、角色）全面一致性检测 | `scripts/check_consistency.py` |
| `audit_with_subagent.py` | 独立子 Agent 文风与设定双轮对抗性终审 | - |

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
# 检查 docs2/ 实体卡片 ID、名称、必填字段规范
python3 scripts2/check_viridia_consistency.py
```

### 3. 独立子 Agent 终审
```bash
python scripts2/audit_with_subagent.py --file "方案/第二部/主线与世界扩充方案/分阶段详规/XX.md"
```


