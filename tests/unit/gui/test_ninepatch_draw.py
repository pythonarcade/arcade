import itertools

import pytest
from PIL import Image, ImageDraw
from pyglet.math import Mat4

import arcade
from arcade.gui import NinePatchTexture
from arcade import LBWH

# Various combinations of borders sizes
PATCH_VARIANTS = list(itertools.product([1, 0], repeat=4))
PATCH_VARIANTS += list(itertools.product([1, 2], repeat=4))
PATCH_VARIANTS += list(itertools.product([1, 3], repeat=4))
PATCH_VARIANTS += list(itertools.product([2, 4], repeat=4))
PATCH_SIZE = 100, 100


def create_ninepatch(
    texture_size: tuple[int, int],
    patch_size: tuple[int, int],
    left: int,
    right: int,
    bottom: int,
    top: int,
) -> tuple[NinePatchTexture, Image.Image,]:
    """Create a ninepatch texture with the given borders."""
    # Manually create a ninepatch texture.
    # We make it white by default and draw a red rectangle in the middle.
    # This means borders are white and the middle is red.
    # NOTE: Pillow's 0,0 is top left, Arcade's is bottom left.
    patch_image = Image.new("RGBA", texture_size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(patch_image)
    draw.rectangle((left, top, texture_size[0] - right - 1, texture_size[1] - bottom - 1), fill=(255, 0, 0, 255))
    texture = arcade.Texture(patch_image)
    # patch_image.show()

    # Create the expected image
    expected_image = Image.new("RGBA", patch_size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(expected_image)
    draw.rectangle((left, top, patch_size[0] - right - 1, patch_size[1] - bottom - 1), fill=(255, 0, 0, 255))

    return NinePatchTexture(
        texture=texture,
        left=left,
        right=right,
        bottom=bottom,
        top=top,
    ), expected_image


@pytest.fixture(scope="module")
def fbo(ctx_static):
    return ctx_static.framebuffer(color_attachments=[ctx_static.texture(PATCH_SIZE)])


@pytest.mark.parametrize("left, right, bottom, top", PATCH_VARIANTS)
def test_draw(ctx, fbo, left, right, bottom, top):
    texture_size = (10, 10)
    patch, expected_image = create_ninepatch(
        texture_size=texture_size,
        patch_size=PATCH_SIZE,
        left=left,
        right=right,
        bottom=bottom,
        top=top,
    )
    with fbo.activate():
        fbo.clear()
        ctx.projection_matrix = Mat4.orthogonal_projection(0, PATCH_SIZE[0], 0, PATCH_SIZE[1], -100, 100)
        patch.draw_rect(
            rect=LBWH(0, 0, PATCH_SIZE[0], PATCH_SIZE[1]),
            pixelated=True,
        )

    fbo_image = ctx.get_framebuffer_image(fbo)
    # fbo_image.show()
    # expected_image.show()

    # Temp dump images
    # expected_image.save(f"_expected-{left}-{right}-{bottom}-{top}.png")
    # fbo_image.save(f"_actual-{left}-{right}-{bottom}-{top}.png")
    # patch.texture.image.save(f"_texture-{left}-{right}-{bottom}-{top}.png")

    assert fbo_image.tobytes() == expected_image.tobytes()
