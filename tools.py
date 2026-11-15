"""
The three FitFindr tools.

    search_listings(description, size, max_price)  -> list[dict]
    suggest_outfit(new_item, wardrobe)             -> str
    create_fit_card(outfit, new_item)              -> str

Each one matches the spec in the Tool Inventory section of README.md.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# Little words that never count toward a listing's score.
STOP_WORDS = {
    "a", "an", "the", "in", "of", "with", "for", "and", "or", "to", "on",
    "my", "i", "im", "looking", "want", "need", "some", "something",
}


def _words(text: str) -> set[str]:
    """Lowercase text split into words (letters and digits only)."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _size_matches(listing_size: str, wanted: str) -> bool:
    """
    Split the listing's size on /, spaces and parentheses; it matches if one
    piece equals the user's size (ignoring case). "One Size" matches any size.
    """
    listing_size = (listing_size or "").lower()
    if "one size" in listing_size:
        return True
    pieces = [p for p in re.split(r"[/\s()]+", listing_size) if p]
    return wanted.strip().lower() in pieces


# -- Tool 1: search_listings ---------------------------------------------------

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Filter listings by price and size, score what's left by how many distinct
    query words appear in title, description, category and style_tags, and
    return up to SEARCH_RESULT_LIMIT listing dicts, highest score first.
    Ties keep original file order. Returns [] when nothing matches.
    """
    query_words = _words(description or "") - STOP_WORDS
    if not query_words:
        return []

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size and not _size_matches(listing.get("size"), size):
            continue

        # Null fields (like brand) are skipped: only these four are searched.
        searchable = " ".join([
            listing.get("title") or "",
            listing.get("description") or "",
            listing.get("category") or "",
            " ".join(listing.get("style_tags") or []),
        ])
        score = len(query_words & _words(searchable))
        if score > 0:
            scored.append((score, listing))

    # sorted() is stable, so equal scores keep their original file order.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# -- Tool 2: suggest_outfit ----------------------------------------------------

def _describe_item(item: dict) -> str:
    return (
        f"{item.get('title')} ({item.get('category')}; "
        f"colors: {', '.join(item.get('colors') or [])}; "
        f"style: {', '.join(item.get('style_tags') or [])}; "
        f"size {item.get('size')}; ${item.get('price')} on {item.get('platform')})"
    )


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Ask the model for 1-2 outfits built around new_item. With a non-empty
    wardrobe, outfits name specific wardrobe pieces. With an empty wardrobe,
    returns general styling advice instead. Always a non-empty string.
    """
    items = (wardrobe or {}).get("items") or []
    system = (
        "You are a friendly thrift-store stylist. Be concrete and brief: "
        "plain text, no markdown headings, under 120 words."
    )

    if not items:
        prompt = (
            f"Someone is thinking about buying this secondhand item:\n"
            f"{_describe_item(new_item)}\n\n"
            "They haven't told you what's in their wardrobe. Give general "
            "styling advice: 1-2 outfit ideas using common basics, with what "
            "kinds of pieces, colors and shoes to pair it with."
        )
    else:
        lines = []
        for w in items:
            line = f"- {w.get('name')} ({w.get('category')}; colors: {', '.join(w.get('colors') or [])})"
            if w.get("notes"):
                line += f" - note: {w['notes']}"
            lines.append(line)
        prompt = (
            f"Someone is thinking about buying this secondhand item:\n"
            f"{_describe_item(new_item)}\n\n"
            f"Their wardrobe:\n" + "\n".join(lines) + "\n\n"
            "Suggest 1-2 outfits that combine the new item with pieces from "
            "this wardrobe. Name each wardrobe piece exactly as written above."
        )

    response = generate(prompt, system=system)
    if not response.strip():
        return f"Try pairing the {new_item.get('title')} with simple basics in neutral colors."
    return response


# -- Tool 3: create_fit_card ---------------------------------------------------

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Ask the model for a 2-4 sentence caption that mentions the item, its price
    and its platform once each. If outfit is empty or whitespace, returns a
    message instead and makes no model call.
    """
    if not outfit or not outfit.strip():
        return "Can't write a fit card: no outfit suggestion was given."

    system = (
        "You write short social media captions for thrift finds. Sound like a "
        "real person posting, not a product description. Plain text only."
    )
    prompt = (
        f"Item: {new_item.get('title')}\n"
        f"Price: ${new_item.get('price')}\n"
        f"Platform: {new_item.get('platform')}\n"
        f"How I'm styling it: {outfit}\n\n"
        "Write a 2-4 sentence caption about this find. Use the item's exact title, "
        f"'{new_item.get('title')}', word for word, exactly once. Mention the "
        "price and the platform exactly once each. Be specific about the vibe. "        "At most 3 hashtags, at the end."
    )
    return generate(prompt, system=system)