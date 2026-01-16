"""CLI argument parsing for remindme."""

from __future__ import annotations

import argparse
from typing import Sequence

from remindme.backends import BACKENDS, Backend
from remindme.models import At, In, Method, Options
from remindme.parsers import parse_duration, parse_when
from remindme.utils import die


def parse_backend(name: str) -> Backend:
    """Parse backend name and return an instantiated Backend.

    Args:
        name: Backend name from user input (e.g., "auto", "systemd", "at")

    Returns:
        Instantiated Backend object ready for scheduling

    Raises:
        argparse.ArgumentTypeError: If backend unknown or unavailable
    """
    if name not in BACKENDS:
        raise argparse.ArgumentTypeError(
            f"unknown backend '{name}': choose from {', '.join(BACKENDS.keys())}"
        )

    backend_cls = BACKENDS[name]
    if not backend_cls.is_available():
        raise argparse.ArgumentTypeError(
            f"backend '{name}' is not available on this system"
        )

    return backend_cls()


def format_backend_details() -> str:
    """Generate detailed backend documentation for epilog."""
    lines: list[str] = []
    for name, backend_cls in BACKENDS.items():
        doc = backend_cls.__doc__ or ""
        if not doc:
            continue
        lines.append(f"  {name}:")
        # Skip first line (already in short help), process rest
        for line in doc.strip().split("\n")[1:]:
            if line.strip():
                lines.append(f"    {line}")
        lines.append("")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> Options:
    """Parse command-line arguments.

    Args:
        argv: Command-line arguments (without program name)

    Returns:
        Parsed options

    Raises:
        SystemExit: If arguments are invalid
    """
    epilog = f"""
Backend Details:
{format_backend_details()}
Examples:
  # Remind me in 30 minutes
  remindme in 30m "Take a break"

  # Remind me at 3pm today
  remindme at 3pm "Meeting with team"

  # Remind me tomorrow at 9am with custom title
  remindme --title "Morning Task" at "2026-01-16 09:00" "Review pull requests"

  # Use specific backend with verbose output
  remindme -vv --backend systemd in 1h "Check deployment"
"""

    p = argparse.ArgumentParser(
        prog="remindme",
        description="Schedule a desktop notification reminder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    p.add_argument(
        "--backend",
        type=str,
        choices=list(BACKENDS.keys()),
        default="auto",
        help="Scheduler backend to use (default: auto)",
    )
    p.add_argument(
        "--title",
        default="Reminder",
        help="Notification title (default: Reminder).",
    )
    verbosity_group = p.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v: INFO, -vv: DEBUG).",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Decrease verbosity (-q: ERROR, -qq: silence non-critical).",
    )

    sub = p.add_subparsers(dest="command", required=True)

    p_in = sub.add_parser("in", help="Remind after a delay, e.g. 30m, 2h, 45s, 1d.")
    p_in.add_argument(
        "duration", type=parse_duration, help="Delay like 30m / 2h / 45s / 1d."
    )
    p_in.add_argument("message", nargs=argparse.REMAINDER, help="Reminder message.")

    p_at = sub.add_parser(
        "at", help="Remind at a time, e.g. 3pm, 15:00, or a full datetime."
    )
    p_at.add_argument(
        "when", type=parse_when, help="Time like 3pm / 15:00 / 2026-01-15 15:00."
    )
    p_at.add_argument("message", nargs=argparse.REMAINDER, help="Reminder message.")

    ns = p.parse_args(list(argv))

    # Calculate verbosity: default is -1 (WARN), -v increases, -q decreases
    verbosity = -1 + ns.verbose - ns.quiet

    # Resolve backend if using default
    backend = parse_backend(ns.backend) if isinstance(ns.backend, str) else ns.backend

    title = ns.title
    method: Method
    if ns.command == "in":
        msg = " ".join(ns.message).strip()
        if not msg:
            die("message is required")
        method = In(duration=ns.duration, message=msg, title=title)
    elif ns.command == "at":
        msg = " ".join(ns.message).strip()
        if not msg:
            die("message is required")
        method = At(when=ns.when, message=msg, title=title)
    else:
        die(f"unknown command: {ns.command}")

    return Options(
        backend=backend,
        method=method,
        verbosity=verbosity,
    )
