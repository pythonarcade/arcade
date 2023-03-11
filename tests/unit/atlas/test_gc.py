import PIL
import gc
import arcade

def test_gc_image_multi_ref(ctx, common):
    """Test how the GC handles multiple references to the same image"""
    atlas = arcade.TextureAtlas((256, 256))

    # Load an image manually to bypass the cache (until this is changed)
    path = arcade.resources.resolve_resource_path(":resources:images/topdown_tanks/tank_sand.png")
    image_data = arcade.texture.ImageData(PIL.Image.open(path).convert("RGBA"))

    texture_1 = arcade.Texture(image_data)
    texture_2 = texture_1.rotate_90()
    texture_3 = texture_1.rotate_180()
    texture_4 = texture_1.rotate_270()
    texture_5 = texture_1.flip_left_right()
    texture_6 = texture_1.flip_top_bottom()

    atlas.add(texture_1)
    atlas.add(texture_2)
    atlas.add(texture_3)
    atlas.add(texture_4)
    atlas.add(texture_5)
    atlas.add(texture_6)

    common.check_internals(atlas, num_images=1, num_textures=6)

    # Remove a texture one by one
    texture_1 = None
    common.check_internals(atlas, num_images=1, num_textures=5)
    texture_2 = None
    common.check_internals(atlas, num_images=1, num_textures=4)
    texture_3 = None
    common.check_internals(atlas, num_images=1, num_textures=3)
    texture_4 = None
    common.check_internals(atlas, num_images=1, num_textures=2)
    texture_5 = None
    common.check_internals(atlas, num_images=1, num_textures=1)
    texture_6 = None
    common.check_internals(atlas, num_images=0, num_textures=0)
