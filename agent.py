"""
The FitFindr planning loop.

    python agent.py          runs both example paths below

Branch rule (see README.md, Planning Loop):
    If search_listings returns an empty list, put a message in session["error"]
    saying what the user could change, and stop without calling suggest_outfit.
    Otherwise take the first result as session["selected_item"], run
    suggest_outfit, then create_fit_card, reading each input from the session.
"""

import re

import config  # noqa: F401
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable  # noqa: F401 - handler comes in unit 4


# -- session state -------------------------------------------------------------

def new_session(query: str, wardrobe: dict) -> dict:
    """A fresh session for one user interaction."""
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one chosen - goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# -- query parsing (regex) -----------------------------------------------------

_PRICE = re.compile(
    r"(?:under|below|less than|max|up to|<)\s*\$?\s*(\d+(?:\.\d+)?)|\$\s*(\d+(?:\.\d+)?)",
    re.I,
)
_SIZE = re.compile(r"\b(?:in\s+)?size\s+([a-z0-9/.]+)", re.I)
_FILLER = re.compile(r"\b(?:looking for|i want|i need|show me)\b", re.I)


def parse_query(query: str) -> dict:
    """
    Pull max_price, size and description out of a plain-language query.
      max_price: number after "under/below/less than/max/up to", or after "$"
      size:      the word after "size"
      description: whatever is left, with filler phrases and punctuation removed
    """
    text = query
    max_price = None
    m = _PRICE.search(text)
    if m:
        max_price = float(m.group(1) or m.group(2))
        text = text[: m.start()] + " " + text[m.end():]

    size = None
    m = _SIZE.search(text)
    if m:
        size = m.group(1).upper()
        text = text[: m.start()] + " " + text[m.end():]

    text = _FILLER.sub(" ", text)
    description = " ".join(re.sub(r"[^\w\s'-]", " ", text).split())
    return {"description": description, "size": size, "max_price": max_price}


def _no_results_message(parsed: dict) -> str:
    """Say what was searched and what the user could change."""
    looked_for = f"'{parsed['description']}'"
    if parsed["size"]:
        looked_for += f" in size {parsed['size']}"
    if parsed["max_price"] is not None:
        looked_for += f" under ${parsed['max_price']:g}"

    tips = []
    if parsed["max_price"] is not None:
        tips.append(f"raise your max price above ${parsed['max_price']:g}")
    if parsed["size"]:
        tips.append(f"drop the size or try a size next to {parsed['size']}")
    tips.append("use a more common word for the item (e.g. 'dress', 'jacket', 'tee', 'jeans')")
    return f"No listings matched {looked_for}. Try: " + "; ".join(tips) + "."


# -- planning loop -------------------------------------------------------------

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.
    Check session["error"] first - if it isn't None, the run ended early and
    the later fields are still None.
    """
    session = new_session(query, wardrobe)
    steps = 0

    # Step 1: parse the query.
    steps += 1
    trace.check_iterations(steps)
    session["parsed"] = parse_query(query)

    # Step 2: search, reading the inputs back out of the session.
    steps += 1
    trace.check_iterations(steps)
    parsed = session["parsed"]
    session["search_results"] = search_listings(
        parsed["description"], size=parsed["size"], max_price=parsed["max_price"]
    )

    # THE BRANCH: nothing came back -> say what to change and stop.
    if len(session["search_results"]) == 0:
        session["error"] = _no_results_message(parsed)
        return session

    # Otherwise pick the best match.
    session["selected_item"] = session["search_results"][0]

    # Step 3: outfit, using the item stored in the session.
    steps += 1
    trace.check_iterations(steps)
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    # Step 4: fit card, using the outfit and item stored in the session.
    steps += 1
    trace.check_iterations(steps)
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    return session


# -- running it directly -------------------------------------------------------

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} - it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} - ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )