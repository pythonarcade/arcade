from arcade.texture_transforms import (
    RotateTransform,
    FlipLeftToRightTransform,
    FlipTopToBottomTransform,
    normalize
)
# Hit box points for a 128 x 128 texture
HIT_BOX_POINTS = (
    (-64.0, -64.0),
    (64.0, -64.0),
    (64.0, 64.0),
    (-64.0, 64.0),
)
ORDER = 0, 1, 2, 3


def test_rotate_transform():
    """Test rotate transform."""
    # One rotation
    result = RotateTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((64.0, -64.0), (64.0, 64.0), (-64.0, 64.0), (-64.0, -64.0))
    # Three more should be the original points
    result = RotateTransform.transform_hit_box_points(result)
    result = RotateTransform.transform_hit_box_points(result)
    result = RotateTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS

    # Test vertex order
    result = RotateTransform.transform_vertex_order(ORDER)
    assert result == (3, 0, 1, 2)


def test_flip_left_to_right_transform():
    # Flip left to right
    result = FlipLeftToRightTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((64.0, -64.0), (-64.0, -64.0), (-64.0, 64.0), (64.0, 64.0))
    # Flip back
    result = FlipLeftToRightTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS

    # Test vertex order
    result = FlipLeftToRightTransform.transform_vertex_order(ORDER)
    assert result == (2, 3, 0, 1)
    result = FlipLeftToRightTransform.transform_vertex_order(result)
    assert result == ORDER


def test_flip_top_to_bottom_transform():
    # Flip top to bottom
    result = FlipTopToBottomTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((-64.0, 64.0), (64.0, 64.0), (64.0, -64.0), (-64.0, -64.0))
    # Flip back
    result = FlipTopToBottomTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS


def test_normalize():
    normalize([RotateTransform, FlipLeftToRightTransform])
