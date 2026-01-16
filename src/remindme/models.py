"""Data models for remindme."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union

from remindme.backends import Backend


@dataclass(frozen=True, slots=True)
class In:
    """Schedule a reminder after a duration."""

    duration: timedelta
    message: str
    title: str


@dataclass(frozen=True, slots=True)
class At:
    """Schedule a reminder at a specific time."""

    when: datetime
    message: str
    title: str


Method = Union[In, At]


@dataclass(frozen=True, slots=True)
class Options:
    """CLI options."""

    backend: Backend
    method: Method
    verbosity: int
