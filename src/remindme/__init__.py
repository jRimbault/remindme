"""remindme - Schedule desktop notification reminders from the command line."""

from __future__ import annotations

__version__ = "0.1.0"

from remindme.backends import AtBackend, AutoBackend, Backend, SystemdBackend
from remindme.models import At, In, Method, Options

__all__ = [
    "At",
    "AtBackend",
    "AutoBackend",
    "Backend",
    "In",
    "Method",
    "Options",
    "SystemdBackend",
]
