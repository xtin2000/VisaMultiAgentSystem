"""Generate 'why-this-rank' bullets deterministically from score breakdown + evidence.

No LLM call — keeps the demo reproducible and removes the API-quota dependency.
"""
from __future__ import annotations

from schema.models import RankedResult

DOMAIN_LABEL: dict[str, str] = {
    "visa":          "visa pathways",
    "job_market":    "job-market access",
    "affordability": "affordability",
    "english":       "English accessibility",
}


def _qualitative_band(score: float) -> str:
    if score >= 85:
        return "very strong"
    if score >= 70:
        return "strong"
    if score >= 55:
        return "moderate"
    if score >= 40:
        return "weak"
    return "very weak"


def generate(result: RankedResult) -> list[str]:
    """Return 3–5 evidence-grounded bullets explaining this country's rank."""
    bullets: list[str] = []

    sorted_breakdown = sorted(result.score_breakdown.items(), key=lambda kv: kv[1], reverse=True)

    if sorted_breakdown:
        top_domain, top_score = sorted_breakdown[0]
        bullets.append(
            f"Highest-scoring domain: {DOMAIN_LABEL.get(top_domain, top_domain)} "
            f"({top_score:.0f}/100, {_qualitative_band(top_score)})."
        )

    if len(sorted_breakdown) > 1:
        bottom_domain, bottom_score = sorted_breakdown[-1]
        if bottom_domain != sorted_breakdown[0][0] and bottom_score < 70:
            bullets.append(
                f"Weakest-scoring domain: {DOMAIN_LABEL.get(bottom_domain, bottom_domain)} "
                f"({bottom_score:.0f}/100, {_qualitative_band(bottom_score)})."
            )

    for domain in (sorted_breakdown[0][0], sorted_breakdown[-1][0] if sorted_breakdown else None):
        if domain is None:
            continue
        ev_list = result.country_profile.resolved_evidence.get(domain, [])
        if ev_list and ev_list[0].raw_excerpt:
            excerpt = ev_list[0].raw_excerpt.strip()
            if len(excerpt) > 140:
                excerpt = excerpt[:137].rstrip() + "…"
            bullets.append(f"Evidence ({domain}): {excerpt}")

    caveats: list[str] = []
    for output in result.country_profile.agent_outputs.values():
        caveats.extend(output.caveats)
    if caveats:
        first_caveat = caveats[0].strip()
        if len(first_caveat) > 140:
            first_caveat = first_caveat[:137].rstrip() + "…"
        bullets.append(f"Caveat: {first_caveat}")

    if result.missing_agents:
        bullets.append(
            f"Note: scored without {', '.join(result.missing_agents)} "
            "(no data); weights renormalized."
        )

    return bullets[:5]
