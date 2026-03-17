#!/usr/bin/env python3
"""
Migration Feasibility and Risk Engine — CLI entry point.

Usage examples:
  python main.py --profile "software engineer" --countries all --output markdown
  python main.py --profile "software engineer" --countries "Canada,Germany" --output json
  python main.py --profile "general professional" --disable-agent english --disable-agent visa
  python main.py --profile "software engineer" --no-cache --output markdown
"""
from __future__ import annotations
import json
import os
import sys
from dataclasses import asdict
from typing import Optional

import typer
from typing_extensions import Annotated

# Ensure project root is on sys.path when run as a script
sys.path.insert(0, os.path.dirname(__file__))

import config

app = typer.Typer(add_completion=False, help="Migration Feasibility and Risk Engine")


def _resolve_profile(raw: str) -> str:
    key = raw.strip().lower()
    if key in config.PROFILE_DISPLAY:
        return config.PROFILE_DISPLAY[key]
    if key in config.PROFILES:
        return key
    valid = list(config.PROFILE_DISPLAY.keys()) + config.PROFILES
    typer.echo(f"[error] Unknown profile '{raw}'. Valid options: {valid}", err=True)
    raise typer.Exit(1)


def _resolve_countries(raw: str) -> list[str]:
    if raw.strip().lower() == "all":
        return config.COUNTRIES
    requested = [c.strip() for c in raw.split(",") if c.strip()]
    invalid = [c for c in requested if c not in config.COUNTRIES]
    if invalid:
        typer.echo(f"[warning] Unknown countries (will be included anyway): {invalid}", err=True)
    return requested


@app.command()
def run(
    profile: Annotated[str, typer.Option("--profile", "-p", help="software engineer | general professional | student-to-work pathway")],
    countries: Annotated[str, typer.Option("--countries", "-c", help="Comma-separated country names, or 'all'")] = "all",
    disable_agent: Annotated[Optional[list[str]], typer.Option("--disable-agent", "-d", help="Agent to disable: visa|job_market|affordability|english")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="terminal | markdown | json")] = "terminal",
    no_cache: Annotated[bool, typer.Option("--no-cache", help="Ignore cache, force fresh Claude calls")] = False,
):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        typer.echo("[error] ANTHROPIC_API_KEY environment variable is not set.", err=True)
        raise typer.Exit(1)

    normalized_profile = _resolve_profile(profile)
    target_countries = _resolve_countries(countries)
    disabled = list(disable_agent) if disable_agent else []

    typer.echo(f"Running: profile={normalized_profile}, countries={len(target_countries)}, "
               f"disabled={disabled or 'none'}, cache={'off' if no_cache else 'on'}")

    from orchestrator.orchestrator import Orchestrator
    from reports.report_generator import render_terminal

    orch = Orchestrator(no_cache=no_cache)
    ranked, report = orch.run(
        profile=normalized_profile,
        countries=target_countries,
        disabled_agents=disabled,
    )

    if output == "markdown":
        print(report)
    elif output == "json":
        print(json.dumps([asdict(r) for r in ranked], indent=2, default=str))
    else:
        render_terminal(ranked)


if __name__ == "__main__":
    app()
