"""
Affordability Agent — Person B to implement.

Contract:
  - Inherit BaseAgent, implement run(country, profile) -> AgentOutput
  - agent_name must be "affordability"
  - domain_score normalized to 0–100 (higher = more affordable)

Data targets:
  - OECD price level indices and PPP framing (primary_stat)
  - Numbeo cost-of-living indices as secondary signal (crowdsourced — label clearly)

This placeholder returns a zero-confidence output so the orchestrator can still run
without this agent. Replace the body of run() with the real implementation.
"""
from __future__ import annotations

from agents.base_agent import BaseAgent
from schema.models import AgentOutput


class AffordabilityAgent(BaseAgent):
    agent_name = "affordability"

    def run(self, country: str, profile: str) -> AgentOutput:
        # TODO (Person B): implement real affordability data gathering
        return AgentOutput(
            agent_name=self.agent_name,
            country=country,
            profile=profile,
            domain_score=0.0,
            confidence=0.0,
            evidence=[],
            caveats=["AffordabilityAgent not yet implemented — placeholder output."],
            raw_data={},
            fetched_at=self._now_iso(),
        )
