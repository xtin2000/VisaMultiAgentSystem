"""Pick the highest-authority evidence per agent.

Source-type priority (lower number wins): primary_stat → index → news → crowdsourced.
Within the winning group, the most recent ``as_of`` date wins.
"""
from __future__ import annotations

from datetime import date

from schema.models import AgentOutput, Evidence

SOURCE_PRIORITY: dict[str, int] = {
    "primary_stat": 1,
    "index":        2,
    "news":         3,
    "crowdsourced": 4,
}

LOW_CONFIDENCE_THRESHOLD = 0.4


def _parse_as_of(ev: Evidence) -> date:
    try:
        return date.fromisoformat(ev.as_of)
    except (ValueError, TypeError):
        return date.min


def resolve(
    agent_outputs: dict[str, AgentOutput],
) -> tuple[dict[str, float], dict[str, list[Evidence]]]:
    """Return (resolved_scores, resolved_evidence) keyed by agent_name."""
    resolved_scores: dict[str, float] = {}
    resolved_evidence: dict[str, list[Evidence]] = {}

    for agent_name, output in agent_outputs.items():
        if not output.evidence:
            resolved_scores[agent_name] = output.domain_score
            resolved_evidence[agent_name] = []
            continue

        best_priority = min(
            SOURCE_PRIORITY.get(ev.source_type, 99) for ev in output.evidence
        )
        best_group = [
            ev for ev in output.evidence
            if SOURCE_PRIORITY.get(ev.source_type, 99) == best_priority
        ]
        best_group.sort(key=_parse_as_of, reverse=True)

        resolved_scores[agent_name] = output.domain_score
        resolved_evidence[agent_name] = best_group

    return resolved_scores, resolved_evidence
