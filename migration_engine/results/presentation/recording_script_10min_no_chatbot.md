# 10-Minute Recorded Demo — CLI-Only Version
*(For the case where Gemini quota is unavailable. Substitutes a code architecture
walkthrough for the chatbot segment — arguably stronger evidence of multi-agent
engineering for a course presentation.)*

---

## TIMING SUMMARY

| Segment | Time | Content |
|---|---|---|
| **A. Orientation** | 0:00 – 0:30 (0:30) | Repo overview |
| **B. Code architecture tour** | 0:30 – 3:00 (2:30) | Schema, agents, orchestrator, ranker — open the files |
| **C. CLI demo** | 3:00 – 6:30 (3:30) | Four runs: full ranking, ablation, profile, JSON |
| **D. Evaluation report** | 6:30 – 8:30 (2:00) | Coverage, consistency, ablation walkthrough |
| **E. Chat-layer mention** | 8:30 – 9:30 (1:00) | Show agent.py, mcp_server.py — explain without demoing |
| **F. Close** | 9:30 – 10:00 (0:30) | GitHub link, what's next |

---

## PART A — ORIENTATION (0:30)

Open terminal at `/Users/xtin2000/git/multi_agent_system/`.

**Run:**
```bash
ls migration_engine/
```

**Say:**
> *"Hi, I'm Christine. With my teammate César I built a multi-agent migration feasibility engine for US citizens considering relocation. The system has four autonomous agents — visa, job market, affordability, English — each owning its own domain with primary-source citations. An orchestrator merges them into a single ranked list with explanations. About 2,500 lines of Python on GitHub. I'll walk through the architecture, then show the engine in action."*

---

## PART B — CODE ARCHITECTURE TOUR (2:30)

### B.1  The shared schema (~30 sec)

**Open:**
```bash
cat migration_engine/schema/models.py
```

**Say:**
> *"This is the contract every agent obeys. Each agent emits an `AgentOutput` — a country score from zero to a hundred, an `Evidence` list with source URLs and as-of dates, a confidence value, and caveats. Because every agent uses this same shape, the orchestrator doesn't need to know the internal scoring of any agent. That's the **autonomy** and **communication** properties the brief asked for, in code."*

---

### B.2  An agent in detail (~45 sec)

**Open:**
```bash
sed -n '1,30p' migration_engine/agents/visa_agent.py
```

**Say:**
> *"Here's the visa agent. The class is small — under twenty lines of logic, plus the static dataset. The `_normalize_score` function turns four raw inputs — Henley access level, processing time, sponsorship requirement, pathway count — into a single zero-to-hundred score with documented weights. Every line is auditable."*

**Then scroll to one of the country entries:**
```bash
sed -n '74,86p' migration_engine/agents/visa_agent.py
```

**Say:**
> *"And here's Portugal. Five immigration pathways, two evidence citations — Henley Passport Index plus the SEF Portugal government site — each with an as-of date and a source-type label."*

---

### B.3  Conflict resolution (~45 sec)

**Open:**
```bash
cat migration_engine/orchestrator/conflict_resolver.py
```

**Say:**
> *"Here's the **coordination** layer the brief asked for. When agents disagree on what the best evidence is, this resolver applies a strict priority — primary statistics outrank indices, indices outrank news, news outranks crowdsourced. Within the winning category, the most recent as-of date wins. If OECD's price level says Germany is at 99 and Numbeo's crowdsourced index says something else, OECD wins, period. That's a deterministic rule, not a vibes-based judgment."*

---

### B.4  The ranker (~30 sec)

**Open:**
```bash
sed -n '15,55p' migration_engine/ranker/ranker.py
```

**Say:**
> *"And here's the **cooperation** layer — the ranker. Default weights are visa thirty percent, job market twenty-five, affordability twenty-five, English twenty. If any agent is disabled or returns no data, the ranker renormalizes the remaining weights so scores still span zero to a hundred. That renormalization is what makes the ablation experiments I'll show next mathematically clean."*

---

## PART C — CLI DEMO (3:30)

### C.1  Headline ranking (~55 sec)

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" \
    --countries "Portugal,Germany,Japan,Mexico,Spain"
```

**Say:**
> *"Five countries, software-engineer profile. Each row was scored independently by all four agents you just saw. The 'Why' column is **not** an LLM — it's a deterministic templated explainer. Same input, same explanation, every time. That matters for trust in a decision-support tool."*

> *"Portugal at 80.5 just edges Germany at 80.3. Japan's job market scores 89 of 100, but its English score of 40 drags the overall down to third. Mexico's 93 on affordability is the highest single-domain score in the table — but everything else is weak."*

---

### C.2  Ablation — drop the English agent (~50 sec)

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" \
    --disable-agent english
```

**Say:**
> *"Now I drop the English agent entirely across all sixteen countries. Watch Japan."*

*(Wait, point at Japan.)*

> *"Japan jumps from rank seven to **rank one**. That's the multi-agent property — when one piece of evidence is removed, the ranking responds in an interpretable way. Japan was always strong on jobs and visa; the English score was just dominating its overall."*

