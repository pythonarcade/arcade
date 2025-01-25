"""
Test fallback for hitbox creation with empty textures.
"""
from PIL import Image
import arcade

EXPECTED = ((-50.0, -50.0), (50.0, -50.0), (50.0, 50.0), (-50.0, 50.0))


def test_simple():
    tex = arcade.Texture(
        Image.new("RGBA", (100, 100)),
        hit_box_algorithm=arcade.hitbox.algo_simple,
    )
    assert tex.hit_box_points == EXPECTED


def test_pymunk():
    tex = arcade.Texture(
        Image.new("RGBA", (100, 100)),
        hit_box_algorithm=arcade.hitbox.algo_detailed,
    )
    assert tex.hit_box_points == EXPECTED
