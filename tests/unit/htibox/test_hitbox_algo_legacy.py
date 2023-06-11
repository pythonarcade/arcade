import pytest
from arcade import hitbox
from PIL import Image


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


def test_texture_cache_name():
    # These algos don't have any parameters
    assert hitbox.algo_simple.cache_name == "SimpleHitBoxAlgorithm"
    assert hitbox.algo_bounding_box.cache_name == "BoundingHitBoxAlgorithm"

    # Detailed has a detail parameter for the number of points
    # Test default value and specifying a value
    assert hitbox.algo_detailed.cache_name == "PymunkHitBoxAlgorithm|detail=4.5"
    assert hitbox.algo_detailed(detail=10.0).cache_name == "PymunkHitBoxAlgorithm|detail=10.0"


def test_call_override():
    assert hitbox.algo_detailed.detail == 4.5
    assert hitbox.algo_detailed(detail=10.0).detail == 10.0
