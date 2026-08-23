---
name: report-writing
description: >-
  Use this skill for writing methodology and structure decisions across docx
  and pptx outputs. Triggers: 调研报告, 汇报, 简报, briefing, 一页纸, 公文,
  official document, or when the user asks "how to structure" a document.
  Covers pyramid principle, SCQA, BLUF, and GB/T 9704 Chinese official document
  format. Also contains the three-tier font decision table.
---

# 写作方法论与结构决策

本 skill 跨 docx/pptx 复用，管"写什么、什么结构"，不管"怎么生成"（那是 docx/pptx skill 的职责）。

## 结构选择表

| 场景 | 结构 | 适用 |
|---|---|---|
| 深度调研报告 | **金字塔原理** | 结论先行，分层论证，数据支撑，适合 10 页+ 长报告 |
| 汇报叙事 | **SCQA** | Situation-Complication-Question-Answer，适合背景→问题→方案的叙事流 |
| 一页纸简报 | **BLUF** | Bottom Line Up Front，结论→关键数据→行动建议，≤1 页 |
| 党政机关公文 | **GB/T 9704** | 严格格式规范，见下文参数表 |

### 金字塔原理（深度报告）

1. **结论先行**：第一段即给出核心结论
2. **分层论证**：每个论点独立成节，节内再分小节
3. **数据支撑**：每个论点配 1-3 个数据点/事实
4. **MECE 原则**：Mutually Exclusive, Collectively Exhaustive（不重不漏）

### SCQA（汇报叙事）

- **S**ituation：背景/现状
- **C**omplication：问题/挑战
- **Q**uestion：核心问题
- **A**nswer：解决方案/建议

### BLUF（简报）

1. **Bottom Line**：核心结论（1-2 句）
2. **Key Data**：支撑结论的 3-5 个关键数据
3. **Action Items**：具体行动建议（谁、做什么、何时）

## 三档字体决策表

| 档 | 用途 | 中文字体 | 拉丁/数字 | 读者侧可用性 |
|---|---|---|---|---|
| A 商务通用 | 跨平台商务文档 | 标题 微软雅黑 / 正文 宋体 / 强调 黑体 | Arial / Times New Roman | Windows 全自带；Mac Office 自带微软中文字体集 |
| B 国标公文 | GB/T 9704-2012 | 见下文参数表 | Times New Roman | 政府/国企 Windows+WPS/Office 常见；Mac 普遍缺失 |
| C 图表渲染 | matplotlib | 思源黑体 Noto Sans CJK SC | — | 服务器合法安装（SIL OFL） |

**决策规则**：
- 读者是 Windows 用户 + 商务场景 → A 档
- 读者是政府/国企 + 正式公文 → B 档
- 图表（无论 A/B） → C 档（思源黑体）

## GB/T 9704-2012 党政机关公文格式参数表

| 项目 | 规范 |
|---|---|
| 页边距 | 上 3.7cm / 下 3.5cm / 左 2.8cm / 右 2.6cm |
| 标题 | 方正小标宋简体，二号（22pt） |
| 一级标题 | 黑体，三号（16pt） |
| 二级标题 | 楷体_GB2312，三号（16pt） |
| 三级/四级标题 | 仿宋_GB2312，三号，加粗 |
| 正文 | 仿宋_GB2312，三号（16pt） |
| 行距 | 固定值 28-30 磅 |
| 页码 | 宋体，四号（14pt），双面外侧 |
| 拉丁/数字 | Times New Roman |

**注意**：方正小标宋、仿宋_GB2312、楷体_GB2312 为 Windows 政府/企业机常见字体，Mac 普遍缺失。公文档默认假设读者为 Windows 环境。

## 大纲先行流程（必须执行）

1. **确认需求**：受众、篇幅、用途、风格（用户已给的不重复问）
2. **产出大纲**：按选择的结构（金字塔/SCQA/BLUF/公文）列出大纲
3. **等用户确认**：大纲确认后再写正文
4. **写正文**：按大纲逐节展开
5. **自检**：结构完整性、字体规范、引用标注

## 引用与来源标注规范

- **数字与事实必须可溯源**：每个数据点标注来源（脚注/尾注/参考文献段）
- **脚注**：python-docx 插入脚注需操作 XML（无直接 API），或改用尾注段
- **参考文献段**：文档末尾加"参考资料"段，列出所有来源
- **格式**：`[1] 来源名称, 日期, URL`

## 产出物落盘规范

统一落盘 `~/office/YYYY-MM-DD-<slug>/`，文件名含日期与主题：

```
~/office/2026-08-23-office-agent-comparison/
├── report.docx          # 主文档
├── slides.pptx          # 配套 PPT（如有）
├── charts/              # matplotlib 生成的图表 PNG
│   ├── market-share.png
│   └── feature-matrix.png
└── draft.md             # markdown 草稿（可选）
```

## 边界

- 不接入消息/日程/邮件
- 不向任何人发送产物
- 产物只落盘
- Excel 需求告知用户属 P2 未开通

## 实测记录

- **matplotlib 中文渲染**：思源黑体 Noto Sans CJK SC 通过 `font_manager.addfont()` 加载成功，无豆腐块
- **字体档决策**：A 档（商务）用微软雅黑/宋体/黑体；B 档（公文）用方正小标宋/仿宋_GB2312；C 档（图表）用思源黑体
