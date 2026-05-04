# Migration Engine — Evaluation Report

_Profile: software engineer | Generated: 2026-05-04T19:48:53.724964+00:00_

## 1. Coverage

| Country | visa | job_market | affordability | english | Complete |
|---|---|---|---|---|---|
| Canada | ✓ | ✓ | ✓ | ✓ | ✓ |
| UK | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ireland | ✓ | ✓ | ✓ | ✓ | ✓ |
| Netherlands | ✓ | ✓ | ✓ | ✓ | ✓ |
| Germany | ✓ | ✓ | ✓ | ✓ | ✓ |
| Portugal | ✓ | ✓ | ✓ | ✓ | ✓ |
| Spain | ✓ | ✓ | ✓ | ✓ | ✓ |
| France | ✓ | ✓ | ✓ | ✓ | ✓ |
| Australia | ✓ | ✓ | ✓ | ✓ | ✓ |
| New Zealand | ✓ | ✓ | ✓ | ✓ | ✓ |
| Singapore | ✓ | ✓ | ✓ | ✓ | ✓ |
| Japan | ✓ | ✓ | ✓ | ✓ | ✓ |
| South Korea | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mexico | ✓ | ✓ | ✓ | ✓ | ✓ |
| Costa Rica | ✓ | ✓ | ✓ | ✓ | ✓ |
| Taiwan | ✓ | ✓ | ✓ | ✓ | ✓ |

**Coverage: 16/16 countries have complete schemas across all 4 agents (100%).**

## 2. Consistency

Two independent reruns with `--no-cache` for the software-engineer profile.

| Country | Run A | Run B | Δ |
|---|---:|---:|---:|
| Canada | 67.25 | 67.25 | 0.00 |
| UK | 72.20 | 72.20 | 0.00 |
| Ireland | 68.94 | 68.94 | 0.00 |
| Netherlands | 79.78 | 79.78 | 0.00 |
| Germany | 80.29 | 80.29 | 0.00 |
| Portugal | 80.49 | 80.49 | 0.00 |
| Spain | 60.28 | 60.28 | 0.00 |
| France | 60.83 | 60.83 | 0.00 |
| Australia | 73.58 | 73.58 | 0.00 |
| New Zealand | 75.18 | 75.18 | 0.00 |
| Singapore | 68.75 | 68.75 | 0.00 |
| Japan | 70.12 | 70.12 | 0.00 |
| South Korea | 67.88 | 67.88 | 0.00 |
| Mexico | 65.30 | 65.30 | 0.00 |
| Costa Rica | 62.75 | 62.75 | 0.00 |
| Taiwan | 66.58 | 66.58 | 0.00 |

**Stable** — all deltas are 0.00 (deterministic static datasets).

## 3. Ablation

Re-run with each agent disabled in turn. ΔRank = ablation rank − baseline rank.

| Country | Baseline | −visa | −job_market | −affordability | −english |
|---|---|---|---|---|---|
| Portugal | 1 | 1 (0) | 1 (0) | 8 (+7) | 2 (+1) |
| Germany | 2 | 2 (0) | 2 (0) | 2 (0) | 3 (+1) |
| Netherlands | 3 | 3 (0) | 7 (+4) | 1 (-2) | 4 (+1) |
| New Zealand | 4 | 4 (0) | 9 (+5) | 3 (-1) | 7 (+3) |
| Australia | 5 | 5 (0) | 10 (+5) | 4 (-1) | 9 (+4) |
| UK | 6 | 6 (0) | 11 (+5) | 5 (-1) | 10 (+4) |
| Japan | 7 | 7 (0) | 16 (+9) | 10 (+3) | 1 (-6) |
| Ireland | 8 | 8 (0) | 14 (+6) | 6 (-2) | 12 (+4) |
| Singapore | 9 | 9 (0) | 12 (+3) | 7 (-2) | 14 (+5) |
| South Korea | 10 | 10 (0) | 13 (+3) | 11 (+1) | 6 (-4) |
| Canada | 11 | 12 (+1) | 3 (-8) | 9 (-2) | 16 (+5) |
| Taiwan | 12 | 11 (-1) | 8 (-4) | 13 (+1) | 8 (-4) |
| Mexico | 13 | 13 (0) | 5 (-8) | 16 (+3) | 5 (-8) |
| Costa Rica | 14 | 14 (0) | 4 (-10) | 14 (0) | 11 (-3) |
| France | 15 | 16 (+1) | 15 (0) | 12 (-3) | 13 (-2) |
| Spain | 16 | 15 (-1) | 6 (-10) | 15 (-1) | 15 (-1) |

Cells show *new rank (ΔRank)*. A large ΔRank indicates the country was leaning heavily on the dropped domain.