import arcade


def test_sprite_gif():
    sprite = arcade.load_animated_gif(":resources:images/test_textures/anim.gif")
    assert len(sprite.animation) == 8
    assert sprite.texture == sprite.animation.keyframes[0].texture
