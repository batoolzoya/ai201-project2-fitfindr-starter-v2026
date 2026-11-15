"""
The runs the test needs (unit 4, Milestone 3).

run_eval.py runs every scenario here five times with caching off.

Criterion 5 (search wording) is not here: it is about search_listings alone,
which is plain code with no model, so it is checked with check_search.py
(each of its 5 queries is one try).
"""

SCENARIOS = [
    {
        # Criterion 1: a matching query completes all three tools.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # Criterion 2: the branch. Nothing can match.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3: state. Compare search_results[0] id, selected_item id
        # and the id passed to suggest_outfit (shown in the trace).
        "name": "selected item is the item passed on",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4: fit card is 2-4 sentences and mentions the item title,
        # price and platform once each.
        "name": "fit card content",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} - "
                f"it should be one of {WARDROBES}"
            )
    return problems
