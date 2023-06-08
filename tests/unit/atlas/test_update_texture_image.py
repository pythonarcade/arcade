"""
Test syncing atlas textures back into PIL images.
"""
import arcade


def test_sync(ctx):
    tex_1 = arcade.load_texture(":assets:images/cards/cardClubs2.png")
    tex_2 = arcade.load_texture(":assets:images/cards/cardDiamonds8.png")

    atlas = arcade.TextureAtlas((256, 256))
    atlas.add(tex_1)

    # Write the second image over the first one
    region = atlas.get_image_region_info(tex_1.image_data.hash)
    atlas.write_image(tex_2.image, region.x, region.y)

    # Sync the texture back into the PIL image.
    # It should contain the same image as tex_2
    atlas.sync_texture_image(tex_1)

    assert tex_1.image.tobytes() == tex_2.image.tobytes()
