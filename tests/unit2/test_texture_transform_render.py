"""
Ensure we are emulating PIL's transforms correctly.
"""
import pytest
from PIL import Image, ImageDraw
from arcade.texture.transforms import (
    Rotate90Transform,
    Rotate180Transform,
    Rotate270Transform,
    FlipLeftToRightTransform,
    FlipTopToBottomTransform,
    TransposeTransform,
    TransverseTransform,
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

@pytest.fixture(scope="module")
def image():
    im = Image.new("RGBA", (8, 8))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 3, 3), fill=arcade.color.RED)
    draw.rectangle((4, 4, 7, 7), fill=arcade.color.BLUE)
    draw.rectangle((4, 0, 7, 3), fill=arcade.color.GREEN)
    draw.rectangle((0, 4, 3, 7), fill=arcade.color.YELLOW)
    return im


def test_rotate90_transform(ctx, image):
    texture = arcade.Texture(image)
    image = image.transpose(Image.Transpose.ROTATE_90)
    fbo = ctx.framebuffer(color_attachments=[ctx.texture(image.size, 4)])
    sprite = arcade.Sprite(arcade.)
    with fbo.activate():

# def test_rotate90_transform():
#     """Test rotate transform."""
#     # One rotation
#     result = Rotate90Transform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((-64.0, 64.0), (-64.0, -64.0), (64.0, -64.0), (64.0, 64.0))
#     # Three more should be the original points
#     result = Rotate90Transform.transform_hit_box_points(result)
#     result = Rotate90Transform.transform_hit_box_points(result)
#     result = Rotate90Transform.transform_hit_box_points(result)
#     assert result == HIT_BOX_POINTS

#     # Test vertex order
#     result = Rotate90Transform.transform_vertex_order(ORDER)
#     assert result == (2, 0, 3, 1)
#     result = Rotate90Transform.transform_vertex_order(result)
#     result = Rotate90Transform.transform_vertex_order(result)
#     result = Rotate90Transform.transform_vertex_order(result)
#     assert result == ORDER


# def test_rotate180_transform():
#     result = Rotate180Transform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((64.0, 64.0), (-64.0, 64.0), (-64.0, -64.0), (64.0, -64.0))

#     result = Rotate180Transform.transform_vertex_order(ORDER)
#     assert result == (3, 2, 1, 0)


# def test_rotate270_transform():
#     result = Rotate270Transform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((64.0, -64.0), (64.0, 64.0), (-64.0, 64.0), (-64.0, -64.0))

#     result = Rotate270Transform.transform_vertex_order(ORDER)
#     assert result == (1, 3, 0, 2)


# def test_flip_left_to_right_transform():
#     # Flip left to right
#     result = FlipLeftToRightTransform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((64.0, -64.0), (-64.0, -64.0), (-64.0, 64.0), (64.0, 64.0))
#     # Flip back
#     result = FlipLeftToRightTransform.transform_hit_box_points(result)
#     assert result == HIT_BOX_POINTS

#     # Test vertex order
#     result = FlipLeftToRightTransform.transform_vertex_order(ORDER)
#     assert result == (1, 0, 3, 2)
#     result = FlipLeftToRightTransform.transform_vertex_order(result)
#     assert result == ORDER


# def test_flip_top_to_bottom_transform():
#     # Flip top to bottom
#     result = FlipTopToBottomTransform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((-64.0, 64.0), (64.0, 64.0), (64.0, -64.0), (-64.0, -64.0))
#     # Flip back
#     result = FlipTopToBottomTransform.transform_hit_box_points(result)
#     assert result == HIT_BOX_POINTS

#     result = FlipTopToBottomTransform.transform_vertex_order(ORDER)
#     assert result == (2, 3, 0, 1)
#     result = FlipTopToBottomTransform.transform_vertex_order(result)
#     assert result == ORDER


# def test_transpose_transform():
#     # Transpose
#     result = TransposeTransform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((-64.0, -64.0), (-64.0, 64.0), (64.0, 64.0), (64.0, -64.0))
#     # Flip back
#     result = TransposeTransform.transform_hit_box_points(result)
#     assert result == HIT_BOX_POINTS

#     # Test vertex order
#     result = TransposeTransform.transform_vertex_order(ORDER)
#     assert result == (3, 1, 2, 0)
#     result = TransposeTransform.transform_vertex_order(result)
#     assert result == ORDER


# def test_transverse_transform():
#     # Transverse
#     result = TransverseTransform.transform_hit_box_points(HIT_BOX_POINTS)
#     assert result == ((64.0, 64.0), (64.0, -64.0), (-64.0, -64.0), (-64.0, 64.0))
#     # Flip back
#     result = TransverseTransform.transform_hit_box_points(result)
#     assert result == HIT_BOX_POINTS

#     # Test vertex order
#     result = TransverseTransform.transform_vertex_order(ORDER)
#     assert result == (0, 2, 1, 3)
#     result = TransverseTransform.transform_vertex_order(result)
#     assert result == ORDER
