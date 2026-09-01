# DSH Office Mode（办公模式）

DeepSeek Harness 的办公模式 agent preset：面向文档产出的会话模式，与标准编码模式并列、互不污染。

## 这是什么

在 DSH Web 的会话模式列表中出现「办公模式」，切换后 agent 以办公文档写作为主业：

- **docx** — Word 文档创建/编辑/tracked changes(OOXML 全链路)
- **pptx** — PPT 创建/编辑/模板改造(含 html2pptx)
- **xlsx** — Excel 建模/公式/审计
- **deep-research** — 六阶段深度调研(规划→搜索→综合→反思→可视化→报告),来源去重、缺口检测、分级质量评估
- **report-writing** — 中文写作方法论:金字塔原理/SCQA/BLUF/GB/T 9704 公文格式参数表、三档字体决策
- **xberg** — 101+ 格式文档提取(kreuzberg)
- **frontend-slides** — HTML 动画演示文稿

## 安装

```bash
git clone git@github.com:bdcrrbb/dsh-office-mode.git
mkdir -p $DSH_HOME/.agent-presets   # DSH_HOME 默认 ~/.dsh
cp -r dsh-office-mode/{preset.yml,agent.cordis.yml,skills,templates} $DSH_HOME/.agent-presets/office/
# 重启 dsh 后,roster 出现「办公模式」
```

### 系统依赖(可选但推荐)

渲染/转换链路:`libreoffice poppler-utils unzip zip pandoc qpdf`(apt)
中文字体:`fonts-noto-cjk`(apt)+ 仓库内 `fonts-config/fonts.conf` 复制到 `~/.config/fontconfig/` + `fc-cache -f`
Python 库:`python-docx python-pptx openpyxl pandas matplotlib pypandoc-binary`(pip)
字体别名验证门槛:`fc-match "微软雅黑"` 必须返回 Noto 而非拉丁 fallback。

## 结构

```
├── preset.yml            # 模式名/描述/排序(order: 3)
├── agent.cordis.yml      # standard 基线 + 办公 persona + customSkillDirs
├── skills/               # 7 个办公 skills(仅办公会话可见,不污染编码模式)
│   ├── docx/ pptx/ xlsx/     # 来自 appautomaton/document-skills (MIT)
│   ├── xberg/                # 来自 kreuzberg-dev/kreuzberg (MIT)
│   ├── frontend-slides/      # 来自 zarazhangrui/frontend-slides
│   ├── presentation-deck/   # 来自 owl-listener/designer-skills (MIT)
│   └── deep-research/ report-writing/  # 自研
├── templates/style.json  # 颜色/字体/版式参数
├── fonts-config/         # fontconfig 中文别名(豆腐块修复)
└── tests/                # 干跑测试(A档docx/GB公文/pptx/cjk冒烟)
```

## 约定

- **产出落盘**:当前工作目录 `./output/YYYY-MM-DD-<slug>/`,不写固定路径
- **字体三档**:A 商务(微软雅黑/宋体)/ B 国标公文(GB/T 9704 参数表)/ C 图表渲染(Noto CJK)
- **skill 触发链**:deep-research(内容)→ report-writing(结构)→ docx/pptx(格式)

## 设计文档与评审

- 设计:`docs/specs/2026-08-23-office-mode-design.md`(部署机 242 上)
- deep-research 实施计划:`docs/plans/2026-08-24-deep-research-implementation.md`
- 全部经过多轮独立评审(办公模式设计、deep-research 计划、部署包三轮)

## 许可

本仓库自有内容见 [LICENSE](LICENSE);捆绑的第三方 skills 许可状态见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。

## 收录

如需上架 DSH 插件市场,向 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) 提 PR 增加条目(name/owner/url/category/description{en,zh})即可,市场自动收录。
