"""
Weighted scoring and ranking.

Default weights: visa=30%, job_market=25%, affordability=25%, english=20%

Ablation: pass disabled_agents=['english'] to drop that domain and renormalize.
Missing agent output (confidence == 0): flagged in missing_agents, excluded from score.
"""
from __future__ import annotations

import config
from schema.models import CountryProfile, RankedResult


def rank(
    country_profiles: list[CountryProfile],
    weights: dict[str, float] | None = None,
    disabled_agents: list[str] | None = None,
) -> list[RankedResult]:
    disabled_agents = disabled_agents or []
    base_weights = weights or config.DEFAULT_WEIGHTS

    # Drop disabled agents and renormalize so weights sum to 1.0
    active_weights = {k: v for k, v in base_weights.items() if k not in disabled_agents}
    total = sum(active_weights.values())
    if total == 0:
        raise ValueError("All agents are disabled — cannot produce a ranking.")
    normalized_weights = {k: v / total for k, v in active_weights.items()}

    results: list[RankedResult] = []

    for cp in country_profiles:
        score = 0.0
        missing: list[str] = []
        conf_components: list[float] = []
        effective_weight_total = 0.0

        for agent_name, w in normalized_weights.items():
            agent_out = cp.agent_outputs.get(agent_name)
            if agent_out is None or agent_out.confidence == 0.0:
                missing.append(agent_name)
                continue
            domain_score = cp.resolved_scores.get(agent_name, agent_out.domain_score)
            score += domain_score * w
            conf_components.append(agent_out.confidence * w)
            effective_weight_total += w

        # Rescale score if some agents were missing
        if effective_weight_total > 0 and effective_weight_total < 1.0:
            score = score / effective_weight_total

        overall_conf = sum(conf_components) / effective_weight_total if effective_weight_total > 0 else 0.0

        results.append(RankedResult(
            rank=0,  # assigned after sort
            country=cp.country,
            profile=cp.profile,
            total_score=round(score, 2),
            score_breakdown={
                k: cp.resolved_scores.get(k, 0.0) for k in normalized_weights
            },
            weight_breakdown=normalized_weights,
            explanation_bullets=[],  # filled by explainer
            missing_agents=missing,
            confidence_overall=round(overall_conf, 3),
            country_profile=cp,
        ))

    results.sort(key=lambda r: r.total_score, reverse=True)
    for i, r in enumerate(results, 1):
        r.rank = i

    return results
