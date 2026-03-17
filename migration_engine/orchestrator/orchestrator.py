"""
Main orchestration logic.

Flow:
  1. For each country × active agent:
       - Check cache → hit: deserialize; miss: agent.run() → cache.set()
       - Log the result
  2. For each country:
       - conflict_resolver.resolve() → resolved_scores, resolved_evidence
       - merger.build() → CountryProfile
  3. ranker.rank() → sorted list of RankedResult
  4. For each result: explainer.generate() → explanation_bullets
  5. db.persist() + return (ranked_results, markdown_report)
"""
from __future__ import annotations

import importlib
import json
import os
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import anthropic

import config
from infra.cache import Cache, build_cache_key
from infra.db import init_db, persist_rankings
from infra.logger import Logger
from orchestrator import conflict_resolver, merger, explainer
from ranker.ranker import rank
from reports.report_generator import render_markdown
from schema.models import AgentOutput, Evidence


def _load_agent(agent_name: str, cache: Cache, logger: Logger):
    """Dynamically import and instantiate an agent class from AGENT_REGISTRY."""
    class_path = config.AGENT_REGISTRY[agent_name]
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(cache=cache, logger=logger)


def _deserialize_output(data: dict) -> AgentOutput:
    evidence = [Evidence(**ev) for ev in data.pop("evidence", [])]
    return AgentOutput(evidence=evidence, **data)


def _serialize_output(output: AgentOutput) -> dict:
    d = asdict(output)
    return d


class Orchestrator:
    def __init__(self, no_cache: bool = False):
        self.no_cache = no_cache
        init_db()
        self.cache = Cache()

    def run(
        self,
        profile: str,
        countries: list[str],
        disabled_agents: list[str] | None = None,
        weights: dict[str, float] | None = None,
    ) -> tuple[list, str]:
        disabled_agents = disabled_agents or []
        active_agent_names = [a for a in config.AGENT_REGISTRY if a not in disabled_agents]

        run_id = str(uuid.uuid4())[:8]
        ran_at = datetime.now(timezone.utc).isoformat()
        logger = Logger(run_id)
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        logger.log("run_start", profile=profile, countries=countries,
                   disabled_agents=disabled_agents, run_id=run_id)

        # --- Phase 1: collect agent outputs ---
        # Structure: {country: {agent_name: AgentOutput}}
        all_outputs: dict[str, dict[str, AgentOutput]] = {c: {} for c in countries}

        for agent_name in active_agent_names:
            agent = _load_agent(agent_name, self.cache, logger)
            for country in countries:
                cache_key = build_cache_key(agent_name, country, profile)
                cached_data = None if self.no_cache else self.cache.get(cache_key)

                if cached_data:
                    output = _deserialize_output(cached_data)
                    logger.agent_run(agent_name, country, output.domain_score,
                                     output.confidence, cached=True)
                else:
                    try:
                        output = agent.run(country, profile)
                        self.cache.set(cache_key, _serialize_output(output), config.CACHE_TTL_HOURS)
                        logger.agent_run(agent_name, country, output.domain_score,
                                         output.confidence, cached=False)
                    except Exception as exc:
                        logger.error(agent_name, country, str(exc))
                        output = AgentOutput(
                            agent_name=agent_name, country=country, profile=profile,
                            domain_score=0.0, confidence=0.0, evidence=[],
                            caveats=[f"Agent failed: {exc}"], raw_data={},
                            fetched_at=datetime.now(timezone.utc).isoformat(),
                        )

                all_outputs[country][agent_name] = output

        # --- Phase 2: merge per country ---
        country_profiles = []
        for country in countries:
            outputs = all_outputs[country]
            resolved_scores, resolved_evidence = conflict_resolver.resolve(outputs)
            cp = merger.build(country, profile, outputs, resolved_scores, resolved_evidence)
            country_profiles.append(cp)

        # --- Phase 3: rank ---
        ranked_results = rank(country_profiles, weights, disabled_agents)

        # --- Phase 4: generate explanations ---
        for result in ranked_results:
            result.explanation_bullets = explainer.generate(client, result)

        # --- Phase 5: persist + report ---
        persist_rankings(run_id, ranked_results, ran_at)
        logger.log("run_complete", run_id=run_id, countries_ranked=len(ranked_results))

        report = render_markdown(ranked_results, profile, run_id, ran_at)
        return ranked_results, report
