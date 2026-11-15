"""
FitFindr MCP server (unit 4, Milestone 1).

Exposes one tool, search_listings, over MCP. The agent calls it through
mcp_client.call_tool instead of importing it directly.

    python mcp_server.py        starts the server (it will just sit there - that's right)
    python mcp_client.py        asks the server what it offers
"""

from mcp.server.fastmcp import FastMCP

# Imported under an alias so the registered tool below doesn't call itself.
from tools import search_listings as _search_listings_impl

mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search 40 secondhand clothing listings (Depop, thredUp, Poshmark) by keywords.
    description (string, required): words like "vintage graphic tee"; a listing scores
    one point per distinct word found in its title, description, category or style tags.
    size (string, optional): e.g. "M" or "8"; matches when it equals one piece of the
    listing's size split on "/", spaces and parentheses ("M" matches "S/M"); "One Size"
    listings match any size. max_price (number, optional): US dollars, inclusive.
    Returns up to 10 listing dicts (id, title, description, category, style_tags, size,
    condition, price, colors, brand, platform), highest score first. Returns an empty
    list [] when nothing matches - never null, never an error.
    """
    return _search_listings_impl(description, size, max_price)


if __name__ == "__main__":
    mcp.run()
