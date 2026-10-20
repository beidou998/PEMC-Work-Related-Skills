# 医学指南新旧版本对比分析

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
    ├── XXX_对比报告.html         （浏览器阅读版）
    ├── XXX_对比报告.pdf          （PDF附件版）
    └── XXX_对比报告_newsletter.eml（Outlook邮件草稿）
```

### 使用步骤（3步）
1. 把新旧两版指南 PDF 放入 `input/` 文件夹
2. 在 Cursor / Claude 中打开本项目文件夹
3. 对 Agent 说：`对比这两个指南`

### 输出
`output/` 文件夹中生成 HTML 对比报告，浏览器打开即可阅读。

---

## 用途

将同一医学指南的两个版本（PDF）进行系统深度对比，输出结构化 HTML 报告。适用于所有疾病领域的国内外指南（AUA, EAU, ESMO, CSCO, NCCN, ADA, ESC, KDIGO 等）。

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

**备选方案**（若 MinerU API 不可用）：
```bash
pip install pymupdf
# 或
pip install marker-pdf
```

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
1. **推荐条目变化**：新增 / 删除 / 修改 / 措辞微调 / 编号重组
2. **正文新增证据**：新引用的关键 RCT / 荟萃分析
3. **治疗路径变化**：决策流程的实质性改变
4. **术语/定义/阈值变化**
5. **（可选）产品策略影响**：利好 + 威胁 + 行动建议

### Phase 4: 生成 HTML 报告

**输出路径**：`output/[指南名称]_对比报告_[旧版年份]vs[新版年份].html`

**默认五章结构（不轻易改变，除非内容确实不适用则可省略）**：
```
一、整体更新总结 (Update Highlights) — 核心要点带标签
二、Recommendations 逐条对比（仅含变化条目）
   - 按疾病阶段/主题分 h3 子节（如 BCR / mHSPC / mCRPC）
   - 不得将各疾病阶段拆成独立 h2 大章节
   - 无变化条目不列出（仅注明"本节无变化"）
   - 表格列：新版# | 旧版# | 变化标签 | 新版内容 | 具体变化说明
三、新增正文内容提取 — 关键试验数据卡片
四、治疗路径变化总结 — 新旧对照表（指南不涉及治疗路径时可省略）
五、对公司产品策略影响分析（用户未提供公司产品时省略）
   - 按适应症逐一分析
   - 利好/威胁/行动建议
