def matches_search(search: str | None, *fields: str | None) -> bool:
    """Case-insensitive substring match against any of the given fields."""
    if not search:
        return True
    needle = search.strip().lower()
    return any(needle in (field or "").lower() for field in fields)
