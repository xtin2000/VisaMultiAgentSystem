"""Visa Requirements Agent — assesses work-visa accessibility for US citizens.

Score normalization:
  henley_access:      visa_required=30 / visa_on_arrival=60 / eta_evisa=80 / visa_free=100  weight=0.20
  processing_months:  24 mo → 0 pts, 3 mo → 100 pts (linear, clamped)                       weight=0.25
  sponsorship:        required=20 / sometimes=60 / not_required=100                          weight=0.25
  pathway_count:      min(count / 4, 1.0) × 100                                             weight=0.30

Sources: Henley Passport Index, official government immigration sites.
"""
from __future__ import annotations

from schema.models import AgentOutput, Evidence

from agents.base_agent import BaseAgent

VISA_DATA: dict[str, dict] = {
    "Canada": {
        "henley_access": "visa_free",
        "processing_months": 6,
        "sponsorship_required": "sometimes",
        "pathway_count": 5,  # Express Entry, LMIA, IEC Working Holiday, Start-up Visa, Provincial Nominee
        "pathways": ["Express Entry (Federal Skilled Worker)", "LMIA employer-sponsored", "IEC Working Holiday", "Start-up Visa", "Provincial Nominee Program"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Canada.", "source_type": "index"},
            {"url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html", "title": "Express Entry - Canada.ca", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Express Entry manages applications for permanent residence for skilled workers. No job offer required for FSW.", "source_type": "primary_stat"},
        ],
        "caveats": ["Express Entry does not require employer sponsorship, but LMIA pathway does."],
    },
    "UK": {
        "henley_access": "visa_free",
        "processing_months": 3,
        "sponsorship_required": "required",
        "pathway_count": 5,  # Skilled Worker, Global Talent, Innovator Founder, ICT, Graduate
        "pathways": ["Skilled Worker Visa", "Global Talent Visa", "Innovator Founder Visa", "Intra-Company Transfer", "Graduate Visa (post-study)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to the UK for up to 6 months.", "source_type": "index"},
            {"url": "https://www.gov.uk/skilled-worker-visa", "title": "Skilled Worker Visa - GOV.UK", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "You must have a job offer from a UK employer with a sponsor licence. Processing time: 3 weeks for standard.", "source_type": "primary_stat"},
        ],
        "caveats": ["Most work visas require employer sponsorship. Global Talent is an exception but highly selective."],
    },
    "Ireland": {
        "henley_access": "visa_free",
        "processing_months": 4,
        "sponsorship_required": "required",
        "pathway_count": 4,  # Critical Skills, General Work Permit, ICT, Stamp 1G
        "pathways": ["Critical Skills Employment Permit", "General Work Permit", "Intra-Company Transfer", "Stamp 1G (graduate)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Ireland.", "source_type": "index"},
            {"url": "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/", "title": "Employment Permits - DETE Ireland", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Critical Skills Employment Permit for occupations on the critical skills list. Processing: up to 4 months.", "source_type": "primary_stat"},
        ],
        "caveats": ["Must have a job offer. Critical Skills permit has a specific occupation list."],
    },
    "Netherlands": {
        "henley_access": "visa_free",
        "processing_months": 3,
        "sponsorship_required": "sometimes",
        "pathway_count": 5,  # Highly Skilled Migrant, Orientation Year, Self-employed, ICT, DAFT
        "pathways": ["Highly Skilled Migrant (Kennismigrant)", "Orientation Year (Zoekjaar)", "Self-employed Permit", "Intra-Company Transfer", "DAFT (Dutch-American Friendship Treaty)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to the Netherlands (Schengen area).", "source_type": "index"},
            {"url": "https://ind.nl/en/work/working-in-the-netherlands", "title": "Working in the Netherlands - IND", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "The DAFT treaty allows US citizens to start a business with a low investment threshold of EUR 4,500.", "source_type": "primary_stat"},
        ],
        "caveats": ["DAFT treaty is uniquely favorable for US citizens. Highly Skilled Migrant requires employer sponsorship."],
    },
    "Germany": {
        "henley_access": "visa_free",
        "processing_months": 4,
        "sponsorship_required": "sometimes",
        "pathway_count": 5,  # EU Blue Card, Job Seeker, Skilled Worker, Freelance, ICT
        "pathways": ["EU Blue Card", "Job Seeker Visa", "Skilled Immigration Act Visa", "Freelance Visa", "Intra-Company Transfer"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Germany (Schengen area).", "source_type": "index"},
            {"url": "https://www.make-it-in-germany.com/en/visa-residence/types/work", "title": "Work Visa - Make It in Germany", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Germany's Skilled Immigration Act allows qualified professionals to come to Germany for work. Freelance visa available without employer.", "source_type": "primary_stat"},
        ],
        "caveats": ["EU Blue Card requires a job offer meeting salary threshold. Freelance visa allows self-employment."],
    },
    "Portugal": {
        "henley_access": "visa_free",
        "processing_months": 4,
        "sponsorship_required": "sometimes",
        "pathway_count": 5,  # Tech Visa, D7 Passive Income, Digital Nomad, Job Seeker, Golden Visa
        "pathways": ["Tech Visa", "D7 Passive Income Visa", "Digital Nomad Visa", "Job Seeker Visa", "Golden Visa (investment)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Portugal (Schengen area).", "source_type": "index"},
            {"url": "https://www.sef.pt/en/pages/conteudo-detalhe.aspx?nID=62", "title": "Work Visa - SEF Portugal", "as_of": "2025-01-15", "confidence": 0.9, "raw_excerpt": "Portugal offers a Digital Nomad Visa for remote workers earning 4x the minimum wage.", "source_type": "primary_stat"},
        ],
        "caveats": ["Digital Nomad and D7 visas do not require employer sponsorship. Tech Visa requires certified company."],
    },
    "Spain": {
        "henley_access": "visa_free",
        "processing_months": 5,
        "sponsorship_required": "sometimes",
        "pathway_count": 4,  # Highly Skilled, Digital Nomad, Entrepreneur, Non-Lucrative
        "pathways": ["Highly Qualified Professional Visa", "Digital Nomad Visa", "Entrepreneur Visa", "Non-Lucrative Visa"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Spain (Schengen area).", "source_type": "index"},
            {"url": "https://www.exteriores.gob.es/en/ServiciosAlCiudadano/Paginas/Trabajo.aspx", "title": "Work Visa - Spanish Ministry of Foreign Affairs", "as_of": "2025-01-15", "confidence": 0.9, "raw_excerpt": "Spain launched its Digital Nomad Visa in 2023 for remote workers.", "source_type": "primary_stat"},
        ],
        "caveats": ["Digital Nomad Visa requires proof of remote work for non-Spanish company."],
    },
    "Australia": {
        "henley_access": "eta_evisa",
        "processing_months": 5,
        "sponsorship_required": "sometimes",
        "pathway_count": 5,  # Skilled Independent, Employer Sponsored, Working Holiday, Global Talent, Student-to-work
        "pathways": ["Skilled Independent (subclass 189)", "Employer Sponsored (subclass 482)", "Working Holiday (subclass 462)", "Global Talent Visa", "Post-study Work Visa (subclass 485)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US citizens require an ETA (Electronic Travel Authority) for Australia.", "source_type": "index"},
            {"url": "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/skilled-independent-189", "title": "Skilled Independent Visa - Australian Government", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Subclass 189 is a points-tested visa for skilled workers who are not sponsored by an employer.", "source_type": "primary_stat"},
        ],
        "caveats": ["Points-based system. ETA required for entry (not visa-free). Working Holiday available for ages 18-30."],
    },
    "New Zealand": {
        "henley_access": "visa_free",
        "processing_months": 5,
        "sponsorship_required": "sometimes",
        "pathway_count": 5,  # Skilled Migrant, Accredited Employer, Working Holiday, Entrepreneur, Post-study
        "pathways": ["Skilled Migrant Category", "Accredited Employer Work Visa", "Working Holiday Visa", "Entrepreneur Work Visa", "Post-Study Work Visa"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to New Zealand.", "source_type": "index"},
            {"url": "https://www.immigration.govt.nz/new-zealand-visas/apply-for-a-visa/about-visa/skilled-migrant-category-resident-visa", "title": "Skilled Migrant Category - INZ", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Points-based resident visa for skilled workers. No employer sponsorship required.", "source_type": "primary_stat"},
        ],
        "caveats": ["Skilled Migrant Category uses points-based system. Working Holiday for ages 18-30."],
    },
    "Singapore": {
        "henley_access": "visa_free",
        "processing_months": 2,
        "sponsorship_required": "required",
        "pathway_count": 4,  # Employment Pass, S Pass, EntrePass, Personalised Employment Pass
        "pathways": ["Employment Pass (EP)", "S Pass", "EntrePass (entrepreneurs)", "Personalised Employment Pass (PEP)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Singapore for 90 days.", "source_type": "index"},
            {"url": "https://www.mom.gov.sg/passes-and-permits/employment-pass", "title": "Employment Pass - MOM Singapore", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Employment Pass for foreign professionals. Minimum salary $5,000/month. Employer must apply.", "source_type": "primary_stat"},
        ],
        "caveats": ["All work passes require employer sponsorship. EntrePass is an exception for entrepreneurs. COMPASS framework introduced in 2023."],
    },
    "Japan": {
        "henley_access": "visa_free",
        "processing_months": 3,
        "sponsorship_required": "required",
        "pathway_count": 4,  # Engineer/Specialist, Highly Skilled Professional, Specified Skilled Worker, Business Manager
        "pathways": ["Engineer/Specialist in Humanities Visa", "Highly Skilled Professional Visa (HSP)", "Specified Skilled Worker Visa", "Business Manager Visa"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Japan for 90 days.", "source_type": "index"},
            {"url": "https://www.mofa.go.jp/j_info/visit/visa/long/index.html", "title": "Work Visa - Ministry of Foreign Affairs Japan", "as_of": "2025-01-15", "confidence": 0.9, "raw_excerpt": "Employer sponsorship required. HSP visa offers fast-track to permanent residency.", "source_type": "primary_stat"},
        ],
        "caveats": ["All work visas require employer sponsorship. HSP points system offers accelerated PR. Language barrier for non-Japanese speakers."],
    },
    "South Korea": {
        "henley_access": "visa_free",
        "processing_months": 3,
        "sponsorship_required": "required",
        "pathway_count": 4,  # E-7 Professional, D-8 Investor, F-2 Points-based, H-1 Working Holiday
        "pathways": ["E-7 Special Occupation Visa", "D-8 Corporate Investment Visa", "F-2 Residence (points-based)", "H-1 Working Holiday Visa"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to South Korea for 90 days.", "source_type": "index"},
            {"url": "https://overseas.mofa.go.kr/us-en/brd/m_4503/view.do?seq=760930", "title": "Visa Information - Korean Embassy", "as_of": "2025-01-15", "confidence": 0.9, "raw_excerpt": "E-7 visa requires employer sponsorship and qualification verification.", "source_type": "primary_stat"},
        ],
        "caveats": ["Most work visas require sponsorship. F-2 points-based system rewards Korean language ability."],
    },
    "Mexico": {
        "henley_access": "visa_free",
        "processing_months": 2,
        "sponsorship_required": "sometimes",
        "pathway_count": 3,  # Temporary Resident (work), Permanent Resident, Digital Nomad (informal)
        "pathways": ["Temporary Resident Visa (work offer)", "Permanent Resident Visa", "Residente Temporal (remote work/freelance)"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Mexico for 180 days.", "source_type": "index"},
            {"url": "https://embamex.sre.gob.mx/eua/index.php/en/visas", "title": "Visa Information - Mexican Embassy", "as_of": "2025-01-15", "confidence": 0.9, "raw_excerpt": "Temporary Resident Visa allows work with a job offer. Freelancers can work on Temporary Resident status.", "source_type": "primary_stat"},
        ],
        "caveats": ["No formal digital nomad visa but widely tolerated. Temporary Resident allows freelance work."],
    },
    "Costa Rica": {
        "henley_access": "visa_free",
        "processing_months": 3,
        "sponsorship_required": "sometimes",
        "pathway_count": 3,  # Digital Nomad, Temporary Resident Worker, Investor/Rentista
        "pathways": ["Digital Nomad Visa", "Temporary Resident Worker Visa", "Rentista/Investor Visa"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Costa Rica for 90 days.", "source_type": "index"},
            {"url": "https://www.migracion.go.cr/", "title": "Immigration - Costa Rica", "as_of": "2025-01-15", "confidence": 0.85, "raw_excerpt": "Digital Nomad Visa launched 2021 for remote workers earning $3,000+/month. Valid for 1 year, renewable.", "source_type": "primary_stat"},
        ],
        "caveats": ["Digital Nomad Visa requires proof of $3,000/month remote income. Local job market is small."],
    },
    "Taiwan": {
        "henley_access": "visa_free",
        "processing_months": 3,
        "sponsorship_required": "required",
        "pathway_count": 4,  # Employment Gold Card, Regular Work Permit, Entrepreneur Visa, Job Seeking Visa
        "pathways": ["Employment Gold Card", "Regular Work Permit", "Entrepreneur Visa", "Job Seeking Visa"],
        "evidence": [
            {"url": "https://www.henleyglobal.com/passport-index", "title": "Henley Passport Index 2025", "as_of": "2025-01-01", "confidence": 0.9, "raw_excerpt": "US passport holders have visa-free access to Taiwan for 90 days.", "source_type": "index"},
            {"url": "https://goldcard.nat.gov.tw/en/", "title": "Employment Gold Card - Taiwan", "as_of": "2025-01-15", "confidence": 0.95, "raw_excerpt": "Gold Card is an open work permit for qualified professionals in key industries. No employer sponsorship needed.", "source_type": "primary_stat"},
        ],
        "caveats": ["Employment Gold Card does not require sponsorship but is selective. Regular work permit needs employer."],
    },
}


