"""
Criterion 5: search finds the right item for differently-worded queries.

search_listings is plain code (no model), so each query gives the same answer
every time. The 5 tries for this criterion are 5 different queries, as written
in criteria.md. Calls go through MCP, the same way the agent calls search.

    python check_search.py
"""

from mcp_client import call_tool

CASES = [
    ("jean jacket", ["lst_007"]),
    ("graphic t-shirt", ["lst_002", "lst_006", "lst_033"]),
    ("band shirt under $25", ["lst_033", "lst_006"]),
    ("chunky knit sweater", ["lst_008"]),
    ("leather jacket", ["lst_022"]),
]

if __name__ == "__main__":
    from agent import parse_query

    print("Criterion 5 - first search result for each query (via MCP)\n")
    passes = 0
    for i, (query, expected) in enumerate(CASES, 1):
        p = parse_query(query)
        results = call_tool("search_listings", p) or []
        first = results[0] if results else None
        got = f"{first['id']} - {first['title']}" if first else "(no results)"
        ok = bool(first) and first["id"] in expected
        passes += ok
        print(f"Try {i}: '{query}'")
        print(f"   expected: {' or '.join(expected)}")
        print(f"   first:    {got}")
        top3 = ", ".join(r["id"] for r in results[:3]) or "-"
        print(f"   top 3:    {top3}")
        print(f"   -> {'PASS' if ok else 'FAIL'}\n")
    print(f"{passes} of {len(CASES)} passed")