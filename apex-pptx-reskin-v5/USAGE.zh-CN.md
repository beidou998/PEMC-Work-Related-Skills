# APEX PPTX 模板换肤 · 快速使用

给任意已排好的 `.pptx`，套上 APEX 2024/2026 品牌层。

**交稿标准 = 像人工排好的 APEX 内容页，不是脚本跑通。**  
每套源稿独立换肤；不要把别的 PPT 整份拷来当交稿。

## 最常见用法

```
用 apex-pptx-reskin-v5 SKILL，把 my-deck.pptx 换上 APEX 模板。
```

指定输出：

```
用 apex-pptx-reskin-v5 SKILL，把 source.pptx 换成 APEX，输出 source_APEX.pptx。
```

## 母版备注（必须）

- 英文全篇 **Avenir Next LT Pro**
- 封面 **40pt** 粗斜体；页标题 **28–36** 灵活，不要锁 28
- 正文 **`#310086`**；文献 **9pt 浅灰**（太多 8pt）
- 柱状图紫 + 青
- 交稿无批注

## 它改什么 / 不改什么

| ✅ 会改 | ❌ 不改 |
|---|---|
| 主题、字体、图表色 | 措辞、数据、引用（断词合并可以） |
| 残留版式 **改挂** `Content page` / Divider | 页数和顺序 |
| 页标题 28–36 `#991BC5`；正文 `#310086`；文献 9/8 灰 | 把标题紫刷到卡片/图注 |
| 表格表头/斑马（单元格文字不动） | 删图、删句 |
| 密页按过关表 **整页重建** | 只灌底图，或旧坐标贴纸 |
| 封面 40pt，浅色左区居中；清批注 | 覆盖源稿；把别的 PPT 整份当交稿 |

## 命令行

```bash
python scripts/reskin-apex-v2.py source.pptx
python scripts/reskin-apex-v2.py source.pptx output.pptx
python scripts/reskin-apex-v2.py source.pptx output.pptx --template /path/to/apex-template.pptx
```

这只是底座。改挂、表格、密页重建、清批注、全页目视，见 `SKILL.md`。

## 流程（任意稿）

1. 源稿拷出 OneDrive  
2. 跑脚本（底座）  
3. 残留版式改挂；表格换肤  
4. 按过关表重建仍像原稿拼贴的密页  
5. 清除批注；审计 40pt / 正文 `#310086` / 文献 9pt  
6. 全页导出目视；失败页重做  

## 注意

- `pip install python-pptx lxml`
- PowerPoint 打开时先拷本地
- 不覆盖源文件
- 内容页底图已含右下 APEX 标
- 仅限有授权的内部使用

文件夹：`.cursor/skills/apex-pptx-reskin-v5/`。安装见 `INSTALL.zh-CN.md`。

---

## 更新记录

### 2026-09-03 · 通用换肤，去掉样本依赖

- SKILL 适用于任意源稿；不再引用具体样本文件名或分档标签
- 明确：给什么源稿就从那份换肤；交稿须清批注
- 密页过关表按现象判断，不绑死页码
- `reskin-apex-v2.py` 仍只负责底座；Agent 必须改挂 + 重建 + 目视
