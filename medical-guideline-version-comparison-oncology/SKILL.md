# 肿瘤指南新旧版本对比分析

> **本文档是 AI Agent 的工作指令。** 适用于 Cursor、VSCode Copilot、Claude、ChatGPT 等任何 AI 编程/对话工具。
> 将本文件放入项目目录，Agent 会自动参照执行。

---

## 给同事的使用说明

### 目录结构
```
guideline-comparison/
├── SKILL.md                      ← 本文件（AI Agent 工作指令，不要修改）
├── mineru-pdf-to-markdown/       ← PDF转Markdown工具（不要修改）
│   ├── convert.py
│   └── SKILL.md
├── input/                        ← 把两个指南PDF放这里
│   ├── 指南旧版.pdf
│   └── 指南新版.pdf
└── output/                       ← 报告自动生成在这里
    ├── markdown_output/          （中间产物：Markdown）
    ├── XXX_对比报告.html         （浏览器版）
    ├── XXX_邮件版.html / _newsletter.eml
    └── [新版文件名]_重点变化标注版.pdf
```

### 使用步骤（3步）
1. 把新旧两版指南 PDF 放入 `input/` 文件夹
2. 在 Cursor / Claude 中打开本项目文件夹
3. 对 Agent 说：`对比这两个指南`

### 输出
`output/` 文件夹中生成 HTML 对比报告，浏览器打开即可阅读。

---

## 用途

将同一肿瘤医学指南的两个版本（PDF）进行系统深度对比，输出结构化 HTML 报告。适用于肿瘤领域的国内外指南（如 NCCN、ESMO、CSCO）。

---

## 执行流程

### Phase 0: 信息收集

向用户确认以下信息（缺什么问什么，已有的不重复问）：

| # | 信息 | 说明 |
|---|------|------|
| 1 | PDF 文件确认 | 扫描 `input/` 文件夹中的 PDF 文件；若有多于2个或无法判断新旧则询问用户 |
| 2 | 新旧版本识别 | 文件名含年份则自动判断；无法判断则询问用户 |
| 3 | 是否需要"产品策略影响"板块？ | **必须主动询问用户**（给"需要/不需要"选项）；用户选"需要"时追问产品名+适应症；选"不需要"则跳过 |

**原则：一次提问收齐信息，不反复追问。**

### Phase 1: PDF 转 Markdown

使用 `mineru-pdf-to-markdown/convert.py` 将 `input/` 中的 PDF 转为 Markdown。

**convert.py 用法**：`python convert.py <PDF文件或目录> [输出目录] [语言]`
- 第1参数：PDF 文件路径，或包含 PDF 的**目录**（会自动扫描目录下所有 .pdf）
- 第2参数：输出目录（默认 `markdown_output`）
- 第3参数：语言，`en`（英文，默认）或 `ch`（中文）

**执行步骤**：
1. 在环境变量 `MINERU_API_KEY` 中配置 API token
2. 设置环境变量并执行：

```bash
export MINERU_API_KEY=your_token
python mineru-pdf-to-markdown/convert.py input/ output/markdown_output en
```

> 中文指南改为：`... input/ output/markdown_output ch`

- 这会扫描 `input/` 下所有 PDF 并批量转换
- 输出到 `output/markdown_output/`，每个 PDF 生成一个同名子文件夹，内含 `full.md`
- 验证：检查每个子文件夹的 `full.md` 存在且非空

**Windows（本机默认）**：不要用 `export` / `cat`。
```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:MINERU_API_KEY = "your_token"
python mineru-pdf-to-markdown/convert.py input/ output/markdown_output en
```

**备选方案**（MinerU API 不可用，或单本 PDF **>200 页**被接口拒收）：
```bash
pip install pymupdf
```
用 pymupdf 抽全文到 `output/markdown_output/[PDF同名]/full.md`。不要为过页限制强行拆本后只读半本；治疗流程图页 / Discussion 关键页可用 pymupdf 按页抽出对照。

### Phase 2: 全文阅读

分段读取 `output/markdown_output/` 下两个子文件夹中的 `full.md` 文件（每次 300-500 行，不可跳过中间内容）。

重点提取：
- 推荐条目 / Statements / Recommendations（逐条）
- 证据等级和推荐强度
- 方法学 / 文献检索范围变化
- 正文引用的关键临床试验
- 术语定义 / 阈值变化
- 编号体系变化

### Phase 3: 系统对比

