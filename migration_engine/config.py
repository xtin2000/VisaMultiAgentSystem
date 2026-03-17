"""
Project-wide constants: countries, profiles, weights, agent registry.
"""

COUNTRIES: list[str] = [
    "Canada",
    "UK",
    "Ireland",
    "Netherlands",
    "Germany",
    "Portugal",
    "Spain",
    "Australia",
    "New Zealand",
    "Singapore",
    "Japan",
    "South Korea",
    "Mexico",
    "Costa Rica",
    "Taiwan",
]

PROFILES: list[str] = [
    "software_engineer",
    "general_professional",
    "student_to_work",
]

PROFILE_DISPLAY: dict[str, str] = {
    "software engineer": "software_engineer",
    "general professional": "general_professional",
    "student-to-work pathway": "student_to_work",
    "student to work": "student_to_work",
}

DEFAULT_WEIGHTS: dict[str, float] = {
    "visa": 0.30,
    "job_market": 0.25,
    "affordability": 0.25,
    "english": 0.20,
}

# Agent registry: maps agent_name → fully-qualified class path
AGENT_REGISTRY: dict[str, str] = {
    "visa": "agents.visa_agent.VisaAgent",
    "job_market": "agents.job_market_agent.JobMarketAgent",
    "affordability": "agents.affordability_agent.AffordabilityAgent",
    "english": "agents.english_agent.EnglishAgent",
}

MODEL = "claude-sonnet-4-6"
CACHE_TTL_HOURS = 168   # 7 days
STALE_MONTHS = 18       # Data older than this gets a confidence penalty
