# In-Class Demo Script (~3 minutes, 3 commands)

Total runtime: ~3 minutes if you talk while it runs.
Each command is **safe to re-run** if something glitches — they're all deterministic, no API key needed.

---

## Pre-demo terminal setup

Open a terminal, make it big and readable (`Cmd-+` to bump font size), and `cd` to the repo:

```bash
cd /Users/xtin2000/git/multi_agent_system
clear
```

Have a second tab ready for the optional chatbot stretch goal.

---

## Step 1 — Show the headline ranking (~1 min)

**Run:**
```bash
uv run python migration_engine/main.py --profile "software engineer" --countries "Portugal,Germany,Japan,Mexico,Spain"
```

**What to say while the table renders:**

> "We're ranking five countries for a software engineer. Each row is computed by four independent agents. You can see the score breakdown: visa pathways, job-market access, affordability, and English. The 'Why' column is **not** an LLM — it's deterministic templated output, so the explanation is reproducible across every run, which we think matters for trust in a decision-support tool."

**What the audience sees:**
- Portugal #1 (80.5) — propped up by English + affordability
- Germany #2 (80.3) — strong everywhere except affordability
- Japan #3 (70.1) — best job market in the set, but English drags it down
- Mexico — extreme affordability, weak everywhere else
- Spain — held back by 12% unemployment

---

## Step 2 — Show the ablation (~45 sec)

**Run:**
```bash
uv run python migration_engine/main.py --profile "software engineer" --disable-agent english
```

**What to say:**

> "Now I'm dropping the English agent entirely. Watch what happens to **Japan** — it had no data missing before; now without English it jumps to **#1**. That's the multi-agent property in action: when one source of evidence is removed, the ranking responds in a way that's interpretable, not opaque."

**Point to:**
- Japan moves from #7 → **#1**
- Spain moves up from #15 → much higher (because we're no longer penalising its English score)
- Portugal still top-2, because its strength is broad — not single-agent-dependent

---

## Step 3 — Show the evaluation report (~45 sec)

**Run:**
```bash
uv run python migration_engine/evaluation/run_evaluation.py
cat migration_engine/evaluation/results.md | less
```

(Or just open the file in your editor on the projector — that's actually nicer for this part.)

**What to say:**

> "We automated three things the brief asked for. **Coverage**: 15 out of 15 countries have data from all four agents. **Consistency**: two reruns produce byte-identical scores — a useful baseline before we wire in any live data. And **ablation**: this matrix shows exactly how every country's rank shifts when each agent is removed. Spain leaping from last to mid-pack when we drop job-market is a great example — it tells you Spain's weakness in our ranking is **specifically** the high unemployment, not anything else."

---

## Step 4 (OPTIONAL stretch — only if your Gemini key works) — Browser chatbot (~1 min)

**Run:**
```bash
cd /Users/xtin2000/git/multi_agent_system/SemesterProject_VisaRanker
export GOOGLE_API_KEY="<your-real-key>"
/Users/xtin2000/git/multi_agent_system/.venv/bin/adk web
```

Then open **http://localhost:8000** in your browser and type:

> *I'm a software engineer thinking about Portugal or Germany. Which is better?*

**What to say:**

> "On top of the deterministic engine we built a Google ADK chat front-end that talks to the engine via the Model Context Protocol. The LLM here is just the conversational layer — the actual scoring is still our deterministic system, so the user gets natural language with reproducible answers underneath."

**Skip this step entirely if** the API key fails or the demo gods are unkind. The CLI demo is the graded substance; the chatbot is bonus.

---

## If something goes wrong

| Glitch | Fast fix |
|---|---|
| `command not found: uv` | Use `/Users/xtin2000/git/multi_agent_system/.venv/bin/python migration_engine/main.py ...` instead |
| `GOOGLE_API_KEY not set` | `export GOOGLE_API_KEY=demo` (any string works for the CLI) |
| Chat says "Failed to create MCP session" | Skip the chatbot demo, fall back to the CLI |
| Terminal too small / font too small | `Cmd-+` a few times before you start |
| Display projector shows nothing | Mirror displays in System Settings → Displays → "Mirror Built-in Display" |

---

## Talking points to repeat during Q&A

- *"The agents don't import each other — that's the autonomy property. They share only the schema."*
- *"Conflict resolution prefers primary statistics over crowdsourced data. So if OECD and Numbeo disagree on Germany's price level, OECD wins."*
- *"The deterministic explainer is a feature, not a workaround — same input, same explanation, every time."*
- *"100% coverage with citations was a non-trivial bar; the brief specifically asked for it."*
- *"The agentic loop scaffold is still in `BaseAgent` — wiring up a live agent is a swap-in, not a rewrite."*