对比维度：
1. **重要推荐变化**：新增 / 删除 / 重大修改 / 有临床意义的方案或等级调整（亚标题、目录、参考文献、措辞微调不纳入报告）
2. **正文大段新增**：新章节或关键 RCT / 荟萃分析的完整论述
3. **术语/定义/阈值变化**（仅当改变临床判断时写入报告）
4. **（可选）产品策略影响**：当前 vs 长远竞争格局（不重复推荐条文）

### Phase 4: 生成 HTML 报告

**输出路径**：`output/[指南名称]_对比报告_[旧版年份]vs[新版年份].html`

报告结构：
```
1. 整体更新总结 — 开篇**一句**点明主题（不写页数、不写“无变化”）→ **产品相关**（只写新变化，一句）→ 核心要点带标签
2. 推荐条目逐条对比（仅含**重要**推荐变化）
   - 章节标题用学术中文（如「低瘤负荷 mCSPC」）
   - 只列新增/删除/重大修改/有临床意义的方案或等级调整
   - 亚标题改写、目录增补、参考文献增补、分页拆合、措辞微调、无变化章节均不列出
   - 表格列：新版# | 旧版# | 变化标签 | 新版内容 | 具体变化说明
3. 正文新增重要内容提取 — 仅大段新增（新章节/新试验完整论述），目录条目或单条文献不单列
4. [可选] 产品策略影响 — 只写**当前 / 长远**竞争格局；不重复前文推荐等级、脚注、试验数据；语言简单直白
```

**第2部分对比表格列结构（强制，不可改列名或列数）**：
```html
<table>
<tr>
  <th>新版编号</th>    <!-- 新版中的条目编号/位置 -->
  <th>旧版编号</th>    <!-- 旧版对应编号，新增条目写"—" -->
  <th>变化类型</th>    <!-- 标签：新增/重大修改/修改/措辞微调/删除整合 -->
  <th>新版内容</th>    <!-- 新版条目原文（保留原文语言） -->
  <th>具体变化说明</th> <!-- 必填！ -->
</tr>
</table>
```

「具体变化说明」列要求：
- **新增**：说明新增原因/来源试验、临床意义
- **重大修改**：用 `<span class="old-text">旧文本</span>` 标注被删内容 + 说明变化核心
- **修改**：写清从X改为Y + 临床影响
- **措辞微调**：必须具体写明改了哪个词（如：删除了"other"一词）
- **删除/整合**：说明被合并到哪条/为什么删除

CSS 中必须定义：`.old-text { color: #c62828; text-decoration: line-through; }` 和 `.new-text { color: #2e7d32; font-weight: 500; }`

### Phase 5: 交付

- 保存 HTML 到 `output/` 文件夹
- 在浏览器中打开
- 告知用户文件路径 + 核心发现概要
- **主动询问用户**："是否需要生成邮件版、报告 PDF，以及在新版指南 PDF 上标注变化？"

### Phase 6: 邮件版 + PDF 版（用户确认后执行）

#### 6a. 邮件版（EML 草稿）— Newsletter 切图方案（首选）

用户偏好：报告邮件应像供应商设计的 newsletter —— 宽版（**1100px**）、纯图片排列、大字体大间距。不依赖 Outlook Word 引擎渲染 HTML。

**两步流程：**
1. **制作专用「邮件版 HTML」**（`*_邮件版.html`）— 不是直接截图浏览器版，而是制作一个 **1100px** 宽、newsletter 风格的专用 HTML
2. **截图 + 智能切割 → EML** — Edge headless 截全页 → 智能切割（避开文字行）→ CID 内嵌

##### 邮件版 HTML 模板要素（vs 浏览器版的差异）

| 维度 | 浏览器版 | 邮件版 |
|------|---------|--------|
| 宽度 | max-width:1360px | width:**1100px** 固定 |
| 正文字号 | 13-14px | 15-16px |
| 表格字号 | 12-13px | 14-15px |
| 行距 | 1.7 | 1.85 |
| 章节分隔 | h2 + border-bottom | 深蓝色横幅 `section-divider`（背景渐变+左侧金色边） |
| 汇总数据 | 表格 | KPI 卡片（大数字 36px + 小标签） |
| padding | 32px | 32-40px |
| 字体 | system font stack | Microsoft YaHei |
| Nav 导航 | 保留 | 去除（邮件中无锚点跳转意义） |

##### 截图 + 智能切割流程

脚本见 `output/generate_eml_newsletter.py`（可直接运行），核心步骤：