def _normalize_score(
    henley_access: str | None,
    processing_months: float | None,
    sponsorship_required: str | None,
    pathway_count: int | None,
) -> tuple[float, float]:
    """Returns (score_0_100, confidence_proxy)."""
    score = 0.0
    weight_used = 0.0

    # Henley visa-free access level (20%)
    if henley_access is not None:
        access_map = {
            "visa_free": 100.0,
            "eta_evisa": 80.0,
            "visa_on_arrival": 60.0,
            "visa_required": 30.0,
        }
        score += access_map.get(henley_access, 50.0) * 0.20
        weight_used += 0.20

    # Processing time in months (25%) — 3 months = 100, 24 months = 0
    if processing_months is not None:
        proc_score = max(0.0, min(100.0, (24.0 - processing_months) / 21.0 * 100.0))
        score += proc_score * 0.25
        weight_used += 0.25

    # Sponsorship requirement (25%)
    if sponsorship_required is not None:
        sponsor_map = {
            "not_required": 100.0,
            "sometimes": 60.0,
            "required": 20.0,
        }
        score += sponsor_map.get(sponsorship_required, 50.0) * 0.25
        weight_used += 0.25

    # Number of pathways (30%) — 4+ pathways = 100
    if pathway_count is not None:
        path_score = min(100.0, pathway_count / 4.0 * 100.0)
        score += path_score * 0.30
        weight_used += 0.30

    if weight_used == 0:
        return 0.0, 0.0

    normalized = score / weight_used
    return round(normalized, 1), round(weight_used, 2)


class VisaAgent(BaseAgent):
    agent_name = "visa"

    def run(self, country: str, profile: str) -> AgentOutput:
        data = VISA_DATA.get(country)

        if data is None:
            return AgentOutput(
                agent_name=self.agent_name,
                country=country,
                profile=profile,
                domain_score=0.0,
                confidence=0.0,
                evidence=[],
                caveats=[f"No visa data available for {country}."],
                raw_data={},
                fetched_at=self._now_iso(),
            )

        # Extract raw values
        henley_access = data["henley_access"]
        processing_months = data["processing_months"]
        sponsorship_required = data["sponsorship_required"]
        pathway_count = data["pathway_count"]

        # Calculate score
        domain_score, confidence = _normalize_score(
            henley_access, processing_months, sponsorship_required, pathway_count,
        )

        # Build evidence
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
            "henley_access": henley_access,
            "processing_months": processing_months,
            "sponsorship_required": sponsorship_required,
            "pathway_count": pathway_count,
            "pathways": data["pathways"],
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
