---
name: deep-research
description: Use only for high-complexity research tasks requiring comprehensive multi-dimensional analysis, systematic evaluation, or when the user explicitly requests deep/comprehensive research. Triggered when ≥2 of 3 criteria are met: explicit depth keywords, ≥3 sub-questions needed, or time budget ≥5 minutes.
---

# Deep Research Skill

## Trigger Decision Tree

### Criteria (need ≥2 to trigger)

**Criterion 1: Explicit Depth Keywords**
Request contains ≥1 of:
- "深度调研" / "全面分析" / "系统评估" / "comprehensive analysis"
- "对比...并给出建议" / "compare and recommend"
- "调研...的历史/现状/趋势" / "survey the history/current state/trends"
- "市场格局" / "competitive landscape"
- "技术选型评估" / "technology due diligence"

**Criterion 2: Multi-Dimensional Scope**
Request implicitly requires ≥3 sub-questions, such as:
- Market analysis (players + technology + policy + trends)
- Product comparison (features + pricing + support + ecosystem)
- Technology assessment (performance + cost + maturity + community)

**Criterion 3: Time Budget**
User explicitly allows ≥5 minutes research time, or request complexity implies >30 minutes manual research time.

### Decision Flowchart

```
User Request
    ↓
[Contains depth keywords?] ──Yes──→ Use deep-research
    ↓ No
[Needs ≥3 sub-questions?] ──Yes──→ Use deep-research
    ↓ No
[Time budget ≥5 min?] ──Yes──→ Use deep-research
    ↓ No
Use web_search + subagent (standard research)
```

### Examples Table

| Request | Decision | Reason |
|---|---|---|
| "Python 最新版本是什么" | web_search | Simple fact, 1 sub-question |
| "对比 Python 和 Go 的优缺点" | web_search + subagent | 2 sub-questions, no depth keyword |
| "分析 2024 年中国电动车市场竞争格局，包括主要玩家、技术路线、政策影响、未来趋势" | **deep-research** | 4 sub-questions + depth keywords |
| "调研 transformer 架构最近 3 年的进展" | **deep-research** | Depth keyword "调研" + multi-dimensional |
| "评估 PostgreSQL vs MySQL 用于高并发场景" | **deep-research** | Technology selection evaluation, ≥3 criteria |
| "What is the capital of France?" | web_search | Simple fact, trivial scope |
| "Compare React and Vue performance benchmarks with migration recommendations" | **deep-research** | Comparison + recommendation = depth keyword, ≥3 dimensions |

### When NOT to Use

- Simple fact queries → `web_search`
- Quick comparisons (≤2 dimensions) → `web_search` + `subagent`
- Writing quality improvement → `writing-skills`
- Document format conversion → `docx`/`pptx` skills

---

## Workflow Integration

```
User Request
    ↓
deep-research skill triggered
    ↓
6-Stage Workflow Execution
    ├── Stage 1: Planning
    ├── Stage 2: Search
    ├── Stage 3: Synthesis
    ├── Stage 4: Reflection
    ├── Stage 5: Visualization
    └── Stage 6: Reporting → report.md
    ↓
writing-skills (optional polish)
    ↓
docx/pptx skill (optional format conversion)
    ↓
Final Deliverable
```

---

## 6-Stage Workflow

### Stage 1: Planning

**Goal**: Decompose the research question into 3-5 sub-questions.

**Agent Action**:
```bash
python3 /home/dsh/office-mode/skills/deep-research/scripts/research.py \
  "<research_query>" \
  ~/office/<date>-<slug>/
```

**Output**: `research_state.json` initialized with query and empty sub-questions list.

---

### Stage 2: Search

**Goal**: Collect 3-5 sources per sub-question.

**Agent Actions**:
1. Use `web_search` with 2-3 query variants per sub-question.
2. Extract key facts and source URLs from results.
3. Add sources via script:

```bash
python3 -c "
import sys
sys.path.insert(0, '/home/dsh/office-mode/skills/deep-research/scripts')
from research import ResearchTracker
tracker = ResearchTracker.load('/home/dsh/office-mode/skills/deep-research/scripts', '~/office/<date>-<slug>/')
tracker.add_source('https://example.com/article', 'Article Title', check_reachability=False)
tracker.save_state()
"
```

---

### Stage 3: Synthesis

**Goal**: Analyze each sub-question in parallel, cross-reference findings.

**Agent Actions**:
1. Use `subagent` to analyze sub-questions in parallel.
2. Cross-reference findings across sub-questions.
3. Assign confidence levels (high/medium/low/unverified).
4. Record findings:

```bash
python3 -c "
import sys
sys.path.insert(0, '/home/dsh/office-mode/skills/deep-research/scripts')
from research import ResearchTracker
tracker = ResearchTracker.load('/home/dsh/office-mode/skills/deep-research/scripts', '~/office/<date>-<slug>/')
tracker.add_finding(
    sub_q_idx=0,
    finding='Key finding text here',
    source_url='https://example.com/article',
    confidence='high'
)
tracker.save_state()
"
```

