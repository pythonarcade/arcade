"""
"Hook" file for pyinstaller - enables Arcade to be easily packaged with PyInstaller.

Docs: https://pyinstaller.readthedocs.io/en/stable/hooks.html
Official Sample: https://github.com/pyinstaller/hooksample

Note: See setup.cfg for entry points that enable this hook file to be found

For a walk through of building an Arcade application with pyinstaller see:
https://api.arcade.academy/en/latest/tutorials/bundling_with_pyinstaller/index.html
"""

from importlib.util import find_spec
from pathlib import Path

from PyInstaller.compat import is_darwin, is_unix, is_win

# check for supported operating systems
if not is_win and not is_darwin and not is_unix:
    raise NotImplementedError(
        "You are running on an unsupported operating system. "
        "Only Linux, Mac, and Windows are supported."
    )

datas = []
binaries = []

# Add Arcade resources
arcade_spec = find_spec("arcade")
if arcade_spec is None or arcade_spec.origin is None:
    raise ImportError("Arcade is not installed. Cannot continue.")

arcade_path = Path(arcade_spec.origin).parent
datas.extend(
    [
        (
            arcade_path / "resources" / "system",
            "./arcade/resources/system",
        ),
        (
            arcade_path / "VERSION",
            "./arcade/VERSION",
        ),
    ]
)

if is_darwin:
    binaries.append((arcade_path / "lib", "./arcade/lib"))

# Add Pymunk resources
pymunk_spec = find_spec("pymunk")
if pymunk_spec is not None and pymunk_spec.origin is not None:
    pymunk_path = Path(pymunk_spec.origin).parent

    if is_win:
        binaries.append((pymunk_path / "_chipmunk.pyd", "."))
    elif is_darwin:
        binaries.append((pymunk_path / "_chipmunk.abi3.so", "."))
    elif is_unix:
        binaries.append((pymunk_path / "_chipmunk.abi3.so", "."))
else:
    print("Pymunk is not available. Skipping Pymunk resources.")
