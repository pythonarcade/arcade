import argparse
import sys

import PIL
import pyglet

import arcade

from .base import BaseCommand


class InfoCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="info",
            description="Print Arcade and System Information",
            help="Print information about the installed Arcade version and system specifications",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    def handle(self, args: argparse.Namespace) -> int:
        window = arcade.Window(visible=False)
        version_str = f"Arcade {arcade.__version__}"
        print()
        print(version_str)
        print("-" * len(version_str))
        print("vendor:", window.ctx.info.VENDOR)
        print("device:", window.ctx.info.RENDERER)
        print("renderer:", window.ctx.info.CTX_INFO)  # type: ignore
        print("python:", sys.version)
        print("platform:", sys.platform)
        print("pyglet version:", pyglet.version)
        print("PIL version:", PIL.__version__)
        return 1
