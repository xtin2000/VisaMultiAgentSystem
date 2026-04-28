#!/usr/bin/env python3
"""Run the three Phase-4 evaluations: coverage, consistency, ablation.

Output: a single Markdown report at ``migration_engine/evaluation/results.md``.
"""
from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("GOOGLE_API_KEY", "evaluation-not-used")

import config  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402
from schema.models import RankedResult  # noqa: E402

PROFILE = "software_engineer"
OUTPUT_PATH = Path(__file__).parent / "results.md"


def _coverage_table(orch: Orchestrator) -> tuple[str, dict[str, dict[str, bool]]]:
    """Return (markdown_section, {country: {agent: has_data}})."""
    from orchestrator.orchestrator import _load_agent

    null_logger = _NullLogger()
    agents = {name: _load_agent(name, orch.cache, null_logger) for name in config.AGENT_REGISTRY}

    matrix: dict[str, dict[str, bool]] = {}
    for country in config.COUNTRIES:
        outputs_per_agent: dict[str, bool] = {}
        for agent_name, agent in agents.items():
            out = agent.run(country, PROFILE)
            outputs_per_agent[agent_name] = out.confidence > 0.0 and len(out.evidence) > 0
        matrix[country] = outputs_per_agent

    lines = ["## 1. Coverage", ""]
    header = "| Country | " + " | ".join(config.AGENT_REGISTRY) + " | Complete |"
    lines.append(header)
    lines.append("|" + "|".join(["---"] * (len(config.AGENT_REGISTRY) + 2)) + "|")

    full_count = 0
    for country, agents in matrix.items():
        marks = ["✓" if agents[a] else "✗" for a in config.AGENT_REGISTRY]
        complete = "✓" if all(agents.values()) else "✗"
        if all(agents.values()):
            full_count += 1
        lines.append(f"| {country} | " + " | ".join(marks) + f" | {complete} |")

    lines.append("")
    lines.append(
        f"**Coverage: {full_count}/{len(config.COUNTRIES)} countries have complete schemas across all 4 agents "
        f"({full_count / len(config.COUNTRIES) * 100:.0f}%).**"
    )
    return "\n".join(lines), matrix


def _consistency_check() -> str:
    """Run the orchestrator twice and report any score deltas."""
    orch_a = Orchestrator(no_cache=True)
    ranked_a, _ = orch_a.run(profile=PROFILE, countries=config.COUNTRIES)

    orch_b = Orchestrator(no_cache=True)
    ranked_b, _ = orch_b.run(profile=PROFILE, countries=config.COUNTRIES)

    score_a = {r.country: r.total_score for r in ranked_a}
    score_b = {r.country: r.total_score for r in ranked_b}

    lines = ["## 2. Consistency", "", "Two independent reruns with `--no-cache` for the software-engineer profile.", ""]
    lines.append("| Country | Run A | Run B | Δ |")
    lines.append("|---|---:|---:|---:|")

    max_delta = 0.0
    for country in config.COUNTRIES:
        a, b = score_a[country], score_b[country]
        delta = abs(a - b)
        max_delta = max(max_delta, delta)
        lines.append(f"| {country} | {a:.2f} | {b:.2f} | {delta:.2f} |")

    lines.append("")
    verdict = (
        "**Stable** — all deltas are 0.00 (deterministic static datasets)."
        if max_delta < 1e-6
        else f"**Drift detected** — maximum score delta: {max_delta:.2f}"
    )
    lines.append(verdict)
    return "\n".join(lines)


def _ablation(baseline: list[RankedResult]) -> str:
    """For each agent, drop it and show how each country's rank changes."""
    baseline_rank = {r.country: r.rank for r in baseline}

    lines = ["## 3. Ablation", "", "Re-run with each agent disabled in turn. ΔRank = ablation rank − baseline rank.", ""]

    header_cells = ["Country", "Baseline"]
    rows: dict[str, list[str]] = {c: [c, str(baseline_rank[c])] for c in config.COUNTRIES}

    for agent_to_drop in config.AGENT_REGISTRY:
        orch = Orchestrator(no_cache=True)
        ranked, _ = orch.run(
            profile=PROFILE,
            countries=config.COUNTRIES,
            disabled_agents=[agent_to_drop],
        )
        ablated_rank = {r.country: r.rank for r in ranked}
        header_cells.append(f"−{agent_to_drop}")
        for country in config.COUNTRIES:
            delta = ablated_rank[country] - baseline_rank[country]
            sign = "+" if delta > 0 else ""
            rows[country].append(f"{ablated_rank[country]} ({sign}{delta})")

    lines.append("| " + " | ".join(header_cells) + " |")
    lines.append("|" + "|".join(["---"] * len(header_cells)) + "|")
    for country in sorted(config.COUNTRIES, key=lambda c: baseline_rank[c]):
        lines.append("| " + " | ".join(rows[country]) + " |")

    lines.append("")
    lines.append(
        "Cells show *new rank (ΔRank)*. A large ΔRank indicates the country was "
        "leaning heavily on the dropped domain."
    )
    return "\n".join(lines)


class _NullLogger:
    """Drop-in logger that silently absorbs all log calls during evaluation."""

    def log(self, *args, **kwargs) -> None: pass
    def agent_run(self, *args, **kwargs) -> None: pass
    def error(self, *args, **kwargs) -> None: pass


def main() -> None:
    print("[evaluation] running coverage check…")
    orch = Orchestrator(no_cache=True)
    coverage_md, _ = _coverage_table(orch)

    print("[evaluation] running consistency check…")
    consistency_md = _consistency_check()

    print("[evaluation] running ablation…")
    baseline_orch = Orchestrator(no_cache=True)
    baseline, _ = baseline_orch.run(profile=PROFILE, countries=config.COUNTRIES)
    ablation_md = _ablation(baseline)

    report = "\n\n".join([
        "# Migration Engine — Evaluation Report",
        f"_Profile: {PROFILE.replace('_', ' ')} | Generated: {datetime.now(UTC).isoformat()}_",
        coverage_md,
        consistency_md,
        ablation_md,
    ])

    OUTPUT_PATH.write_text(report)
    print(f"[evaluation] wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
