# Migration Feasibility and Risk Engine

A multi-agent system that helps a US citizen identify and compare countries for relocation by producing an explainable ranked shortlist across four domains: visa pathways, job market accessibility, affordability, and English accessibility.

Each domain is owned by an autonomous agent that gathers evidence, normalizes it to a 0–100 score with citations and an `as_of` date, and reports its confidence. An orchestrator merges outputs, resolves source conflicts (primary statistics outrank crowdsourced indices), and a ranker produces the final weighted ordering with per-country explanations.

## Project Layout

```
migration_engine/
├── main.py                  # CLI entry point
├── config.py                # Countries, profiles, weights, agent registry
├── agents/                  # Domain agents (one per requirement area)
│   ├── base_agent.py
│   ├── visa_agent.py
│   ├── english_agent.py
│   ├── affordability_agent.py
│   └── job_market_agent.py
├── orchestrator/            # Run loop, conflict resolution, explanation
├── ranker/                  # Weighted ranking + ablation support
├── reports/                 # Markdown and terminal renderers
├── schema/                  # Shared dataclasses (Evidence, AgentOutput, ...)
├── infra/                   # SQLite cache, structured logger, persistence
├── data/                    # SQLite databases (auto-created)
└── logs/                    # Per-run JSON logs (auto-created)
```

## Install

Requires Python 3.12+.

```bash
uv sync
# or
pip install -e .
```

Set your Gemini API key:

```bash
export GOOGLE_API_KEY="your-key-here"
```

## Run

```bash
cd migration_engine

# Rank all 15 countries for a software engineer
python main.py --profile "software engineer"

# A subset, with markdown output
python main.py --profile "general professional" --countries "Canada,Germany,Portugal" --output markdown

# Ablation: drop the English domain and re-rank
python main.py --profile "software engineer" --disable-agent english

# Force fresh agent calls (skip cache)
python main.py --profile "software engineer" --no-cache
```

Profiles: `software engineer`, `general professional`, `student-to-work pathway`.

## Test

```bash
pytest
```

## Lint and Format

```bash
ruff check .
ruff format .
mypy migration_engine
```

## Data Sources

| Domain | Primary | Secondary |
|---|---|---|
| Visa | Government immigration sites | Henley Passport Index |
| Job market | OECD employment, World Bank / ILO unemployment | EURES vacancy signal |
| Affordability | OECD price level indices | Numbeo cost-of-living |
| English | EF English Proficiency Index 2024 | Official-language status |

Every claim carries a source URL, an `as_of` date, and a confidence score. Primary statistics outrank indices, which outrank crowdsourced data.

## Authors

Christine Langmayr and César Gallardo.
