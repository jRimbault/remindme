"""Tests for dataclass structures."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from remindme import At, Backend, In, Options


class TestDataClasses:
    """Tests for dataclass structures."""

    def test_in_immutable(self):
        method = In(duration=timedelta(minutes=30), message="test", title="Test")
        with pytest.raises(AttributeError):
            method.duration = timedelta(hours=1)  # type: ignore

    def test_at_immutable(self):
        method = At(when=datetime.now(), message="test", title="Test")
        with pytest.raises(AttributeError):
            method.when = datetime.now()  # type: ignore

    def test_options_immutable(self):
        mock_backend = Mock(spec=Backend)
        method = In(duration=timedelta(minutes=30), message="test", title="Test")
        opts = Options(backend=mock_backend, method=method, verbosity=-1)
        with pytest.raises(AttributeError):
            opts.verbosity = 0  # type: ignore
