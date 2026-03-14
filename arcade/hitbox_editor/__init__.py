"""HitBox Editor - A visual tool for creating and editing sprite hitbox regions."""

from __future__ import annotations

from pathlib import Path


def run_editor(
    texture_path: str | Path | None = None,
    hitbox_path: str | Path | None = None,
    width: int = 1280,
    height: int = 720,
) -> int:
    """Launch the HitBox Editor application.

    Args:
        texture_path: Optional path to a texture image file to load on startup.
        hitbox_path: Optional path to an existing hitbox JSON file to load.
        width: Window width in pixels.
        height: Window height in pixels.

    Returns:
        Exit code (0 for success).
    """
    import arcade
    from arcade.hitbox_editor.app import HitBoxEditorView

    window = arcade.Window(width, height, "HitBox Editor", resizable=True)
    view = HitBoxEditorView(texture_path=texture_path, hitbox_path=hitbox_path)
    window.show_view(view)
    arcade.run()
    return 0