---

### Stage 4: Reflection

**Goal**: Identify knowledge gaps and supplement search.

**Agent Actions**:
1. Detect gaps:

```bash
python3 -c "
import sys, json
sys.path.insert(0, '/home/dsh/office-mode/skills/deep-research/scripts')
from research import ResearchTracker
tracker = ResearchTracker.load('/home/dsh/office-mode/skills/deep-research/scripts', '~/office/<date>-<slug>/')
gaps = tracker.detect_knowledge_gaps()
print(json.dumps(gaps, indent=2, ensure_ascii=False))
"
```

2. If gaps exist, return to Stage 2 for targeted search.
3. Maximum 2 reflection cycles.

---

### Stage 5: Visualization

**Goal**: Generate 2-3 matplotlib charts.

**Chart Types**:
- Comparison bar chart
- Timeline/trend line chart
- Pie chart (market share, distribution)

**Agent Actions**:
1. Use matplotlib to generate charts.
2. Save to `~/office/<date>-<slug>/charts/`.
3. Use Noto Sans CJK font: `~/office-toolchain/fonts/NotoSansCJKsc-Regular.otf`.
4. Register charts:

```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '/home/dsh/office-mode/skills/deep-research/scripts')
from research import ResearchTracker
tracker = ResearchTracker.load('/home/dsh/office-mode/skills/deep-research/scripts', '~/office/<date>-<slug>/')
tracker.add_chart(Path('~/office/<date>-<slug>/charts/chart_name.png'))
tracker.save_state()
"
```

---

### Stage 6: Reporting

**Goal**: Generate structured markdown report.

**Agent Action**:
```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '/home/dsh/office-mode/skills/deep-research/scripts')
from research import ResearchTracker
tracker = ResearchTracker.load('/home/dsh/office-mode/skills/deep-research/scripts', '~/office/<date>-<slug>/')
report = tracker.generate_report()
Path('~/office/<date>-<slug>/report.md').write_text(report)
print('Report generated')
"
```

**Output Structure**:
```
~/office/<date>-<slug>/
├── research_state.json      # Machine-readable state
├── report.md                # Human-readable report
└── charts/
    ├── chart1.png
    └── chart2.png
```

---

## Quality Assessment (Tiered)

### Excellent
- ≥5 unique sources
- ≥80% sources reachable (only among checked sources)
- Each sub-question has ≥3 sources
- ≥1 matplotlib chart
- ≥1 reflection cycle executed
- Report length 1500-3000 characters

### Acceptable
- ≥3 unique sources
- ≥60% sources reachable (only among checked sources)
- Each sub-question has ≥2 sources
- ≥1 chart or detailed table
- Report length 1000-1500 characters

### Insufficient
- All other cases

**Degradation Strategy**: If quality is "Insufficient", agent should:
1. Identify specific gaps (which sub-questions lack sources).
2. Return to Stage 2 for targeted search.
3. After 2 cycles, if still insufficient, honestly state limitations in the report.

---

## Failure Handling

| Stage | Failure | Concrete Degradation Strategy |
|---|---|---|
| Search | No results | Remove restrictive qualifiers (e.g., "2024" → remove year), use synonyms, broaden scope |
| Fetch | URL unreachable (HTTP ≠200) | Use search snippet cache, mark source as "✗" in report |
| Subagent | Timeout (>60s) | Use main agent for direct analysis instead of parallel subagents |
| Chart | matplotlib error (font missing, invalid data) | Use markdown table instead of chart, note "Chart unavailable" |
| Report | Too short (<1000 chars) | Expand finding details, add "Limitations" section |
| Sources | <3 sources after 2 cycles | Add "Research Limitations" section, suggest manual follow-up |

---

## Integration with Other Skills

### Responsibility Boundaries

| Task | Skill | Responsibility |
|---|---|---|
| Research content | **deep-research** | Collect, synthesize, visualize |
| Writing quality | **writing-skills** | Polish language, ensure clarity |
| Document format | **docx/pptx skill** | Convert markdown to docx/pptx |
| Fact verification | **deep-research** (built-in) | Source validation, confidence labeling |

### Example Workflow

```
User: "Write a comprehensive report on China EV market"
  ↓
Agent: Triggers deep-research (depth keyword + multi-dimensional)
  ↓
Agent: Executes 6-stage workflow → generates report.md
  ↓
Agent: Applies writing-skills to polish language (optional)
  ↓
Agent: Uses docx skill to convert to report.docx (optional)
  ↓
Agent: Delivers final document
```

---

## Limitations

1. **Source Quality Verification**: Only checks reachability (HTTP status), not authority or credibility. A blog and a peer-reviewed journal are treated equally if both return HTTP 200.

2. **Gap Detection**: Uses source-count heuristics (≥3 sources per sub-question), not semantic coverage analysis. A sub-question may have 3 sources that all say the same thing, yet pass the gap check.

3. **Citation Format**: Simplified format `(Title) URL`, not full APA/MLA/Chicago style. Suitable for internal reports but not academic publication.
