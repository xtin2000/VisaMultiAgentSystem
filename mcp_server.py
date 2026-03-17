"""
MCP server for the passport / migration-ranking project.

Exposes one tool:
  rank_countries(profile, countries?) → markdown report
"""
import os
import sys

# Make sure the migration_engine package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "migration_engine"))

from mcp.server.fastmcp import FastMCP
from orchestrator.orchestrator import Orchestrator
import config

mcp = FastMCP("passport-ranker")


@mcp.tool()
def rank_countries(
    profile: str,
    countries: list[str] | None = None,
) -> str:
    """
    Rank countries for immigration based on a user profile.

    Args:
        profile: One of 'software_engineer', 'general_professional', or 'student_to_work'.
        countries: Optional list of countries to evaluate. Defaults to all supported countries.

    Returns:
        A markdown report with ranked results and explanations.
    """
    # Normalise profile string (allow natural language input)
    profile = config.PROFILE_DISPLAY.get(profile.lower().strip(), profile.strip())

    if profile not in config.PROFILES:
        return (
            f"Unknown profile '{profile}'. "
            f"Valid options: {', '.join(config.PROFILES)}"
        )

    target_countries = countries or config.COUNTRIES

    unknown = [c for c in target_countries if c not in config.COUNTRIES]
    if unknown:
        return (
            f"Unknown countries: {', '.join(unknown)}. "
            f"Supported: {', '.join(config.COUNTRIES)}"
        )

    orchestrator = Orchestrator()
    _ranked, report = orchestrator.run(profile=profile, countries=target_countries)
    return report


if __name__ == "__main__":
    mcp.run(transport="stdio")
