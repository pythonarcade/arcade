from PIL import Image

from arcade import Texture, Sprite


def test_sprite_refreshes_hitbox_after_switching_texture():
    tex_1 = Texture('tex1', Image.new('RGBA', (50, 50), (0, 0, 0, 1)))
    tex_2 = Texture('tex1', Image.new('RGBA', (100, 100), (0, 0, 0, 1)))

    box = Sprite()
    box.texture = tex_1

    assert box.get_adjusted_hit_box() == [[-25.0, -25.0], [25.0, -25.0], [25.0, 25.0], [-25.0, 25.0]]

    box.texture = tex_2

    assert box.get_adjusted_hit_box() == [[-50.0, -50.0], [50.0, -50.0], [50.0, 50.0], [-50.0, 50.0]]

def test_sprite_refreshes_hitbox_after_resize_texture():
    tex_1 = Texture('tex1', Image.new('RGBA', (50, 50), (0, 0, 0, 1)))

    box = Sprite()
    box.texture = tex_1

    assert box.get_adjusted_hit_box() == [[-25.0, -25.0], [25.0, -25.0], [25.0, 25.0], [-25.0, 25.0]]

    box.width = 100
    box.height = 100
    assert box.get_adjusted_hit_box() == [[-50.0, -50.0], [50.0, -50.0], [50.0, 50.0], [-50.0, 50.0]]

def test_sprite_refreshes_hitbox_after_scale():
    tex_1 = Texture('tex1', Image.new('RGBA', (50, 50), (0, 0, 0, 1)))

    box = Sprite()
    box.texture = tex_1

    assert box.get_adjusted_hit_box() == [[-25.0, -25.0], [25.0, -25.0], [25.0, 25.0], [-25.0, 25.0]]

    box.scale = 2
    assert box.get_adjusted_hit_box() == [[-50.0, -50.0], [50.0, -50.0], [50.0, 50.0], [-50.0, 50.0]]
