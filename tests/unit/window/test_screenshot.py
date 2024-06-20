"""Make sure window screenshots work.

We use pytests's ``tmp_path`` instead of :py:mod:`tempdir` or manually
creating a temp dir through :py:mod:`os` or other modules. The
``tmp_path`` fixture passes a :py:class:`~pathlib.Path` of a temp dir
unique to the test invocation to all tests with a ``tmp_path`` argument.

See https://docs.pytest.org/en/8.0.x/tmpdir.html#the-tmp-path-fixture

"""
import arcade
from pathlib import Path


def test_save_screenshot_window(window: arcade.Window, tmp_path: Path):
    # Test Path support
    file_1 = tmp_path / "screen.png"
    assert not file_1.exists()
    window.save_screenshot(file_1)
    assert file_1.is_file()

    # Test str support
    file_2 = tmp_path / "screen2.png"
    assert not file_2.exists()
    window.save_screenshot(str(file_2))
    assert file_2.is_file()


def test_command_with_location(window: arcade.Window, tmp_path):
    # Test Path support
    file_1 = tmp_path / "screen.png"
    assert not file_1.exists()
    window.save_screenshot(file_1)
    assert file_1.is_file()

    # Test str support
    file_2 = tmp_path / "screen2.png"
    assert not file_2.exists()
    window.save_screenshot(str(file_2))
    assert file_2.is_file()