1. **Edge headless 截图**（脚本默认 `WIDTH=1100`，`DEVICE_SCALE=2`）：
   ```bash
   msedge.exe --headless --disable-gpu --hide-scrollbars \
     --window-size=1100,10000 --force-device-scale-factor=2 \
     --screenshot=full.png "file:///path/to/report_邮件版.html"
   ```
   - Edge 路径：`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
   - `subprocess.run(..., text=True)` 时 Edge stderr 可能含 Unicode，Windows GBK 控制台会 `UnicodeDecodeError`——截图文件已写出即可，不要因此判失败
2. **裁剪底部空白**：找最后「有内容」行。判断必须用 **像素 < 220**（不要用 245）。邮件底色 `#f0f2f5` 约 240，阈值偏高会裁不掉灰底
3. **智能切割（关键）**：不在固定高度切，在目标切点 ±400px 搜索"安全行"（连续背景色、像素方差极低的区域），不会把文字/表格行切成两半
   ```python
   def is_safe_row(row_idx):
       row = arr[row_idx, :, :3]
       return np.mean(row) > 230 and np.std(row) < 15
   ```
4. **打包 EML**：切图 CID 内嵌；图前放 **两个空 `<p>&nbsp;</p>`**，容器 `line-height:1; mso-line-height-rule:exactly`，避免 Outlook 把首图顶到栏外
   ```python
   <img src="cid:slice01" width="1100" style="display:block;margin:0 auto;border:0;">
   ```
5. **X-Unsent: 1** 让 Outlook 双击打开为草稿

**输出**：`output/[报告名]_newsletter.eml`（约 3-5MB）

**依赖**：`pip install Pillow numpy`（Edge 系统自带）

**交付说明告知用户**：
- Windows Outlook：双击 .eml → 未发送草稿 → 填收件人发送
- Mac Outlook：.eml 以已收邮件打开，需转发或复制正文到新邮件

##### 备选：HTML inline 方案（仅当用户需要可选中文字时）

如用户需要收件人可以复制文本：
1. 用 premailer（`pip install premailer`）CSS 内联
2. 去掉 border-radius/box-shadow/gradient
3. Python email 标准库打包 .eml（X-Unsent:1）

#### 6b. PDF 版

从 HTML 报告生成 PDF：

```bash
# 首选：Edge headless（Windows 无需安装，中文渲染完美）
msedge.exe --headless --disable-gpu --print-to-pdf="output/报告名.pdf" "file:///绝对路径/output/报告名.html"

# 备选：weasyprint（需 GTK/Pango 系统库，Windows 上安装复杂）
pip install weasyprint
python -c "from weasyprint import HTML; HTML('output/报告.html').write_pdf('output/报告.pdf')"

# 备选：playwright
pip install playwright && playwright install chromium
```

输出：`output/[报告名].pdf`

### Phase 7: 新版指南 PDF 标注（用户确认后执行）

在**新版**原文 PDF 上用黄色高亮标出本次变化。输出：`output/[新版文件名]_重点变化标注版.pdf`。

**只标这两类（与报告取舍一致）**
- 指南**推荐变化行**（治疗流程图页新增/改写的方案行、对应新脚注）
- 正文**大段新增**（新章节或新试验完整论述）

**不要标**
- Updates / 修订说明页、目录、参考文献、分页拆合、亚标题改写、措辞微调
- 未改的相邻行：分类标题（如 Useful in Certain Circumstances）、下一条旧方案、旧脚注（如 Capivasertib `**`）、未改适应症的旧论述（如原有 mCRPC Lu-177）
- 页眉页脚

**做法（pymupdf）**
1. 用报告里的页码（PROS-xx / MS-xx）在新版 PDF 里 `search_for` 锚点，再目视收紧 y/x 带
2. 按**行顶** `word[1]` 过滤，不要按字框重叠过滤（否则上一行会被带进高亮）
3. 治疗流程图页收紧 x，避开邻栏（如 monitor / response）
4. `add_highlight_annot` 一次最多约 32 个 quad；Discussion 整节须 **每 8 行一个 annot**，否则中间段会丢标
5. 先打印带内文本核对，再渲染标注页确认：没有邻行、没有页脚、大段中间不断档
6. 核对完删除临时预览图，只留标注 PDF

---

## 报告视觉规范（V2 配色）

