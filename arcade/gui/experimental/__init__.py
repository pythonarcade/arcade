"""Contains experimental GUI elements.

The API of these components may change within minor version updates.
No Deprecation warnings are given for changes in this module.
"""

from arcade.gui import UIManager

from arcade.gui.experimental.scroll_area import UIScrollArea
from arcade.gui.experimental.password_input import UIPasswordInput
from arcade.gui.experimental.animate import Animation, rel
from arcade.gui.experimental.group import UIRenderGroup, UIAnimatedGroup
from arcade.gui.experimental.transition import (
    TransitionBase,
    EventTransitionBase,
    TransitionAttr,
    TransitionAttrIncr,
    TransitionAttrSet,
    TransitionChain,
    TransitionParallel,
    TransitionDelay,
)


def pixelated_ui():
    """
    Set the UI to be pixelated, with no text anti-aliasing and nearest-neighbor
    font filtering. This is useful for pixel-art games that want to maintain a
    pixelated look for their UI.

    This will take effect to any text within the game and has to be activated before
    any text or UIManager is created.

    (Best Practices: within main function, before creating the window.)
    """
    import pyglet

    pyglet.options.text_antialiasing = False
    pyglet.font.base.Font.texture_min_filter = pyglet.gl.GL_NEAREST
    pyglet.font.base.Font.texture_mag_filter = pyglet.gl.GL_NEAREST

    UIManager._pixelated = True


__all__ = [
    "UIScrollArea",
    "UIPasswordInput",
    "UIRenderGroup",
    "UIAnimatedGroup",
    "Animation",
    "rel",
    "TransitionBase",
    "EventTransitionBase",
    "TransitionAttr",
    "TransitionAttrIncr",
    "TransitionAttrSet",
    "TransitionChain",
    "TransitionParallel",
    "TransitionDelay",
    "pixelated_ui",
]