```
省略规则：第一～三部分必须保留；第四部分仅在指南确实不涉及治疗路径时可省略；第五部分仅在用户未提供公司产品时省略。结构不因指南类型（AUA/NCCN/ESMO/CSCO等）而随意重组。

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

### Phase 4b: 输出自检（MANDATORY — 交付前必须逐项确认）

生成 HTML 后，逐项检查以下内容。任何一项缺失必须补上后再交付：

- [ ] **Nav 导航栏**：Header 下方有白色 Nav 卡片，含"目录导航"标题 + 各章节锚点链接
- [ ] **章节编号**：每个 section 的 h2 标题包含中文数字编号（一、二、三、四、五、）
- [ ] **逐条对比表格有「具体变化说明」列**：不可只有新版/旧版两列对照
- [ ] **clinical-impact 框**：第二部分中每组有重大临床意义的变化表格后，紧跟一个橙色边框的临床影响点评框（`class="clinical-impact"`），解释该变化对临床实践的影响
- [ ] **section-summary 概述框**：每个大章节开头有灰底概述框，用 1-2 句话总结本节核心变化
- [ ] **标签统一中文**：新增/重大修改/修改/措辞微调/删除整合（不混用英文 New/Modified 等）
- [ ] **旧文本删除线 + 新文本绿色**：`<span class="old-text">` 和 `<span class="new-text">` 标注差异
- [ ] **无变化条目不列出**：只展示有差异的内容
- [ ] **头部**：仅文献来源 + 分析日期（不写分析师/检索截止日期）
- [ ] **底部**：固定署名格式

### Phase 5: 交付

- 保存 HTML 到 `output/` 文件夹
- 在浏览器中打开
- 告知用户文件路径 + 核心发现概要
- **主动询问用户**："是否需要生成邮件版和PDF版？"

### Phase 6: 邮件版 + PDF 版（用户确认后执行）

#### 6a. 邮件版（EML 草稿）— Newsletter 切图方案（首选）

用户偏好：报告邮件应像供应商设计的 newsletter —— 宽版（800px）、纯图片排列、大字体大间距。不依赖 Outlook Word 引擎渲染 HTML。

**两步流程：**
1. **制作专用「邮件版 HTML」**（`*_邮件版.html`）— 不是直接截图浏览器版，而是制作一个 800px 宽、newsletter 风格的专用 HTML
2. **截图 + 智能切割 → EML** — Edge headless 截全页 → 智能切割（避开文字行）→ CID 内嵌

##### 邮件版 HTML 模板要素（vs 浏览器版的差异）

| 维度 | 浏览器版 | 邮件版 |
|------|---------|--------|
| 宽度 | max-width:1360px | width:800px 固定 |
| 正文字号 | 13-14px | 15-16px |
| 表格字号 | 12-13px | 14-15px |
| 行距 | 1.7 | 1.85 |
| 章节分隔 | h2 + border-bottom | 深蓝色横幅 `section-divider`（背景渐变+左侧金色边） |
| 汇总数据 | 表格 | KPI 卡片（大数字 36px + 小标签） |
| padding | 32px | 32-40px |
| 字体 | system font stack | Microsoft YaHei, PingFang SC |
| Nav 导航 | 保留 | 去除（邮件中无锚点跳转意义） |

##### 截图 + 智能切割流程

脚本见 `output/generate_eml_newsletter.py`（可直接运行），核心步骤：

1. **Edge headless 截图**：
   ```bash
   msedge.exe --headless --disable-gpu --hide-scrollbars \
     --window-size=800,10000 --force-device-scale-factor=2 \
     --screenshot=full.png "file:///path/to/report_邮件版.html"
   ```
   - `window-size` 高度设 10000（≥ 页面实际高度 @1x）
   - `force-device-scale-factor=2` 产出 1600px 宽高清图（显示 800px）
2. **裁剪底部空白**：numpy 找最后有内容行 → +40px 留白后裁切
3. **智能切割（关键）**：不在固定高度切，在目标切点 ±400px 搜索"安全行"（连续背景色、像素方差极低的区域），不会把文字/表格行切成两半
   ```python
   def is_safe_row(row_idx):
       row = arr[row_idx, :, :3]
       return np.mean(row) > 230 and np.std(row) < 15
   ```
4. **打包 EML**：
   ```python
   <img src="cid:slice01" width="800" style="display:block;margin:0 auto;border:0;">
   # 每张切图作为 MIMEImage inline 附件, Content-ID: <slice01>
   ```
5. **X-Unsent: 1** 让 Outlook 双击打开为草稿

**输出**：`output/[报告名]_newsletter.eml`（约 3-5MB）

**依赖**：`pip install Pillow numpy`（Edge 系统自带）

**交付说明告知用户**：
- Windows Outlook：双击 .eml → 未发送草稿 → 填收件人发送
- Mac Outlook：.eml 以已收邮件打开，需转发或复制正文到新邮件

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
| 措辞微调 | 灰色 #a0aec0 | 拼写/格式/非实质性文字变化 |
| 删除/整合 | 红色 #fc8181 | 条目被删除或整合到其他条目 |

### 核心原则

1. **无变化不列出** — 只展示有差异的内容，高效阅读
2. **措辞微调要具体** — 不能只写"微调"，必须说明具体改了哪个词/哪句话
3. **保留原文** — 不翻译不改写推荐条目原文（英文保留英文，中文保留中文）
4. **视觉标注差异** — 旧文本用红色删除线，新文本用绿色加粗
5. **临床影响标注** — 重大变化后加黄色高亮框说明实践影响
6. **头部信息** — 仅含：文献来源 + 分析日期（当天日期）
7. **底部署名** — 固定："仅用于内部参考，不构成临床决策依据。如有疑问请参考指南原文。｜报告编制：拜耳医学部 PEMC · 竞争情报团队"

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
