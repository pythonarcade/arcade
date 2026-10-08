"""Shared render scenes for the pyglet 3.0.dev6 migration reference-image
comparison harness (SC-003, FR-011).

Both the pre-migration baseline capture (see ``generate_baseline.py``) and the
post-migration comparison test (``test_dev6_reference_images.py``) render
these exact same scenes, so any measured difference reflects a real
rendering change rather than a scene mismatch between the two runs.
"""

from __future__ import annotations

from collections.abc import Callable

import arcade
from arcade import camera
from arcade.types import LBWH

SCENE_WIDTH = 800
SCENE_HEIGHT = 600

#: Scene name -> render function. Iterate this mapping to keep the baseline
#: capture script and the comparison test in sync automatically.
SCENES: dict[str, Callable[[arcade.Window], None]] = {}


def _register(name):
    def decorator(func):
        SCENES[name] = func
        return func

    return decorator


def _reset(window: arcade.Window) -> None:
    window.set_size(SCENE_WIDTH, SCENE_HEIGHT)
    # A resize needs a pass through the event queue before the window's
    # framebuffer/viewport actually reflect the new size (see conftest.py's
    # prepare_window(), which does the same) — without this, default_camera
    # recomputes its projection against the stale pre-resize viewport.
    window.dispatch_pending_events()
    window.default_camera.use()
    window.clear(color=arcade.color.AMAZON)


@_register("sprite")
def render_sprite_scene(window: arcade.Window) -> None:
    """A single sprite drawn at a fixed position under the default camera."""
    _reset(window)
    sprite = arcade.Sprite(":resources:images/items/gold_1.png", center_x=400, center_y=300)
    sprite_list = arcade.SpriteList()
    sprite_list.append(sprite)
    sprite_list.draw()


@_register("shape")
def render_shape_scene(window: arcade.Window) -> None:
    """A filled rectangle and a filled circle drawn under the default camera."""
    _reset(window)
    arcade.draw_rect_filled(LBWH(150, 150, 200, 150), arcade.color.BLUE)
    arcade.draw_circle_filled(550, 400, 80, arcade.color.YELLOW_ORANGE)


@_register("orthographic_camera")
def render_orthographic_camera_scene(window: arcade.Window) -> None:
    """The shape scene viewed through an offset/zoomed OrthographicProjector."""
    _reset(window)
    ortho = camera.OrthographicProjector(
        window=window,
        view=camera.CameraData(
            (300.0, 250.0, 0.0),  # Position: offset from center
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward
            1.5,  # Zoom
        ),
    )
    with ortho.activate():
        arcade.draw_rect_filled(LBWH(150, 150, 200, 150), arcade.color.BLUE)
        arcade.draw_circle_filled(550, 400, 80, arcade.color.YELLOW_ORANGE)
    window.default_camera.use()


@_register("perspective_camera")
def render_perspective_camera_scene(window: arcade.Window) -> None:
    """The shape scene viewed through a pulled-back PerspectiveProjector.

    Pulled back far enough (Z=520, with a widened far plane of 1000 — the
    default far plane is only 100) that the full 800x600 scene falls inside
    the 60-degree-FOV frustum instead of being far-plane-clipped or cropped
    to a sliver.
    """
    _reset(window)
    persp = camera.PerspectiveProjector(
        window=window,
        view=camera.CameraData(
            (400.0, 300.0, 520.0),  # Position: pulled back along +Z
            (0.0, 1.0, 0.0),  # Up
            (0.0, 0.0, -1.0),  # Forward: looking back at the Z=0 plane
            1.0,  # Zoom
        ),
        projection=camera.PerspectiveProjectionData(
            SCENE_WIDTH / SCENE_HEIGHT,  # Aspect
            60,  # Field of view
            1.0,  # Near
            1000.0,  # Far — widened so content at Z=0 isn't far-plane-clipped
        ),
    )
    with persp.activate():
        arcade.draw_rect_filled(LBWH(150, 150, 200, 150), arcade.color.BLUE)
        arcade.draw_circle_filled(550, 400, 80, arcade.color.YELLOW_ORANGE)
    window.default_camera.use()
