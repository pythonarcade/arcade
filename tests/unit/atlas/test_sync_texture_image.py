"""
Test syncing atlas textures back into PIL images.
"""
from PIL import Image
import arcade
from arcade.resources import resolve


def test_sync(ctx):
    im_1 = Image.open(resolve(":assets:images/cards/cardClubs2.png"))
    im_2 = Image.open(resolve(":assets:images/cards/cardDiamonds8.png"))
    tex = arcade.Texture(im_1)

    atlas = arcade.TextureAtlas((256, 256))
    atlas.add(tex)

    # Write the second image over the first one
    region = atlas.get_image_region_info(tex.image_data.hash)
    atlas.write_image(im_2, region.x, region.y)

    # Sync the texture back into the PIL image.
    # It should contain the same image as tex_2
    atlas.sync_texture_image(tex)

    assert tex.image.tobytes() == im_2.tobytes()
