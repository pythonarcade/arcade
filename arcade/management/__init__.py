from pathlib import Path
import shutil
import sys
import arcade

EXAMPLE_PATH = Path(__file__).parent.parent.resolve() / "examples"


def execute_from_command_line():
    if len(sys.argv) == 1:
        show_info()
        return

    command = sys.argv[1]
    if command == "startproject":
        start_project(sys.argv[2])
    else:
        print("Unsupported command")


def show_info():
    window = arcade.Window()
    version_str = f"Arcade {arcade.__version__}"
    print()
    print(version_str)
    print('-' * len(version_str))
    print('vendor:', window.ctx.info.VENDOR)
    print('renderer:', window.ctx.info.RENDERER)
    print('version:', window.ctx.gl_version)
    print('python:', sys.version)
    print('platform:', sys.platform)


def start_project(path_str: str):
    path = Path(path_str)
    if path.exists():
        print("File already exists")

    shutil.copy(EXAMPLE_PATH / "starting_template.py", path)
    print("Created", path)
