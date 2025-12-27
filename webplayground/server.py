#! /usr/bin/env python

import importlib
import os
import pkgutil
import shutil
import subprocess
import sys
from pathlib import Path

from bottle import route, run, static_file, template  # type: ignore

from arcade import examples

here = Path(__file__).parent.resolve()

path_arcade = Path("../")
arcade_wheel_filename = "arcade-4.0.0.dev1-py3-none-any.whl"
path_arcade_wheel = path_arcade / "dist" / arcade_wheel_filename


def find_modules(module):
    path_list = []
    spec_list = []
    for importer, modname, ispkg in pkgutil.walk_packages(module.__path__):
        import_path = f"{module.__name__}.{modname}"
        if ispkg:
            pkg = importlib.import_module(import_path)
            path_list.extend(find_modules(pkg))
        else:
            path_list.append(import_path)
    for spec in spec_list:
        del sys.modules[spec.name]
    return path_list


@route("/static/<filepath:re:.*\.whl>")
def whl(filepath):
    return static_file(filepath, root="./")


@route("/")
def index():
    examples_list = find_modules(examples)
    return template("index.tpl", examples=examples_list)


@route("/example")
@route("/example/<name>")
def example(name="platform_tutorial.01_open_window"):
    return template(
        "example.tpl",
        name=name,
        arcade_wheel=arcade_wheel_filename,
    )


def main():
    # Get us in this file's parent directory
    os.chdir(here)

    # Go to arcade and build a wheel
    os.chdir(path_arcade)
    subprocess.run(["uv", "build"])
    os.chdir(here)
    shutil.copy(path_arcade_wheel, f"./{arcade_wheel_filename}")

    run(host="localhost", port=8000)


if __name__ == "__main__":
    main()
