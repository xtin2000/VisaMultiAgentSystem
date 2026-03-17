"""
Merges individual AgentOutputs + resolved scores into a CountryProfile.
"""
from __future__ import annotations

from datetime import datetime, timezone
from schema.models import AgentOutput, CountryProfile, Evidence


def build(
    country: str,
    profile: str,
    agent_outputs: dict[str, AgentOutput],
    resolved_scores: dict[str, float],
    resolved_evidence: dict[str, list[Evidence]],
) -> CountryProfile:
    return CountryProfile(
        country=country,
        profile=profile,
        agent_outputs=agent_outputs,
        resolved_scores=resolved_scores,
        resolved_evidence=resolved_evidence,
        merged_at=datetime.now(timezone.utc).isoformat(),
    )
