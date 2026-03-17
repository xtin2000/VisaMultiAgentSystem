"""
Job Market Agent — Person A's domain agent.

Data targets (via web_search):
  - OECD employment rate (% working-age population employed)
  - World Bank / ILO unemployment rate
  - EURES tech vacancy signal (software_engineer profile only)

Score normalization:
  employment_rate:  (rate - 60) / 20 * 100  weight=0.50  [80%=100pts, 60%=0pts]
  unemployment_rate: (12 - rate) / 9 * 100  weight=0.35  [3%=100pts, 12%=0pts]
  tech_signal:      high=100/medium=60/low=20             weight=0.15 (se only)

Stale data rule: as_of > 18 months ago → add caveat + reduce confidence by 0.2
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta

from agents.base_agent import BaseAgent
import config
from schema.models import AgentOutput, Evidence


RECORD_TOOL_NAME = "record_job_market_score"

RECORD_TOOL_SCHEMA = {
    "name": RECORD_TOOL_NAME,
    "description": (
        "Record the final job market assessment after gathering all data via web_search. "
        "Call this tool ONLY once, after you have searched for all required data points."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "domain_score": {
                "type": "number",
                "description": "Job market ease score, 0–100.",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence in this score, 0.0–1.0.",
            },
            "evidence": {
                "type": "array",
                "description": "2–5 citations supporting the score.",
                "items": {
                    "type": "object",
                    "properties": {
                        "url":         {"type": "string"},
                        "title":       {"type": "string"},
                        "as_of":       {"type": "string", "description": "ISO date e.g. 2024-10-01"},
                        "confidence":  {"type": "number"},
                        "raw_excerpt": {"type": "string"},
                        "source_type": {
                            "type": "string",
                            "enum": ["primary_stat", "index", "news", "crowdsourced"],
                        },
                    },
                    "required": ["url", "title", "as_of", "confidence", "raw_excerpt", "source_type"],
                },
            },
            "raw_data": {
                "type": "object",
                "description": "Intermediate numeric values before normalization.",
                "properties": {
                    "employment_rate":   {"type": ["number", "null"]},
                    "unemployment_rate": {"type": ["number", "null"]},
                    "tech_vacancy_signal": {
                        "type": ["string", "null"],
                        "enum": ["high", "medium", "low", None],
                    },
                },
                "required": ["employment_rate", "unemployment_rate", "tech_vacancy_signal"],
            },
            "caveats": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Warnings, data gaps, or limitations.",
            },
        },
        "required": ["domain_score", "confidence", "evidence", "raw_data", "caveats"],
    },
}


def _normalize_score(
    employment_rate: float | None,
    unemployment_rate: float | None,
    tech_signal: str | None,
    profile: str,
) -> tuple[float, float]:
    """Returns (score_0_100, confidence_proxy)."""
    score = 0.0
    weight_used = 0.0

    if employment_rate is not None:
        emp_score = max(0.0, min(100.0, (employment_rate - 60.0) / 20.0 * 100.0))
        score += emp_score * 0.50
        weight_used += 0.50

    if unemployment_rate is not None:
        unemp_score = max(0.0, min(100.0, (12.0 - unemployment_rate) / 9.0 * 100.0))
        score += unemp_score * 0.35
        weight_used += 0.35

    if profile == "software_engineer" and tech_signal is not None:
        signal_map = {"high": 100.0, "medium": 60.0, "low": 20.0}
        score += signal_map.get(tech_signal, 0.0) * 0.15
        weight_used += 0.15

    if weight_used == 0:
        return 0.0, 0.0

    normalized = score / weight_used
    return round(normalized, 1), round(weight_used, 2)


def _is_stale(as_of_str: str) -> bool:
    try:
        as_of = date.fromisoformat(as_of_str)
        cutoff = date.today() - relativedelta(months=config.STALE_MONTHS)
        return as_of < cutoff
    except (ValueError, TypeError):
        return False


class JobMarketAgent(BaseAgent):
    agent_name = "job_market"

    def run(self, country: str, profile: str) -> AgentOutput:
        year = datetime.now(timezone.utc).year
        se_only = profile == "software_engineer"

        system = f"""\
You are the Job Market Analyst agent in a Migration Feasibility and Risk Engine.

Your task: Assess how accessible the job market is for a {profile.replace("_", " ")} \
(US citizen) migrating to {country}.

IMPORTANT rules:
- Every claim must have a source URL and an "as_of" date.
- Prefer official primary statistics (OECD, World Bank, ILO) over news articles.
- Do NOT invent numbers. If you cannot find a source, set the value to null and explain in caveats.
- After gathering data, call the `{RECORD_TOOL_NAME}` tool ONCE with your findings.

Search strategy — perform these web_search queries in order:
1. OECD employment rate for {country}: \
   "OECD employment rate {country} {year} site:data.oecd.org OR stats.oecd.org"
2. World Bank / ILO unemployment rate for {country}: \
   "World Bank unemployment rate {country} latest"
{"3. Tech vacancy signal for " + country + " (software engineer profile): " +
 '"EURES software developer vacancies ' + country + ' ' + str(year) + '"' if se_only else ""}

Score normalization (for your reference, NOT for you to compute — the system will do it):
- Employment rate:   80% → 100 pts, 60% → 0 pts (linear)
- Unemployment rate: 3%  → 100 pts, 12% → 0 pts (linear)
- Tech signal:       high=100 / medium=60 / low=20 pts (software_engineer only)
"""

        user = (
            f"Assess the job market accessibility for a {profile.replace('_', ' ')} "
            f"migrating to {country}. "
            f"Search for the data points described in your instructions, then call "
            f"`{RECORD_TOOL_NAME}` with your findings."
        )

        raw = self._call_claude_with_tools(
            system=system,
            user=user,
            tools=[RECORD_TOOL_SCHEMA],
            record_tool_name=RECORD_TOOL_NAME,
        )

        # Re-normalize score from raw data (overrides Claude's self-computed score
        # to ensure consistent formula application)
        rd = raw.get("raw_data", {})
        computed_score, computed_conf = _normalize_score(
            rd.get("employment_rate"),
            rd.get("unemployment_rate"),
            rd.get("tech_vacancy_signal"),
            profile,
        )
        domain_score = computed_score if computed_score > 0 else raw.get("domain_score", 0.0)
        confidence = computed_conf if computed_conf > 0 else raw.get("confidence", 0.0)

        # Build Evidence objects and apply staleness check
        evidence_list: list[Evidence] = []
        caveats: list[str] = list(raw.get("caveats", []))

        for ev in raw.get("evidence", []):
            as_of = ev.get("as_of", "")
            ev_confidence = ev.get("confidence", 0.7)
            if _is_stale(as_of):
                caveats.append(f"Data may be stale (as_of: {as_of}) from {ev.get('title', ev.get('url', ''))}")
                confidence = max(0.0, confidence - 0.2)
            evidence_list.append(Evidence(
                url=ev.get("url", ""),
                title=ev.get("title", ""),
                as_of=as_of,
                confidence=ev_confidence,
                raw_excerpt=ev.get("raw_excerpt", ""),
                source_type=ev.get("source_type", "news"),
            ))

        if not evidence_list:
            caveats.append(f"No data found for {country} — score is unreliable.")
            confidence = 0.0
            domain_score = 0.0

        return AgentOutput(
            agent_name=self.agent_name,
            country=country,
            profile=profile,
            domain_score=domain_score,
            confidence=round(confidence, 2),
            evidence=evidence_list,
            caveats=caveats,
            raw_data=rd,
            fetched_at=self._now_iso(),
        )
