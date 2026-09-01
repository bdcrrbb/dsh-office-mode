# Third-Party Notices

本仓库捆绑的第三方 skills 及其许可状态。各上游许可证原文以其仓库为准。

| 目录 | 上游 | 许可证 | 备注 |
|---|---|---|---|
| `skills/docx/` `skills/pptx/` `skills/xlsx/` | [appautomaton/document-skills](https://github.com/appautomaton/document-skills) | MIT | 含 SKILL.md、ooxml 脚本与 XSD schema;本地改动:`uv run` 调用方式替换为 venv python 绝对路径 |
| `skills/xberg/` | [kreuzberg-dev/kreuzberg](https://github.com/kreuzberg-dev/kreuzberg) `plugin/skills/xberg` | MIT | 仅取 SKILL.md;运行时依赖 kreuzberg pip 包(未捆绑) |
| `skills/frontend-slides/` | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | **上游未声明** | 仅内部使用;如需再分发,须先取得上游授权或上游补充许可证 |
| `skills/presentation-deck/` | [owl-listener/designer-skills](https://github.com/owl-listener/designer-skills) `designer-toolkit/skills/presentation-deck` | MIT | 本地改动:frontmatter description 扩展中英触发词(正文未动) |
| `skills/kw-data/`(10 skills) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) `data/skills` | Apache-2.0 | Anthropic 官方知识工作套件;CONNECTORS.md 引用的外部连接器未随附,相关步骤降级为纯文本生成 |
| `skills/kw-product-management/`(8 skills) | 同上 `product-management/skills` | Apache-2.0 | 同上 |
| `skills/baoyu-diagram/` | [jimliu/baoyu-skills](https://github.com/jimliu/baoyu-skills) `skills/baoyu-diagram` | MIT | 与 baoyu-infographic 同作者;纯 SVG 代码生成,零外部依赖 |
| `skills/deep-research/` | 自研 | 见本仓库 LICENSE | 含 scripts/research.py |
| `skills/report-writing/` | 自研 | 见本仓库 LICENSE | GB/T 9704 参数表为公开标准要点的整理 |

历史版本曾捆绑 antv/infographic skills(MIT),已于 2026-08-24 移除,历史提交中仍可见。
