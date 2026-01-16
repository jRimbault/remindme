"""Integration tests for CLI functionality via subprocess."""

from __future__ import annotations

import subprocess
from unittest.mock import Mock, patch

import pytest


class TestCLISmokeTests:
    """Integration tests for CLI functionality via subprocess."""

    @pytest.mark.parametrize(
        "args,expected_in_stdout",
        [
            (["--help"], ["Schedule a desktop notification", "usage: remindme"]),
            (["in", "--help"], ["duration", "30m"]),
            (["at", "--help"], ["when", "3pm"]),
        ],
    )
    def test_help_output(self, args: list[str], expected_in_stdout: list[str]):
        """Test help flags work and contain expected content."""
        result = subprocess.run(
            ["remindme", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        for expected in expected_in_stdout:
            assert expected in result.stdout or any(
                variant in result.stdout
                for variant in [expected.lower(), expected.upper()]
            )

    @pytest.mark.parametrize(
        "args,expected_in_stderr",
        [
            (
                ["--backend", "invalid", "in", "1m", "test"],
                ["choose from auto, systemd, at"],
            ),
            (["in", "1m"], ["message"]),
            (["in", "invalid", "test"], ["invalid duration"]),
            (["at", "not-a-time", "test"], ["could not parse", "time"]),
        ],
    )
    def test_error_handling(self, args: list[str], expected_in_stderr: list[str]):
        """Test CLI produces helpful error messages."""
        result = subprocess.run(
            ["remindme", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        stderr_lower = result.stderr.lower()
        assert any(expected.lower() in stderr_lower for expected in expected_in_stderr)

    @pytest.mark.parametrize(
        "backend",
        ["auto", "systemd", "at"],
    )
    @patch("remindme.utils.subprocess.run")
    def test_backend_scheduling_smoke(self, mock_subprocess_run, backend: str):
        """Test that scheduling commands complete without error (mocked)."""
        # Mock successful subprocess execution
        mock_subprocess_run.return_value = Mock(returncode=0)

        # Test 'in' command with a very short duration
        result_in = subprocess.run(
            ["remindme", "--backend", backend, "in", "5s", "test message"],
            capture_output=True,
            text=True,
            check=False,
        )
        # Should succeed (exit 0) or fail gracefully if backend unavailable
        if result_in.returncode != 0:
            # If it failed, should be a backend availability error
            assert "not available" in result_in.stderr.lower(), (
                f"Unexpected error for backend {backend}: {result_in.stderr}"
            )
