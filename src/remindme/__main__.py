"""Main entry point for remindme."""

from __future__ import annotations

import logging
import sys

from remindme.cli import parse_args
from remindme.models import At, In, Options
from remindme.utils import check_notify_send, verbosity_to_log_level


def main(opt: Options) -> int:
    """Run remindme with the given options.

    Args:
        opt: Parsed CLI options

    Returns:
        Exit code (0 for success)
    """
    logging.basicConfig(
        level=verbosity_to_log_level(opt.verbosity),
        format="%(levelname)s: %(message)s",
    )

    check_notify_send()

    logging.debug("Selected backend: %s", type(opt.backend).__name__)

    match opt.method:
        case In(duration=duration, message=msg, title=title):
            opt.backend.schedule_in(duration=duration, title=title, message=msg)
        case At(when=when, message=msg, title=title):
            opt.backend.schedule_at(when=when, title=title, message=msg)

    return 0


def script() -> None:
    """CLI entry point."""
    raise SystemExit(main(parse_args(sys.argv[1:])))


if __name__ == "__main__":
    script()
