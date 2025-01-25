import pytest
from pyglet.math import Vec2

import arcade
from arcade import LBWH
from arcade.gui import NinePatchTexture


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
        ":resources:gui_basic_assets/button/red_normal.png",
    )
    patch.draw_rect(rect=LBWH(0, 0, 200, 200))
    patch.texture = new_texture
    assert patch.texture == new_texture
    patch.draw_rect(rect=LBWH(0, 0, 200, 200))


def test_draw_position(ctx, texture):
    patch = NinePatchTexture(texture=texture, left=7, right=8, bottom=9, top=10)
    patch.draw_rect(rect=LBWH(0, 0, 200, 200))
    patch.draw_rect(rect=LBWH(200, 200, 200, 200))
    patch.draw_rect(rect=LBWH(400, 400, 200, 200))
    # arcade.get_image().save("test_draw_position.png")


def shader_math():
    """
    This is just around to debug shader math.
    The shader needs to be simplified at some point.
    """
    atlas_size = Vec2(8, 8)
    atlas_size_uniform = 8
    # 8 x x texture
    uv0 = Vec2(0.0625, 0.0625)  # upper_left
    uv1 = Vec2(0.9375, 0.0625)  # upper_right
    uv2 = Vec2(0.0625, 0.9375)  # lower_left
    uv3 = Vec2(0.9375, 0.9375)  # lower_right

    # Initial borders per side
    left, right, top, bottom = 1, 1, 1, 1

    # The size of the patch
    size = Vec2(8, 8)
    # The inner area of the patch
    start = Vec2(left, bottom)
    end = Vec2(size.x - right, size.y - top)
    # Size of the patch texture
    t_size = Vec2(8, 8)

    # Borders adjusted rectangle (and reverse y axis)
    left = start.x
    right = t_size.x - end.x
    top = t_size.y - end.y
    bottom = start.y

    c1 = Vec2(left, top) / atlas_size_uniform
    # Upper left corner
    c2 = Vec2(right, top) / atlas_size_uniform
    # Upper right corner
    c3 = Vec2(left, bottom) / atlas_size_uniform
    # Lower left corner
    c4 = Vec2(right, bottom) / atlas_size_uniform
    # Lower right corner

    print("--- left, right, bottom, top ---")
    print(left, right, top, bottom)
    print("--- corners ---")
    print("c1:", c1, 1 / c1.x, 1 / c1.y)
    print("c2:", c2, 1 / c2.x, 1 / c2.y)
    print("c3:", c3, 1 / c3.x, 1 / c3.y)
    print("c4:", c4, 1 / c4.x, 1 / c4.y)

    t1 = uv0
    t2 = uv0 + Vec2(c1.x, 0.0)
    t3 = uv1 - Vec2(c2.x, 0.0)
    t4 = uv1

    t5 = uv0 + Vec2(0.0, c1.y)
    t6 = uv0 + c1
    t7 = uv1 + Vec2(-c2.x, c2.y)
    t8 = uv1 + Vec2(0.0, c2.y)

    t9 = uv2 - Vec2(0.0, c3.y)
    t10 = uv2 + Vec2(c3.x, -c3.y)
    t11 = uv3 - c4
    t12 = uv3 - Vec2(0.0, c4.y)

    t13 = uv2
    t14 = uv2 + Vec2(c3.x, 0.0)
    t15 = uv3 - Vec2(c4.x, 0.0)
    t16 = uv3

    print("--- row 1 ---")
    print(t1, t5, t2, t6)
    print(t2, t6, t3, t7)
    print(t3, t7, t4, t8)

    print("--- row 2 ---")
    print(t5, t9, t6, t10)
    print(t6, t10, t7, t11)
    print(t7, t11, t8, t12)

    print("--- row 3 ---")
    print(t9, t13, t10, t14)
    print(t10, t14, t11, t15)
    print(t11, t15, t12, t16)
