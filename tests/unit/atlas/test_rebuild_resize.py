import PIL.Image
import pytest
from pyglet.image.atlas import AllocatorException
import arcade
from arcade import DefaultTextureAtlas, load_texture


def test_rebuild(ctx, common):
    """Build and atlas and rebuild it"""
    # 36 x 36 : 6a9c1abbf2719dc59b9ebe2b7c2a6d662432dfe9e3d77f202ee042f98caf3616
    tex_small = load_texture(":resources:images/topdown_tanks/treeGreen_small.png")
    # 64 x 64 : b883bf9ece9ab2dc738b24dc6bf664b056bea59503040eac15e7374e4a806b1b
    tex_big = load_texture(":resources:images/topdown_tanks/treeGreen_large.png")

    atlas = DefaultTextureAtlas((104, 104), border=1)
    slot_a, region_a = atlas.add(tex_big)
    slot_b, region_b = atlas.add(tex_small)
    region_a = atlas.get_texture_region_info(tex_big.atlas_name)
    region_b = atlas.get_texture_region_info(tex_small.atlas_name)
    common.check_internals(atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0)

    # Re-build and check states
    atlas.rebuild()
    assert slot_a == atlas.get_texture_id(tex_big)
    assert slot_b == atlas.get_texture_id(tex_small)
    region_aa = atlas.get_texture_region_info(tex_big.atlas_name)
    region_bb = atlas.get_texture_region_info(tex_small.atlas_name)
    common.check_internals(atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0)

    # The textures have switched places in the atlas and should
    # have the same left position
    assert region_a.texture_coordinates[0] == region_bb.texture_coordinates[0]
    # check that textures moved at the very least
    assert region_b.texture_coordinates[0] != region_bb.texture_coordinates[0]
    assert region_a.texture_coordinates[0] != region_aa.texture_coordinates[0]

    common.check_internals(atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0)


def test_resize(ctx, common):
    """Attempt to resize the atlas"""
    atlas = DefaultTextureAtlas((50, 100), border=1, auto_resize=False)
    # sha256 0118296e6c16a0113a31e71a64cac301152e44d9623ca2db92bbbfb166dd22fa
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (255, 0, 0, 255)))
    # sha256 81776589b8a141ac4ac01cce9cf16ee239fb82564c8ec026473aa185c1d6786e
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (0, 255, 0, 255)))

    atlas.add(t1)
    atlas.add(t2)
    common.check_internals(atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0)
    atlas.resize((50, 100))
    common.check_internals(atlas, images=2, textures=2, unique_textures=2, textures_added=2, textures_removed=0)

    assert atlas._textures_added == 2
    assert atlas._finalizers_created == 2
    assert atlas._textures_removed == 0

    # Make atlas so small the current textures won't fit
    with pytest.raises(AllocatorException):
        atlas.resize((50, 99))

    # Resize past max size
    atlas = DefaultTextureAtlas((50, 50), border=0)
    atlas._max_size = 60, 60
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (255, 0, 0, 255)))
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (0, 255, 0, 255)))
    atlas.add(t1)
    common.check_internals(atlas, images=1, textures=1, unique_textures=1, textures_added=1, textures_removed=0)

    with pytest.raises(AllocatorException):
        atlas.add(t2)
