"""Job Market Agent — assesses labour-market accessibility for US migrants.

Score normalization:
  employment_rate:    60% → 0 pts, 80% → 100 pts  weight=0.50
  unemployment_rate:  12% → 0 pts, 3%  → 100 pts  weight=0.35
  tech_signal:        low=20 / medium=60 / high=100  weight=0.15  (software_engineer only)

Sources: OECD employment rate, World Bank / ILO modelled unemployment rate,
EURES tech-vacancy signal (Europe) and equivalents elsewhere.
"""
from __future__ import annotations

from datetime import date

import config
from dateutil.relativedelta import relativedelta
from schema.models import AgentOutput, Evidence

from agents.base_agent import BaseAgent

JOB_MARKET_DATA: dict[str, dict] = {
    "Canada": {
        "employment_rate": 62.0,
        "unemployment_rate": 6.4,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Canada", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Canada employment rate (15–64): ~62% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=CA", "title": "World Bank — Unemployment, total (% of labor force) — Canada", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Canada unemployment rate (ILO modeled): ~6.4% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Tech hiring concentrated in Toronto, Vancouver, Montreal; LMIA process can be slow."],
    },
    "UK": {
        "employment_rate": 75.0,
        "unemployment_rate": 4.2,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — United Kingdom", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "UK employment rate (15–64): ~75% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=GB", "title": "World Bank — Unemployment — United Kingdom", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "UK unemployment rate (ILO modeled): ~4.2% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Sponsor licence required for most non-EU work; salary thresholds raised in 2024."],
    },
    "Ireland": {
        "employment_rate": 74.0,
        "unemployment_rate": 4.5,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Ireland", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Ireland employment rate (15–64): ~74% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=IE", "title": "World Bank — Unemployment — Ireland", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Ireland unemployment rate (ILO modeled): ~4.5% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Heavy concentration of US tech multinationals in Dublin (Google, Meta, Microsoft, Stripe)."],
    },
    "Netherlands": {
        "employment_rate": 82.0,
        "unemployment_rate": 3.5,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Netherlands", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Netherlands employment rate (15–64): ~82% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=NL", "title": "World Bank — Unemployment — Netherlands", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Netherlands unemployment rate (ILO modeled): ~3.5% (2024).", "source_type": "primary_stat"},
            {"url": "https://eures.europa.eu/", "title": "EURES — Tech vacancies in the Netherlands", "as_of": "2024-10-01", "confidence": 0.7, "raw_excerpt": "Software developer roles among the highest-volume EURES vacancy categories for NL.", "source_type": "index"},
        ],
        "caveats": ["Highest OECD employment rate; small population means high competition for senior roles."],
    },
    "Germany": {
        "employment_rate": 77.0,
        "unemployment_rate": 3.5,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Germany", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Germany employment rate (15–64): ~77% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=DE", "title": "World Bank — Unemployment — Germany", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Germany unemployment rate (ILO modeled): ~3.5% (2024).", "source_type": "primary_stat"},
            {"url": "https://eures.europa.eu/", "title": "EURES — Tech vacancies in Germany", "as_of": "2024-10-01", "confidence": 0.7, "raw_excerpt": "Germany consistently leads EU EURES tech vacancy volume (Berlin, Munich, Hamburg).", "source_type": "index"},
        ],
        "caveats": ["German B1+ often required outside Berlin/Munich tech scenes."],
    },
    "Portugal": {
        "employment_rate": 73.0,
        "unemployment_rate": 6.5,
        "tech_vacancy_signal": "medium",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Portugal", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Portugal employment rate (15–64): ~73% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=PT", "title": "World Bank — Unemployment — Portugal", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Portugal unemployment rate (ILO modeled): ~6.5% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Lisbon tech scene growing fast (Tech Visa, Web Summit), but local salaries are markedly below Western EU."],
    },
    "Spain": {
        "employment_rate": 64.0,
        "unemployment_rate": 12.0,
        "tech_vacancy_signal": "medium",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Spain", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Spain employment rate (15–64): ~64% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=ES", "title": "World Bank — Unemployment — Spain", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Spain unemployment rate (ILO modeled): ~12% (2024) — highest in OECD.", "source_type": "primary_stat"},
        ],
        "caveats": ["Highest unemployment rate in the OECD; tech demand concentrated in Madrid and Barcelona."],
    },
    "Australia": {
        "employment_rate": 76.0,
        "unemployment_rate": 3.9,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Australia", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Australia employment rate (15–64): ~76% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=AU", "title": "World Bank — Unemployment — Australia", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Australia unemployment rate (ILO modeled): ~3.9% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Sydney/Melbourne tech market healthy; mining and resources sector still major employer."],
    },
    "New Zealand": {
        "employment_rate": 78.0,
        "unemployment_rate": 4.0,
        "tech_vacancy_signal": "medium",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — New Zealand", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "New Zealand employment rate (15–64): ~78% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=NZ", "title": "World Bank — Unemployment — New Zealand", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "New Zealand unemployment rate (ILO modeled): ~4.0% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Smaller tech market than Australia; senior roles fewer; agriculture and tourism still dominant."],
    },
    "Singapore": {
        "employment_rate": 70.0,
        "unemployment_rate": 2.0,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://www.mom.gov.sg/", "title": "Singapore MOM Labour Market Report", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Singapore employment rate (residents 15–64): ~70% (MOM 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=SG", "title": "World Bank — Unemployment — Singapore", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Singapore unemployment rate (ILO modeled): ~2.0% (2024) — among the world's lowest.", "source_type": "primary_stat"},
        ],
        "caveats": ["COMPASS framework (2023) tightened EP eligibility; min salary $5,000/mo."],
    },
    "Japan": {
        "employment_rate": 78.0,
        "unemployment_rate": 2.6,
        "tech_vacancy_signal": "medium",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Japan", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Japan employment rate (15–64): ~78% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=JP", "title": "World Bank — Unemployment — Japan", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Japan unemployment rate (ILO modeled): ~2.6% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Tight labour market overall, but English-only tech roles concentrated in foreign firms in Tokyo."],
    },
    "South Korea": {
        "employment_rate": 69.0,
        "unemployment_rate": 2.9,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Korea", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "South Korea employment rate (15–64): ~69% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=KR", "title": "World Bank — Unemployment — Korea", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "South Korea unemployment rate (ILO modeled): ~2.9% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Strong domestic tech sector (Samsung, Naver, Kakao) but Korean fluency typically required."],
    },
    "Mexico": {
        "employment_rate": 60.0,
        "unemployment_rate": 3.2,
        "tech_vacancy_signal": "low",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — Mexico", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "Mexico employment rate (15–64): ~60% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=MX", "title": "World Bank — Unemployment — Mexico", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Mexico unemployment rate (ILO modeled): ~3.2% (2024) — note large informal sector.", "source_type": "primary_stat"},
        ],
        "caveats": ["Low headline unemployment masks large informal sector; remote-for-US is the dominant high-paid path."],
    },
    "Costa Rica": {
        "employment_rate": 60.0,
        "unemployment_rate": 7.5,
        "tech_vacancy_signal": "medium",
        "evidence": [
            {"url": "https://data.worldbank.org/indicator/SL.EMP.TOTL.SP.ZS?locations=CR", "title": "World Bank — Employment to population ratio — Costa Rica", "as_of": "2024-12-01", "confidence": 0.85, "raw_excerpt": "Costa Rica employment-to-population ratio (15+): ~60% (2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=CR", "title": "World Bank — Unemployment — Costa Rica", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "Costa Rica unemployment rate (ILO modeled): ~7.5% (2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Strong nearshoring/BPO sector for US firms; senior tech roles fewer than in Mexico."],
    },
    "France": {
        "employment_rate": 68.0,
        "unemployment_rate": 7.3,
        "tech_vacancy_signal": "medium",
        "evidence": [
            {"url": "https://data.oecd.org/emp/employment-rate.htm", "title": "OECD Employment Rate — France", "as_of": "2024-09-01", "confidence": 0.9, "raw_excerpt": "France employment rate (15–64): ~68% (OECD, Q3 2024).", "source_type": "primary_stat"},
            {"url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=FR", "title": "World Bank — Unemployment — France", "as_of": "2024-12-01", "confidence": 0.9, "raw_excerpt": "France unemployment rate (ILO modeled): ~7.3% (2024).", "source_type": "primary_stat"},
            {"url": "https://eures.europa.eu/", "title": "EURES — Tech vacancies in France", "as_of": "2024-10-01", "confidence": 0.7, "raw_excerpt": "France tech vacancies concentrated in Paris (Station F ecosystem); volume below Germany and Netherlands.", "source_type": "index"},
        ],
        "caveats": ["Tech market concentrated in Paris; French B2+ typically required outside multinationals."],
    },
    "Taiwan": {
        "employment_rate": 60.0,
        "unemployment_rate": 3.7,
        "tech_vacancy_signal": "high",
        "evidence": [
            {"url": "https://eng.dgbas.gov.tw/", "title": "DGBAS Taiwan — Labour Statistics", "as_of": "2024-12-01", "confidence": 0.85, "raw_excerpt": "Taiwan labour-force employment ratio (15+): ~60% (DGBAS 2024).", "source_type": "primary_stat"},
            {"url": "https://eng.dgbas.gov.tw/", "title": "DGBAS Taiwan — Unemployment Rate", "as_of": "2024-12-01", "confidence": 0.85, "raw_excerpt": "Taiwan unemployment rate: ~3.7% (DGBAS 2024).", "source_type": "primary_stat"},
        ],
        "caveats": ["Hardware/semi sector world-class (TSMC); software product roles fewer; Mandarin often required."],
    },
}


