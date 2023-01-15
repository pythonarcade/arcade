from uuid import uuid4

import PIL
from PIL.Image import Image

import arcade


def test_calculate_points():
    texture = arcade.load_texture(":resources:images/items/coinGold.png")
    result = arcade.calculate_hit_box_points_detailed(texture.image)
    print(result)
    assert result == ((-32, 7), (-17, 28), (7, 32), (29, 15), (32, -7), (17, -28), (-8, -32), (-28, -17))

    texture = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
    result = arcade.calculate_hit_box_points_detailed(texture.image)
    print(result)
    assert result == ((-32, -31), (-22, -18), (-27, -14), (-21, 21), (-8, 31), (10, 31), (25, 17), (29, -16), (22, -18),
                      (32, -31), (32, -52), (29, -59), (17, -57), (22, -39), (15, -28), (19, -63), (4, -64), (-2, -46),
                      (-3, -63), (-18, -64), (-15, -30), (-22, -39), (-16, -47), (-18, -59), (-31, -56))


def test_empty_image():
    texture = arcade.Texture(name=str(uuid4()), image=PIL.Image.new("RGBA", (50, 50)))

    result = arcade.calculate_hit_box_points_simple(texture.image)
    print(result)
    assert result == ()

    result = arcade.calculate_hit_box_points_detailed(texture.image)
    print(result)
    assert result == ()

