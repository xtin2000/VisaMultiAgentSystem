#!/usr/bin/env bash
# In-class demo runner — press Enter to advance through each step.
# Run from the repo root: bash migration_engine/results/presentation/demo_run.sh

set -e

# Resolve repo root (script is 3 levels deep)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

PYTHON="$REPO_ROOT/.venv/bin/python"
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-demo-not-actually-called}"

# ANSI styling
BOLD=$'\033[1m'
DIM=$'\033[2m'
CYAN=$'\033[36m'
YELLOW=$'\033[33m'
GREEN=$'\033[32m'
RESET=$'\033[0m'

banner() {
    clear
    echo
    echo "${CYAN}${BOLD}=================================================================${RESET}"
    echo "${CYAN}${BOLD}  $1${RESET}"
    echo "${CYAN}${BOLD}=================================================================${RESET}"
    echo
}

pause() {
    echo
    echo "${DIM}--- press Enter to ${YELLOW}$1${DIM} ---${RESET}"
    read -r
}

# ─────────────────────────────────────────────────────────────────────
# Title screen
# ─────────────────────────────────────────────────────────────────────
banner "Migration Feasibility & Risk Engine — Live Demo"
cat <<EOF
  Team:    Christine Langmayr & César Gallardo
  Project: Multi-Agent AI — 4 autonomous domain agents
           ranking 15 countries for US migration

  Three demo steps:
    1. Headline ranking (5 countries, software engineer)
    2. Ablation — drop English, watch Japan rise
    3. Evaluation report — coverage, consistency, ablation matrix
EOF
pause "begin step 1"

# ─────────────────────────────────────────────────────────────────────
# STEP 1
# ─────────────────────────────────────────────────────────────────────
banner "STEP 1  ·  Software-engineer ranking, 5 countries"
echo "${GREEN}\$ python main.py --profile \"software engineer\" --countries \"Portugal,Germany,Japan,Mexico,Spain\"${RESET}"
echo
"$PYTHON" migration_engine/main.py --profile "software engineer" \
    --countries "Portugal,Germany,Japan,Mexico,Spain" 2>/dev/null

cat <<EOF

  ${BOLD}Talking points:${RESET}
  • Portugal (80.5) and Germany (80.3) are basically tied
  • Each row was scored by FOUR independent agents — see the breakdown
  • The "Why" column is deterministic templated text — same input, same explanation
EOF
pause "begin step 2 (ablation)"

# ─────────────────────────────────────────────────────────────────────
# STEP 2
# ─────────────────────────────────────────────────────────────────────
banner "STEP 2  ·  Ablation — drop the English agent"
echo "${GREEN}\$ python main.py --profile \"software engineer\" --disable-agent english${RESET}"
echo "${DIM}(showing top 8 only)${RESET}"
echo
"$PYTHON" migration_engine/main.py --profile "software engineer" \
    --disable-agent english 2>/dev/null | head -90

cat <<EOF

  ${BOLD}Talking points:${RESET}
  • Japan jumps from #7 to ${YELLOW}#1${RESET} — its strong job market and visa were
    being masked by the English score
  • Portugal stays #2 — its rank is broad-based, not single-agent-dependent
  • The "Missing" column would now show \"english\" if any rows had partial data
EOF
pause "begin step 3 (evaluation report)"

# ─────────────────────────────────────────────────────────────────────
# STEP 3
# ─────────────────────────────────────────────────────────────────────
banner "STEP 3  ·  Phase-4 evaluation — coverage, consistency, ablation"
echo "${GREEN}\$ cat migration_engine/evaluation/results.md${RESET}"
echo
cat migration_engine/evaluation/results.md

cat <<EOF

  ${BOLD}Talking points:${RESET}
  • ${BOLD}Coverage: 15/15${RESET} — every country has data from every agent
  • ${BOLD}Consistency: max Δ = 0.00${RESET} — deterministic and reproducible
  • ${BOLD}Ablation matrix${RESET}: every cell is a story
      Costa Rica  #14 → #4  when job-market dropped
      Spain       #15 → #6  when job-market dropped
      Japan       #7  → #1  when English dropped
      Portugal    #1  → #8  when affordability dropped
EOF

echo
echo "${CYAN}${BOLD}=================================================================${RESET}"
echo "${CYAN}${BOLD}  Demo complete — questions?${RESET}"
echo "${CYAN}${BOLD}=================================================================${RESET}"
echo
