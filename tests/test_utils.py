"""Tests for utility functions."""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from remindme.utils import check_notify_send, run, unit_name, verbosity_to_log_level


class TestUnitName:
    """Tests for unit_name() function."""

    def test_basic_format(self):
        dt = datetime(2026, 1, 15, 14, 30, 45, 123456)
        result = unit_name(prefix="remindme", when=dt)
        assert result == "remindme-20260115-143045-123456"

    def test_collision_prevention(self):
        # Two reminders in the same second have different microseconds
        dt1 = datetime(2026, 1, 15, 14, 30, 45, 0)
        dt2 = datetime(2026, 1, 15, 14, 30, 45, 1)

        name1 = unit_name(prefix="remindme", when=dt1)
        name2 = unit_name(prefix="remindme", when=dt2)

        assert name1 != name2
        assert name1 == "remindme-20260115-143045-000000"
        assert name2 == "remindme-20260115-143045-000001"

    def test_different_prefix(self):
        dt = datetime(2026, 1, 15, 14, 30, 45, 123456)
        result = unit_name(prefix="test", when=dt)
        assert result.startswith("test-")


class TestCheckNotifySend:
    """Tests for check_notify_send() function."""

    @patch("remindme.utils.shutil.which")
    def test_notify_send_available(self, mock_which):
        mock_which.return_value = "/usr/bin/notify-send"
        # Should not raise
        check_notify_send()

    @patch("remindme.utils.shutil.which")
    def test_notify_send_missing(self, mock_which):
        mock_which.return_value = None
        with pytest.raises(SystemExit, match="notify-send not found"):
            check_notify_send()


class TestRun:
    """Tests for run() function."""

    @patch("remindme.utils.subprocess.run")
    def test_successful_command(self, mock_run):
        mock_run.return_value = Mock(returncode=0)
        # Should not raise
        run(["echo", "test"])
        mock_run.assert_called_once_with(["echo", "test"], check=True)

    @patch("remindme.utils.subprocess.run")
    def test_command_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError("command not found")
        with pytest.raises(SystemExit, match="command not found"):
            run(["nonexistent"])

    @patch("remindme.utils.subprocess.run")
    def test_command_failed(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, ["false"])
        with pytest.raises(SystemExit, match="exit code 1"):
            run(["false"])


class TestVerbosityToLogLevel:
    """Tests for verbosity_to_log_level() function."""

    def test_error_level(self):
        assert verbosity_to_log_level(-2) == logging.ERROR
        assert verbosity_to_log_level(-3) == logging.ERROR

    def test_warning_level(self):
        assert verbosity_to_log_level(-1) == logging.WARNING

    def test_info_level(self):
        assert verbosity_to_log_level(0) == logging.INFO

    def test_debug_level(self):
        assert verbosity_to_log_level(1) == logging.DEBUG
        assert verbosity_to_log_level(2) == logging.DEBUG
