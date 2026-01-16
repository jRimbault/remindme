"""Parsing functions for remindme."""

from __future__ import annotations

from datetime import datetime, timedelta

from dateutil import parser as dtparser

from remindme.utils import die


def parse_duration(text: str) -> timedelta:
    """Parse duration string like '30m', '2h', '45s', '1d'.

    Supported: <int><unit> where unit in s/m/h/d (e.g. 30m, 2h, 45s, 1d).

    Maximum duration: 365 days (1 year).

    Args:
        text: Duration string to parse

    Returns:
        Parsed timedelta

    Raises:
        SystemExit: If duration is invalid or exceeds maximum
    """

    text = text.strip().lower()
    if not text:
        die("empty duration")

    # simple, predictable parser (no "1h30m" gymnastics)
    n_str = text[:-1]
    unit = text[-1]
    if unit not in {"s", "m", "h", "d"} or not n_str.isdigit():
        die(f"invalid duration {text!r}: expected like 30m, 2h, 45s, 1d")

    n = int(n_str)
    if n <= 0:
        die(f"invalid duration {text!r}: must be > 0")

    delta: timedelta
    match unit:
        case "s":
            delta = timedelta(seconds=n)
        case "m":
            delta = timedelta(minutes=n)
        case "h":
            delta = timedelta(hours=n)
        case "d":
            delta = timedelta(days=n)
        case _:
            # This should be unreachable due to earlier validation
            die(f"invalid duration unit: {unit}")

    # Sanity check: max 365 days
    max_duration = timedelta(days=365)
    if delta > max_duration:
        die(f"invalid duration {text!r}: maximum is 365 days")

    return delta


def format_systemd_duration(delta: timedelta) -> str:
    """Format timedelta as systemd duration string.

    Prefer largest unit when exact; otherwise fall back to seconds.

    Args:
        delta: Duration to format

    Returns:
        Systemd duration string (e.g., "30m", "2h", "1d")

    Raises:
        SystemExit: If duration is <= 0 seconds
    """

    seconds = int(delta.total_seconds())
    if seconds <= 0:
        die("duration must be > 0 seconds")

    day = 24 * 3600
    hour = 3600
    minute = 60

    if seconds % day == 0:
        return f"{seconds // day}d"
    if seconds % hour == 0:
        return f"{seconds // hour}h"
    if seconds % minute == 0:
        return f"{seconds // minute}m"
    return f"{seconds}s"


def parse_when(text: str) -> datetime:
    """Parse time string into datetime.

    Accepts:
      - "15:00" / "15:00:00"
      - "3pm" / "3:30pm"
      - "2026-01-15 15:00" (or many dateutil-supported forms)

    Rules:
      - If only a time-of-day is provided and it's already in the past today,
        schedule it for tomorrow.
      - Naive datetimes are interpreted in local time.

    Args:
        text: Time string to parse

    Returns:
        Parsed datetime in the future

    Raises:
        SystemExit: If time is invalid or in the past
    """

    raw = text.strip()
    if not raw:
        die("empty time")

    now = datetime.now()

    # First try: treat as time-only by parsing with today's date as default.
    # If the user didn't specify a date, dateutil will keep the default date.
    try:
        dt = dtparser.parse(raw, default=now.replace(microsecond=0))
    except Exception as e:
        die(f"could not parse time {raw!r}: {e}")

    dt = dt.replace(microsecond=0)

    # Heuristic: if the input looks like time-only, then roll forward if needed.
    # This catches "3pm", "15:00", "15:00:00".
    looks_time_only = not any(ch.isdigit() for ch in raw.split()[0] if ch in "-/") and (
        ":" in raw
        or "am" in raw.lower()
        or "pm" in raw.lower()
        or raw.strip().isdigit()
    )
    if looks_time_only:
        candidate = now.replace(
            hour=dt.hour, minute=dt.minute, second=dt.second, microsecond=0
        )
        if candidate <= now:
            candidate = candidate + timedelta(days=1)
        return candidate

    # Date provided (or at least we assume so). Ensure it's in the future.
    if dt <= now:
        die(
            f"requested time is not in the future: {dt.isoformat(sep=' ', timespec='minutes')}"
        )
    return dt
