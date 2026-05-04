"""English Accessibility Agent — assesses workplace-English friendliness.

Native-English countries get a flat 100 with high confidence; the rest are scored
from their EF EPI 2024 proficiency band.

Sources: EF English Proficiency Index 2024, official-language status.
"""
from __future__ import annotations

from schema.models import AgentOutput, Evidence

from agents.base_agent import BaseAgent

EPI_BAND_TO_SCORE: dict[str, float] = {
    "very_high": 100.0,
    "high":       80.0,
    "moderate":   60.0,
    "low":        40.0,
    "very_low":   20.0,
}

ENGLISH_DATA: dict[str, dict] = {
    "Canada": {
        "native_english": True,
        "epi_band": None,
        "epi_rank": None,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/canadians/canadian-identity-society/anthems-symbols/official-languages.html", "title": "Official Languages — Government of Canada", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "English and French are the official languages of Canada.", "source_type": "primary_stat"},
        ],
        "caveats": ["Quebec workplaces may require functional French; rest of Canada operates in English."],
    },
    "UK": {
        "native_english": True,
        "epi_band": None,
        "epi_rank": None,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.gov.uk/", "title": "GOV.UK — official portal (English-language nation)", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "English is the de facto official language of the United Kingdom.", "source_type": "primary_stat"},
        ],
        "caveats": [],
    },
    "Ireland": {
        "native_english": True,
        "epi_band": None,
        "epi_rank": None,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.gov.ie/en/", "title": "Gov.ie — Government of Ireland", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "English is one of the two official languages of Ireland and the working language of business.", "source_type": "primary_stat"},
        ],
        "caveats": ["Irish (Gaeilge) is co-official but rarely required for employment."],
    },
    "Netherlands": {
        "native_english": False,
        "epi_band": "very_high",
        "epi_rank": 1,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Netherlands ranks #1 globally", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Netherlands ranks #1 in the EF English Proficiency Index 2024 with 'Very High' proficiency.", "source_type": "index"},
        ],
        "caveats": ["Most professional jobs operate in English, especially in Amsterdam and Eindhoven."],
    },
    "Germany": {
        "native_english": False,
        "epi_band": "very_high",
        "epi_rank": 10,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Germany 'Very High' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Germany scores in the 'Very High' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["Tech/research roles in Berlin and Munich are often English-only; local industry/admin frequently requires German B1+."],
    },
    "Portugal": {
        "native_english": False,
        "epi_band": "very_high",
        "epi_rank": 7,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Portugal 'Very High' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Portugal scores in the 'Very High' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["Tech/digital-nomad scene is fully English-friendly; smaller cities and government offices often require Portuguese."],
    },
    "Spain": {
        "native_english": False,
        "epi_band": "moderate",
        "epi_rank": 36,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Spain 'Moderate' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Spain scores in the 'Moderate' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["Outside multinationals and the Madrid/Barcelona tech scene, Spanish is required for most work."],
    },
    "Australia": {
        "native_english": True,
        "epi_band": None,
        "epi_rank": None,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.australia.gov.au/", "title": "Australia.gov.au — official portal", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "English is the de facto national language of Australia.", "source_type": "primary_stat"},
        ],
        "caveats": [],
    },
    "New Zealand": {
        "native_english": True,
        "epi_band": None,
        "epi_rank": None,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.govt.nz/", "title": "Govt.nz — Government of New Zealand", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "English is the predominant language of business and government in New Zealand.", "source_type": "primary_stat"},
        ],
        "caveats": ["Te Reo Māori is co-official but rarely required for employment."],
    },
    "Singapore": {
        "native_english": True,
        "epi_band": "very_high",
        "epi_rank": 3,
        "needs_local_language_for_work": False,
        "evidence": [
            {"url": "https://www.gov.sg/", "title": "Gov.sg — Government of Singapore", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "English is the language of business, government, and education in Singapore.", "source_type": "primary_stat"},
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Singapore #3 globally", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Singapore ranks #3 in EF EPI 2024 (Very High band).", "source_type": "index"},
        ],
        "caveats": [],
    },
    "Japan": {
        "native_english": False,
        "epi_band": "low",
        "epi_rank": 92,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Japan 'Low' band (rank 92)", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Japan scores in the 'Low' proficiency band on the EF EPI 2024, ranked 92nd globally.", "source_type": "index"},
        ],
        "caveats": ["Outside large multinationals, working-level Japanese (JLPT N2+) is typically required."],
    },
    "South Korea": {
        "native_english": False,
        "epi_band": "moderate",
        "epi_rank": 50,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — South Korea 'Moderate' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "South Korea scores in the 'Moderate' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["Korean is required for most non-teaching work outside multinational tech firms."],
    },
    "Mexico": {
        "native_english": False,
        "epi_band": "low",
        "epi_rank": 87,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Mexico 'Low' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Mexico scores in the 'Low' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["Spanish is required for most local employment; remote-work for US companies bypasses this."],
    },
    "Costa Rica": {
        "native_english": False,
        "epi_band": "moderate",
        "epi_rank": 45,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Costa Rica 'Moderate' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Costa Rica scores in the 'Moderate' band — highest in Latin America.", "source_type": "index"},
        ],
        "caveats": ["Tourism and BPO sectors are English-friendly; other local employment generally requires Spanish."],
    },
    "France": {
        "native_english": False,
        "epi_band": "moderate",
        "epi_rank": 43,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — France 'Moderate' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "France scores in the 'Moderate' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["French is required for most work outside Paris-based multinationals and the English-friendly tech scene at Station F."],
    },
    "Taiwan": {
        "native_english": False,
        "epi_band": "moderate",
        "epi_rank": 41,
        "needs_local_language_for_work": True,
        "evidence": [
            {"url": "https://www.ef.com/wwen/epi/", "title": "EF EPI 2024 — Taiwan 'Moderate' band", "as_of": "2024-11-01", "confidence": 0.85, "raw_excerpt": "Taiwan scores in the 'Moderate' proficiency band on the EF EPI 2024.", "source_type": "index"},
        ],
        "caveats": ["Mandarin is typically required outside English-teaching and select tech roles."],
    },
}


def _normalize_score(native_english: bool, epi_band: str | None) -> tuple[float, float]:
    """Returns (score_0_100, confidence_proxy)."""
    if native_english:
        return 100.0, 0.95
    if epi_band is None:
        return 0.0, 0.0
    score = EPI_BAND_TO_SCORE.get(epi_band, 50.0)
    return score, 0.85


class EnglishAgent(BaseAgent):
    agent_name = "english"

    def run(self, country: str, profile: str) -> AgentOutput:
        data = ENGLISH_DATA.get(country)

        if data is None:
            return AgentOutput(
                agent_name=self.agent_name,
                country=country,
                profile=profile,
                domain_score=0.0,
                confidence=0.0,
                evidence=[],
                caveats=[f"No English-accessibility data available for {country}."],
                raw_data={},
                fetched_at=self._now_iso(),
            )

        domain_score, confidence = _normalize_score(
            data["native_english"], data["epi_band"],
        )

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
            "native_english": data["native_english"],
            "epi_band": data["epi_band"],
            "epi_rank": data["epi_rank"],
            "needs_local_language_for_work": data["needs_local_language_for_work"],
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
