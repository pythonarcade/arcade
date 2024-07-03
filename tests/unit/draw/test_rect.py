import pytest
import arcade
from arcade import LBWH

TEXTURE = arcade.load_texture(":resources:images/items/coinGold.png")


def test_draw_texture_rect(offscreen):
    assert offscreen.ctx.active_framebuffer == offscreen.fbo
    region = LBWH(0, 0, *TEXTURE.size)
    arcade.draw_texture_rect(TEXTURE, region, blend=False, pixelated=True) 

    screen_image = offscreen.read_region_image(region, components=4)
    # screen_image.show()
    # TEXTURE.image.show()
    screen_image.save("test_screen_image.png")
    TEXTURE.image.save("test_texture_image.png")
    assert tuple(screen_image.tobytes()) == pytest.approx(tuple(TEXTURE.image.tobytes()), abs=1)

    # TEXTURE.image.show()
    # assert offscreen.read_region_bytes(region) == TEXTURE.image.tobytes()
