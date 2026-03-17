"""
Abstract base class for all domain agents.

Every agent (job_market, visa, affordability, english) must:
  1. Inherit BaseAgent
  2. Implement run(country, profile) -> AgentOutput
  3. Set self.agent_name to one of the registry keys in config.AGENT_REGISTRY

The shared _call_claude_with_tools helper handles the agentic loop:
  - Claude calls web_search (built-in) to gather evidence
  - Claude then calls a custom "record_*_score" tool to submit structured output
  - We intercept that tool_use block and return its input as validated data
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import anthropic

import config
from schema.models import AgentOutput


class BaseAgent(ABC):
    agent_name: str  # Must be set by subclass

    def __init__(self, cache=None, logger=None):
        self.cache = cache
        self.logger = logger
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    @abstractmethod
    def run(self, country: str, profile: str) -> AgentOutput:
        """Gather evidence and return a normalized AgentOutput."""
        ...

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _call_claude_with_tools(
        self,
        system: str,
        user: str,
        tools: list[dict],
        record_tool_name: str,
        max_iterations: int = 10,
    ) -> dict:
        """
        Run the agentic tool-use loop until Claude calls `record_tool_name`.

        Claude will:
          1. Call web_search (built-in) one or more times to gather data
          2. Call `record_tool_name` with structured JSON as its final output

        Returns the input dict of the record tool call.
        Raises RuntimeError if the loop completes without a record call.
        """
        messages = [{"role": "user", "content": user}]
        # Include the built-in web_search tool alongside the custom record tool
        all_tools = [{"type": "web_search_20250305", "name": "web_search"}] + tools

        for _ in range(max_iterations):
            response = self.client.messages.create(
                model=config.MODEL,
                max_tokens=4096,
                system=system,
                tools=all_tools,
                messages=messages,
            )

            # Scan for our record tool call
            record_input = None
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    if block.name == record_tool_name:
                        record_input = block.input
                        # We don't need to continue the loop
                        break
                    # For web_search the SDK handles execution automatically
                    # but we need to include tool_result blocks in the next turn
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "",  # SDK fills actual search results
                    })

            if record_input is not None:
                return record_input

            if response.stop_reason == "end_turn":
                break

            # Append assistant turn + tool results and continue
            messages.append({"role": "assistant", "content": response.content})
            if tool_results:
                messages.append({"role": "user", "content": tool_results})

        raise RuntimeError(
            f"Agent '{self.agent_name}' did not call '{record_tool_name}' "
            f"within {max_iterations} iterations."
        )
