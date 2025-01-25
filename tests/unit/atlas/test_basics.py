import PIL.Image
import pytest
from pyglet.image.atlas import AllocatorException
import arcade
from arcade import DefaultTextureAtlas, load_texture
from arcade.gl import Texture2D, Framebuffer


def test_create(ctx, common):
    atlas = DefaultTextureAtlas((100, 200))
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
    common.check_internals(atlas, images=0, textures=0, unique_textures=0)


def test_create_add(ctx, common):
    """Create atlas with initial textures"""
    texture = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    atlas = DefaultTextureAtlas((100, 200), textures=[texture])
    common.check_internals(atlas, images=1, textures=1, unique_textures=1)


def test_add(ctx, common):
    """Test adding textures to atlas"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = DefaultTextureAtlas((200, 200), border=1)
    slot_a, region_a = atlas.add(tex_a)
    slot_b, region_b = atlas.add(tex_b)
    assert slot_a == 0
    assert slot_b == 1
    common.check_internals(atlas, images=2, textures=2, unique_textures=2)
    # Add existing textures
    assert slot_a == atlas.add(tex_a)[0]
    assert slot_b == atlas.add(tex_b)[0]
    common.check_internals(atlas, images=2, textures=2, unique_textures=2)
    atlas.use_uv_texture()


def test_remove(ctx, common):
    """Default atlas doesn't support remove"""
    atlas = DefaultTextureAtlas((200, 200))
    with pytest.raises(RuntimeError):
        atlas.remove("object")


def test_add_overflow(ctx):
    """Ensure AllocatorException is raised when atlas is full"""
    tex_a = load_texture(":resources:onscreen_controls/shaded_dark/a.png")
    tex_b = load_texture(":resources:onscreen_controls/shaded_dark/b.png")
    atlas = DefaultTextureAtlas((100, 100), auto_resize=False)
    slot_a, region = atlas.add(tex_a)
    assert slot_a == 0
    # Atlas should be full at this point
    with pytest.raises(AllocatorException):
        atlas.add(tex_b)


def test_max_size(ctx):
    """The maximum atlas size should at least be 8192 (2^13)"""
    atlas = DefaultTextureAtlas((100, 100))
    assert atlas.max_size[0] >= 4096
    assert atlas.max_size[1] >= 4096

    # Resize the atlas to something any hardware wouldn't support
    with pytest.raises(Exception):
        atlas.resize((100_000, 100_000))
    with pytest.raises(Exception):
        atlas.resize((100, 100_000))
    with pytest.raises(Exception):
        atlas.resize((100_000, 100))

    # Create an unreasonable sized atlas
    with pytest.raises(Exception):
        DefaultTextureAtlas((100_000, 100_000))


def test_to_image(ctx):
    """Convert atlas to image"""
    atlas = DefaultTextureAtlas((100, 100))
    img = atlas.to_image()
    assert img.mode == "RGBA"
    assert img.size == (100, 100)
    img = atlas.to_image(components=4)
    assert img.mode == "RGBA"
    assert img.size == (100, 100)
    img = atlas.to_image(components=3)
    assert img.mode == "RGB"
    assert img.size == (100, 100)


def test_update_texture_image(ctx):
    """Test partial image updates"""
    # Create the smallest atlas possible without border
    atlas = DefaultTextureAtlas((64 * 3, 64), border=0)
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


def test_uv_buffers_after_change(ctx):
    capacity = 2
    atlas = DefaultTextureAtlas((100, 100), capacity=capacity)

    def buf_check(atlas):
        # Check that the byte data of the uv data and texture is the same
        assert len(atlas._image_uvs._data) == 4096 * capacity * 8
        assert len(atlas._image_uvs._data.tobytes()) == len(atlas._image_uvs.texture.read())
        assert len(atlas._texture_uvs._data) == 4096 * capacity * 8
        assert len(atlas._texture_uvs._data.tobytes()) == len(atlas._texture_uvs.texture.read())

    buf_check(atlas)
    atlas.resize((200, 200))
    buf_check(atlas)
    atlas.rebuild()
    buf_check(atlas)
