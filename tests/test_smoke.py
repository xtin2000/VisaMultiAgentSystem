"""Smoke tests: every static-dataset agent returns a valid AgentOutput per country."""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("GOOGLE_API_KEY", "test-dummy-not-used")

import config  # noqa: E402
from agents.affordability_agent import AffordabilityAgent  # noqa: E402
from agents.english_agent import EnglishAgent  # noqa: E402
from agents.job_market_agent import JobMarketAgent  # noqa: E402
from agents.visa_agent import VisaAgent  # noqa: E402
from ranker.ranker import rank  # noqa: E402
from schema.models import AgentOutput, CountryProfile  # noqa: E402

STATIC_AGENT_CLASSES = [VisaAgent, EnglishAgent, AffordabilityAgent, JobMarketAgent]


@pytest.mark.parametrize("agent_cls", STATIC_AGENT_CLASSES)
@pytest.mark.parametrize("country", config.COUNTRIES)
def test_agent_returns_valid_output_for_every_country(agent_cls, country):
    out = agent_cls().run(country, "software_engineer")
    assert isinstance(out, AgentOutput)
    assert 0.0 <= out.domain_score <= 100.0
    assert 0.0 <= out.confidence <= 1.0
    assert out.country == country
    assert out.evidence, f"{agent_cls.__name__} for {country} returned no evidence"


def test_evidence_carries_required_fields():
    out = VisaAgent().run("Canada", "software_engineer")
    for ev in out.evidence:
        assert ev.url and ev.title and ev.as_of and ev.raw_excerpt
        assert ev.source_type in {"primary_stat", "index", "news", "crowdsourced"}


def test_ranker_renormalizes_when_agent_disabled():
    cps = [
        CountryProfile(
            country=c, profile="software_engineer",
            agent_outputs={
                "visa":          VisaAgent().run(c, "software_engineer"),
                "english":       EnglishAgent().run(c, "software_engineer"),
                "affordability": AffordabilityAgent().run(c, "software_engineer"),
            },
            resolved_scores={},
            resolved_evidence={},
            merged_at="2026-01-01T00:00:00+00:00",
        )
        for c in ["Canada", "Portugal"]
    ]
    for cp in cps:
        cp.resolved_scores = {k: v.domain_score for k, v in cp.agent_outputs.items()}
        cp.resolved_evidence = {k: v.evidence for k, v in cp.agent_outputs.items()}

    results = rank(cps, disabled_agents=["job_market"])
    weight_sum = sum(results[0].weight_breakdown.values())
    assert abs(weight_sum - 1.0) < 1e-9
    assert "job_market" not in results[0].weight_breakdown
