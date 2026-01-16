"""Tests for backend availability and scheduling."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from remindme import AtBackend, AutoBackend, Backend, SystemdBackend


class TestBackendAvailability:
    """Tests for backend availability checks."""

    @patch("remindme.utils.shutil.which")
    @pytest.mark.parametrize(
        "backend_cls,command",
        [
            (SystemdBackend, "systemd-run"),
            (AtBackend, "at"),
        ],
    )
    def test_backend_available(
        self, mock_which, backend_cls: type[Backend], command: str
    ):
        """Test backend availability checks."""
        mock_which.return_value = f"/usr/bin/{command}"
        assert backend_cls.is_available() is True

    @patch("remindme.utils.shutil.which")
    @pytest.mark.parametrize(
        "backend_cls",
        [SystemdBackend, AtBackend],
    )
    def test_backend_unavailable(self, mock_which, backend_cls: type[Backend]):
        """Test backend unavailability checks."""
        mock_which.return_value = None
        assert backend_cls.is_available() is False

    @patch("remindme.backends.SystemdBackend.is_available")
    @patch("remindme.backends.AtBackend.is_available")
    @pytest.mark.parametrize(
        "systemd_avail,at_avail,expected",
        [
            (True, False, True),
            (False, True, True),
            (False, False, False),
        ],
    )
    def test_auto_availability(
        self, mock_at, mock_systemd, systemd_avail: bool, at_avail: bool, expected: bool
    ):
        """Test AutoBackend availability logic."""
        mock_systemd.return_value = systemd_avail
        mock_at.return_value = at_avail
        assert AutoBackend.is_available() is expected


class TestBackendScheduling:
    """Integration tests for backend scheduling logic."""

    @patch("remindme.utils.subprocess.run")
    @patch("remindme.backends.SystemdBackend.is_available")
    def test_systemd_schedule_in(self, mock_available, mock_run):
        mock_available.return_value = True
        mock_run.return_value = Mock(returncode=0)

        backend = SystemdBackend()
        backend.schedule_in(
            duration=timedelta(minutes=30), title="Test", message="Test message"
        )

        # Verify systemd-run was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "systemd-run" in args
        assert "--user" in args
        assert "--on-active" in args
        assert "30m" in args

    @patch("remindme.utils.subprocess.run")
    @patch("remindme.backends.SystemdBackend.is_available")
    def test_systemd_schedule_at(self, mock_available, mock_run):
        mock_available.return_value = True
        mock_run.return_value = Mock(returncode=0)

        backend = SystemdBackend()
        when = datetime(2026, 1, 16, 15, 0, 0)
        backend.schedule_at(when=when, title="Test", message="Test message")

        # Verify systemd-run was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "systemd-run" in args
        assert "--user" in args
        assert "--on-calendar" in args

    @patch("remindme.utils.subprocess.run")
    @patch("remindme.backends.AtBackend.is_available")
    def test_at_schedule_at(self, mock_available, mock_run):
        mock_available.return_value = True
        mock_run.return_value = Mock(returncode=0)

        backend = AtBackend()
        when = datetime(2026, 1, 16, 15, 0, 0)
        backend.schedule_at(when=when, title="Test", message="Test message")

        # Verify at was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "at"
        assert "-t" in args
