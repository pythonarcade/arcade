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


def test_param_str():
    simple = arcade.hitbox.get_algorithm("simple")
    bounding = arcade.hitbox.get_algorithm("bounding_box")
    detailed = arcade.hitbox.get_algorithm("detailed")

    # These algos don't have any parameters
    assert simple.create_param_str() == ""
    assert bounding.create_param_str() == ""

    # Detailed has a detail parameter for the number of points
    # Test default value and specifying a value
    assert detailed.create_param_str() == "detail=4.5"
    assert simple.create_param_str(detail=10.0) == "detail=10.0"
