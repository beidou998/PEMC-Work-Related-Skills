# APEX PPTX 模板换肤 · 安装与配置说明

## 1. 分发内容

复制整个 `apex-pptx-reskin-v5` 文件夹即可。核心文件：

```
apex-pptx-reskin-v5/
├── SKILL.md                        # 技能定义（AI Agent 读取）
├── USAGE.zh-CN.md                  # 快速使用指南
├── INSTALL.zh-CN.md                # 本文件
├── 1 APEX模板和参考页 1 (1).pptx   # APEX 主题模板源文件（必需）
├── scripts/
│   └── reskin-apex-v2.py           # 底座脚本（主题/封面/字体/图表）
└── assets/                         # 品牌素材、母版文件、设计参数
```

**不需要复制**：`work/`、示例输出、`node_modules/`。

## 2. 安装位置

### Cursor（推荐）

```text
<项目>/.cursor/skills/apex-pptx-reskin-v5/
```

### VS Code + GitHub Copilot

```text
<项目>/.github/skills/apex-pptx-reskin-v5/
```

### Claude Code

```text
<项目>/.claude/skills/apex-pptx-reskin-v5/
```

### Hermes Agent

```text
%LOCALAPPDATA%/hermes/skills/apex-pptx-reskin-v5/
```

文件夹名称必须保持为 `apex-pptx-reskin-v5`。

## 3. 环境要求

### 必需

- **Python 3.9+**
- **python-pptx** — 读写 PPTX
- **lxml** — XML 层主题替换

```bash
pip install python-pptx lxml
```

### 推荐

- **PowerPoint** 或 **LibreOffice** — 打开验证最终效果
- **Avenir Next LT Pro 字体** — APEX 英文标准字体（无则降级为 Arial）
- **Microsoft YaHei** — 中文 PPT 用（Windows 自带）

## 4. 快速自检

```bash
python scripts/reskin-apex-v2.py --help
```

显示使用说明。然后测试：

```bash
python scripts/reskin-apex-v2.py test.pptx
```

脚本成功只表示底座（主题/字体/图表/封面）写上了，**不能当交稿**。交稿还要按 `SKILL.md` 改挂、按过关表整页重建、清批注，并全页目视。

## 5. 通过 AI Agent 调用

向 Agent 说（Cursor / Copilot / Claude / Hermes 均可）：

```text
请使用 apex-pptx-reskin-v5 SKILL，把 <源PPT路径> 换上 APEX 模板。
```

Agent 读 SKILL.md：脚本只是底座；必须改挂、密页重建、清批注、全页目视。说明见 `USAGE.zh-CN.md`。

## 6. 脚本能力

| | reskin-apex-v2.py |
|---|---|
| Theme 替换 | ✅ |
| 字体替换 | ✅ |
| 图表重配色 | ✅ 紫+浅青按系列数 |
| 封面重建 | ✅ 背景+logo+分隔线 |
| 标题字号 | 脚本常锁 28；Agent 必须按 28–36 灵活调 |
| Master BG 修复 | ✅ solidFill 白色 |
| 封面标题样式 | 脚本尝试 40pt；交稿前必须审计到 40pt |
| 残留版式改挂 / 密页重建 / 清批注 | ❌ 必须由 Agent 按 SKILL 做 |

## 7. 品牌和权限

本技能包含 APEX 与 Bayer 标识。仅在接收者拥有相应内部使用权限时分发：

- 不要公开发布；
- 不要用于外部项目或无关公司；
- 不要修改、重绘或重新组合 Logo。

## 8. 常见问题

**Q: PermissionError**  
A: 关闭 PowerPoint 中打开的文件，或先复制源文件到本地再运行。

**Q: Discussion 页背景是深紫色，正常吗？**  
A: 正常。APEX 模板的 Discussion/Divider 布局设计规范就是深紫色背景。

**Q: 标题在白色背景上看不清？**  
A: 页标题必须显式设为 `#991BC5` 粗体 28–36pt（非占位符不会继承母版）。正文才是 `#310086`。

**Q: 脚本跑完能不能直接交？**  
A: 不能。还必须改挂残留版式、表格换肤、密页重建、清批注、全页目视。

**Q: 字体显示为 Arial？**  
A: 系统未安装 Avenir Next LT Pro 字体。需向品牌部门获取并安装。

**Q: 能不能拿另一份做好的 APEX 稿直接当输出？**  
A: 不能。SKILL 已沉淀通用规则；给什么源稿就从那份源稿换肤。
