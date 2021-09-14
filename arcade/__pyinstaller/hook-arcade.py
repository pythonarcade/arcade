"""
"Hook" file for pyinstaller - enables Arcade to be easily packaged with PyInstaller.

Docs: https://pyinstaller.readthedocs.io/en/stable/hooks.html
Official Sample: https://github.com/pyinstaller/hooksample

Note: See setup.cfg for entry points that enable this hook file to be found

For a walk through of building an Arcade application with pyinstaller see:
https://api.arcade.academy/en/latest/tutorials/bundling_with_pyinstaller/index.html
"""
from pathlib import Path

import arcade
import pymunk
from PyInstaller.compat import is_darwin, is_unix, is_win

pymunk_path = Path(pymunk.__file__).parent
arcade_path = Path(arcade.__file__).parent

datas = [
    (
        arcade_path / "resources",
        "./arcade/resources",
    ),
]

if is_win:
    binaries = [
        (pymunk_path / "_chipmunk.pyd", "."),
    ]
elif is_darwin:
    binaries = [
        (pymunk_path / "_chipmunk.abi3.so", "."),
        (arcade_path / "lib", "./arcade/lib"),
    ]
elif is_unix:
    binaries = [
        (pymunk_path / "_chipmunk.abi3.so", "."),
    ]
else:
    raise NotImplementedError(
        "You are running on an unsupported operating system. "
        "Only Linux, Mac, and Windows are supported."
    )
