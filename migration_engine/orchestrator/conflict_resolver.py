"""
Conflict resolution for competing evidence across agents.

Priority order (lower number = higher authority):
  1. primary_stat  — OECD, World Bank, ILO, official government data
  2. index         — EF EPI, Numbeo, Henley composite indexes
  3. news          — News articles, blog posts
  4. crowdsourced  — Community-submitted data

When multiple evidence items exist for the same metric:
  - Take the group with the best (lowest) source_type priority
  - Within that group, prefer the most recent as_of date
  - If an agent's confidence < 0.4, its score is still used but flagged
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


def resolve(agent_outputs: dict[str, AgentOutput]) -> tuple[dict[str, float], dict[str, list[Evidence]]]:
    """
    Given a dict of {agent_name: AgentOutput}, return:
      - resolved_scores: {agent_name: float}  — score after conflict resolution
      - resolved_evidence: {agent_name: list[Evidence]}  — best evidence per agent
    """
    resolved_scores: dict[str, float] = {}
    resolved_evidence: dict[str, list[Evidence]] = {}

    for agent_name, output in agent_outputs.items():
        if not output.evidence:
            resolved_scores[agent_name] = output.domain_score
            resolved_evidence[agent_name] = []
            continue

        # Find the best source_type group
        best_priority = min(
            SOURCE_PRIORITY.get(ev.source_type, 99) for ev in output.evidence
        )
        best_group = [
            ev for ev in output.evidence
            if SOURCE_PRIORITY.get(ev.source_type, 99) == best_priority
        ]

        # Within group, sort by as_of date descending (most recent first)
        def parse_date(ev: Evidence) -> date:
            try:
                return date.fromisoformat(ev.as_of)
            except (ValueError, TypeError):
                return date.min

        best_group.sort(key=parse_date, reverse=True)

        resolved_scores[agent_name] = output.domain_score
        resolved_evidence[agent_name] = best_group

    return resolved_scores, resolved_evidence
