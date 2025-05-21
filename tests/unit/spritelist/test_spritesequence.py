import arcade


class _CustomSpriteSolidColor(arcade.SpriteSolidColor):
    pass


def test_collective_draw(window: arcade.Window) -> None:
    sprite_list1: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
    sprite_list1.append(arcade.SpriteSolidColor(16, 16, color=(255, 0, 0, 1)))

    sprite_list2: arcade.SpriteList[_CustomSpriteSolidColor] = arcade.SpriteList()
    sprite_list2.append(_CustomSpriteSolidColor(16, 16, color=(255, 0, 0, 1)))

    # It really is a SpriteList with a good type; this would not typecheck otherwise
    custom_sprite: _CustomSpriteSolidColor = sprite_list2[0]  # assert_type

    # Assert that SpriteSequence is truly covariant:
    # It can be used as a common type for different types of SpriteLists.
    scene: list[arcade.SpriteSequence[arcade.Sprite]] = [
        sprite_list1,
        sprite_list2,
    ]
    sprite: arcade.Sprite = scene[0][0]  # assert_type

    # We can collectively draw all the SpriteSequences.
    for sprite_list in scene:
        sprite_list.draw()
