#!/usr/bin/env python3
"""Render the migration_engine architecture diagram as PNG and SVG.

Pure-matplotlib (no graphviz binary required). Run from the repo root:
    uv run python migration_engine/results/presentation/render_architecture.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_DIR = Path(__file__).parent

COLORS = {
    "entry":    {"fc": "#E8F0FE", "ec": "#1A73E8"},
    "orch":     {"fc": "#FEF7E0", "ec": "#F9AB00"},
    "agent":    {"fc": "#E6F4EA", "ec": "#188038"},
    "schema":   {"fc": "#F3E8FD", "ec": "#9334E6"},
    "coord":    {"fc": "#FCE8E6", "ec": "#D93025"},
    "coop":     {"fc": "#FFF3E0", "ec": "#E37400"},
    "output":   {"fc": "#E0F2F1", "ec": "#00695C"},
    "infra":    {"fc": "#F5F5F5", "ec": "#5F6368"},
}


def add_box(ax, x, y, w, h, label, kind, *, bold=False, fontsize=9):
    style = COLORS[kind]
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=1.4,
        edgecolor=style["ec"],
        facecolor=style["fc"],
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2, y + h / 2, label,
        ha="center", va="center",
        fontsize=fontsize + (1.5 if bold else 0),
        fontweight="bold" if bold else "normal",
        color="#202124",
    )
    return (x + w / 2, y + h / 2), (x, y, w, h)


def add_arrow(ax, src_pt, dst_pt, *, label="", style="solid", offset=0.0, color="#5F6368"):
    linestyle = {"solid": "-", "dashed": (0, (5, 3)), "dotted": (0, (1, 3))}[style]
    arrow = FancyArrowPatch(
        src_pt, dst_pt,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.2,
        color=color,
        linestyle=linestyle,
        connectionstyle=f"arc3,rad={offset}",
        shrinkA=8, shrinkB=8,
    )
    ax.add_patch(arrow)
    if label:
        mx, my = (src_pt[0] + dst_pt[0]) / 2, (src_pt[1] + dst_pt[1]) / 2
        ax.text(
            mx + offset * 1.2, my,
            label,
            fontsize=7.5, color="#3C4043",
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.25",
                      facecolor="white", edgecolor="#DADCE0", linewidth=0.5, alpha=0.95),
        )


def main() -> None:
    fig, ax = plt.subplots(figsize=(16, 12), dpi=180)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 18)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.suptitle(
        "Migration Feasibility & Risk Engine — System Architecture",
        fontsize=17, fontweight="bold", y=0.97, color="#202124",
    )
    fig.text(
        0.5, 0.935,
        "Four autonomous agents · shared schema · deterministic conflict resolution · weighted ranking",
        ha="center", fontsize=11, style="italic", color="#5F6368",
    )

    # ── Entry points (top) ──
    cli_c,  _ = add_box(ax, 0.5,  16.2, 3.5, 1.1, "main.py\n(CLI)",                                "entry")
    mcp_c,  _ = add_box(ax, 6.25, 16.2, 3.5, 1.1, "mcp_server.py\n(MCP tool: rank_countries)",     "entry")
    chat_c, _ = add_box(ax, 12.0, 16.2, 3.5, 1.1, "adk_agent.py\n(Gemini chat front-end)",         "entry")

    # ── Orchestrator (centre) ──
    orch_c, orch_box = add_box(ax, 5.5, 14.0, 5.0, 1.3, "Orchestrator\n5-phase run loop", "orch", bold=True, fontsize=10)

    # ── Infrastructure (right side, separate column) ──
    infra_x = 13.0
    cache_c,  _ = add_box(ax, infra_x, 14.0, 2.8, 1.3, "infra/cache.py\nSQLite\n(week TTL)",      "infra", fontsize=8)
    # Drop arrows orch ↔ cache later for clarity

    # ── Domain agents (4 in a row) ──
    visa_c, _ = add_box(ax, 0.3,  11.5, 3.2, 1.5, "VisaAgent\nHenley + government\nimmigration portals", "agent", fontsize=8.5)
    job_c,  _ = add_box(ax, 3.85, 11.5, 3.2, 1.5, "JobMarketAgent\nOECD + WB ILO\n+ EURES",              "agent", fontsize=8.5)
    aff_c,  _ = add_box(ax, 7.4,  11.5, 3.2, 1.5, "AffordabilityAgent\nOECD PPP\n+ Numbeo",              "agent", fontsize=8.5)
    eng_c,  _ = add_box(ax, 10.95, 11.5, 3.2, 1.5, "EnglishAgent\nEF EPI 2024\n+ native flag",           "agent", fontsize=8.5)

    # ── Shared schema (full-width band under agents) ──
    schema_c, _ = add_box(
        ax, 0.5, 9.5, 14.5, 1.0,
        "schema/models.py — AgentOutput · Evidence · CountryProfile · RankedResult",
        "schema", fontsize=10,
    )

    # ── Coordination layer ──
    conflict_c, _ = add_box(ax, 0.7, 7.0, 6.7, 1.7,
                            "conflict_resolver.py\nprimary_stat > index > news > crowdsourced\nthen most-recent as_of wins",
                            "coord", fontsize=8.5)
    merger_c,   _ = add_box(ax, 8.1, 7.0, 6.7, 1.7,
                            "merger.py\nbuilds CountryProfile\n(per-country merged view)",
                            "coord", fontsize=8.5)

    # ── Cooperation layer (ranker) ──
    ranker_c, _ = add_box(ax, 3.5, 4.6, 9.0, 1.5,
                          "ranker.py\nweighted ranking + ablation renormalization\nvisa 30%  ·  jobs 25%  ·  affordability 25%  ·  english 20%",
                          "coop", bold=True, fontsize=9)

    # ── Output layer ──
    explainer_c, _ = add_box(ax, 0.5, 2.2, 6.7, 1.4,
                             "explainer.py\ndeterministic 'why this rank' bullets\n(no LLM dependency)",
                             "output", fontsize=8.5)
    report_c,    _ = add_box(ax, 8.3, 2.2, 6.7, 1.4,
                             "report_generator.py\nmarkdown + Rich terminal output",
                             "output", fontsize=8.5)

    # ── DB + Logger (bottom infra row) ──
    db_c,     _ = add_box(ax, 1.5,  0.3, 5.5, 1.3, "infra/db.py\nrankings + evidence_log\n(SQLite persistence)",  "infra", fontsize=8.5)
    logger_c, _ = add_box(ax, 9.0,  0.3, 5.5, 1.3, "infra/logger.py\nper-run JSON logs\n(one file per run_id)",   "infra", fontsize=8.5)

    # ── Edges ──
    add_arrow(ax, cli_c,  orch_c, label="run()")
    add_arrow(ax, mcp_c,  orch_c, label="rank_countries()")
    add_arrow(ax, chat_c, mcp_c,  label="MCP/stdio")

    # Orchestrator → agents (single fan-out, no labels for clarity)
    add_arrow(ax, orch_c, visa_c)
    add_arrow(ax, orch_c, job_c)
    add_arrow(ax, orch_c, aff_c)
    add_arrow(ax, orch_c, eng_c)

    # Agents → schema (single representative arrow with label)
    add_arrow(ax, visa_c, schema_c, style="dashed")
    add_arrow(ax, job_c,  schema_c, style="dashed")
    add_arrow(ax, aff_c,  schema_c, style="dashed", label="emits AgentOutput")
    add_arrow(ax, eng_c,  schema_c, style="dashed")

    # Schema → coordination
    add_arrow(ax, schema_c, conflict_c, style="dashed", offset=0.05)
    add_arrow(ax, schema_c, merger_c,   style="dashed", offset=-0.05)

    # Coordination → ranker
    add_arrow(ax, conflict_c, ranker_c)
    add_arrow(ax, merger_c,   ranker_c)

    # Ranker → output
    add_arrow(ax, ranker_c, explainer_c)
    add_arrow(ax, ranker_c, report_c)

    # Side: orchestrator ↔ cache (clearly to the right, doesn't cross the main flow)
    add_arrow(ax, orch_c, cache_c, style="dotted", label="cache hit/miss")

    # Side: ranker → db, logger (out the bottom)
    add_arrow(ax, explainer_c, db_c,     style="dotted", offset=-0.2, label="persist")
    add_arrow(ax, report_c,    logger_c, style="dotted", offset=0.2)

    # ── Legend ──
    legend_handles = [
        mpatches.Patch(facecolor=COLORS["entry"]["fc"],  edgecolor=COLORS["entry"]["ec"],  label="Entry points"),
        mpatches.Patch(facecolor=COLORS["agent"]["fc"],  edgecolor=COLORS["agent"]["ec"],  label="Autonomy  —  domain agents"),
        mpatches.Patch(facecolor=COLORS["schema"]["fc"], edgecolor=COLORS["schema"]["ec"], label="Communication  —  shared schema"),
        mpatches.Patch(facecolor=COLORS["coord"]["fc"],  edgecolor=COLORS["coord"]["ec"],  label="Coordination  —  conflict + merge"),
        mpatches.Patch(facecolor=COLORS["coop"]["fc"],   edgecolor=COLORS["coop"]["ec"],   label="Cooperation  —  ranker"),
        mpatches.Patch(facecolor=COLORS["output"]["fc"], edgecolor=COLORS["output"]["ec"], label="Output renderers"),
        mpatches.Patch(facecolor=COLORS["infra"]["fc"],  edgecolor=COLORS["infra"]["ec"],  label="Infra (cache · DB · logger)"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=4,
        frameon=False,
        fontsize=9,
    )

    plt.tight_layout(rect=[0, 0.02, 1, 0.93])

    png_path = OUT_DIR / "architecture.png"
    svg_path = OUT_DIR / "architecture.svg"
    fig.savefig(png_path, dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"wrote {png_path}")
    print(f"wrote {svg_path}")


if __name__ == "__main__":
    main()
