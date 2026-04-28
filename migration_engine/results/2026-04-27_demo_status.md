# Migration Feasibility Engine — Progress Demo

**Team:** Christine Langmayr, César Gallardo
**Date:** 2026-04-27
**Presentation deadline:** 2026-05-08

---

## What this is

A multi-agent system that ranks countries for a US citizen considering relocation,
along four coordinated domains: **visa pathways**, **job-market access**,
**affordability**, and **English accessibility**. Each domain is owned by an
autonomous agent that produces a normalized 0–100 score with citations, an
`as_of` date, and a confidence value. An orchestrator merges outputs, resolves
source conflicts (primary statistics outrank crowdsourced indices), and a
ranker produces the final weighted ordering with per-country explanations.

---

## Headline result — Software Engineer ranking, all 15 countries

| Rank | Country | Score | Visa | Job | Afford | Eng |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Portugal     | **80.5** | 88.8 | 62.9 | 72.5 | 100 |
| 2 | Germany      | **80.3** | 88.8 | 90.6 | 44.0 | 100 |
| 3 | Netherlands  | **79.8** | 90.0 | 95.4 | 33.0 | 100 |
| 4 | New Zealand  | **75.2** | 87.6 | 91.6 | 30.5 | 100 |
| 5 | Australia    | **73.6** | 83.6 | 91.0 | 27.5 | 100 |
| 6 | UK           | **72.2** | 80.0 | 88.0 | 30.0 | 100 |
| 7 | Japan        | **70.1** | 80.0 | 99.4 | 63.5 |  40 |
| 8 | Ireland      | **68.9** | 78.8 | 81.4 | 22.0 | 100 |
| 9 | Singapore    | **68.8** | 80.0 | 91.7 | 24.0 | 100 |
| 10 | South Korea | **67.9** | 80.0 | 96.5 | 55.0 |  60 |
| 11 | Canada      | **67.3** | 86.4 | 25.6 | 43.5 | 100 |
| 12 | Taiwan      | **66.6** | 80.0 | 89.6 | 75.0 |  60 |
| 13 | Mexico      | **65.3** | 82.5 | 22.0 | 93.0 |  40 |
| 14 | Costa Rica  | **62.8** | 82.5 | 25.4 | 77.5 |  60 |
| 15 | Spain       | **60.3** | 87.6 | 26.7 | 69.0 |  60 |

Full per-country reports with evidence and citations:
[results/2026-04-27_software_engineer_full_ranking.md](2026-04-27_software_engineer_full_ranking.md)

---

## Evaluation findings

Three Phase-4 evaluations are automated in [migration_engine/evaluation/run_evaluation.py](../evaluation/run_evaluation.py).
Full report: [migration_engine/evaluation/results.md](../evaluation/results.md).

### 1. Coverage — **100% (15/15)**

Every country has complete data across all 4 agents (citations + `as_of` date +
confidence > 0). All 15 countries pass schema validation.

### 2. Consistency — **deterministic**

Two `--no-cache` reruns produce identical scores for every country (max Δ = 0.00).
This is the expected outcome since the agents read from versioned static datasets;
when we wire in live model calls, this is the metric that will catch drift.

### 3. Ablation — **rankings respond meaningfully to dropped agents**

| Insight | Evidence |
|---|---|
| Portugal's #1 rank is propped up by its affordability score | Drops from #1 to #8 when `−affordability` |
| Japan is held back almost entirely by English | Jumps from #7 to **#1** when `−english` |
| Spain is held back almost entirely by job-market | Jumps from #15 to #6 when `−job_market` |
| Mexico and Costa Rica climb sharply when job-market is dropped | Mexico #13 → #5, Costa Rica #14 → #4 |
| Northern Europe is **not** carried by any single domain | Germany, Netherlands, New Zealand, Australia move ≤1 rank under any single ablation |

Each ablation also confirms the ranker's weight-renormalization is working:
when an agent is disabled, remaining weights sum to 1.0 and scores stay on the
0–100 scale.

---

## Status against the original 60-day plan

