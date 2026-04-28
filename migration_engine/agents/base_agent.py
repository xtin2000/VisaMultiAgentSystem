"""Abstract base class for all domain agents."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

import config
import google.generativeai as genai
from schema.models import AgentOutput


def _to_python(value: Any) -> Any:
    """Recursively convert protobuf / proto-plus values to plain Python types."""
    if isinstance(value, (int, float, str, bool, type(None))):
        return value
    if hasattr(value, "items"):
        return {k: _to_python(v) for k, v in value.items()}
    if hasattr(value, "__iter__"):
        return [_to_python(v) for v in value]
    return value


def _convert_schema(schema: dict) -> genai.protos.Schema:
    """Convert a JSON-schema dict to a Gemini Schema proto."""
    kwargs: dict[str, Any] = {}

    json_type = schema.get("type", "string")
    if isinstance(json_type, list):
        non_null = [t for t in json_type if t != "null"]
        json_type = non_null[0] if non_null else "string"

    type_map = {
        "string":  "STRING",
        "number":  "NUMBER",
        "integer": "INTEGER",
        "boolean": "BOOLEAN",
        "object":  "OBJECT",
        "array":   "ARRAY",
    }
    kwargs["type"] = type_map.get(json_type, "STRING")

    if "description" in schema:
        kwargs["description"] = schema["description"]
    if "enum" in schema:
        kwargs["enum"] = [e for e in schema["enum"] if e is not None]
    if "properties" in schema:
        kwargs["properties"] = {k: _convert_schema(v) for k, v in schema["properties"].items()}
    if "required" in schema:
        kwargs["required"] = schema["required"]
    if "items" in schema:
        kwargs["items"] = _convert_schema(schema["items"])

    return genai.protos.Schema(**kwargs)


class BaseAgent(ABC):
    """Every domain agent inherits this class and implements :meth:`run`."""

    agent_name: str

    def __init__(self, cache: Any = None, logger: Any = None) -> None:
        self.cache = cache
        self.logger = logger
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    @abstractmethod
    def run(self, country: str, profile: str) -> AgentOutput:
        """Gather evidence for one country and return a normalized AgentOutput."""
        ...

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _call_model_with_tools(
        self,
        system: str,
        user: str,
        tools: list[dict],
        record_tool_name: str,
        max_iterations: int = 10,
    ) -> dict:
        """Run a Gemini tool-use loop until the model calls ``record_tool_name``.

        The model uses Google Search grounding to gather evidence, then submits
        structured findings via the named function-call. Returns the call's input dict.
        """
        function_declarations = [
            genai.protos.FunctionDeclaration(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=_convert_schema(tool["input_schema"]),
            )
            for tool in tools
            if "input_schema" in tool
        ]

        gemini_tools = [
            genai.protos.Tool(google_search=genai.protos.GoogleSearch()),
            genai.protos.Tool(function_declarations=function_declarations),
        ]

        model = genai.GenerativeModel(
            config.MODEL,
            system_instruction=system,
            tools=gemini_tools,
        )
        chat = model.start_chat()
        message = user

        for _ in range(max_iterations):
            response = chat.send_message(message)
            for part in response.parts:
                fn = getattr(part, "function_call", None)
                if fn and fn.name == record_tool_name:
                    return _to_python(fn.args)
            message = (
                f"You have gathered enough data. Now call the `{record_tool_name}` "
                f"tool with your structured findings."
            )

        raise RuntimeError(
            f"Agent '{self.agent_name}' did not call '{record_tool_name}' "
            f"within {max_iterations} iterations."
        )
