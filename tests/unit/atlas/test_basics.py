import PIL
import pytest
from pyglet.image.atlas import AllocatorException
import arcade
from arcade import TextureAtlas, load_texture
from arcade.gl import Texture2D, Framebuffer


def test_create(ctx, common):
    atlas = TextureAtlas((100, 200))
    assert atlas.width == 100
    assert atlas.height == 200
    assert atlas.size == (100, 200)
    assert atlas.border == 1
    assert atlas.auto_resize is True
    assert isinstance(atlas.max_size, tuple)
    assert atlas.max_size > (0, 0)
    assert isinstance(atlas.texture, Texture2D)
    assert isinstance(atlas.image_uv_texture, Texture2D)
    assert isinstance(atlas.texture_uv_texture, Texture2D)
    assert isinstance(atlas.fbo, Framebuffer)
    assert atlas._image_uv_data_changed is True
    assert atlas._texture_uv_data_changed is True
    common.check_internals(atlas, num_images=0, num_textures=0)


def test_create_from_texture_sequence(ctx):
    tex_1 = arcade.load_texture(":resources:images/topdown_tanks/tileGrass1.png")
    tex_2 = arcade.load_texture(":resources:images/topdown_tanks/tileSand2.png")
    tex_3 = arcade.load_texture(":resources:images/topdown_tanks/tileGrass_roadCrossing.png")
    atlas = arcade.TextureAtlas.create_from_texture_sequence([tex_1, tex_2, tex_3])
    assert atlas.size == (192, 192)


def test_add(ctx, common):
    """Test adding textures to atlas"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = TextureAtlas((200, 200), border=1)
    slot_a, region_a = atlas.add(tex_a)
    slot_b, region_b = atlas.add(tex_b)
    assert slot_a == 0
    assert slot_b == 1
    common.check_internals(atlas, num_images=2, num_textures=2)
    # Add existing textures
    assert slot_a == atlas.add(tex_a)[0]
    assert slot_b == atlas.add(tex_b)[0]
    common.check_internals(atlas, num_images=2, num_textures=2)
    atlas.use_uv_texture()


def test_remove(ctx, common):
    """Remove textures from atlas"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = TextureAtlas((200, 200), border=1)
    slot_a, region_a = atlas.add(tex_a)
    slot_b, region_b = atlas.add(tex_b)
    common.check_internals(atlas, num_images=2, num_textures=2)
    atlas.remove(tex_a)
    common.check_internals(atlas, num_images=1, num_textures=1)
    atlas.rebuild()
    common.check_internals(atlas, num_images=1, num_textures=1)
    atlas.remove(tex_b)
    common.check_internals(atlas, num_images=0, num_textures=0)
    atlas.rebuild()
    common.check_internals(atlas,  num_images=0, num_textures=0)


def test_add_overflow(ctx):
    """Ensure AllocatorException is raised when atlas is full"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = TextureAtlas((100, 100), auto_resize=False)
    slot_a, region = atlas.add(tex_a)
    assert slot_a == 0
    # Atlas should be full at this point
    with pytest.raises(AllocatorException):
        atlas.add(tex_b)


def test_clear(ctx, common):
    """Clear the atlas"""
    atlas = TextureAtlas((200, 200))
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas.add(tex_a)
    atlas.add(tex_b)
    common.check_internals(atlas, num_images=2, num_textures=2)
    atlas.clear()
    common.check_internals(atlas, num_images=0, num_textures=0)


def test_max_size(ctx):
    """The maximum atlas size should at least be 8192 (2^13)"""
    atlas = TextureAtlas((100, 100))
    assert atlas.max_size[0] >= 4096
    assert atlas.max_size[1] >= 4096

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

    # Re-build and check states
    atlas.rebuild()
    assert slot_a == atlas.get_texture_id(tex_big.atlas_name)
    assert slot_b == atlas.get_texture_id(tex_small.atlas_name)
    region_aa = atlas.get_texture_region_info(tex_big.atlas_name)
    region_bb = atlas.get_texture_region_info(tex_small.atlas_name)

    # The textures have switched places in the atlas and should
    # have the same left position
    assert region_a.texture_coordinates[0] == region_bb.texture_coordinates[0]
    # check that textures moved at the very least
    assert region_b.texture_coordinates[0] != region_bb.texture_coordinates[0]
    assert region_a.texture_coordinates[0] != region_aa.texture_coordinates[0]

    common.check_internals(atlas, num_images=2, num_textures=2)


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
    atlas = TextureAtlas((50, 100), border=1, auto_resize=False)
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (255, 0, 0, 255)))
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (48, 48), (0, 255, 0, 255)))
    atlas.add(t1)
    atlas.add(t2)
    atlas.resize((50, 100))

    # Make atlas so small the current textures won't fit
    with pytest.raises(AllocatorException):
        atlas.resize((50, 99))

    # Resize past max size
    atlas = TextureAtlas((50, 50), border=0)
    atlas._max_size = 60, 60
    t1 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (255, 0, 0, 255)))
    t2 = arcade.Texture(image=PIL.Image.new("RGBA", (50, 50), (0, 255, 0, 255)))
    atlas.add(t1)
    with pytest.raises(AllocatorException):
        atlas.add(t2)


def test_uv_buffers_after_change(ctx):
    capacity = 2
    atlas = TextureAtlas((100, 100), capacity=capacity)

    def buf_check(atlas):
        # Check that the byte data of the uv data and texture is the same
        assert len(atlas._image_uv_data) == 4096 * capacity * 8
        assert len(atlas._image_uv_data.tobytes()) == len(atlas._image_uv_texture.read())
        assert len(atlas._texture_uv_data) == 4096 * capacity * 8
        assert len(atlas._texture_uv_data.tobytes()) == len(atlas._texture_uv_texture.read())

    buf_check(atlas)
    atlas.resize((200, 200))
    buf_check(atlas)
    atlas.rebuild()
    buf_check(atlas)
    atlas.clear()
    buf_check(atlas)