### 设计原则
- **统一蓝色系**：全局主色为一个色阶 `#1e3a5f → #2c5282 → #3b6fa0`，不混用其他蓝
- **背景层次**：body 底色 `#f0f2f5`（微灰），白卡片浮于上方形成层次
- **标签柔和**：饱和度适中（`#48bb78`/`#9f7aea`/`#ed8936`/`#a0aec0`/`#fc8181`）
- **圆角层级**：Header 14px > Section 10px > 小组件 8px > 标签 4px
- **行距宽松**：body line-height: 1.7

### 布局结构
- **Header**：三段渐变 `linear-gradient(135deg, #1e3a5f 0%, #2c5282 50%, #3b6fa0 100%)` + 白色文字 + 径向光晕装饰（`radial-gradient(circle, rgba(255,255,255,0.06), transparent)`）
- **Nav 导航**：白底卡片 + `border: 1px solid #e8ecf0` + 链接带 hover 背景（`#edf2f7`）
- **Section 卡片**：白底 `border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border: 1px solid #e8ecf0`
- **Footer**：居中 `color: #a0aec0` + 顶部分割线 `border-top: 1px solid #e2e8f0`

### 内容呈现
- **h3 分组**：`color: #1e3a5f; border-left: 4px solid #2c5282; padding-left: 14px`
- **section-summary**：`background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px`
- **对比表格**：表头 `background: #2c5282`（与 Header 同色系）+ 斑马纹 `#f7fafc` + hover `#edf2f7` + `border-radius: 8px; overflow: hidden`
- **临床影响框**：`background: #fff8f0; border-left: 4px solid #ed8936`
- **文本标注**：`.old-text { color: #c53030; }` + `.new-text { color: #276749; font-weight: 600; }`
- **高亮框分色**：黄色 `#fffbeb + #d69e2e` / 绿色 `#f0fff4 + #48bb78` / 红色 `#fff5f5 + #fc8181` / 蓝色 `#ebf8ff + #4299e1`

---

## 报告格式规范

### 标签体系（统一中文）

| 标签 | 颜色 | 含义 |
|------|------|------|
| 新增 | 绿色 #48bb78 | 新版新增条目 |
| 重大修改 | 紫色 #9f7aea | 推荐内容/适用人群/治疗方案实质性变化 |
| 修改 | 橙色 #ed8936 | 有临床意义的内容调整 |
| 措辞微调 | 灰色 #a0aec0 | 拼写/格式/非实质性文字变化（**默认不写入报告**） |
| 删除/整合 | 红色 #fc8181 | 条目被删除或整合到其他条目 |

### 核心原则

1. **只列重要变化** — 推荐内容/适用人群/方案/证据等级的实质性变化，以及正文大段新增。亚标题、目录、参考文献、版式拆页、措辞微调一律不写
2. **无变化不列出** — 不罗列“本节无变化”，不写未改条目；开篇与产品段也不写“其余无变化”
3. **按原文译为学术中文** — 「新版内容」列保留指南原文；其余说明须按原意译成学术中文，**不要直接粘贴英文**，也不要用「伙伴」「算法」「点名」「并列无优先」等非指南、非学术改写
4. **视觉标注差异** — 旧文本用红色删除线，新文本用绿色加粗
5. **临床影响标注** — 重大变化后加黄色高亮框，用指南原意的学术中文写适用人群与专家组保留意见
6. **头部信息** — 仅含：文献来源 + 分析日期（当天日期）
7. **底部署名** — 固定："仅用于内部参考，不构成临床决策依据。如有疑问请参考指南原文。｜报告编制：拜耳医学部 PEMC · 竞争情报团队"

### 写作约定（2026-09 审阅后固化，下次必须遵守）

来自 NCCN 前列腺癌 V6 vs V7 报告的用户反馈，后续所有指南对比沿用。

**结构**
- **不要**单独写「治疗路径变化」专节（路径变化并入推荐条目对比即可）
- 第一部分顺序：开篇一句 → 产品相关（若需要）→ 核心更新要点
- 开篇只写这次更新了什么，一句话；不写页数、Panel 名单、未改章节
- 产品相关只写**新出现的产品相关变化**，不写“三药/双药地位未变”

**取舍**
- 只保留重要推荐变化 + 正文大段新增
- 不写：亚标题改写、Discussion 目录增补、单条参考文献、分页拆合（如 PROS-14 拆成 14A/14B）、措辞微调、「本节无变化」清单

**术语（前列腺癌 / 转移负荷）**
- high volume → **高瘤负荷**（不要写「高容量」）
- low volume → **低瘤负荷**（不要写「低容量」）
- Useful in Certain Circumstances → **特定情形下可用**
- is an option → **可作为治疗选择**
- algorithm / 治疗流程图页 → 写 **PROS-xx 治疗选择 / 治疗推荐**，禁止写「算法」

