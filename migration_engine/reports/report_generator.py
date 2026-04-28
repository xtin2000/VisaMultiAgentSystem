"""Render ranked results as Markdown or a Rich terminal table."""
from __future__ import annotations

from schema.models import RankedResult


def render_markdown(
    results: list[RankedResult],
    profile: str,
    run_id: str,
    ran_at: str,
) -> str:
    lines = [
        "# Migration Feasibility Report",
        f"**Profile:** {profile.replace('_', ' ').title()}  ",
        f"**Run ID:** {run_id}  ",
        f"**Generated:** {ran_at}",
        "",
        "---",
        "",
    ]

    for r in results:
        missing_note = f" _(missing: {', '.join(r.missing_agents)})_" if r.missing_agents else ""
        lines += [
            f"## #{r.rank} — {r.country}",
            f"**Score:** {r.total_score:.1f}/100 | **Confidence:** {r.confidence_overall:.2f}{missing_note}",
            "",
            "| Domain | Score | Weight |",
            "|--------|-------|--------|",
        ]
        for domain, score in r.score_breakdown.items():
            weight = r.weight_breakdown.get(domain, 0)
            lines.append(f"| {domain} | {score:.1f} | {weight:.0%} |")
        lines.append("")

        if r.explanation_bullets:
            lines.append("**Why this ranked here:**")
            lines += [f"- {bullet}" for bullet in r.explanation_bullets]
            lines.append("")

        seen_urls: set[str] = set()
        evidence_lines: list[str] = []
        for ev_list in r.country_profile.resolved_evidence.values():
            for ev in ev_list:
                if ev.url not in seen_urls:
                    seen_urls.add(ev.url)
                    evidence_lines.append(f"- [{ev.title or ev.url}]({ev.url}) _(as of {ev.as_of})_")

        if evidence_lines:
            lines.append("**Sources:**")
            lines += evidence_lines
            lines.append("")

        lines += ["---", ""]

    return "\n".join(lines)


def render_terminal(results: list[RankedResult]) -> None:
    """Print a Rich table; fall back to plain text if Rich is unavailable."""
    try:
        from rich import box
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        for r in results:
            print(f"#{r.rank:2d}  {r.country:<15}  {r.total_score:5.1f}  conf={r.confidence_overall:.2f}")
            for b in r.explanation_bullets:
                print(f"     • {b}")
            print()
        return

    console = Console()
    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("Rank", style="bold cyan", width=6)
    table.add_column("Country", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Confidence", justify="right")
    table.add_column("Why", max_width=60)
    table.add_column("Missing", style="dim")

    for r in results:
        why = "\n".join(f"• {b}" for b in r.explanation_bullets[:3])
        missing = ", ".join(r.missing_agents) or "—"
        table.add_row(
            f"#{r.rank}",
            r.country,
            f"{r.total_score:.1f}",
            f"{r.confidence_overall:.2f}",
            why,
            missing,
        )

    console.print(table)
