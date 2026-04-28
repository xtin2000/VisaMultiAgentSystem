import requests
from fastmcp import FastMCP

mcp = FastMCP("Country Server")

@mcp.tool()
def get_capital(country: str) -> str:
    """Get the capital city of a given country."""
    resp = requests.get(f"https://restcountries.com/v3.1/name/{country}")
    resp.raise_for_status()
    return resp.json()[0]["capital"][0]

if __name__ == "__main__":
    mcp.run()
