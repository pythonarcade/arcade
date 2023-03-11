import arcade


def test_add():
    sl_1 = arcade.SpriteList()
    sl_2 = arcade.SpriteList()
    sprite_1 = arcade.SpriteSolidColor(width=16, height=16, color=arcade.color.RED)
    sprite_2 = arcade.SpriteSolidColor(width=16, height=16, color=arcade.color.BLUE)
    sprite_3 = arcade.SpriteSolidColor(width=16, height=16, color=arcade.color.GREEN)
    sl_1.extend((sprite_1, sprite_2, sprite_3))
    sl_2.extend((sprite_1, sprite_2, sprite_3))

    assert len(sl_1) == 3
    assert sl_1[0] == sprite_1
    assert sl_1[1] == sprite_2
    assert sl_1[2] == sprite_3

    assert sl_2[0] == sprite_1
    assert sl_2[1] == sprite_2
    assert sl_2[2] == sprite_3

    # Check internal references
    assert sprite_1.sprite_lists == [sl_1, sl_2]
    assert sprite_2.sprite_lists == [sl_1, sl_2]
    assert sprite_3.sprite_lists == [sl_1, sl_2]

    sprite_1.remove_from_sprite_lists()
    sprite_2.remove_from_sprite_lists()
    sprite_3.remove_from_sprite_lists()
    assert len(sl_1) == 0

    assert sprite_1.sprite_lists == []
    assert sprite_2.sprite_lists == []
    assert sprite_3.sprite_lists == []
