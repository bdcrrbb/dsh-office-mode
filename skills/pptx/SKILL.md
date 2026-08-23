---
name: pptx
description: >-
  Use this skill whenever the user wants to create, read, or edit PowerPoint
  presentations (.pptx). Triggers: any mention of PPT, .pptx, 演示文稿, 幻灯片,
  deck, slides, presentation, or requests to produce slide decks.
---

# PPTX 创建、编辑与分析

## 工具链

所有 python 脚本使用 `~/office-toolchain/venv/bin/python` 执行。核心库：python-pptx（创建/编辑）。

## 创建流程

1. **读 style.json**：`/var/lib/dsh/.agent-presets/office/templates/style.json` 获取颜色/字体/版式参数。
2. **创建 Presentation**：
   ```python
   from pptx import Presentation
   from pptx.util import Inches, Pt, Emu
   from pptx.enum.text import PP_ALIGN
   prs = Presentation()
   prs.slide_width = Inches(13.33)   # 16:9 宽屏
   prs.slide_height = Inches(7.5)
   ```
3. **选择 layout**：
   - `prs.slide_layouts[0]` — Title Slide（标题页）
   - `prs.slide_layouts[1]` — Title and Content（标题+内容）
   - `prs.slide_layouts[5]` — Blank（空白，自定义布局）
4. **填充内容**：标题≥32pt，正文≥18pt，一页一义。

### 字体设置（关键）

python-pptx 同样需要分别设 eastAsia 和 ascii：

```python
from pptx.oxml.ns import qn

def set_text_frame_font(text_frame, east_asia, ascii_name, size_pt, bold=False):
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.name = ascii_name
            run.font.size = Pt(size_pt)
            run.font.bold = bold
            # 设 eastAsia
            rPr = run._r.get_or_add_rPr()
            rPr.set(qn('a:ea'), east_asia)
```

对占位符文本框：
```python
title_shape = slide.shapes.title
title_shape.text = "标题"
set_text_frame_font(title_shape.text_frame, "微软雅黑", "Arial", 32, bold=True)
```

### 图表插图流程

1. **matplotlib 生成 PNG**：
   ```python
   import matplotlib
   matplotlib.use("Agg")
   from matplotlib import font_manager, pyplot as plt
   import pathlib

   FONT_DIR = pathlib.Path.home() / "office-toolchain/fonts"
   font_manager.fontManager.addfont(FONT_DIR / "NotoSansCJKsc-Regular.otf")
   plt.rcParams["font.family"] = "Noto Sans CJK SC"

   fig, ax = plt.subplots(figsize=(8, 5))
   ax.bar(["Q1", "Q2", "Q3"], [120, 150, 90])
   fig.savefig("/tmp/chart.png", dpi=150, bbox_inches="tight")
   ```
2. **插入 PPT**：
   ```python
   from pptx.util import Inches
   slide.shapes.add_picture("/tmp/chart.png", Inches(1), Inches(2), width=Inches(10))
   ```

### 版式纪律

- **标题≥32pt**，正文≥18pt（小字不可读）
- **一页一义**：每页只讲一个核心观点
- **占位符先行**：先布局再填内容，避免手动算位置
- **颜色统一**：主色 #1F4E79，强调 #2E75B6，正文 #333333
- **图表标题**：图表上方加标题，字号 20pt

## 编辑存量文档

1. **备份**：`cp original.pptx original.pptx.bak`
2. **解压**：python zipfile 解压到 unpacked/
3. **编辑 XML**：改 `ppt/slides/slideN.xml`
4. **回包**：python zipfile 重新打包

## 输出自检（必须执行）

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation('output.pptx')
assert len(prs.slides) >= 8, f'至少 8 页，实际 {len(prs.slides)}'

for i, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.size and run.font.size < Pt(18):
                        print(f'警告: slide {i+1} 字号 {run.font.size.pt}pt < 18pt')
print('自检完成')
```

## Gotchas（实测固化）

- **默认画布非 16:9**：python-pptx 默认 10×7.5 英寸，需显式设 `slide_width=Inches(13.33)`
- **EMU 单位换算**：1cm=360000 EMU，1inch=914400 EMU，1pt=12700 EMU
- **文本框 autofit 不生效**：需手动设 `text_frame.word_wrap = True` 并控制字号
- **图片尺寸**：`add_picture` 后需设 width 或 height，否则按原图尺寸
- **eastAsia 设置**：python-pptx 的 `font.name` 只设 latin，中文需通过 `a:ea` 属性设（`rPr.set(qn('a:ea'), '微软雅黑')`）
- **字号是 EMU 整数**：`run.font.size` 返回 EMU 值（int），非 Pt 对象；转 pt 需 `/12700`
- **实测验证**：8 页样张生成成功，最小字号 20pt，图表插入正常
