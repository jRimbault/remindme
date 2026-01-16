"""Utility functions for remindme."""

from __future__ import annotations

import logging
import shlex
import shutil
import subprocess
from datetime import datetime
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from typing import NoReturn


def unit_name(*, prefix: str, when: datetime) -> str:
    """Generate unique systemd unit name from prefix and timestamp.

    Format: {prefix}-YYYYMMDD-HHMMSS-microseconds
    Example: remindme-20260115-150000-123456

    Includes microseconds to prevent collisions when scheduling multiple
    reminders for the same second.

    Args:
        prefix: Unit name prefix
        when: Timestamp for the unit

    Returns:
        Unique systemd unit name
    """
    # systemd unit names can't contain spaces; keep it boring.
    stamp = when.strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stamp}-{when.microsecond:06d}"


def check_notify_send() -> None:
    """Verify notify-send is available on the system.

    Note: notify-send requires DISPLAY (X11) or WAYLAND_DISPLAY environment
    variables to be set. When using systemd-run or at, these may not be
    available in the scheduled environment. Consider using:
    - systemd: --setenv=DISPLAY=:0 --setenv=DBUS_SESSION_BUS_ADDRESS=...
    - at: Ensure atd runs with access to user session bus

    Raises:
        SystemExit: If notify-send is not found
    """
    if not shutil.which("notify-send"):
        die(
            "notify-send not found: install libnotify package\n"
            "  Debian/Ubuntu: sudo apt install libnotify-bin\n"
            "  Fedora/RHEL: sudo dnf install libnotify\n"
            "  Arch: sudo pacman -S libnotify"
        )


def run(cmd: Sequence[str]) -> None:
    """Execute a command and handle common errors.

    Args:
        cmd: Command and arguments to run

    Raises:
        SystemExit: If command fails
    """
    logging.debug("Running: %s", " ".join(map(shlex.quote, cmd)))
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        die(str(e))
    except subprocess.CalledProcessError as e:
        die(f"command failed with exit code {e.returncode}")


def die(msg: str) -> NoReturn:
    """Exit with error message.

    Args:
        msg: Error message to display

    Raises:
        SystemExit: Always
    """
    raise SystemExit(f"error: {msg}")


def verbosity_to_log_level(verbosity: int) -> int:
    """Convert verbosity level to logging level.

    Verbosity scale:
      -2 or less: ERROR
      -1: WARNING (default)
       0: INFO
       1: DEBUG
       2 or more: DEBUG (with potential for future granularity)

    Args:
        verbosity: Verbosity level

    Returns:
        Logging level constant
    """
    error_threshold = -2
    match verbosity:
        case v if v <= error_threshold:
            return logging.ERROR
        case -1:
            return logging.WARNING
        case 0:
            return logging.INFO
        case _:
            return logging.DEBUG
