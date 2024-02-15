import PIL
import pytest
from pyglet.image.atlas import AllocatorException
import arcade
from arcade import TextureAtlas, load_texture


def test_rebuild(ctx, common):
    """Build and atlas and rebuild it"""
    # 36 x 36
    tex_small = load_texture(":resources:images/topdown_tanks/treeGreen_small.png")
    # 64 x 64
    tex_big = load_texture(":resources:images/topdown_tanks/treeGreen_large.png")
    atlas = TextureAtlas((104, 104), border=1)
    slot_a, region_a = atlas.add(tex_big)
    slot_b, region_b = atlas.add(tex_small)
    region_a = atlas.get_texture_region_info(tex_big.atlas_name)
    region_b = atlas.get_texture_region_info(tex_small.atlas_name)
    common.check_internals(atlas, num_images=2, num_textures=2)

    # Re-build and check states
    atlas.rebuild()
    assert slot_a == atlas.get_texture_id(tex_big)
    assert slot_b == atlas.get_texture_id(tex_small)
    region_aa = atlas.get_texture_region_info(tex_big.atlas_name)
    region_bb = atlas.get_texture_region_info(tex_small.atlas_name)
    common.check_internals(atlas, num_images=2, num_textures=2)

    # The textures have switched places in the atlas and should
    # have the same left position
    assert region_a.texture_coordinates[0] == region_bb.texture_coordinates[0]
    # check that textures moved at the very least
    assert region_b.texture_coordinates[0] != region_bb.texture_coordinates[0]
    assert region_a.texture_coordinates[0] != region_aa.texture_coordinates[0]

    common.check_internals(atlas, num_images=2, num_textures=2)


def test_resize(ctx, common):
    """Attempt to resize the atlas"""
    atlas = TextureAtlas((50, 100), border=1, auto_resize=False)
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (255, 0, 0, 255)))
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (0, 255, 0, 255)))
    atlas.add(t1)
    atlas.add(t2)
    common.check_internals(atlas, num_images=2, num_textures=2)
    atlas.resize((50, 100))
    common.check_internals(atlas, num_images=2, num_textures=2)

    # Make atlas so small the current textures won't fit
    with pytest.raises(AllocatorException):
        atlas.resize((50, 99))

    # Resize past max size
    atlas = TextureAtlas((50, 50), border=0)
    atlas._max_size = 60, 60
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (255, 0, 0, 255)))
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (0, 255, 0, 255)))
    atlas.add(t1)
    common.check_internals(atlas, num_images=1, num_textures=1)
    with pytest.raises(AllocatorException):
        atlas.add(t2)
