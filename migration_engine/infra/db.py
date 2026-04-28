"""SQLite setup and persistence for rankings and evidence."""
from __future__ import annotations

import contextlib
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "results.db"
CACHE_DB_PATH = Path(__file__).parent.parent / "data" / "cache.db"


def _get_conn(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create cache + rankings + evidence_log tables if missing."""
    with _get_conn(CACHE_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key        TEXT PRIMARY KEY,
                value      TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                ttl_hours  INTEGER NOT NULL DEFAULT 168
            )
        """)

    with _get_conn(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rankings (
                run_id          TEXT NOT NULL,
                profile         TEXT NOT NULL,
                country         TEXT NOT NULL,
                rank            INTEGER NOT NULL,
                total_score     REAL NOT NULL,
                score_breakdown TEXT NOT NULL,
                weight_used     TEXT NOT NULL,
                missing_agents  TEXT NOT NULL,
                confidence      REAL NOT NULL,
                ran_at          TEXT NOT NULL,
                PRIMARY KEY (run_id, country)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_log (
                run_id      TEXT NOT NULL,
                country     TEXT NOT NULL,
                agent_name  TEXT NOT NULL,
                url         TEXT NOT NULL,
                title       TEXT,
                as_of       TEXT,
                confidence  REAL,
                source_type TEXT,
                raw_excerpt TEXT,
                PRIMARY KEY (run_id, country, agent_name, url)
            )
        """)


def persist_rankings(run_id: str, ranked_results: list, ran_at: str) -> None:
    with _get_conn(DB_PATH) as conn:
        for r in ranked_results:
            conn.execute(
                """INSERT OR REPLACE INTO rankings
                   (run_id, profile, country, rank, total_score, score_breakdown,
                    weight_used, missing_agents, confidence, ran_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    run_id, r.profile, r.country, r.rank, r.total_score,
                    json.dumps(r.score_breakdown),
                    json.dumps(r.weight_breakdown),
                    json.dumps(r.missing_agents),
                    r.confidence_overall,
                    ran_at,
                ),
            )
            for agent_name, evidence_list in r.country_profile.resolved_evidence.items():
                for ev in evidence_list:
                    with contextlib.suppress(sqlite3.IntegrityError):
                        conn.execute(
                            """INSERT OR IGNORE INTO evidence_log
                               (run_id, country, agent_name, url, title, as_of,
                                confidence, source_type, raw_excerpt)
                               VALUES (?,?,?,?,?,?,?,?,?)""",
                            (run_id, r.country, agent_name, ev.url, ev.title,
                             ev.as_of, ev.confidence, ev.source_type, ev.raw_excerpt),
                        )
