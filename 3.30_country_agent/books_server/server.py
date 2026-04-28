import requests
from fastmcp import FastMCP

mcp = FastMCP("Books Server")


@mcp.tool()
def get_books_by_author(author: str) -> list[dict]:
    """Get books written by a given author using the OpenLibrary API."""
    resp = requests.get(
        "https://openlibrary.org/search.json",
        params={"author": author, "limit": 5},
    )
    resp.raise_for_status()
    docs = resp.json().get("docs", [])[:5]
    return [
        {"title": doc.get("title"), "year": doc.get("first_publish_year")}
        for doc in docs
    ]


if __name__ == "__main__":
    mcp.run()
