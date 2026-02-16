#! /usr/bin/env python

import importlib
import os
import pkgutil
import shutil
import subprocess
import sys
from pathlib import Path

import bottle
from bottle import route, run, static_file, template  # type: ignore

from arcade import examples

# Disable template caching for development
bottle.TEMPLATES.clear()
bottle.debug(True)

here = Path(__file__).parent.resolve()

path_arcade = Path("../")
arcade_wheel_filename = "arcade-4.0.0.dev3-py3-none-any.whl"
path_arcade_wheel = path_arcade / "dist" / arcade_wheel_filename

# Directory for local test scripts
local_scripts_dir = here / "local_scripts"
local_scripts_dir.mkdir(exist_ok=True)


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


@route(r"/static/<filepath:re:.*\.whl>")
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


@route("/local")
def local_index():
    """List available local scripts"""
    local_scripts = []
    if local_scripts_dir.exists():
        for script in local_scripts_dir.glob("*.py"):
            local_scripts.append(script.stem)
    return template("local.tpl", scripts=local_scripts)


@route("/local/<script_name>")
def local_script(script_name):
    """Run a local script"""
    return template(
        "local_run.tpl",
        script_name=script_name,
        arcade_wheel=arcade_wheel_filename,
    )


@route("/local_scripts/<filename>")
def serve_local_script(filename):
    """Serve local script files with no-cache headers"""
    from bottle import response

    response.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
    response.set_header("Pragma", "no-cache")
    response.set_header("Expires", "0")
    return static_file(filename, root=local_scripts_dir)


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
