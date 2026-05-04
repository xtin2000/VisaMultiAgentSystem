# Pre-flight checklist — run during the 15-minute setup window

Class advice was "arrive 15 minutes early to test setup — there are always glitches."
Here's a 10-minute drill that catches every glitch we anticipate.

---

## ⏱ T-15 min — Hardware

- [ ] Laptop charged and plugged in
- [ ] Display dongle / HDMI / USB-C connected and confirmed working (mirror or extend mode — pick one and stick with it)
- [ ] External display shows your terminal at readable font size from the back row
- [ ] Wi-Fi connected (only needed for the chatbot stretch demo; CLI demo works offline)
- [ ] Sound off / notifications silenced (`Do Not Disturb` on macOS)

## ⏱ T-12 min — Repo state

In a terminal:

```bash
cd /Users/xtin2000/git/multi_agent_system
git status                # should say "working tree clean, up to date with origin/main"
git log --oneline -3      # should show f6bf69e (the cleanup commit) at the top
```

If `git status` is dirty, decide whether to commit or stash before the demo so you don't accidentally show in-progress edits.

## ⏱ T-10 min — Smoke tests

Run these three commands. If any fail, **stop and fix before the demo**:

```bash
# (a) Lint clean?
uv run ruff check migration_engine tests
# expected: "All checks passed!"

# (b) Tests pass?
uv run pytest -q
# expected: "62 passed"

# (c) CLI renders?
uv run python migration_engine/main.py --profile "software engineer" --countries "Portugal,Germany,Japan"
# expected: a 3-row Rich table
```

## ⏱ T-7 min — Pre-render the artifacts

In case the live demo glitches, have these open in tabs/windows as fallback:

- [ ] [migration_engine/results/2026-04-27_software_engineer_full_ranking.md](../2026-04-27_software_engineer_full_ranking.md) — full 15-country ranking
- [ ] [migration_engine/evaluation/results.md](../../evaluation/results.md) — coverage / consistency / ablation
- [ ] GitHub repo open: https://github.com/xtin2000/VisaMultiAgentSystem
- [ ] Slides in presenter mode

## ⏱ T-5 min — Optional chatbot test (only if you plan to demo it)

```bash
cd /Users/xtin2000/git/multi_agent_system/SemesterProject_VisaRanker
export GOOGLE_API_KEY="<your-real-key>"
/Users/xtin2000/git/multi_agent_system/.venv/bin/adk web
```

Open http://localhost:8000 in the browser, send **one** test message, confirm it responds.
**Then Ctrl-C the server** so the demo starts from a clean state.

If it fails to respond — **drop the chatbot demo from your plan**. Don't risk it.

## ⏱ T-2 min — Final terminal hygiene

```bash
clear
cd /Users/xtin2000/git/multi_agent_system
```

- [ ] Big readable font (Cmd-+ a few times)
- [ ] Single full-screen terminal window — no clutter
- [ ] Slides app in second space, ready to swipe to

## ⏱ T-0 — Breathe

- You've already pushed to GitHub. The code works.
- You have three deterministic CLI commands and they all run in seconds.
- The evaluation report is pre-rendered.
- If the projector cable melts, your slides have the headline numbers screenshotted. You're fine.
