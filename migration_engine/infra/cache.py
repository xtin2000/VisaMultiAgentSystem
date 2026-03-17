"""
SQLite-backed cache for agent outputs with TTL support.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from infra.db import CACHE_DB_PATH, _get_conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_cache_key(agent_name: str, country: str, profile: str) -> str:
    """Week-granular cache key so both collaborators share results within a work week."""
    iso = datetime.now(timezone.utc).isocalendar()
    week_label = f"{iso.year}-W{iso.week:02d}"
    safe_country = country.lower().replace(" ", "_")
    return f"{agent_name}|{safe_country}|{profile}|{week_label}"


class Cache:
    def get(self, key: str) -> dict | None:
        with _get_conn(CACHE_DB_PATH) as conn:
            row = conn.execute(
                "SELECT value, fetched_at, ttl_hours FROM cache WHERE key=?", (key,)
            ).fetchone()
        if row is None:
            return None
        fetched = datetime.fromisoformat(row["fetched_at"])
        age_hours = (datetime.now(timezone.utc) - fetched).total_seconds() / 3600
        if age_hours > row["ttl_hours"]:
            return None  # stale
        return json.loads(row["value"])

    def set(self, key: str, value: dict, ttl_hours: int = 168) -> None:
        with _get_conn(CACHE_DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, fetched_at, ttl_hours) VALUES (?,?,?,?)",
                (key, json.dumps(value), _now_iso(), ttl_hours),
            )

    def invalidate(self, key: str) -> None:
        with _get_conn(CACHE_DB_PATH) as conn:
            conn.execute("DELETE FROM cache WHERE key=?", (key,))
