"""Structured per-run JSON logger; writes one file per run_id under logs/."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "logs"


class Logger:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        LOGS_DIR.mkdir(exist_ok=True)
        self._path = LOGS_DIR / f"{run_id}.json"
        self._entries: list[dict] = []

    def log(self, event: str, **kwargs) -> None:
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "run_id": self.run_id,
            "event": event,
            **kwargs,
        }
        self._entries.append(entry)
        with open(self._path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def agent_run(
        self, agent: str, country: str, score: float, confidence: float, cached: bool,
    ) -> None:
        self.log("agent_run", agent=agent, country=country,
                 score=score, confidence=confidence, cached=cached)

    def error(self, agent: str, country: str, message: str) -> None:
        self.log("error", agent=agent, country=country, message=message)
