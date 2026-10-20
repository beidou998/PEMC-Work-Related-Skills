# PEMC Work-Related Skills

## 仓库简介

**PEMC Work-Related Skills** 是一个统一、可持续维护的团队工作技能库，集中沉淀和共享经过实践验证、可直接复用的工作 Skill，减少重复摸索，提升日常工作的效率与一致性。

目前已包含指南对比（通用版 / ONC 版）、APEX PPT 模板换肤等 Skill。欢迎团队成员持续补充和完善，共同将其建设为可持续复用的工作技能库。

## Available skills

| Skill | Description |
| --- | --- |
| `apex-pptx-reskin-v5` | Reskins completed PowerPoint decks to the APEX 2026 template. Internal use only. |
| `medical-guideline-version-comparison-general` | Compares two medical guideline PDF versions and produces a structured HTML report. |
| `medical-guideline-version-comparison-oncology` | Compares two oncology guideline PDF versions, prioritizes clinically meaningful treatment changes, and supports change annotation in the updated PDF. |

Each skill is self-contained. Credentials, source PDFs, and generated reports are deliberately excluded from version control.

## 同事使用说明

### 1. 下载仓库

任选一种方式下载：

- 在 GitHub 页面点击 **Code**，选择 **Download ZIP**，解压后使用。
- 已安装 Git 时，在终端执行：

	```powershell
	git clone https://github.com/beidou998/PEMC-Work-Related-Skills.git
	cd PEMC-Work-Related-Skills
	```

### 2. 选择技能版本

- `apex-pptx-reskin-v5`：适用于将已完成的 PowerPoint 套用 APEX 2026 模板，达到一键换模板包括但不仅限于 logo、字体、字号、图表颜色配比等的效果。
- `medical-guideline-version-comparison-general`：适用于各疾病领域的指南版本对比。
- `medical-guideline-version-comparison-oncology`：适用于肿瘤指南，重点识别有临床意义的治疗方案变化，并支持对新版 PDF 标注关键变化。

进入所选技能文件夹，先阅读其中的 `SKILL.md`，再用 Cursor、VS Code Copilot、Claude 或其他 AI 工具打开该文件夹。

### 3. 配置 MinerU API

PDF 转 Markdown 需要个人 MinerU API 密钥。请前往 [MinerU 官网](https://mineru.net/) 注册并在账户的 API 管理页面获取密钥；配置步骤见 [API_KEY_SETUP.md](medical-guideline-version-comparison-oncology/mineru-pdf-to-markdown/API_KEY_SETUP.md)。

请只在本地终端或密钥管理工具中保存密钥。不要将密钥写入 `API.txt`、`.env`、报告、截图或邮件附件。

### 4. 运行指南对比

1. 将具有使用授权的新旧两版 PDF 放入所选技能的 `input/` 文件夹。
2. 在 AI 工具中打开该技能文件夹。
3. 输入：`对比这两个指南`。
4. 根据提示确认新旧版本、是否需要产品策略影响分析等信息。
5. 在 `output/` 文件夹查看生成的 HTML 报告；确认后可按 `SKILL.md` 的说明生成邮件版和 PDF 版。

### 5. 合规与文件管理

- 仅使用已获授权的指南 PDF，不要将受版权保护的原始指南或其衍生材料上传至公开仓库。
- `input/`、`output/`、API 密钥和运行时生成的中间文件均默认不纳入 Git。
- 仓库只保存可复用的技能说明和脚本；将正式交付报告保存在经批准的内部位置。

### 6. 上传新 Skill

欢迎补充可复用的工作 Skill。建议每个 Skill 使用一个独立文件夹，并至少包含 `SKILL.md`；如需脚本、模板或使用说明，也一并放在该文件夹中。

通过 GitHub 网页提交：

1. 打开本仓库，点击右上角 **Fork**，将仓库复制到自己的 GitHub 账号。
2. 在自己的仓库中创建一个新的 Skill 文件夹，点击 **Add file** -> **Upload files** 上传文件。
3. 更新根目录 `README.md` 的 **Available skills** 表格，补充新 Skill 的名称和一句用途说明。
4. 点击 **Contribute** -> **Open pull request**，填写 Skill 的用途、适用场景和主要文件后创建 Pull Request。
5. 仓库维护人核对内容与合规要求后，将 Pull Request 合并到主仓库。

提交前请确认：

- 不包含 API Key、密码、个人信息、内部交付文件或未获授权的源材料。
- 已在本地试用；`SKILL.md` 说明清楚输入、输出和基本使用方式。
- 不上传 `node_modules/`、`__pycache__/`、`input/`、`output/` 等依赖或运行时生成目录。

如暂时没有 GitHub 账号、不熟悉 Fork 或 Pull Request，可将完整 Skill 文件夹和简要说明发给仓库维护人，由维护人协助上传。