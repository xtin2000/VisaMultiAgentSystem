from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Evidence:
    """A single citation supporting a domain score."""
    url: str
    title: str
    as_of: str          # ISO 8601 date string, e.g. "2025-01-15"
    confidence: float   # 0.0–1.0; primary_stat ~0.9, crowdsourced ~0.4
    raw_excerpt: str    # Verbatim relevant text from the source
    source_type: str    # "primary_stat" | "index" | "news" | "crowdsourced"


@dataclass
class AgentOutput:
    """
    Standardized output contract every domain agent must return.
    Person B's agents (visa, affordability, english) must return this exact shape.
    """
    agent_name: str     # "job_market" | "visa" | "affordability" | "english"
    country: str        # Must match a value in config.COUNTRIES exactly
    profile: str        # "software_engineer" | "general_professional" | "student_to_work"
    domain_score: float # Normalized 0–100
    confidence: float   # Aggregate confidence for this score (0.0–1.0)
    evidence: list[Evidence]
    caveats: list[str]
    raw_data: dict      # Agent-specific intermediate values for debugging
    fetched_at: str     # ISO 8601 datetime of the run


@dataclass
class CountryProfile:
    """
    Merged view of all agent outputs for one country + profile combination.
    Built by orchestrator/merger.py after collecting all AgentOutputs.
    """
    country: str
    profile: str
    agent_outputs: dict[str, AgentOutput]       # keyed by agent_name
    resolved_scores: dict[str, float]           # After conflict resolution
    resolved_evidence: dict[str, list[Evidence]]
    merged_at: str                              # ISO 8601 datetime


@dataclass
class RankedResult:
    """One entry in the final ranked list."""
    rank: int
    country: str
    profile: str
    total_score: float                  # Weighted composite 0–100
    score_breakdown: dict[str, float]   # {"job_market": 74.0, "visa": 65.0, ...}
    weight_breakdown: dict[str, float]  # {"job_market": 0.25, "visa": 0.30, ...}
    explanation_bullets: list[str]      # LLM-generated, e.g. "Strong employment rate (78%)"
    missing_agents: list[str]           # Agents that returned no data
    confidence_overall: float           # Weighted average of agent confidences
    country_profile: CountryProfile
