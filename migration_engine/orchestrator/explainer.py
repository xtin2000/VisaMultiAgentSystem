"""
Generates "Why this ranked high/low" explanation bullets for each RankedResult.
Makes one lightweight Claude call per country using score breakdown as context.
"""
from __future__ import annotations

import os
import anthropic
import config
from schema.models import RankedResult


def generate(client: anthropic.Anthropic, result: RankedResult) -> list[str]:
    """Return 3–5 plain-English bullet points explaining this country's ranking."""
    # Build a concise context block for Claude
    breakdown_lines = []
    for agent, score in result.score_breakdown.items():
        weight = result.weight_breakdown.get(agent, 0)
        breakdown_lines.append(f"  {agent}: {score:.1f}/100 (weight {weight:.0%})")

    missing_note = ""
    if result.missing_agents:
        missing_note = f"\nMissing data from: {', '.join(result.missing_agents)} (those domains were excluded from scoring)."

    evidence_excerpts = []
    for agent_name, ev_list in result.country_profile.resolved_evidence.items():
        for ev in ev_list[:2]:  # Top 2 per agent
            if ev.raw_excerpt:
                evidence_excerpts.append(f"[{agent_name}] {ev.raw_excerpt[:200]}")

    evidence_block = "\n".join(evidence_excerpts[:6]) if evidence_excerpts else "No evidence excerpts available."

    user = f"""\
Country: {result.country}
Overall rank: #{result.rank} (score: {result.total_score:.1f}/100)
Profile: {result.profile.replace("_", " ")}

Score breakdown:
{chr(10).join(breakdown_lines)}
{missing_note}

Key evidence excerpts:
{evidence_block}

Write 3–5 short, specific bullet points explaining WHY this country ranked where it did.
Focus on concrete facts from the evidence. Be honest about weaknesses too.
Each bullet should start with a bullet character "•".
Do not include a header or intro sentence — just the bullets.
"""

    response = client.messages.create(
        model=config.MODEL,
        max_tokens=512,
        system=(
            "You are a concise migration analyst. "
            "Produce factual, evidence-grounded bullet points. "
            "No fluff, no filler phrases like 'Overall,'. Max 15 words per bullet."
        ),
        messages=[{"role": "user", "content": user}],
    )

    text = response.content[0].text.strip()
    bullets = [line.strip().lstrip("•").strip() for line in text.splitlines() if line.strip().startswith("•")]
    if not bullets:
        # Fallback: split on newlines
        bullets = [line.strip() for line in text.splitlines() if line.strip()]
    return bullets[:5]
