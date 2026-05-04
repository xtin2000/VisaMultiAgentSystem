"""Affordability Agent — scores cost of living for a US citizen.

Score normalization (higher = more affordable):
  oecd_price_level: 130 → 0 pts, 60 → 100 pts (linear, clamped)  weight=0.70
  numbeo_col_index:  90 → 0 pts, 30 → 100 pts (linear, clamped)  weight=0.30

Sources: OECD price level indices (primary), Numbeo cost-of-living (crowdsourced).
"""
from __future__ import annotations

from schema.models import AgentOutput, Evidence

from agents.base_agent import BaseAgent

AFFORDABILITY_DATA: dict[str, dict] = {
    "Canada": {
        "oecd_price_level": 98.0,
        "numbeo_col_index": 67.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Canada", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Canada price level index: ~98 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Canada", "title": "Numbeo — Canada cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Canada ~67 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Toronto and Vancouver run substantially higher than the national average."],
    },
    "UK": {
        "oecd_price_level": 110.0,
        "numbeo_col_index": 70.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — United Kingdom", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "UK price level index: ~110 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=United+Kingdom", "title": "Numbeo — UK cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for UK ~70 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["London is a substantial outlier — 30–40% higher than UK average."],
    },
    "Ireland": {
        "oecd_price_level": 115.0,
        "numbeo_col_index": 76.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Ireland", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Ireland price level index: ~115 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Ireland", "title": "Numbeo — Ireland cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Ireland ~76 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Dublin housing market is acutely constrained; rents have risen sharply since 2022."],
    },
    "Netherlands": {
        "oecd_price_level": 107.0,
        "numbeo_col_index": 70.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Netherlands", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Netherlands price level index: ~107 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Netherlands", "title": "Numbeo — Netherlands cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Netherlands ~70 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Amsterdam housing is severely tight; expect 40%+ premium over national average."],
    },
    "Germany": {
        "oecd_price_level": 99.0,
        "numbeo_col_index": 64.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Germany", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Germany price level index: ~99 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Germany", "title": "Numbeo — Germany cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Germany ~64 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Munich is the priciest city; Berlin and Leipzig remain below average."],
    },
    "Portugal": {
        "oecd_price_level": 78.0,
        "numbeo_col_index": 49.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Portugal", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Portugal price level index: ~78 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Portugal", "title": "Numbeo — Portugal cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Portugal ~49 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Lisbon has gentrified rapidly since 2020; rents now closer to Spanish capital levels."],
    },
    "Spain": {
        "oecd_price_level": 80.0,
        "numbeo_col_index": 52.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Spain", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Spain price level index: ~80 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Spain", "title": "Numbeo — Spain cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Spain ~52 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Barcelona and Madrid run above average; secondary cities like Valencia and Seville are notably cheaper."],
    },
    "Australia": {
        "oecd_price_level": 110.0,
        "numbeo_col_index": 75.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Australia", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Australia price level index: ~110 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Australia", "title": "Numbeo — Australia cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Australia ~75 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Sydney and Melbourne housing among the world's least affordable relative to local wages."],
    },
    "New Zealand": {
        "oecd_price_level": 108.0,
        "numbeo_col_index": 73.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — New Zealand", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "New Zealand price level index: ~108 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=New+Zealand", "title": "Numbeo — New Zealand cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for New Zealand ~73 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Auckland housing is severely constrained; wages outside tech and trades are modest."],
    },
    "Singapore": {
        "oecd_price_level": 108.0,
        "numbeo_col_index": 86.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Singapore", "as_of": "2024-12-01", "confidence": 0.85, "raw_excerpt": "Singapore price level index: ~108 (OECD=100, derived from EIU PPP data).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Singapore", "title": "Numbeo — Singapore cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Singapore ~86 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Housing dominates the cost picture; vehicles are extremely expensive due to COE quotas."],
    },
    "Japan": {
        "oecd_price_level": 85.0,
        "numbeo_col_index": 53.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Japan", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Japan price level index: ~85 (OECD=100), down from ~100 in 2019 due to yen weakness.", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Japan", "title": "Numbeo — Japan cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Japan ~53 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Tokyo housing is reasonable for a major capital; wages are modest by OECD standards."],
    },
    "South Korea": {
        "oecd_price_level": 88.0,
        "numbeo_col_index": 64.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Korea", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "South Korea price level index: ~88 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=South+Korea", "title": "Numbeo — South Korea cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for South Korea ~64 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Seoul housing (jeonse and monthly rentals) is increasingly expensive; secondary cities are far cheaper."],
    },
    "Mexico": {
        "oecd_price_level": 63.0,
        "numbeo_col_index": 38.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Mexico", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Mexico price level index: ~63 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Mexico", "title": "Numbeo — Mexico cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Mexico ~38 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Mexico City and Playa del Carmen rents have risen sharply with US digital-nomad inflows since 2021."],
    },
    "Costa Rica": {
        "oecd_price_level": 72.0,
        "numbeo_col_index": 51.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — Costa Rica", "as_of": "2024-12-01", "confidence": 0.85, "raw_excerpt": "Costa Rica price level index: ~72 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Costa+Rica", "title": "Numbeo — Costa Rica cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Costa Rica ~51 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Imported goods (cars, electronics) carry steep tariffs; produce and services are cheap."],
    },
    "France": {
        "oecd_price_level": 104.0,
        "numbeo_col_index": 62.0,
        "evidence": [
            {"url": "https://data.oecd.org/conversion/price-level-indices.htm", "title": "OECD Price Level Indices — France", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "France price level index: ~104 (OECD=100).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=France", "title": "Numbeo — France cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for France ~62 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Paris is markedly more expensive than the national average; provincial cities (Lyon, Toulouse, Bordeaux) are notably cheaper."],
    },
    "Taiwan": {
        "oecd_price_level": 72.0,
        "numbeo_col_index": 56.0,
        "evidence": [
            {"url": "https://eng.dgbas.gov.tw/", "title": "DGBAS Taiwan — National Statistics (PPP-equivalent)", "as_of": "2024-12-01", "confidence": 0.85, "raw_excerpt": "Taiwan PPP-derived price level: ~72 (OECD=100, Taiwan not an OECD member).", "source_type": "primary_stat"},
            {"url": "https://www.numbeo.com/cost-of-living/country_result.jsp?country=Taiwan", "title": "Numbeo — Taiwan cost of living", "as_of": "2025-01-01", "confidence": 0.5, "raw_excerpt": "Numbeo COL index for Taiwan ~56 (NYC=100).", "source_type": "crowdsourced"},
        ],
        "caveats": ["Taipei housing is the costliest segment; transit, food, and healthcare are very affordable."],
    },
}


