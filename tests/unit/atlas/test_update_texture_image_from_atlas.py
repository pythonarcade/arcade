"""
Test syncing atlas textures back into PIL images.
"""
from PIL import Image, ImageDraw
import arcade


def _create_image_with_square(x, y) -> Image.Image:
    # Create an image with a centered square
    w, h = 4, 4
    im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.rectangle((x, y, x + w, y + h), fill=(255, 0, 0, 255))
    return im


def test_update_texture_image_from_atlas(ctx):
    # Original image
    im_1 = _create_image_with_square(1, 1)
    # The simulated image we render into the atlas using arcade.draw_rectangle_filled
    im_2 = _create_image_with_square(4, 4)

    atlas = arcade.TextureAtlas((256, 256))
    tex = arcade.Texture(im_1)
    atlas.add(tex)

    # Check that the original image matches
    atlas_im = atlas.read_texture_image_from_atlas(tex)
    assert atlas_im.tobytes() == im_1.tobytes()

    # Render new content and verify this content
    with atlas.render_into(tex) as area:
        area.clear()
        arcade.draw_lrbt_rectangle_filled(4, 8, 1, 4,arcade.color.RED)

    # atlas_im = atlas.read_texture_image_from_atlas(tex)
    # atlas_im.save("test_1.png")
    # im_2.save("test_2.png")
    # assert atlas_im.tobytes() == im_2.tobytes()
