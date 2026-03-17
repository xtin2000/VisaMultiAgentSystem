"""
Visa Requirements Agent — Person B to implement.

Contract:
  - Inherit BaseAgent, implement run(country, profile) -> AgentOutput
  - agent_name must be "visa"
  - domain_score normalized to 0–100

Data targets:
  - Work visa pathways: skilled migration, digital nomad, student-to-work, ancestry, investor
  - Key constraints: eligibility, required documents, processing time, fees, sponsorship required
  - Source: official government immigration pages (primary_stat)

This placeholder returns a zero-confidence output so the orchestrator can still run
without this agent. Replace the body of run() with the real implementation.
"""
from __future__ import annotations

from agents.base_agent import BaseAgent
from schema.models import AgentOutput


class VisaAgent(BaseAgent):
    agent_name = "visa"

    def run(self, country: str, profile: str) -> AgentOutput:
        # TODO (Person B): implement real visa data gathering
        return AgentOutput(
            agent_name=self.agent_name,
            country=country,
            profile=profile,
            domain_score=0.0,
            confidence=0.0,
            evidence=[],
            caveats=["VisaAgent not yet implemented — placeholder output."],
            raw_data={},
            fetched_at=self._now_iso(),
        )
