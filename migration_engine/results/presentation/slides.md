# Class Presentation — 3 Slides

Paste each section below into one slide (PowerPoint, Google Slides, Keynote — whichever).
Visuals are described in italics; replace with actual images / screenshots when you build the slides.

---

## SLIDE 1 — Title

# Migration Feasibility and Risk Engine

### A Multi-Agent, Evidence-Tracked Decision Support System for US Citizens Considering Relocation

**Team:** Christine Langmayr & César Gallardo
**Course:** Multi-Agent AI — Spring 2026

*(Visual idea: a small world map with the 15 candidate countries highlighted, plus the four domain icons: passport, briefcase, dollar, speech bubble.)*

---

## SLIDE 2 — Objectives, Vision, and Why It's a Multi-Agent Problem

### Objectives
- Help a US citizen produce an **explainable** shortlist of 15 candidate countries
- Score each on four coordinated domains:
  **visa pathways · job market · affordability · English accessibility**
- Every claim carries a **source URL, an `as_of` date, and a confidence value**

### Vision
- An open, auditable decision-support tool — the user can click any score and see the evidence behind it
- Not "the model says Portugal" — instead "Portugal scored 88.8 on visa pathways because of Tech Visa, D7, Digital Nomad, Job Seeker, and Golden Visa pathways (source: SEF Portugal, 2025-01-15)"

### Why this is a Multi-Agent AI problem
- **The answer is not a single fact** — it requires synthesis across four domains that update at different cadences and come from different source types (government statistics vs. crowdsourced indices)
- **Autonomy:** each agent owns its domain end-to-end (data, scoring formula, evidence, confidence)
- **Communication:** all four agents emit the *same* `AgentOutput` schema — orchestrator doesn't need to know agent internals
- **Coordination:** an orchestrator enforces a source-priority rule (primary statistics > indices > news > crowdsourced) so disagreements between agents resolve deterministically
- **Cooperation:** a ranker combines per-domain scores into a single weighted result with citations and a "why this ranked here" explanation

*(Visual idea: a 4-box agent diagram → arrows into orchestrator → arrow into ranker → ranked list output.)*

---

## SLIDE 3 — Demo Preview + What Remains

### What you'll see in the demo (~3 minutes)
1. **CLI ranking** — all 15 countries scored for a software-engineer profile, each row with score breakdown, deterministic "why this rank" bullets, and citations
2. **Ablation** — drop the English agent → **Japan jumps from #7 to #1**, showing the system responds meaningfully to which evidence is available
3. **Evaluation report** — coverage 100%, consistency Δ=0.00, full ablation matrix
4. *(Stretch)* Browser chatbot via Google ADK + MCP — natural-language question to ranked answer

### What remains to be done
- **Final written report** (in progress)
- **Profile differentiation** — currently only the job-market agent uses the profile field; visa/english/affordability could be made profile-aware (e.g. student-to-work boosts countries with strong post-study work visas)
- **Live data fetching** — replace one static agent with live OECD/government grounding via the new `google.genai` SDK. The agentic-loop scaffold is already in place; it's a swap-in
- **CI + LICENSE** for full open-source readiness

### Engineering quality (numbers for the slide)
- 4 autonomous agents · 15 countries · 60+ evidence citations
- ~2,500 lines of Python · 62/62 pytest tests passing · ruff clean
- Code on GitHub: **github.com/xtin2000/VisaMultiAgentSystem**

*(Visual idea: a screenshot of the CLI ranking table, plus a small bar chart of the ablation rank-changes — Japan +6, Spain +9, Portugal −7 when their dependency agent is dropped.)*
