import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

import arcade.version as version_module
from arcade.version import _parse_py_version_from_file, _parse_python_friendly_version


def test_default_version_file_is_loaded():
    version_path = Path(version_module.__file__).with_name("_VERSION")

    assert version_path.is_file()
    assert _parse_py_version_from_file(version_path) == version_module.VERSION


def test_package_data_names_do_not_collide_with_modules_when_casefolded():
    package_dir = Path(version_module.__file__).parent
    importable_names = {
        path.stem.casefold() for path in package_dir.iterdir() if path.suffix == ".py"
    }
    importable_names.update(
        path.name.casefold()
        for path in package_dir.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )
    data_names = {
        path.name.casefold()
        for path in package_dir.iterdir()
        if path.is_file() and path.suffix != ".py"
    }

    collisions = importable_names & data_names
    assert not collisions, f"Case-insensitive package path collisions: {sorted(collisions)}"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("3.0.0.dev1", "3.0.0.dev1"),
        ("3.0.0", "3.0.0"),
        # Edge cases
        ("11.22.333.dev4444", "11.22.333.dev4444"),
        ("11.22.333", "11.22.333"),
        ("111.2222.3333rc0", "111.2222.3333rc0"),
    ],
)
class TestParsingWellFormedData:
    def test_parse_python_friendly_version(self, value, expected):
        assert _parse_python_friendly_version(value) == expected

    def test_parse_py_version_from_file(self, value, expected):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(value)
            f.close()

            assert _parse_py_version_from_file(f.name) == expected


@pytest.mark.parametrize(
    "bad_value",
    (
        "",
        "This string is not a version number at all!"
        # Malformed version numbers
        "3",
        "3.",
        "3.1",
        "3.1.",
        "3.1.2.",
        "3.1.0.dev",
        "3.1.0-dev."
        "3.1.0-dev.4"  # No longer valid input
        # Hex is not valid in version numbers
        "A",
        "3.A.",
        "3.1.A",
        "3.1.0.A",
        "3.1.0-dev.A",
        # Can't be both a release candidate and a dev preview
        "3.1.0.dev4rc1",
    ),
)
def test_parse_python_friendly_version_raises_value_errors(bad_value):
    with pytest.raises(ValueError):
        _parse_python_friendly_version(bad_value)


@pytest.mark.parametrize("bad_type", (None, 0xBAD, 0.1234, (3, 1, 0), ("3", "10")))
def test_parse_python_friendly_version_raises_typeerror_on_bad_values(bad_type):
    with pytest.raises(TypeError):
        _parse_python_friendly_version(bad_type)  # type: ignore  # Type mistmatch is the point


def test_parse_py_version_from_file_returns_zeroes_on_errors():
    fake_stderr = mock.MagicMock(sys.stderr)
    assert _parse_py_version_from_file("FILEDOESNOTEXIST", write_errors_to=fake_stderr) == "0.0.0"
