"""
Ensure we are emulating PIL's transforms correctly.
"""
import arcade
import pytest
from pyglet.math import Mat4
from PIL import Image, ImageDraw
from arcade.texture.transforms import (
    Transform,
    Rotate90Transform,
    Rotate180Transform,
    Rotate270Transform,
    FlipLeftRightTransform,
    FlipTopBottomTransform,
    TransposeTransform,
    TransverseTransform,
)
# Arcade transform, PIL transform
TRANSFORMS = [
    (Rotate90Transform, Image.Transpose.ROTATE_270, 1),
    (Rotate180Transform, Image.Transpose.ROTATE_180, 2),
    (Rotate270Transform, Image.Transpose.ROTATE_90, 3),
    (FlipLeftRightTransform, Image.FLIP_LEFT_RIGHT, 4),
    (FlipTopBottomTransform, Image.FLIP_TOP_BOTTOM, 5),
    (TransposeTransform, Image.TRANSPOSE, 6),
    (TransverseTransform, Image.TRANSVERSE, 7)
]

@pytest.fixture(scope="module")
def image():
    im = Image.new("RGBA", (8, 8))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 3, 3), fill=arcade.color.RED)
    draw.rectangle((4, 4, 7, 7), fill=arcade.color.BLUE)
    draw.rectangle((4, 0, 7, 3), fill=arcade.color.GREEN)
    draw.rectangle((0, 4, 3, 7), fill=arcade.color.YELLOW)
    return im


@pytest.mark.parametrize("transform, pil_transform, number", TRANSFORMS)
def test_rotate90_transform(ctx: arcade.ArcadeContext, image, transform, pil_transform, number):
    """
    Compare pixel data between PIL and Arcade transforms.
    """
    texture = arcade.Texture(image).transform(transform)
    fbo = ctx.framebuffer(color_attachments=[ctx.texture(image.size, components=4)])
    assert image.size == fbo.size
    sprite = arcade.Sprite(texture, center_x=image.width // 2, center_y=image.height // 2)
    with fbo.activate():
        fbo.clear()
        ctx.projection_matrix = Mat4.orthogonal_projection(0, image.width, 0, image.height, -100, 100)
        arcade.draw_sprite(sprite, pixelated=True)

    expected_image = image.transpose(pil_transform)
    fbo_data = fbo.read(components=4)
    fbo_image = Image.frombytes("RGBA", image.size, fbo_data).transpose(Image.FLIP_TOP_BOTTOM)

    # expected_image.save(f"im_expected_{number}.png")
    # fbo_image.save(f"im_fbo_{number}.png")
    assert fbo_image.size == expected_image.size

    assert fbo_image.tobytes() == expected_image.tobytes()
