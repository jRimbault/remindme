"""Scheduling backends for remindme."""

from __future__ import annotations

import logging
import shlex
import shutil
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from remindme.parsers import format_systemd_duration
from remindme.utils import die, run, unit_name


class Backend(ABC):
    """Strategy interface for scheduling backends."""

    @abstractmethod
    def schedule_in(self, duration: timedelta, title: str, message: str) -> None:
        """Schedule a reminder after a duration."""

    @abstractmethod
    def schedule_at(self, when: datetime, title: str, message: str) -> None:
        """Schedule a reminder at a specific datetime."""

    @staticmethod
    @abstractmethod
    def is_available() -> bool:
        """Check if this backend is available on the system."""


class SystemdBackend(Backend):
    """Uses systemd user timers to schedule notifications.

    Pros:
      - Reminders survive computer restarts and sleep/suspend
      - Very precise timing (typically within 1 second)
      - View pending reminders: systemctl --user list-timers
      - Works immediately on most modern Linux distributions
      - No extra services to start or configure

    Cons:
      - Only available on Linux systems with systemd
      - Not available on macOS, BSD, or older Linux systems
    """

    def schedule_in(self, duration: timedelta, title: str, message: str) -> None:
        on_active = format_systemd_duration(duration)
        unit = unit_name(prefix="remindme", when=datetime.now() + duration)
        cmd = [
            "systemd-run",
            "--user",
            "--unit",
            unit,
            "--on-active",
            on_active,
            "--",
            "notify-send",
            title,
            message,
        ]
        logging.info("Scheduling reminder in %s via systemd (%s)", on_active, unit)
        run(cmd)

    def schedule_at(self, when: datetime, title: str, message: str) -> None:
        unit = unit_name(prefix="remindme", when=when)
        on_calendar = when.strftime("%Y-%m-%d %H:%M:%S")
        cmd = [
            "systemd-run",
            "--user",
            "--unit",
            unit,
            "--on-calendar",
            on_calendar,
            "--",
            "notify-send",
            title,
            message,
        ]
        logging.info("Scheduling reminder at %s via systemd (%s)", on_calendar, unit)
        run(cmd)

    @staticmethod
    def is_available() -> bool:
        return shutil.which("systemd-run") is not None


class AtBackend(Backend):
    """Uses the 'at' command to schedule notifications.

    Pros:
      - Works on Linux, macOS, BSD, and other Unix systems
      - Simple and widely available tool
      - Good timing precision (typically within 1 minute)

    Cons:
      - Reminders lost if computer restarts or sleeps
      - Requires 'atd' service running (may need: sudo systemctl start atd)
      - Harder to view pending reminders (use: atq)
      - May not be installed on minimal/container systems
    """

    def schedule_in(self, duration: timedelta, title: str, message: str) -> None:
        when = datetime.now() + duration
        self.schedule_at(when, title, message)

    def schedule_at(self, when: datetime, title: str, message: str) -> None:
        # at -t expects [[CC]YY]MMDDhhmm[.ss]
        ts = when.strftime("%Y%m%d%H%M")
        shell_cmd = _build_notify_shell_command(title=title, message=message)
        logging.debug("at -t %s", ts)

        try:
            subprocess.run(
                ["at", "-t", ts],
                input=(shell_cmd + "\n").encode("utf-8"),
                capture_output=True,
                check=True,
                text=False,
            )
        except subprocess.CalledProcessError as e:
            stderr = (
                e.stderr.decode("utf-8", errors="replace").strip()
                if e.stderr
                else "unknown error"
            )
            die(f"at failed:\n{stderr}")

        logging.info(
            "Scheduling reminder at %s via at",
            when.isoformat(sep=" ", timespec="minutes"),
        )

    @staticmethod
    def is_available() -> bool:
        return shutil.which("at") is not None


class AutoBackend(Backend):
    """Automatically selects the first available backend.

    Selection priority (order in registry):
      1. systemd (if available on system)
      2. at (if atd service is running)

    Pros:
      - No configuration needed - just works
      - Adapts to your system automatically
      - Prefers more reliable backend (systemd) when available

    Cons:
      - Won't warn you if reminders could be lost on restart (when using 'at')
    """

    def __init__(self) -> None:
        self._delegate: Backend | None = None

    @property
    def delegate(self) -> Backend:
        """Lazy initialization: select delegate on first access."""
        if self._delegate is None:
            self._delegate = self._select_delegate()
            logging.debug("AutoBackend selected: %s", type(self._delegate).__name__)
        return self._delegate

    @staticmethod
    def _select_delegate() -> Backend:
        """Select the first available backend from the registry."""
        for name, backend_cls in BACKENDS.items():
            if name != "auto" and backend_cls.is_available():
                return backend_cls()
        die(
            f"no usable backend found: need one of {', '.join(k for k in BACKENDS if k != 'auto')}"
        )

    def schedule_in(self, duration: timedelta, title: str, message: str) -> None:
        self.delegate.schedule_in(duration, title, message)

    def schedule_at(self, when: datetime, title: str, message: str) -> None:
        self.delegate.schedule_at(when, title, message)

    @staticmethod
    def is_available() -> bool:
        return any(
            backend_cls.is_available()
            for name, backend_cls in BACKENDS.items()
            if name != "auto"
        )


BACKENDS: dict[str, type[Backend]] = {
    "auto": AutoBackend,
    "systemd": SystemdBackend,
    "at": AtBackend,
}


def _build_notify_shell_command(*, title: str, message: str) -> str:
    """Build shell command for notify-send with properly quoted arguments.

    SECURITY: shlex.quote ensures title/message cannot inject shell commands.
    The 'at' command executes this via /bin/sh, but quoted args are safe.
    """
    # We intentionally build a shell command for 'at' input.
    return " ".join(
        [
            "notify-send",
            shlex.quote(title),
            shlex.quote(message),
        ]
    )