def _normalize_score(
    employment_rate: float | None,
    unemployment_rate: float | None,
    tech_signal: str | None,
    profile: str,
) -> tuple[float, float]:
    """Returns (score_0_100, weight_used)."""
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
    return round(score / weight_used, 1), round(weight_used, 2)


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
        data = JOB_MARKET_DATA.get(country)

        if data is None:
            return AgentOutput(
                agent_name=self.agent_name,
                country=country,
                profile=profile,
                domain_score=0.0,
                confidence=0.0,
                evidence=[],
                caveats=[f"No job-market data available for {country}."],
                raw_data={},
                fetched_at=self._now_iso(),
            )

        domain_score, confidence = _normalize_score(
            data["employment_rate"],
            data["unemployment_rate"],
            data["tech_vacancy_signal"],
            profile,
        )

        evidence_list: list[Evidence] = []
        caveats: list[str] = list(data.get("caveats", []))

        for ev in data["evidence"]:
            if _is_stale(ev["as_of"]):
                caveats.append(f"Data may be stale (as_of: {ev['as_of']}) from {ev['title']}")
                confidence = max(0.0, confidence - 0.2)
            evidence_list.append(Evidence(
                url=ev["url"],
                title=ev["title"],
                as_of=ev["as_of"],
                confidence=ev["confidence"],
                raw_excerpt=ev["raw_excerpt"],
                source_type=ev["source_type"],
            ))

        raw_data = {
            "employment_rate": data["employment_rate"],
            "unemployment_rate": data["unemployment_rate"],
            "tech_vacancy_signal": data["tech_vacancy_signal"],
        }

        return AgentOutput(
            agent_name=self.agent_name,
            country=country,
            profile=profile,
            domain_score=domain_score,
            confidence=round(confidence, 2),
            evidence=evidence_list,
            caveats=caveats,
            raw_data=raw_data,
            fetched_at=self._now_iso(),
        )
