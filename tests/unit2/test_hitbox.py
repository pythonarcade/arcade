import pytest
from arcade import hitbox
from PIL import Image


def test_module():
    # Make sure the module is loaded
    assert hitbox.default
    assert hitbox.detailed
    assert hitbox.simple
    assert hitbox.bounding_box


def test_calculate_hit_box_points_simple():
    # Completely filled RGBA image
    image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    expected_points = ((-50.0, -50.0), (50.0, -50.0), (50.0, 50.0), (-50.0, 50.0))
    points =  hitbox.calculate_hit_box_points_simple(image)
    assert points == expected_points

    # Fail trying RGB
    image = Image.new("RGB", (100, 100))
    with pytest.raises(ValueError):
        hitbox.calculate_hit_box_points_simple(image)


def test_calculate_hit_box_points_detailed():
    # Completely filled RGBA image
    image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    expected_points = ((-50.0, -50.0), (50.0, -50.0), (50.0, 50.0), (-50.0, 50.0))
    points =  hitbox.calculate_hit_box_points_detailed(image)
    assert points == expected_points

    # Fail trying RGB
    image = Image.new("RGB", (100, 100))
    with pytest.raises(ValueError):
        hitbox.calculate_hit_box_points_detailed(image)


def test_param_str():
    simple = hitbox.get_algorithm("simple")
    bounding = hitbox.get_algorithm("bounding_box")
    detailed = hitbox.get_algorithm("pymunk")

    # These algos don't have any parameters
    assert simple.create_param_str() == ""
    assert bounding.create_param_str() == ""

    # Detailed has a detail parameter for the number of points
    # Test default value and specifying a value
    assert detailed.create_param_str() == "detail=4.5"
    assert detailed.create_param_str(detail=10.0) == "detail=10.0"


def test_call_override():
    algo = hitbox.get_algorithm("pymunk")
    assert algo.detail == 4.5
    algo = algo(detail=10.0)
    assert algo.detail == 10.0