def _normalize_score(
    oecd_price_level: float | None,
    numbeo_col_index: float | None,
) -> tuple[float, float]:
    """Returns (score_0_100, confidence_proxy). Higher score = more affordable."""
    score = 0.0
    weight_used = 0.0

    # OECD price level (70%) — 60 = 100 pts, 130 = 0 pts (linear)
    if oecd_price_level is not None:
        oecd_score = max(0.0, min(100.0, (130.0 - oecd_price_level) / 70.0 * 100.0))
        score += oecd_score * 0.70
        weight_used += 0.70

    # Numbeo COL index (30%) — 30 = 100 pts, 90 = 0 pts (linear)
    if numbeo_col_index is not None:
        numbeo_score = max(0.0, min(100.0, (90.0 - numbeo_col_index) / 60.0 * 100.0))
        score += numbeo_score * 0.30
        weight_used += 0.30

    if weight_used == 0:
        return 0.0, 0.0

    normalized = score / weight_used
    return round(normalized, 1), round(weight_used, 2)


class AffordabilityAgent(BaseAgent):
    agent_name = "affordability"

    def run(self, country: str, profile: str) -> AgentOutput:
        data = AFFORDABILITY_DATA.get(country)

        if data is None:
            return AgentOutput(
                agent_name=self.agent_name,
                country=country,
                profile=profile,
                domain_score=0.0,
                confidence=0.0,
                evidence=[],
                caveats=[f"No affordability data available for {country}."],
                raw_data={},
                fetched_at=self._now_iso(),
            )

        oecd_price_level = data["oecd_price_level"]
        numbeo_col_index = data["numbeo_col_index"]

        domain_score, confidence = _normalize_score(oecd_price_level, numbeo_col_index)

        evidence_list = [
            Evidence(
                url=ev["url"],
                title=ev["title"],
                as_of=ev["as_of"],
                confidence=ev["confidence"],
                raw_excerpt=ev["raw_excerpt"],
                source_type=ev["source_type"],
            )
            for ev in data["evidence"]
        ]

        raw_data = {
            "oecd_price_level": oecd_price_level,
            "numbeo_col_index": numbeo_col_index,
        }

        return AgentOutput(
            agent_name=self.agent_name,
            country=country,
            profile=profile,
            domain_score=domain_score,
            confidence=confidence,
            evidence=evidence_list,
            caveats=data.get("caveats", []),
            raw_data=raw_data,
            fetched_at=self._now_iso(),
        )
