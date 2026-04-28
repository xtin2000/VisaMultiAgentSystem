"""Google ADK entry point — chat agent backed by the migration_engine MCP server."""
import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

# agent.py → visa_ranker/ → SemesterProject_VisaRanker/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER_PATH = str(REPO_ROOT / "mcp_server.py")
PYTHON_BIN = str(REPO_ROOT / ".venv" / "bin" / "python")

toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=PYTHON_BIN,
            args=[MCP_SERVER_PATH],
            env={**os.environ},
        ),
        timeout=60,
    )
)

root_agent = Agent(
    name="visa_ranker",
    model="gemini-2.5-flash",
    instruction="""You are a Migration Feasibility Analyst that helps US citizens evaluate
countries for immigration.

You have access to the rank_countries tool which analyzes countries based on:
- Job market accessibility
- Visa pathway feasibility
- Cost of living / affordability
- English language friendliness

When a user asks about immigration or moving abroad:
1. Determine their profile type: software_engineer, general_professional, or student_to_work
2. Ask which languages they are comfortable speaking
3. Call rank_countries with the profile and optional country list
4. Present the results clearly and offer to answer follow-up questions

Supported countries: Canada, UK, Ireland, Netherlands, Germany, Portugal, Spain,
Australia, New Zealand, Singapore, Japan, South Korea, Mexico, Costa Rica, Taiwan

Supported profiles:
- software_engineer (or "software engineer")
- general_professional (or "general professional")
- student_to_work (or "student to work")

Be friendly, informative, and help users understand the tradeoffs between countries.""",
    tools=[toolset],
)
