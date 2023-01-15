import pytest
from arcade.gui import NinePatchTexture
import arcade

# ":resources:gui_basic_assets/button_square_blue_pressed.png"
# ":resources:gui_basic_assets/button_square_blue.png"
# ":resources:gui_basic_assets/red_button_hover.png"
# ":resources:gui_basic_assets/red_button_normal.png"


@pytest.fixture(scope="module")
def texture():
    return arcade.load_texture(
        ":resources:gui_basic_assets/window/grey_panel.png",
    )


def test_properties(ctx, texture):
    patch = NinePatchTexture(texture=texture, left=7, right=8, bottom=9, top=10)
    assert patch.left == 7
    assert patch.right == 8
    assert patch.bottom == 9
    assert patch.top == 10
    assert patch.texture == texture
    assert patch.width == texture.width
    assert patch.height == texture.height
    assert patch.size == (texture.width, texture.height)
    assert patch.ctx == ctx


def test_negative_borders(ctx, texture):
    # Borders cannot be negative
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=-1, right=0, bottom=0, top=0)
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=0, right=-1, bottom=0, top=0)
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=0, right=0, bottom=-1, top=0)
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=0, right=0, bottom=0, top=-1)


def test_borders_too_big(ctx, texture):
    # Borders cannot be bigger than the texture
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=texture.width + 1, right=0, bottom=0, top=0)
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=0, right=texture.width + 1, bottom=0, top=0)
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=0, right=0, bottom=texture.height + 1, top=0)
    with pytest.raises(ValueError):
        NinePatchTexture(texture=texture, left=0, right=0, bottom=0, top=texture.height + 1)


def test_swap_texture(ctx, texture):
    patch = NinePatchTexture(texture=texture, left=7, right=8, bottom=9, top=10)
    new_texture = arcade.load_texture(
        ":resources:gui_basic_assets/red_button_normal.png",
    )
    patch.draw_sized(size=(200, 200))
    patch.texture = new_texture
    assert patch.texture == new_texture
    patch.draw_sized(size=(200, 200))


def test_draw_position(ctx, texture):
    patch = NinePatchTexture(texture=texture, left=7, right=8, bottom=9, top=10)
    patch.draw_sized(size=(200, 200), position=(0, 0))
    patch.draw_sized(size=(200, 200), position=(200, 200))
    patch.draw_sized(size=(200, 200), position=(400, 400))
    arcade.get_image().save("test_draw_position.png")
