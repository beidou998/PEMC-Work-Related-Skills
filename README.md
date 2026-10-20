# PEMC Work-Related Skills

Version-controlled collection of reusable PEMC work-related AI skills.

## Available skills

| Skill | Description |
| --- | --- |
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