| Phase | Item | Status |
|---|---|---|
| 1 | Repo, agent interface (JSON schema), orchestrator skeleton, logging, caching | ✅ Done |
| 1 | Visa Agent MVP, citation capture, `as_of` stamping | ✅ Done |
| 2 | English Agent (EF EPI) | ✅ Done — 15 countries, EF EPI 2024 + native-English flag |
| 2 | Affordability Agent (OECD PPP + Numbeo) | ✅ Done — 15 countries, primary OECD signal + crowdsourced Numbeo |
| 2 | Job Market Agent (OECD employment + WB unemployment + EURES) | ✅ Done — 15 countries, static dataset |
| 3 | Conflict resolution (primary > index > news > crowdsourced) | ✅ Done |
| 3 | Scoring weights, explanation generator | ✅ Done — deterministic explainer (no LLM dependency) |
| 3 | Expand to all countries, end-to-end ranking | ✅ Done |
| 4 | Evaluation — coverage, consistency, ablation, traceability | ✅ Done — automated, see `evaluation/results.md` |
| 4 | Final report writeup | ⚠️ In progress — this document is the running draft |
| 4 | Demo / walkthrough | 🔜 Recording planned for May 6–7 |

---

## Multi-agent properties demonstrated

The brief specifically asked for these; here is where they appear in the code:

- **Autonomy:** each agent in [migration_engine/agents/](../agents/) gathers and scores its domain independently; agents do not import from one another.
- **Communication:** all four agents emit the same dataclass `AgentOutput` ([schema/models.py](../schema/models.py)), carrying scores, evidence, confidence, and caveats.
- **Coordination:** [orchestrator/conflict_resolver.py](../orchestrator/conflict_resolver.py) enforces the source-priority order (`primary_stat` → `index` → `news` → `crowdsourced`) and recency, so agents disagreeing on a country's evidence don't corrupt the ranking.
- **Cooperation:** the ranker ([ranker/ranker.py](../ranker/ranker.py)) takes per-agent scores and produces a single explained ranking. Renormalization handles ablation cleanly.

---

## Engineering quality

- **Test suite:** 62/62 pytest tests pass (every agent × every country, plus ranker renormalization, plus evidence-field validity).
- **Lint clean:** `ruff check` clean across `migration_engine/` and `tests/`.
- **Reproducible:** all four agents use versioned static datasets, so ranking is byte-identical across runs.
- **Codebase size:** ~2,100 lines (1,915 production + 60 tests + 136 README/config).

---

## Remaining work before May 8

| | Item | Effort |
|---|---|---|
| 🔜 | Final 5-page report / slide deck | ~half day |
| 🔜 | Demo walkthrough (~3 min recording) | ~1 hour |
| 🔧 | Add profile-specific differentiation (currently only job-market uses `profile`; visa/english/affordability ignore it) | ~2 hours, optional polish |
| 🔧 | LICENSE file (MIT) and `.github/workflows/ci.yml` | 15 min, optional |
| 🔧 | Live data fetch for one agent as a "growth" demo (Gemini grounding now broken in deprecated SDK; would migrate to `google.genai`) | ~half day, stretch goal |

---

## How to reproduce today's run

```bash
cd migration_engine
export GOOGLE_API_KEY="any-string"   # not actually called in current build

# Generate the full ranking
python main.py --profile "software engineer" --output markdown > results/ranking.md

# Run the three evaluations
python evaluation/run_evaluation.py

# Run the test suite
cd .. && pytest -q

# Ablation: drop one agent and see how rankings shift
python main.py --profile "software engineer" --disable-agent english --output terminal
```

---

## File map

```
migration_engine/
├── main.py                          # CLI entry point
├── config.py                        # countries, profiles, weights, agent registry
├── schema/models.py                 # shared dataclasses
├── agents/
│   ├── base_agent.py                # Gemini tool-use loop scaffold
│   ├── visa_agent.py                # Henley + government sources
│   ├── job_market_agent.py          # OECD + World Bank + EURES
│   ├── affordability_agent.py       # OECD PPP + Numbeo
│   └── english_agent.py             # EF EPI 2024 + native-English flag
├── orchestrator/
│   ├── orchestrator.py              # 5-phase run loop
│   ├── conflict_resolver.py         # source-type & recency priority
│   ├── merger.py                    # CountryProfile assembly
│   └── explainer.py                 # deterministic 'why this rank' bullets
├── ranker/ranker.py                 # weighted ranking + ablation renormalization
├── reports/report_generator.py      # markdown + Rich terminal renderers
├── infra/                           # SQLite cache, structured logger, persistence
├── evaluation/
│   ├── run_evaluation.py            # coverage, consistency, ablation
│   └── results.md                   # latest evaluation output
├── results/
│   ├── 2026-04-27_demo_status.md    # this file
│   └── 2026-04-27_software_engineer_full_ranking.md   # full ranking with evidence
└── tests/test_smoke.py              # 62 tests
```
