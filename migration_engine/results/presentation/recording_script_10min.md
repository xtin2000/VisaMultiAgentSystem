# 10-Minute Recorded Demo Script
*(Pure demo time — slides not included. Add ~30s intro + ~30s outro slides for total ≈11 min.)*

---

## TIMING SUMMARY

| Segment | Time | Content |
|---|---|---|
| **A. CLI engine** | 0:00 – 3:30 (3:30) | 4 runs: full ranking, ablation, profile, JSON |
| **B. Chatbot** | 3:30 – 8:00 (4:30) | 6 questions through the browser UI |
| **C. Evaluation** | 8:00 – 9:45 (1:45) | Coverage, consistency, ablation walkthrough |
| **D. Quick close** | 9:45 – 10:00 (0:15) | "Code on GitHub, thanks" |

---

## PART A — CLI ENGINE (3:30)

### A.1  Project layout (0:00 – 0:20) — *20 sec*

Open terminal at the repo root with a fresh prompt.

**Run:**
```bash
cd /Users/xtin2000/git/multi_agent_system
ls migration_engine/
```

**Say while it runs:**
> *"Quick orientation. Four agents — one per domain — share a single schema. The orchestrator merges their outputs, the ranker turns those into a final ordering, and we have an evaluation suite for coverage and ablation. About twenty-five hundred lines of Python, all on GitHub."*

---

### A.2  Headline ranking (0:20 – 1:15) — *55 sec*

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" \
    --countries "Portugal,Germany,Japan,Mexico,Spain"
```

**Say while the table renders:**
> *"Five countries, software-engineer profile. Each row is computed by four independent agents — visa, job market, affordability, English. You can see the score breakdown explicitly. The 'Why' column is **not** an LLM — it's a deterministic templated explainer. Same input, same explanation, every time, which matters for trust in a decision-support tool."*

> *"Portugal at 80.5 just edges Germany at 80.3. Japan's job market is the strongest in this table at 89 out of 100, but its English score of 40 drags its overall down to third. Mexico's 93 on affordability is the highest single-domain score in the table — but everything else is weak."*

---

### A.3  Ablation — drop the English agent (1:15 – 2:00) — *45 sec*

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" \
    --disable-agent english
```

**Say while it runs:**
> *"Now I drop the English agent entirely. Watch what happens to Japan."*

*(Wait for output to settle, then point at Japan.)*

> *"Japan jumps from rank seven all the way to **number one**. That's the multi-agent property — when one piece of evidence is removed, the ranking responds in an interpretable way. Japan was always strong on jobs and visa; the English score was just dominating its overall."*

> *"Notice the Missing column for every row would say 'english' if any country had partial data. Here, since we dropped the entire agent, the ranker renormalizes the remaining weights so scores still span zero to a hundred."*

---

### A.4  Profile comparison — honest moment (2:00 – 2:45) — *45 sec*

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "general professional" \
    --countries "Portugal,Germany,Japan"
```

**Say:**
> *"One honest disclosure. The system supports three profiles — software engineer, general professional, and student-to-work. Today, only the job-market agent actually uses the profile field — it adds a tech-vacancy signal for software engineers. The other three agents currently ignore profile."*

> *"So a 'general professional' query mostly produces the same scores. Profile-aware scoring across all four agents is on our remaining-work list. We surface this honestly because it matters for what the system does — and doesn't — claim."*

---

### A.5  Structured JSON output (2:45 – 3:30) — *45 sec*

**Run:**
```bash
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" \
    --countries "Portugal" \
    --output json | head -60
