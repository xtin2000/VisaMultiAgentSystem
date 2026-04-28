"""
Standalone ADK agent that connects to the MCP server via stdio.
Run with: uv run adk_agent.py
"""
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types
import asyncio
import os

MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
PYTHON_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python")


async def main():
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
    agent = Agent(
        name="visa_ranker",
        model="gemini-2.5-flash",
        instruction="You are a Migration Feasibility Analyst. Use your tools to rank countries for immigration based on user profiles. Be helpful and informative.",
        tools=[toolset],
    )

    runner = Runner(
        agent=agent,
        app_name="visa_ranker",
        session_service=InMemorySessionService(),
    )
    session = await runner.session_service.create_session(
        app_name="visa_ranker",
        user_id="user1"
    )

    print("Visa Migration Ranker - type 'quit' to exit")
    print("Example: 'Rank Canada, Germany, and Japan for a software engineer'\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        content = types.Content(role="user", parts=[types.Part(text=question)])
        async for event in runner.run_async(
            user_id="user1",
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent: {part.text.strip()}")


if __name__ == "__main__":
    asyncio.run(main())
