import pytest
import arcade
from PIL import Image


def test_calculate_hit_box_points_simple():
    # Completely filled RGBA image
    image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    expected_points = ((-50.0, -50.0), (50.0, -50.0), (50.0, 50.0), (-50.0, 50.0))
    points =  arcade.calculate_hit_box_points_simple(image)
    assert points == expected_points

    # Fail trying RGB
    image = Image.new("RGB", (100, 100))
    with pytest.raises(ValueError):
        arcade.calculate_hit_box_points_simple(image)


def test_calculate_hit_box_points_detailed():
    # Completely filled RGBA image
    image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    expected_points = ((-50.0, -50.0), (50.0, -50.0), (50.0, 50.0), (-50.0, 50.0))
    points =  arcade.calculate_hit_box_points_detailed(image)
    assert points == expected_points

    # Fail trying RGB
    image = Image.new("RGB", (100, 100))
    with pytest.raises(ValueError):
        arcade.calculate_hit_box_points_detailed(image)
