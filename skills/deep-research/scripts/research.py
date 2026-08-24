#!/usr/bin/env python3
"""Research state tracker for deep-research skill.

Provides source deduplication, optional reachability checking,
knowledge gap detection, tiered quality assessment, and report generation.
Uses only Python standard library (no third-party dependencies).
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


class ResearchTracker:
    """Tracks research state including sources, findings, charts, and quality metrics."""

    def __init__(self, query: str, output_dir: Path):
        self.query = query
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.output_dir / "research_state.json"

        self.sources: list[dict] = []  # [{url, title, reachable}]
        self.sub_questions: list[str] = []
        self.findings: list[dict] = []  # [{sub_q_idx, finding, source_url, confidence}]
        self.charts: list[str] = []  # [chart_path_str]
        self.reflection_cycles: int = 0

    @classmethod
    def load(cls, scripts_dir: str, output_dir: str) -> "ResearchTracker":
        """Restore tracker from research_state.json."""
        out = Path(output_dir)
        state_file = out / "research_state.json"
        if not state_file.exists():
            raise FileNotFoundError(f"No state file found at {state_file}")

        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        tracker = cls(data["query"], out)
        tracker.sources = data.get("sources", [])
        tracker.sub_questions = data.get("sub_questions", [])
        tracker.findings = data.get("findings", [])
        tracker.charts = data.get("charts", [])
        tracker.reflection_cycles = data.get("reflection_cycles", 0)
        return tracker

    @staticmethod
    def normalize_url(url: str) -> str:
        """Remove tracking parameters (utm_*, ref) and trailing slash."""
        parsed = urlparse(url)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        filtered = {k: v for k, v in qs.items() if not k.startswith("utm_") and k != "ref"}
        normalized_query = urlencode(filtered, doseq=True) if filtered else ""
        normalized = urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", normalized_query, "")
        )
        return normalized

    def add_source(self, url: str, title: str = "", check_reachability: bool = False) -> bool:
        """Add a source with deduplication. Returns True if added, False if duplicate."""
        normalized = self.normalize_url(url)
        existing_urls = {self.normalize_url(s["url"]) for s in self.sources}
        if normalized in existing_urls:
            return False

        reachable = None
        if check_reachability:
            reachable = self._check_reachability(normalized)

        self.sources.append({"url": normalized, "title": title, "reachable": reachable})
        return True

    def _check_reachability(self, url: str, timeout: int = 10) -> bool:
        """Check URL reachability via curl HEAD request. Prints warning to stderr on failure."""
        try:
            result = subprocess.run(
                ["curl", "-sI", "--max-time", str(timeout), url],
                capture_output=True,
                text=True,
                timeout=timeout + 5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Warning: Could not check reachability of {url}: {e}", file=sys.stderr)
            return False

    def batch_check_reachability(self, timeout: int = 10) -> dict:
        """Batch check reachability for all unchecked sources. Returns {url: bool}."""
        results = {}
        for src in self.sources:
            if src["reachable"] is None:
                src["reachable"] = self._check_reachability(src["url"], timeout)
                results[src["url"]] = src["reachable"]
        return results

    def add_sub_question(self, q: str):
        """Add a sub-question to the research plan."""
        self.sub_questions.append(q)

    def add_finding(self, sub_q_idx: int, finding: str, source_url: str, confidence: str = "medium"):
        """Add a finding linked to a sub-question and source. Ensures source exists."""
        normalized = self.normalize_url(source_url)
        existing_urls = {self.normalize_url(s["url"]) for s in self.sources}
        if normalized not in existing_urls:
            self.sources.append({"url": normalized, "title": "", "reachable": None})

        # Build simplified citation: find title for this URL
        title = ""
        for s in self.sources:
            if self.normalize_url(s["url"]) == normalized:
                title = s.get("title", "")
                break
        citation = f"({title}) {normalized}" if title else normalized

        self.findings.append({
            "sub_q_idx": sub_q_idx,
            "finding": finding,
            "source_url": normalized,
            "confidence": confidence,
            "citation": citation,
        })

    def detect_knowledge_gaps(self, min_sources_per_subq: int = 3) -> list:
        """Detect sub-questions with insufficient sources (heuristic based on count)."""
        gaps = []
        for idx, sq in enumerate(self.sub_questions):
            count = sum(1 for f in self.findings if f["sub_q_idx"] == idx)
            if count < min_sources_per_subq:
                gaps.append({
                    "sub_question": sq,
                    "sub_q_idx": idx,
                    "current_sources": count,
                    "required_sources": min_sources_per_subq,
                })
        return gaps

    def add_chart(self, chart_path: Path):
        """Register a generated chart."""
        self.charts.append(str(chart_path))

    def assess_quality(self) -> dict:
        """Assess research quality and return tier with metrics."""
        num_sources = len(self.sources)
        num_charts = len(self.charts)
        num_subqs = len(self.sub_questions)

        # Reachability rate: only among checked sources
        checked = [s for s in self.sources if s["reachable"] is not None]
        reachable_count = sum(1 for s in checked if s["reachable"] is True)
        if len(checked) > 0:
            reachability_rate = reachable_count / len(checked)
        else:
            reachability_rate = 0

        # Sources per sub-question
        sources_per_subq = []
        for idx in range(num_subqs):
            count = sum(1 for f in self.findings if f["sub_q_idx"] == idx)
            sources_per_subq.append(count)
        min_sources_per_subq = min(sources_per_subq) if sources_per_subq else 0

        # Knowledge gaps
        gaps = self.detect_knowledge_gaps(min_sources_per_subq=3)

        # Determine tier
        if (
            num_sources >= 5
            and reachability_rate >= 0.8
            and min_sources_per_subq >= 3
            and num_charts >= 1
            and len(gaps) == 0
        ):
            tier = "Excellent"
        elif (
            num_sources >= 3
            and reachability_rate >= 0.6
            and min_sources_per_subq >= 2
            and num_charts >= 1
        ):
            tier = "Acceptable"
        else:
            tier = "Insufficient"

        return {
            "tier": tier,
            "metrics": {
                "num_sources": num_sources,
                "reachability_rate": round(reachability_rate, 2),
                "min_sources_per_subq": min_sources_per_subq,
                "num_charts": num_charts,
                "num_sub_questions": num_subqs,
                "num_findings": len(self.findings),
                "reflection_cycles": self.reflection_cycles,
            },
            "gaps": gaps,
        }

    def save_state(self):
        """Save current state to research_state.json."""
        quality = self.assess_quality()
        data = {
            "query": self.query,
            "sources": self.sources,
            "sub_questions": self.sub_questions,
            "findings": self.findings,
            "charts": self.charts,
            "reflection_cycles": self.reflection_cycles,
            "quality_assessment": quality,
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_report(self) -> str:
        """Generate a markdown report from current state."""
        quality = self.assess_quality()
        tier = quality["tier"]
        metrics = quality["metrics"]
        gaps = quality["gaps"]

        lines = []
        lines.append(f"# Research Report: {self.query}")
        lines.append("")
        lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Quality Tier**: {tier}")
        lines.append("")

        # Source statistics
        lines.append("## Source Statistics")
        lines.append(f"- Total sources: {metrics['num_sources']}")
        lines.append(f"- Reachability rate: {metrics['reachability_rate']:.0%}")
        lines.append(f"- Sub-questions: {metrics['num_sub_questions']}")
        lines.append(f"- Findings: {metrics['num_findings']}")
        lines.append(f"- Charts: {metrics['num_charts']}")
        lines.append("")

        # Executive Summary (placeholder for agent to fill)
        lines.append("## Executive Summary")
        lines.append("")
        lines.append("*[Agent to fill with key takeaways]*")
        lines.append("")

        # Methodology
        lines.append("## Methodology")
        lines.append("")
        lines.append("### Sub-Questions")
        for i, sq in enumerate(self.sub_questions):
            lines.append(f"{i + 1}. {sq}")
        lines.append("")

        # Findings grouped by sub-question
        lines.append("## Findings")
        lines.append("")
        for i, sq in enumerate(self.sub_questions):
            lines.append(f"### {sq}")
            lines.append("")
            sub_findings = [f for f in self.findings if f["sub_q_idx"] == i]
            if not sub_findings:
                lines.append("*No findings recorded.*")
            else:
                for f in sub_findings:
                    conf_label = f["confidence"].upper()
                    lines.append(f"- **[{conf_label}]** {f['finding']} — {f['citation']}")
            lines.append("")

        # Knowledge Gaps
        if gaps:
            lines.append("## Knowledge Gaps")
            lines.append("")
            for g in gaps:
                lines.append(
                    f"- **{g['sub_question']}**: {g['current_sources']}/{g['required_sources']} sources"
                )
            lines.append("")

        # Visualizations
        if self.charts:
            lines.append("## Visualizations")
            lines.append("")
            for c in self.charts:
                chart_name = Path(c).name
                lines.append(f"![{chart_name}]({c})")
            lines.append("")

        # Recommendations (placeholder)
        lines.append("## Recommendations")
        lines.append("")
        lines.append("*[Agent to fill with actionable recommendations]*")
        lines.append("")

        # Sources list with status markers
        lines.append("## Sources")
        lines.append("")
        for i, s in enumerate(self.sources, 1):
            status = "?"
            if s["reachable"] is True:
                status = "✓"
            elif s["reachable"] is False:
                status = "✗"
            title_part = f"{s['title']} — " if s.get("title") else ""
            lines.append(f"{i}. [{status}] {title_part}{s['url']}")
        lines.append("")

        # Research Limitations (only if Insufficient)
        if tier == "Insufficient":
            lines.append("## Research Limitations")
            lines.append("")
            lines.append("This research did not meet the minimum quality thresholds:")
            if metrics["num_sources"] < 3:
                lines.append(f"- Insufficient sources ({metrics['num_sources']} < 3)")
            if metrics["reachability_rate"] < 0.5:
                lines.append(f"- Low reachability rate ({metrics['reachability_rate']:.0%} < 50%)")
            if metrics["min_sources_per_subq"] < 2:
                lines.append(
                    f"- Some sub-questions have fewer than 2 sources (min: {metrics['min_sources_per_subq']})"
                )
            if metrics["num_charts"] == 0:
                lines.append("- No visualizations generated")
            lines.append("")
            lines.append("Manual follow-up is recommended to address these gaps.")
            lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    # Usage: research.py <query> <output_dir>
    if len(sys.argv) < 3:
        print("Usage: research.py <query> <output_dir>", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    output_dir = Path(sys.argv[2])

    tracker = ResearchTracker(query, output_dir)
    tracker.save_state()
    print(f"Initialized research tracker for: {query}")
    print(f"State saved to: {tracker.state_file}")
