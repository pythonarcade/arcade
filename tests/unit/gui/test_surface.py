import pytest

import arcade
from arcade import LBWH, load_texture
from arcade.gui import Surface, NinePatchTexture


def test_surface_draw_texture_raises_not_implemented_error_on_unsupported_values(window):
    ninepatch_tx = NinePatchTexture(
        left=5,
        right=5,
        top=5,
        bottom=5,
        texture=load_texture(":resources:gui_basic_assets/window/dark_blue_gray_panel.png"),
    )
    surface = Surface(size=(100, 100))

    def keywords_only(**kwargs):
        surface.draw_texture(0, 0, 20, 20, ninepatch_tx, **kwargs)

    with pytest.raises(NotImplementedError):
        keywords_only(alpha=128)

    with pytest.raises(NotImplementedError):
        keywords_only(angle=30.0)

    with pytest.raises(NotImplementedError):
        keywords_only(alpha=10, angle=30.0)


def test_limit_surface(window):
    surface = Surface(size=(100, 100))
    assert surface._cam.viewport == LBWH(0, 0, 100, 100)

    surface.limit(LBWH(10, 10, 80, 80))
    assert surface._cam.viewport == LBWH(10, 10, 80, 80)

    surface.limit(None)
    assert surface._cam.viewport == LBWH(0, 0, 100, 100)


@pytest.mark.backendgl
def test_draw_enforces_blending(window):
    """Surface.draw() has to enforce GL blending.

    pyglet toggles GL_BLEND directly (e.g. text layouts disable it after
    drawing), bypassing arcade's context flag cache. Without a forced enable
    the composite runs in replace mode: the surface's transparent texels
    overwrite the destination, punching an alpha hole through the UI.
    """
    from pyglet.graphics.api import gl

    parent = Surface(size=(50, 50))
    child = Surface(size=(50, 50))  # stays fully transparent

    with parent.activate():
        parent.clear((255, 255, 255, 255))

        # simulate pyglet disabling blending behind arcade's state cache
        window.ctx.enable(window.ctx.BLEND)
        gl.glDisable(gl.GL_BLEND)

        child.draw()

    center = parent.to_image().getpixel((25, 25))
    assert center == (255, 255, 255, 255)


def test_draw_composites_premultiplied(window):
    """Content rendered into a surface over transparent black is
    premultiplied; a straight-alpha composite would darken the content and
    erode the destination alpha."""
    parent = Surface(size=(50, 50))
    child = Surface(size=(50, 50))

    with child.activate():
        # 50% red over transparent black -> premultiplied (128, 0, 0, 128)
        arcade.draw_rect_filled(LBWH(0, 0, 50, 50), (255, 0, 0, 128))

    with parent.activate():
        parent.clear((255, 255, 255, 255))
        child.draw()

    r, g, b, a = parent.to_image().getpixel((25, 25))
    # 50% red over opaque white keeps full alpha
    assert (r, g, b, a) == pytest.approx((255, 127, 127, 255), abs=2)
