import PIL
import pytest
from pyglet.image.atlas import AllocatorException
from arcade import TextureAtlas, load_texture
import arcade
from arcade.texture_atlas import TEXCOORD_BUFFER_SIZE


def check_internals(atlas, num_textures):
    assert len(atlas._uv_slots_free) == TEXCOORD_BUFFER_SIZE - num_textures
    assert len(atlas._uv_slots) == num_textures
    assert len(atlas._textures) == num_textures
    assert len(atlas._atlas_regions) == num_textures


def test_create(ctx):
    TextureAtlas((100, 100), border=1)
    TextureAtlas((100, 200), border=0)


def test_add(ctx):
    """Test adding textures to atlas"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = TextureAtlas((200, 200), border=1)
    slot_a, region_a = atlas.add(tex_a)
    slot_b, region_b = atlas.add(tex_b)
    assert slot_a == 0
    assert slot_b == 1
    check_internals(atlas, 2)
    # Add existing textures
    assert slot_a == atlas.add(tex_a)[0]
    assert slot_b == atlas.add(tex_b)[0]
    check_internals(atlas, 2)
    atlas.use_uv_texture()


def test_remove(ctx):
    """Remove textures from atlas"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = TextureAtlas((200, 200), border=1)
    slot_a, region_a = atlas.add(tex_a)
    slot_b, region_b = atlas.add(tex_b)
    check_internals(atlas, 2)
    atlas.remove(tex_a)
    check_internals(atlas, 1)
    atlas.rebuild()
    check_internals(atlas, 1)
    atlas.remove(tex_b)
    check_internals(atlas, 0)
    atlas.rebuild()
    check_internals(atlas, 0)


