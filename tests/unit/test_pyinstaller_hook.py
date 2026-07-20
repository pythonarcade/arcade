import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

import arcade


def test_version_data_is_bundled_at_package_root(monkeypatch: pytest.MonkeyPatch):
    pyinstaller = ModuleType("PyInstaller")
    compat = ModuleType("PyInstaller.compat")
    compat.is_darwin = False
    compat.is_unix = True
    compat.is_win = False
    monkeypatch.setitem(sys.modules, "PyInstaller", pyinstaller)
    monkeypatch.setitem(sys.modules, "PyInstaller.compat", compat)

    package_dir = Path(arcade.__file__).parent
    hook_globals = runpy.run_path(package_dir / "__pyinstaller" / "hook-arcade.py")
    bundled_version_paths = [
        Path(destination) / Path(source).name
        for source, destination in hook_globals["datas"]
        if Path(source).name == "_VERSION"
    ]

    assert bundled_version_paths == [Path("arcade/_VERSION")]
