"""Small language helpers for multilingual document workflows."""


def contains_devanagari(text: str) -> bool:
    """Return whether text contains Devanagari characters (used for Hindi)."""
    return any("\u0900" <= character <= "\u097f" for character in text)
