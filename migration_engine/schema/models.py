"""Shared dataclasses returned by every agent and consumed by the orchestrator."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Evidence:
    """A single citation supporting a domain score."""

    url: str
    title: str
    as_of: str          # ISO 8601 date
    confidence: float   # 0.0–1.0
    raw_excerpt: str
    source_type: str    # "primary_stat" | "index" | "news" | "crowdsourced"


@dataclass
class AgentOutput:
    """Standardized output contract every domain agent must return."""

    agent_name: str
    country: str
    profile: str
    domain_score: float   # 0–100
    confidence: float     # 0.0–1.0
    evidence: list[Evidence]
    caveats: list[str]
    raw_data: dict
    fetched_at: str       # ISO 8601 datetime


@dataclass
class CountryProfile:
    """Merged view of all agent outputs for one country + profile."""

    country: str
    profile: str
    agent_outputs: dict[str, AgentOutput]
    resolved_scores: dict[str, float]
    resolved_evidence: dict[str, list[Evidence]]
    merged_at: str


@dataclass
class RankedResult:
    """One entry in the final ranked list."""

    rank: int
    country: str
    profile: str
    total_score: float                  # weighted composite, 0–100
    score_breakdown: dict[str, float]
    weight_breakdown: dict[str, float]
    explanation_bullets: list[str]
    missing_agents: list[str]
    confidence_overall: float
    country_profile: CountryProfile
