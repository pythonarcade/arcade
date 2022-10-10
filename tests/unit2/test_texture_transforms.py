from arcade.texture_transforms import (
    RotateTransform,
    FlipLeftToRightTransform,
    FlipTopToBottomTransform,
    TransposeTransform,
    TransverseTransform,
    VertexOrder,
    normalize,
    VertexOrder,
)
# Hit box points for a 128 x 128 texture
HIT_BOX_POINTS = (
    (-64.0, -64.0),
    (64.0, -64.0),
    (64.0, 64.0),
    (-64.0, 64.0),
)
ORDER = (
    VertexOrder.UPPER_LEFT.value,
    VertexOrder.UPPER_RIGHT.value,
    VertexOrder.LOWER_LEFT.value,
    VertexOrder.LOWER_RIGHT.value,
)


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
    assert result == (2, 0, 3, 1)
    result = RotateTransform.transform_vertex_order(result)
    result = RotateTransform.transform_vertex_order(result)
    result = RotateTransform.transform_vertex_order(result)
    assert result == ORDER


def test_flip_left_to_right_transform():
    # Flip left to right
    result = FlipLeftToRightTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((64.0, -64.0), (-64.0, -64.0), (-64.0, 64.0), (64.0, 64.0))
    # Flip back
    result = FlipLeftToRightTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS

    # Test vertex order
    result = FlipLeftToRightTransform.transform_vertex_order(ORDER)
    assert result == (1, 0, 3, 2)
    result = FlipLeftToRightTransform.transform_vertex_order(result)
    assert result == ORDER


def test_flip_top_to_bottom_transform():
    # Flip top to bottom
    result = FlipTopToBottomTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((-64.0, 64.0), (64.0, 64.0), (64.0, -64.0), (-64.0, -64.0))
    # Flip back
    result = FlipTopToBottomTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS

    result = FlipTopToBottomTransform.transform_vertex_order(ORDER)
    assert result == (2, 3, 0, 1)


def test_transpose_transform():
    # Transpose
    result = TransposeTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((-64.0, -64.0), (-64.0, 64.0), (64.0, 64.0), (64.0, -64.0))
    # Flip back
    result = TransposeTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS

    # Test vertex order
    result = TransposeTransform.transform_vertex_order(ORDER)
    assert result == (3, 1, 2, 0)
    result = TransposeTransform.transform_vertex_order(result)
    assert result == ORDER


def test_transverse_transform():
    # Transverse
    result = TransverseTransform.transform_hit_box_points(HIT_BOX_POINTS)
    assert result == ((64.0, 64.0), (64.0, -64.0), (-64.0, -64.0), (-64.0, 64.0))
    # Flip back
    result = TransverseTransform.transform_hit_box_points(result)
    assert result == HIT_BOX_POINTS

    # Test vertex order
    result = TransverseTransform.transform_vertex_order(ORDER)
    assert result == (0, 2, 1, 3)
    result = TransverseTransform.transform_vertex_order(result)
    assert result == ORDER


def test_normalize():
    normalize([RotateTransform, FlipLeftToRightTransform])
