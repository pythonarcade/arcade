import pytest

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
