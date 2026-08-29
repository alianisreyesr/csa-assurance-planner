"""Shared helpers used by both the API router and the seed script, so the
two write paths can't drift on timestamp/reference formatting."""
from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone


def now(days_ago: int = 0) -> str:
    """UTC ISO 8601 timestamp, optionally backdated (used by the seed script
    to produce a plausible-looking history)."""
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def reference(prefix: str = "CSA") -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"