```

**Say:**
> *"The same engine emits structured JSON for programmatic consumption. You can see the per-agent breakdown, the source-priority resolved evidence with as-of dates and confidence values, and the explanation bullets. This is what the chat front-end I'm about to show consumes through the Model Context Protocol."*

---

## PART B — CHATBOT (4:30)

### B.1  Switch to browser, brief intro (3:30 – 4:00) — *30 sec*

Switch to the browser tab at http://localhost:8000. Make sure `visa_ranker` is selected.

**Say:**
> *"On top of the deterministic engine, we built a chat front-end using Google's Agent Development Kit. The chatbot is a Gemini 2.0 Flash agent that connects to our engine through MCP — the Model Context Protocol. The LLM provides the conversational layer; the actual scoring is still our reproducible system underneath. Every answer you'll see is grounded in a tool call you can inspect in the trace panel."*

---

### B.2  Q1 — opener: simple two-country compare (4:00 – 4:45) — *45 sec*

**Type into chat:**
> *I'm a software engineer thinking about Portugal or Germany. Which is better for me?*

**Say while it processes:**
> *"Watch the trace — Gemini called our `rank_countries` tool with profile equals software_engineer and the two countries I named. It got back the structured ranking and is now phrasing it for me in natural language. The numbers — Portugal 80.5, Germany 80.3 — come from our engine, not from Gemini's training data."*

---

### B.3  Q2 — geographic filter (4:45 – 5:30) — *45 sec*

**Type into chat:**
> *Rank my best options in Europe*

**Say:**
> *"Notice Gemini decided which of our sixteen countries qualify as European — that's the LLM's interpretive layer. Our engine just ranks. Gemini handled the country filtering itself, called the tool with that subset, and is now presenting the result. The two pieces — interpretation and scoring — are decoupled."*

---

### B.4  Q3 — constraint-driven reasoning (5:30 – 6:15) — *45 sec*

**Type into chat:**
> *What if I don't speak any local languages? How does that change my best options?*

**Say:**
> *"This is interesting. The engine doesn't know how to re-weight scores by user constraint. But Gemini reads our English column as a near-binary filter — high-English countries surface, low-English ones drop. Japan and Mexico fall; Portugal, Netherlands, Singapore stay strong. The LLM is reasoning **over** our structured output."*

---

### B.5  Q4 — multi-criteria synthesis (6:15 – 6:45) — *30 sec*

**Type into chat:**
> *Where can I get the best balance of affordability and English-speaking work culture?*

**Say:**
> *"Now Gemini has to read two columns simultaneously. Portugal usually wins this one — English score of 100, affordability score of 73. That's the sweet spot the engine identified."*

---

### B.6  Q5 — honest-limit (6:45 – 7:15) — *30 sec*

**Type into chat:**
> *What about Norway?*

**Say:**
> *"We restricted to sixteen candidate countries from the project brief. Norway isn't one of them. The tool returns 'unknown country' with the supported list. Gemini relays this honestly — it does **not** make up data for Norway. That's an important property for a decision-support system. The architecture refuses to pretend."*

---

### B.7  Q6 — drill-down on evidence (7:15 – 8:00) — *45 sec*

**Type into chat:**
> *Why did Portugal rank so high? Show me the actual sources.*

**Say:**
> *"Every score has a source URL, an 'as of' date, and a confidence level. Gemini is now reading the evidence excerpts from our engine and listing them with links. France-Visas dot gouv dot fr, OECD, Numbeo, EF EPI 2024. You could click any of these and verify the underlying data point. Real sources, not hallucination — the brief specifically asked for traceability and this is how we deliver it."*

---

## PART C — EVALUATION REPORT (1:45)

Switch to terminal or open `migration_engine/evaluation/results.md` in the editor — whichever shows the markdown more clearly on screen.

### C.1  Coverage (8:00 – 8:30) — *30 sec*

**Run or scroll to:**
```bash
cat migration_engine/evaluation/results.md
```

**Say while pointing at the coverage table:**
> *"Three Phase-4 deliverables, all automated. First, **coverage** — every checkmark in this table is a complete, validated agent output for that country. Sixteen out of sixteen, one hundred percent. The brief specifically asked for this metric."*

### C.2  Consistency (8:30 – 9:00) — *30 sec*

**Point at the consistency table:**
> *"Second, **consistency**. We ran the entire ranking twice with the cache disabled and recorded every score. Every delta is zero point zero zero. That's expected because our datasets are static and versioned — but it sets the baseline. When we wire in live data later, this is the metric that catches drift."*

### C.3  Ablation matrix walkthrough (9:00 – 9:45) — *45 sec*

**Point at the ablation matrix and call out specific cells:**
> *"And third, the **ablation matrix**. Every cell is a story."*

> *"Look at Spain — rank sixteen baseline, but jumps to rank six when we drop the job-market agent. That tells you Spain's weakness in our ranking is specifically the twelve percent unemployment, not anything else."*

> *"Costa Rica jumps from rank fourteen to rank four when job-market is dropped, for the same reason."*

> *"Japan jumps from seven to one when English is dropped — the same insight you saw earlier in the CLI demo, now quantified across all sixteen countries simultaneously."*

> *"And Portugal — the country at rank one — falls all the way to rank eight when affordability is dropped. Its top spot is propped up by affordability; it's not as broadly strong as Germany or the Netherlands."*

> *"Every cell here is a defensible, citable claim."*

---

## PART D — QUICK CLOSE (0:15)

**Say (no command needed):**
> *"To recap: four autonomous agents, one shared schema, deterministic conflict resolution, evidence-grounded explanations, and a chat front-end on top. Code on GitHub at xtin2000 slash VisaMultiAgentSystem. Thanks for watching."*

---

## RECORDING NOTES

### Practical setup

| Tool | Setting |
|---|---|
| Screen recorder | macOS `Cmd-Shift-5` → "Record Selected Portion" — capture only your terminal + browser, not the menu bar |
| Audio | Wired mic or AirPods. Test 30 seconds and play it back before doing the real take. |
| Cursor | macOS Settings → Accessibility → Display → cursor size to "Large" |
| Resolution | 1920×1080 is plenty; bigger = bigger files |
| Editor | iMovie or QuickTime trim — no transitions needed |

### How to handle takes

- **Record in 4 segments**, not one long take. Each segment break is a natural cut point. If you fumble Part B, you only re-record Part B.
- **Don't worry about long Gemini latency** — trim it in post. Aim for at most ~2 second pauses in the final cut.
- **Read the script aloud once before recording** so the words feel natural, not stiff.
- **Record at the time of day Gemini is least loaded** — early morning Pacific is quieter than peak working hours.

### Plan B if Gemini 503s during the recording window

- **If `gemini-2.5-flash` keeps failing:** edit [agent.py](/Users/xtin2000/git/multi_agent_system/SemesterProject_VisaRanker/visa_ranker/agent.py) to use `gemini-2.0-flash` (more available). Restart `adk web`.
- **If Gemini is broken entirely:** record Parts A, C, D — that's a 6-minute substantive demo by itself. Skip Part B and add a sentence to the close: *"In the chat front-end we built using Google's ADK, you can ask the same questions in natural language — repo includes setup instructions."*
- **Alternative pad** if you need to fill the time without the chatbot: run the CLI on more profiles and country subsets, walk through `agents/visa_agent.py` showing the static-dataset structure live, or open `schema/models.py` and explain the shared `AgentOutput` contract.

### Pre-recording checklist

```bash
cd /Users/xtin2000/git/multi_agent_system

# 1. Repo is clean and current
git status                  # should be clean
git pull                    # if collaborating

# 2. Engine works
uv run pytest -q            # 66 passed
GOOGLE_API_KEY=demo uv run python migration_engine/main.py \
    --profile "software engineer" --countries "Portugal,Germany"

# 3. Evaluation is fresh
uv run python migration_engine/evaluation/run_evaluation.py

# 4. Chatbot works
cd SemesterProject_VisaRanker
export GOOGLE_API_KEY="<real key>"
/Users/xtin2000/git/multi_agent_system/.venv/bin/adk web &
# open browser, send ONE test message to confirm chat works
# Ctrl-C the server, restart fresh for the recording

# 5. Silence laptop
# - Do Not Disturb on
# - Close all other apps that might notify
# - Plug in charger; you don't want a low-battery beep mid-recording
```
