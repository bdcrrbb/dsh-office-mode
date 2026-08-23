---
name: docx
description: >-
  Use this skill whenever the user wants to create, read, or edit Word documents
  (.docx). Triggers: any mention of Word doc, .docx, 调研报告, 公文, 简报, 报告文档,
  or requests to produce professional documents with formatting like TOC, headings,
  page numbers, tables, or Chinese official document (GB/T 9704) layout.
---

# DOCX 创建、编辑与分析

## 工具链

所有 python 脚本使用 `~/office-toolchain/venv/bin/python` 执行。核心库：python-docx（创建/编辑）、pypandoc（读取转 md）。

## 创建流程

1. **读 style.json**：`/var/lib/dsh/.agent-presets/office/templates/style.json` 获取字体/颜色/版式参数。
2. **确定字体档**：
   - A 档（商务通用）：标题 微软雅黑 / 正文 宋体 / 强调 黑体 / 拉丁 Arial
   - B 档（国标公文）：见 report-writing skill 的 GB/T 9704 参数表
   - 由 report-writing skill 的决策表决定用哪档
3. **用 python-docx 构建**：
   - 标题用内置 HeadingLevel.STYLE_1/2/3（保证 TOC 域可生成）
   - 段落用 Normal 样式，手动设字体
   - 表格用 Table 对象，设列宽（DXA 单位，1cm=567 DXA）
   - 分页符：`add_page_break()`
   - 页码：需操作 section footer XML（python-docx 无直接 API）

### 中文字体设置（关键）

python-docx 的 `run.font.name` 只设 ascii 字体。中文字体必须通过 XML 设置 eastAsia：

```python
from docx.oxml.ns import qn
run.font.name = 'Arial'                    # 拉丁字体
run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')  # 中文字体
```

对标题、正文、表格单元格都要分别设。封装为辅助函数：

```python
def set_run_font(run, east_asia, ascii_name, size_pt=None):
    run.font.name = ascii_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), east_asia)
    if size_pt:
        run.font.size = Pt(size_pt)
```

### 目录（TOC）

python-docx 插入 TOC 域代码，但**不会自动更新**——打开文档时需按 F9 或 Word 自动提示更新。插入方式：

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

paragraph = doc.add_paragraph()
run = paragraph.add_run()
fldChar = OxmlElement('w:fldChar')
fldChar.set(qn('w:fldCharType'), 'begin')
run._element.append(fldChar)

run2 = paragraph.add_run()
instrText = OxmlElement('w:instrText')
instrText.set(qn('xml:space'), 'preserve')
instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
run2._element.append(instrText)

run3 = paragraph.add_run()
fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run3._element.append(fldChar2)
```

### 页码

python-docx 无直接 API，需操作 section footer XML：

```python
section = doc.sections[0]
footer = section.footer
footer.is_linked_to_previous = False
p = footer.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 插入 PAGE 域
run = p.add_run()
fldChar = OxmlElement('w:fldChar')
fldChar.set(qn('w:fldCharType'), 'begin')
run._element.append(fldChar)
run2 = p.add_run()
instrText = OxmlElement('w:instrText')
instrText.text = 'PAGE'
run2._element.append(instrText)
run3 = p.add_run()
fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run3._element.append(fldChar2)
```

## 编辑存量文档

1. **备份**：`cp original.docx original.docx.bak`
2. **解压**：`unzip -q original.docx -d unpacked/`（服务器无 unzip 时用 python zipfile）
3. **编辑 XML**：直接改 `word/document.xml`，**不要 pretty-print**（会破坏 XML 结构）
4. **回包**：`cd unpacked && zip -Xr ../output.docx .`（服务器无 zip 时用 python zipfile）

## 读取内容

```bash
~/office-toolchain/venv/bin/python -c "
import pypandoc
md = pypandoc.convert_file('input.docx', 'markdown')
print(md)
"
```

## 输出自检（必须执行）

生成 docx 后，用 python-docx 重新打开并断言：

```python
from docx import Document
doc = Document('output.docx')
# 断言
assert len([p for p in doc.paragraphs if p.style.name.startswith('Heading')]) >= 3, '至少 3 个标题'
assert len(doc.tables) >= 1, '至少 1 个表格'
# 检查字体
for p in doc.paragraphs[:5]:
    for run in p.runs:
        ea = run._element.rPr.rFonts.get(qn('w:eastAsia')) if run._element.rPr is not None else None
        assert ea in ['宋体', '微软雅黑', '黑体', '仿宋_GB2312', None], f'意外字体: {ea}'
print('自检通过')
```

## Gotchas（实测固化）

- **TOC 域不自动更新**：文档内注明"请在 Word 中按 F9 更新目录"
- **eastAsia 忘设**：中文会回退 Calibri，必须在每个 run 上设 `rPr.rFonts.set(qn('w:eastAsia'), '宋体')`
- **表格宽度 PERCENTAGE**：在 Google Docs 中不兼容，用 DXA 绝对宽度
- **节属性继承**：新 section 默认继承前一节的页边距，需显式覆盖
- **图片插入**：`add_picture` 后需设 width/height（EMU 单位，1cm=360000 EMU）
- **实测验证**：A 档样张生成成功，eastAsia 字体可正确设置（微软雅黑/宋体/黑体）
- **实测验证**：B 档公文样张生成成功，页边距 3.7/3.5/2.8/2.6cm 精确，字体方正小标宋/仿宋_GB2312 可设
