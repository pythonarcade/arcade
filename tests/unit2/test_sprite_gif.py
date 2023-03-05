import arcade


def test_sprite_gif():
    sprite = arcade.load_animated_gif(":resources:images/test_textures/anim.gif")
    assert len(sprite.textures) == 8



test_sprite_gif()
