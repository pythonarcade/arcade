import arcade
from arcade import LBWH

TEXTURE = arcade.load_texture(":resources:images/items/coinGold.png")


def test_draw_texture_rect(offscreen):
    assert offscreen.ctx.active_framebuffer == offscreen.fbo
    region = LBWH(0, 0, *TEXTURE.size)
    arcade.draw_texture_rect(TEXTURE, region, blend=True, pixelated=False) 
    offscreen.read_region_image(region).show()
    # TEXTURE.image.show()
    # assert offscreen.read_region_bytes(region) == TEXTURE.image.tobytes()
