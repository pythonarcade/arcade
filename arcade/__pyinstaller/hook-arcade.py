"""
"Hook" file for pyinstaller - enables Arcade to be easily packaged with PyInstaller.

Docs: https://pyinstaller.readthedocs.io/en/stable/hooks.html
Official Sample: https://github.com/pyinstaller/hooksample

Note: See setup.cfg for entry points that enable this hook file to be found

For people who want to modify hook-arcade.py from a git checkout of Arcade,
here is a sequence of steps that will let you test your changes:

    cd arcade  # set top dir of repo as your current working directory
    venv\Scripts\activate  # activate your venv
    # edit setup.cfg or hook-arcade.py with your changes
    pip uninstall arcade
    pip install .
    pyinstaller arcade\examples\starting_template_simple.py
    dist\starting_template_simple\starting_template_simple.exe

Simply put, after you edit setup.cfg or hook-arcade.py, you will need to uninstall and reinstall arcade.

NOTE: The sequence of steps above do NOT support editable installs of Arcade (ex: `pip install -e .`) because
the paths to binary files can be slightly different.
"""
from pathlib import Path
from PyInstaller.compat import is_win, is_darwin, is_unix  # type: ignore

hook_path = Path(__file__)

if is_win:
    datas = [
        (hook_path.parent.parent.joinpath("resources"), "./arcade/resources"),
    ]

    binaries = [
        (hook_path.parent.parent.parent.joinpath("pymunk/chipmunk.dll"), "."),
        (hook_path.parent.parent.joinpath("soloud/soloud*.dll"), "./arcade/soloud"),
    ]

elif is_darwin:
    raise NotImplementedError("Arcade does not support pyinstaller on Mac yet")

elif is_unix:
    datas = [
        (hook_path.parent.parent.joinpath("resources"), "./arcade/resources"),
    ]

    binaries = [
        (hook_path.parent.parent.parent.joinpath("pymunk/libchipmunk.so"), "."),
        (hook_path.parent.parent.joinpath("soloud/libsoloud.so"), "./arcade/soloud"),
    ]
