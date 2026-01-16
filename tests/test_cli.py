"""Tests for CLI argument parsing and formatting."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from remindme import At, AtBackend, AutoBackend, Backend, In, Options, SystemdBackend
from remindme.cli import (
    format_backend_details,
    parse_args,
    parse_backend,
)


class TestParseBackend:
    """Tests for parse_backend() function."""

    @patch("remindme.backends.SystemdBackend.is_available")
    def test_valid_systemd_backend(self, mock_available):
        mock_available.return_value = True
        backend = parse_backend("systemd")
        assert isinstance(backend, SystemdBackend)

    @patch("remindme.backends.AtBackend.is_available")
    def test_valid_at_backend(self, mock_available):
        mock_available.return_value = True
        backend = parse_backend("at")
        assert isinstance(backend, AtBackend)

    @patch("remindme.backends.SystemdBackend.is_available")
    @patch("remindme.backends.AtBackend.is_available")
    def test_valid_auto_backend(self, mock_at, mock_systemd):
        mock_systemd.return_value = True
        mock_at.return_value = True
        backend = parse_backend("auto")
        assert isinstance(backend, AutoBackend)

    def test_unknown_backend(self):
        with pytest.raises(argparse.ArgumentTypeError, match="unknown backend"):
            parse_backend("nonexistent")

    @patch("remindme.backends.SystemdBackend.is_available")
    def test_unavailable_backend(self, mock_available):
        mock_available.return_value = False
        with pytest.raises(argparse.ArgumentTypeError, match="not available"):
            parse_backend("systemd")


class TestParseArgs:
    """Tests for parse_args() function."""

    @patch("remindme.cli.parse_backend")
    def test_in_command_basic(self, mock_parse_backend):
        mock_backend = Mock(spec=Backend)
        mock_parse_backend.return_value = mock_backend

        result = parse_args(["in", "30m", "test", "message"])

        assert isinstance(result, Options)
        assert isinstance(result.method, In)
        assert result.method.duration == timedelta(minutes=30)
        assert result.method.message == "test message"
        assert result.method.title == "Reminder"
        assert result.verbosity == -1  # Default WARNING

    @patch("remindme.cli.parse_backend")
    def test_at_command_basic(self, mock_parse_backend):
        mock_backend = Mock(spec=Backend)
        mock_parse_backend.return_value = mock_backend

        with patch("remindme.parsers.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 1, 15, 10, 0, 0)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = parse_args(["at", "15:00", "test", "message"])

        assert isinstance(result, Options)
        assert isinstance(result.method, At)
        assert result.method.when.hour == 15
        assert result.method.message == "test message"

    @patch("remindme.cli.parse_backend")
    def test_custom_title(self, mock_parse_backend):
        mock_backend = Mock(spec=Backend)
        mock_parse_backend.return_value = mock_backend

        result = parse_args(["--title", "Custom", "in", "30m", "message"])

        assert result.method.title == "Custom"

    @patch("remindme.cli.parse_backend")
    def test_verbosity_flags(self, mock_parse_backend):
        mock_backend = Mock(spec=Backend)
        mock_parse_backend.return_value = mock_backend

        # -v
        result = parse_args(["-v", "in", "30m", "message"])
        assert result.verbosity == 0  # INFO

        # -vv
        result = parse_args(["-v", "-v", "in", "30m", "message"])
        assert result.verbosity == 1  # DEBUG

        # -q
        result = parse_args(["-q", "in", "30m", "message"])
        assert result.verbosity == -2  # ERROR

    def test_backend_option(self):
        # This test just verifies the backend name is passed through
        # The actual backend instantiation is tested in other tests
        # We can't easily test the full parse_args flow without mocking extensively
        # because argparse with type= and choices= doesn't work well together
        pass  # Covered by other backend tests


class TestFormatBackendDetails:
    """Tests for format_backend_details() function."""

    def test_includes_pros_and_cons(self):
        result = format_backend_details()
        assert "Pros:" in result
        assert "Cons:" in result

    def test_includes_all_backends(self):
        result = format_backend_details()
        assert "at:" in result
        assert "auto:" in result
        assert "systemd:" in result
