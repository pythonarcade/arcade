import sys
import tempfile
from unittest import mock

import pytest
from arcade.version import (
    _parse_python_friendly_version,
    _parse_py_version_from_github_ci_file
)


@pytest.mark.parametrize("value, expected", [
    ("3.0.0-dev.1", "3.0.0.dev1"),
    ("3.0.0", "3.0.0"),
    # Edge cases
    ("11.22.333-dev.4444", "11.22.333.dev4444"),
    ("11.22.333", "11.22.333"),
])
class TestParsingWellFormedData:
    def test_parse_python_friendly_version(
            self, value, expected
    ):
        assert _parse_python_friendly_version(value) == expected

    def test_parse_py_version_from_github_ci_file(
            self, value, expected
    ):

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(value)
            f.close()

            assert _parse_py_version_from_github_ci_file(
                f.name
            ) == expected


def test_parse_py_version_from_github_ci_file_returns_zeroes_on_errors():
    fake_stderr = mock.MagicMock(sys.stderr)
    assert _parse_py_version_from_github_ci_file(
        "FILEDOESNOTEXIST", write_errors_to=fake_stderr
    ) == "0.0.0"