> *"And the 'Missing' column would mark 'english' for any partial-data rows. Here we dropped the entire agent, so the ranker renormalizes from a 100 percent weight base to an 80 percent weight base — scores stay on the same zero-to-hundred scale."*

---

### C.3  Profile comparison — honest moment (~45 sec)

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "general professional" \
    --countries "Portugal,Germany,Japan"
```

**Say:**
> *"One honest disclosure. The system supports three profiles — software engineer, general professional, and student-to-work. Today, only the job-market agent uses the profile field — it adds a tech-vacancy signal for software engineers. The other three agents currently ignore profile."*

> *"So a 'general professional' query produces nearly identical scores. Profile-aware scoring across all four agents is on our remaining-work list. We surface this honestly because it matters for what the system does — and doesn't — claim."*

---

### C.4  Structured JSON output (~60 sec)

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" \
    --countries "Portugal" \
    --output json
```

**Say:**
> *"The same engine emits structured JSON for programmatic consumption. You can see the per-agent breakdown: Portugal scored 88 on visa, 63 on job market, 72 on affordability, 100 on English. The resolved evidence is the highest-priority source per agent — France-Visas dot gouv dot fr for visa, OECD and World Bank for job market, OECD PPP for affordability, EF EPI 2024 for English. Every record has an as-of date and a confidence value."*

> *"This is the JSON our chat front-end consumes through MCP — I'll show that architecture in a moment."*

---

## PART D — EVALUATION REPORT (2:00)

### D.1  Coverage (~30 sec)

**Run:**
```bash
cat migration_engine/evaluation/results.md
```

**Say while scrolling to the coverage section:**
> *"Three Phase-4 deliverables, all automated in one Python script. First, **coverage** — every checkmark is a complete, validated agent output. Sixteen out of sixteen countries, one hundred percent. The brief specifically asked for this metric."*

### D.2  Consistency (~30 sec)

**Scroll to consistency table:**
> *"Second, **consistency**. We ran the entire ranking twice with the cache disabled. Every delta is zero point zero zero. Expected, because our datasets are static and versioned. But this is the baseline — when we wire in live data fetching later, this is the metric that catches drift."*

### D.3  Ablation matrix (~60 sec)

**Scroll to the ablation matrix:**
> *"And third, the **ablation matrix**. Every cell is a story."*

> *"Spain — rank sixteen baseline, but jumps to rank six when we drop the job-market agent. That tells you Spain's weakness in our ranking is specifically the twelve percent unemployment, not anything else."*

> *"Costa Rica — rank fourteen baseline, jumps to rank four when job-market is dropped, for the same reason."*

> *"Japan — rank seven, jumps to one when English is dropped. The same insight from the CLI demo, now quantified across all sixteen countries."*

> *"And Portugal — the country at rank one — falls all the way to rank eight when affordability is dropped. Its top spot is propped up by affordability; it's not as broadly strong as Germany or the Netherlands."*

> *"Every cell here is a defensible, citable, click-through-able claim."*

---

## PART E — THE CHAT LAYER (mention without demoing) (1:00)

### E.1  The MCP server (~30 sec)

**Open:**
```bash
cat mcp_server.py
```

**Say:**
> *"On top of the engine, we expose one tool through the Model Context Protocol — `rank_countries`. This is what an LLM agent would call. About sixty lines of code. The MCP layer means our engine isn't bound to a single chat client — anything that speaks MCP can call it."*

### E.2  The ADK agent (~30 sec)

**Open:**
```bash
sed -n '14,55p' SemesterProject_VisaRanker/visa_ranker/agent.py
```

**Say:**
> *"And here's the chat front-end — Google's Agent Development Kit. It connects to our MCP server, declares which model it uses, and gives the LLM a system prompt that explains what tools are available. We tested the full chat round-trip earlier; in this recording we're focusing on the engine itself, but the chat layer is wired and works when the API quota allows."*

---

## PART F — CLOSE (0:30)

**Say (no command needed):**
> *"To recap: four autonomous agents, one shared schema, deterministic conflict resolution, evidence-grounded explanations, and a chat front-end on top through Model Context Protocol. What's still ahead — live data fetching to replace the static datasets, profile-aware scoring across all four agents, and a CLI flag to let users adjust per-domain weights. Code is on GitHub at xtin2000 slash VisaMultiAgentSystem. Thanks for watching."*

---

## RECORDING NOTES (CLI-only version)

### Why this version is actually fine for a graded demo

- It demonstrates **all four multi-agent properties** the brief asked for (autonomy, communication, coordination, cooperation), each with a code reference, not just a slide bullet.
- The CLI demo + evaluation report **is** the deterministic core. The chatbot is a UI on top.
- For a course on Multi-Agent **AI**, showing real engineering and real evaluation rigor is more credible than a chat conversation.
- Zero external dependencies — works offline, no API key, no quota.

### Practical tips

- Use a font size readable from a phone screen — viewers may watch on mobile.
- Trim long Gemini-API delays in post (they don't exist in this version, but other latency might).
- Consider zooming in (`Cmd-+`) for the code-tour segments so syntax is legible.
- Keep your terminal width at ~120 columns so the Rich tables don't wrap.