**语言**
- 「按指南原文」= **按原意译成学术中文**，不是把英文句子贴进说明栏
- 「新版内容」列：保留英文/原文推荐条文
- 说明、临床影响、专家组意见、产品策略：中文学术表述（药名可用中文通用名：阿比特龙、阿帕他胺、达罗他胺、恩扎卢胺）
- 章节标题用中文（如「低瘤负荷 / 寡转移 mCSPC」），不要整行英文小标题
- 禁止营销/AI 腔：伙伴、点名、话语权、存量份额、差异化、默认骨架、沟通话术、强化选项、不冲击

**产品策略（第四部分）**
- 只回答：对产品竞争格局**当前**和**长远**有何影响
- 不重复第一～三部分已写过的推荐等级、脚注、试验数字
- 两段即可，简单直白。示例语气：「三药仍是首选……短期内用法变化不大。」「若后续证实总生存获益……可能与三药形成竞争。」
- 不做利好/威胁/竞品/行动建议多表拆解

**交付**
- 报告写在 `output/`；告知用户完整路径，说明可用浏览器打开 HTML
- 用户要标注新版 PDF 时：只标推荐变化行 + 大段新增（见 Phase 7）

### HTML 模板参考

**报告头部：**
```html
<h1>[指南名称]<br>[旧版年份] vs [新版年份] 对比分析报告</h1>
<p class="subtitle">
    文献来源：[指南全称及版本]<br>
    分析日期：[当天日期]
</p>
```

**CSS 标签样式（V2 配色）：**
```css
.tag-new { background: #48bb78; color: white; padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-major { background: #9f7aea; color: white; padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-modified { background: #ed8936; color: white; padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-minor { background: #a0aec0; color: white; padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-deleted { background: #fc8181; color: white; padding: 2px 9px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.old-text { color: #c53030; text-decoration: line-through; }
.new-text { color: #276749; font-weight: 600; }
.section-summary { background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 22px; margin: 16px 0; }
.clinical-impact { background: #fff8f0; border-left: 4px solid #ed8936; padding: 16px 20px; margin: 14px 0; border-radius: 0 8px 8px 0; }
.clinical-impact strong { color: #c05621; }
.highlight-box { background: #fffbeb; border-left: 4px solid #d69e2e; padding: 16px 20px; margin: 16px 0; border-radius: 0 8px 8px 0; }
.impact-positive { border-left-color: #48bb78; background: #f0fff4; }
.impact-negative { border-left-color: #fc8181; background: #fff5f5; }
.impact-neutral { border-left-color: #4299e1; background: #ebf8ff; }
.panel-note { background: #fff5f5; border: 1px solid #fed7d7; padding: 14px 18px; border-radius: 8px; }
.evidence-detail { background: #f7fafc; padding: 16px 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
```

---

## 注意事项 (Pitfalls)

1. **PDF转换质量**：学术指南表格多 → MinerU VLM 模型效果最好；如格式乱需对照原PDF
2. **编号重组**：新版可能整体重编号（新增一条导致后续+1），必须追踪原始对应关系，不可简单按编号对齐
3. **证据等级变化**：推荐文字没变但 Grade/Strength 变了 = 重要变化，不可遗漏
4. **分散→整合**：某些条目并非"删除"而是整合入其他条目 — 须标明去向
5. **正文 vs 条目**：重要变化可能只在正文讨论中出现而未反映在条目 — 必须通读正文
6. **中文指南适配**：CSCO 等使用 I/II/III 级推荐 + 1A/1B/2A/2B/3 类证据，表格需适配
7. **大文件**：超过 500 行必须分段读取，不可跳过中间内容
8. **产品板块**：必须主动询问用户是否需要，不可自动假设
9. **不要写治疗路径专节**：用户已明确删除该板块，路径变化并入第 2 部分即可
10. **说明栏禁止粘贴英文原句**：译成学术中文；NCCN 的 algorithm 不要译成「算法」
11. **瘤负荷用词**：high/low volume 固定译为高/低瘤负荷
12. **MinerU 页数上限**：单本超过约 200 页会被拒；改 pymupdf 抽全文，或只拆关键页对照，不可只转换前半本就出报告
13. **新版 PDF 标注**：只标推荐变化行和大段新增；按行顶过滤 + 分块高亮；标完必须渲染抽查