def test_add_overflow(ctx):
    """Ensure AllocatorException is raised when atlas is full"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = TextureAtlas((100, 100), border=1, auto_resize=False)
    slot_a, region = atlas.add(tex_a)
    assert slot_a == 0
    # Atlas should be full at this point
    with pytest.raises(AllocatorException):
        atlas.add(tex_b)


def test_rebuild(ctx):
    """Build and atlas and rebuild it"""
    # 36 x 36
    tex_small = load_texture(":resources:images/topdown_tanks/treeGreen_small.png")
    # 64 x 64
    tex_big = load_texture(":resources:images/topdown_tanks/treeGreen_large.png")
    atlas = TextureAtlas((104, 104), border=1)
    slot_a, region_a = atlas.add(tex_big)
    slot_b, region_b = atlas.add(tex_small)
    region_a = atlas.get_region_info(tex_big.name)
    region_b = atlas.get_region_info(tex_small.name)

    # Re-build and check states
    atlas.rebuild()
    assert slot_a == atlas.get_texture_id(tex_big.name)
    assert slot_b == atlas.get_texture_id(tex_small.name)
    region_aa = atlas.get_region_info(tex_big.name)
    region_bb = atlas.get_region_info(tex_small.name)

    # The textures have switched places in the atlas and should
    # have the same left position
    assert region_a.texture_coordinates[0] == region_bb.texture_coordinates[0]
    # check that textures moved at the very least
    assert region_b.texture_coordinates[0] != region_bb.texture_coordinates[0]
    assert region_a.texture_coordinates[0] != region_aa.texture_coordinates[0]

    check_internals(atlas, 2)


def test_clear(ctx):
    """Clear the atlas"""
    atlas = TextureAtlas((200, 200))
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas.add(tex_a)
    atlas.add(tex_b)
    check_internals(atlas, 2)
    atlas.clear()
    check_internals(atlas, 0)


def test_to_image(ctx):
    """Convert atlas to image"""
    atlas = TextureAtlas((100, 100))
    img = atlas.to_image()
    assert img.mode == "RGBA"
    assert img.size == (100, 100)
    img = atlas.to_image(components=4)
    assert img.mode == "RGBA"
    assert img.size == (100, 100)
    img = atlas.to_image(components=3)
    assert img.mode == "RGB"
    assert img.size == (100, 100)


def test_calculate_minimum_size(ctx):
    """Calculate the min size for an atlas"""
    texture_paths = [
        ":resources:images/topdown_tanks/tankBlue_barrel1.png",
        ":resources:images/topdown_tanks/tankBlue_barrel1_outline.png",
        ":resources:images/topdown_tanks/tankBlue_barrel2.png",
        ":resources:images/topdown_tanks/tankBlue_barrel2_outline.png",
        ":resources:images/topdown_tanks/tankBlue_barrel3.png",
        ":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
        ":resources:images/topdown_tanks/tankBody_bigRed.png",
        ":resources:images/topdown_tanks/tankBody_bigRed_outline.png",
        ":resources:images/topdown_tanks/tankBody_blue.png",
        ":resources:images/topdown_tanks/tankBody_blue_outline.png",
        ":resources:images/topdown_tanks/tankBody_dark.png",
        ":resources:images/topdown_tanks/tankBody_darkLarge.png",
        ":resources:images/topdown_tanks/tankBody_darkLarge_outline.png",
        ":resources:images/topdown_tanks/tankBody_dark_outline.png",
        ":resources:images/topdown_tanks/tankBody_green.png",
        ":resources:images/topdown_tanks/tankBody_green_outline.png",
        ":resources:images/topdown_tanks/tankBody_huge.png",
        ":resources:images/topdown_tanks/tankBody_huge_outline.png",
        ":resources:images/topdown_tanks/tankBody_red.png",
        ":resources:images/topdown_tanks/tankSand_barrel3_outline.png",
        ":resources:images/topdown_tanks/tankGreen_barrel1_outline.png",
        ":resources:images/topdown_tanks/tankRed_barrel2_outline.png",
        ":resources:images/topdown_tanks/tank_sand.png",
        ":resources:images/topdown_tanks/tank_green.png",
        ":resources:images/topdown_tanks/tank_green.png",
        ":resources:images/topdown_tanks/tank_green.png",
    ]
    textures = []
    for path in texture_paths:
        textures.append(arcade.load_texture(path))

    size = TextureAtlas.calculate_minimum_size(textures)
    atlas = TextureAtlas(size, textures=textures)
    # We have two duplicate textures in the list
    check_internals(atlas, len(textures) - 2)
    assert size == (320, 320)

    textures = textures[:len(textures) // 2]
    size = TextureAtlas.calculate_minimum_size(textures)
    atlas = TextureAtlas(size, textures=textures)
    check_internals(atlas, len(textures))
    assert size == (192, 192)

    textures = textures[:len(textures) // 2]
    size = TextureAtlas.calculate_minimum_size(textures)
    atlas = TextureAtlas(size, textures=textures)
    check_internals(atlas, len(textures))
    assert size == (64, 64)

    # Empty list should at least create the minimum atlas
    size = TextureAtlas.calculate_minimum_size([])
    assert size == (128, 128)


def test_update_texture_image(ctx):
    """Test partial image updates"""
    # Create the smallest atlas possible without border
    atlas = TextureAtlas((64 * 3, 64), border=0)
    # Load 3 x 64 x 64 images
    tex_1 = arcade.load_texture(":resources:images/topdown_tanks/tileGrass1.png")
    tex_2 = arcade.load_texture(":resources:images/topdown_tanks/tileSand2.png")
    tex_3 = arcade.load_texture(":resources:images/topdown_tanks/tileGrass_roadCrossing.png")
    # Add to atlas
    atlas.add(tex_1)
    atlas.add(tex_2)
    atlas.add(tex_3)
    # Change the internal images of each texture
    tex_1.image = PIL.Image.new("RGBA", tex_1.image.size, (255, 0, 0, 255))
    tex_2.image = PIL.Image.new("RGBA", tex_1.image.size, (0, 255, 0, 255))
    tex_3.image = PIL.Image.new("RGBA", tex_1.image.size, (0, 0, 255, 255))
    # Update the images in the atlas
    atlas.update_texture_image(tex_1)
    atlas.update_texture_image(tex_2)
    atlas.update_texture_image(tex_3)
    # Test pixels one pixel in the middle of each texture to verify
    # the images was replaced with colored textures
    assert b'\xff\x00\x00\xff' == atlas.fbo.read(viewport=(32, 32, 1, 1), components=4)
    assert b'\x00\xff\x00\xff' == atlas.fbo.read(viewport=(96, 32, 1, 1), components=4)
    assert b'\x00\x00\xff\xff' == atlas.fbo.read(viewport=(160, 32, 1, 1), components=4)


def test_resize(ctx):
    """Attempt to resize the atlas"""
    atlas = TextureAtlas((50, 100), border=0, auto_resize=False)
    t1 = arcade.Texture("t1", image=PIL.Image.new("RGBA", (48, 48), (255, 0, 0, 255)))
    t2 = arcade.Texture("t2", image=PIL.Image.new("RGBA", (48, 48), (0, 255, 0, 255)))
    atlas.add(t1)
    atlas.add(t2)
    atlas.resize((50, 100))

    with pytest.raises(AllocatorException):
        atlas.resize((50, 99))

    # Resize past max size
    atlas = TextureAtlas((50, 50), border=0)
    atlas._max_size = 60, 60
    t1 = arcade.Texture("t1", image=PIL.Image.new("RGBA", (50, 50), (255, 0, 0, 255)))
    t2 = arcade.Texture("t2", image=PIL.Image.new("RGBA", (50, 50), (0, 255, 0, 255)))
    atlas.add(t1)
    with pytest.raises(AllocatorException):
        atlas.add(t2)


def test_create_from_texture_sequence(ctx):
    tex_1 = arcade.load_texture(":resources:images/topdown_tanks/tileGrass1.png")
    tex_2 = arcade.load_texture(":resources:images/topdown_tanks/tileSand2.png")
    tex_3 = arcade.load_texture(":resources:images/topdown_tanks/tileGrass_roadCrossing.png")
    atlas = arcade.TextureAtlas.create_from_texture_sequence([tex_1, tex_2, tex_3])
    assert atlas.size == (192, 192)


def test_max_size(ctx):
    """The maximum atlas size should at least be 8192 (2^13)"""
    atlas = TextureAtlas((100, 100))
    assert atlas.max_size[0] >= 8192
    assert atlas.max_size[1] >= 8192

    # Resize the atlas to something any hardware wouldn't support
    with pytest.raises(ValueError):
        atlas.resize((100_000, 100_000))
    with pytest.raises(ValueError):
        atlas.resize((100, 100_000))
    with pytest.raises(ValueError):
        atlas.resize((100_000, 100))

    # Create an unreasonable sized atlas
    with pytest.raises(ValueError):
        TextureAtlas((100_000, 100_000))
