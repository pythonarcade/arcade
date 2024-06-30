import gc
import arcade



def test_gc_image_multi_ref(ctx, common):
    """Test how atlas handles unique textures with the same image"""
    atlas = arcade.DefaultTextureAtlas((256, 256))

    # All vertex order variations of the same texture
    texture_1 = arcade.load_texture(":assets:images/topdown_tanks/tank_sand.png")
    texture_2 = texture_1.rotate_90()
    texture_3 = texture_1.rotate_180()
    texture_4 = texture_1.rotate_270()
    texture_5 = texture_1.flip_left_right()
    texture_6 = texture_1.flip_top_bottom()

    for i, texture in enumerate((texture_1, texture_2, texture_3, texture_4, texture_5, texture_6)):
        atlas.add(texture)
        common.check_internals(atlas, images=1, textures=i + 1, unique_textures=i + 1, textures_added=i + 1, textures_removed=0)
    texture = None

    common.check_internals(atlas, images=1, textures=6, unique_textures=6)

    # # Remove a texture one by one
    texture_1 = None
    common.check_internals(atlas, images=1, textures=5, unique_textures=5, textures_added=6, textures_removed=1)
    texture_2 = None
    common.check_internals(atlas, images=1, textures=4, unique_textures=4, textures_added=6, textures_removed=2)
    texture_3 = None
    common.check_internals(atlas, images=1, textures=3, unique_textures=3, textures_added=6, textures_removed=3)
    texture_4 = None
    common.check_internals(atlas, images=1, textures=2, unique_textures=2, textures_added=6, textures_removed=4)
    texture_5 = None
    common.check_internals(atlas, images=1, textures=1, unique_textures=1, textures_added=6, textures_removed=5)
    texture_6 = None
    gc.collect()
    gc.collect()
    common.check_internals(atlas, images=0, textures=0, unique_textures=0, textures_added=6, textures_removed=6)


def test_gc_image_multi_ref_duplicates(ctx, common):
    """Test how atlas handles unique textures with duplicates"""
    atlas = arcade.DefaultTextureAtlas((256, 256))

    # Load the texture multiple times
    texture_1 = arcade.load_texture(":assets:images/topdown_tanks/tank_sand.png")  # unique 1
    texture_2 = texture_1.rotate_90()                                              # unique 2
    texture_3 = arcade.load_texture(":assets:images/topdown_tanks/tank_sand.png")  # duplicate or 1
    texture_4 = texture_3.rotate_180()                                             # unique 3

    # Add them one by one and check the internals
    atlas.add(texture_1)
    common.check_internals(atlas, images=1, textures=1, unique_textures=1, textures_added=1, textures_removed=0)
    atlas.add(texture_2)
    common.check_internals(atlas, images=1, textures=2, unique_textures=2, textures_added=2, textures_removed=0)
    atlas.add(texture_3)
    common.check_internals(atlas, images=1, textures=3, unique_textures=2, textures_added=3, textures_removed=0)
    atlas.add(texture_4)
    common.check_internals(atlas, images=1, textures=4, unique_textures=3, textures_added=4, textures_removed=0)

    # Remove a texture one by one and check the internals
    texture_1 = None
    common.check_internals(atlas, images=1, textures=3, unique_textures=3, textures_added=4, textures_removed=1)
