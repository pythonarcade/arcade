"""CLI command for launching the HitBox Editor."""

from __future__ import annotations

import argparse

from arcade.cli.commands.base import BaseCommand


class HitBoxEditorCommand(BaseCommand):
    """CLI command to launch the HitBox Editor."""

    def __init__(self) -> None:
        super().__init__(
            name="hitbox-editor",
            description="Launch the visual HitBox Editor for creating and editing sprite hitbox regions.",
            help="Visual editor for creating and editing sprite hitbox regions",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "texture",
            nargs="?",
            default=None,
            help="Path to a texture image file to load on startup",
        )
        parser.add_argument(
            "--hitbox",
            default=None,
            help="Path to an existing hitbox JSON file to load",
        )
        parser.add_argument(
            "--width",
            type=int,
            default=1280,
            help="Window width in pixels (default: 1280)",
        )
        parser.add_argument(
            "--height",
            type=int,
            default=720,
            help="Window height in pixels (default: 720)",
        )

    def handle(self, args: argparse.Namespace) -> int:
        from arcade.hitbox_editor import run_editor

        return run_editor(
            texture_path=args.texture,
            hitbox_path=args.hitbox,
            width=args.width,
            height=args.height,
        )
