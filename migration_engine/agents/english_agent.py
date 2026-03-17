"""
English Accessibility Agent — Person B to implement.

Contract:
  - Inherit BaseAgent, implement run(country, profile) -> AgentOutput
  - agent_name must be "english"
  - domain_score normalized to 0–100 (higher = more English-friendly)

Data targets:
  - EF English Proficiency Index (EF EPI) — country-level proficiency bands and ranking
  - Output: english_friendliness_score + recommendation on local language requirement for work

This placeholder returns a zero-confidence output so the orchestrator can still run
without this agent. Replace the body of run() with the real implementation.
"""
from __future__ import annotations

from agents.base_agent import BaseAgent
from schema.models import AgentOutput


class EnglishAgent(BaseAgent):
    agent_name = "english"

    def run(self, country: str, profile: str) -> AgentOutput:
        # TODO (Person B): implement real EF EPI data gathering
        return AgentOutput(
            agent_name=self.agent_name,
            country=country,
            profile=profile,
            domain_score=0.0,
            confidence=0.0,
            evidence=[],
            caveats=["EnglishAgent not yet implemented — placeholder output."],
            raw_data={},
            fetched_at=self._now_iso(),
        )
