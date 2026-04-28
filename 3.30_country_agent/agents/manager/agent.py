import pathlib

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# this'll be the root of the whole 'project'
_root = pathlib.Path(__file__).resolve().parent.parent.parent

books_agent = Agent(
    name="books_agent",
    model="gemini-2.5-flash",
    instruction="You find books by a given author. Use the get_books_by_author tool.",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command=str(_root / "books_server" / ".venv" / "bin" / "python"),
                args=["server.py"],
                cwd=str(_root / "books_server"),
            )
        )
    ],
)

country_agent = Agent(
    name="country_agent",
    model="gemini-2.5-flash",
    instruction="You find capital cities of countries. Use the get_capital tool.",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command=str(_root / "country_server" / ".venv" / "bin" / "python"),
                args=["server.py"],
                cwd=str(_root / "country_server"),
            )
        )
    ],
)

root_agent = Agent(
    name="manager",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful manager agent. "
        "Delegate to books_agent for finding books by author, "
        "and country_agent for finding capital cities of countries."
    ),
    sub_agents=[books_agent, country_agent],
)
