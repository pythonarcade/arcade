"""
Test syncing atlas textures back into PIL images.
"""
from PIL import Image, ImageDraw
import arcade


def _create_image_with_rect(rect) -> Image.Image:
    # Create an image with a centered square
    im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.rectangle(rect, fill=(255, 0, 0, 255))
    return im


def test_update_texture_image_from_atlas(ctx):
    # Original image
    im = _create_image_with_rect((1, 1, 4, 4))
    im = im.transpose(Image.FLIP_TOP_BOTTOM)

    atlas = arcade.DefaultTextureAtlas((256, 256), border=10)
    tex = arcade.Texture(im)
    atlas.add(tex)

    # Check that the original image matches
    atlas_im = atlas.read_texture_image_from_atlas(tex)
    assert atlas_im.tobytes() == im.tobytes()

    # Render new content and verify this content
    with atlas.render_into(tex) as area:
        area.clear()
        arcade.draw_lrbt_rectangle_filled(1, 5, 1, 5, arcade.color.RED)

    atlas_im = atlas.read_texture_image_from_atlas(tex)
    assert atlas_im.tobytes() == im.tobytes()
