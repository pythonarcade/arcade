"""
Low level tests for OpenGL 3.3 wrappers.
"""
import pytest
from pyglet.math import Mat4


def test_ctx(ctx):
    if ctx.gl_api == "gl":
        assert ctx.gl_version >= (3, 3)
    elif ctx.gl_api == "gles":
        assert ctx.gl_version >= (3, 1)
    else:
        raise ValueError(f"Unsupported api: {ctx.gl_api}")

    assert ctx.info.MAX_TEXTURE_SIZE >= 4096
    assert ctx.info.MAX_ARRAY_TEXTURE_LAYERS >= 256

    assert ctx.blend_func == ctx.BLEND_DEFAULT
    ctx.blend_func = ctx.BLEND_PREMULTIPLIED_ALPHA
    assert ctx.blend_func == ctx.BLEND_PREMULTIPLIED_ALPHA


def test_viewport(ctx):
    vp = 0, 0, 100, 100
    ctx.viewport = vp
    assert ctx.viewport == vp


def test_projection(window):
    ctx = window.ctx
    assert ctx.projection_2d == (0, window.width, 0, window.height)
    ctx.projection_2d = (1, 10, 2, 11)
    assert ctx.projection_2d == (1, 10, 2, 11)

    with pytest.raises(ValueError):
        ctx.projection_2d = "moo"

    with pytest.raises(ValueError):
        ctx.projection_2d = 1, 2, 3, 4, 5


def test_projection_matrix(window):
    """Test setting projection matrix directly"""
    window.ctx.projection_2d_matrix = Mat4()

    with pytest.raises(ValueError):
        window.ctx.projection_2d_matrix = "moo"


def test_point_size(ctx):
    """Attempt to set point size"""
    assert ctx.point_size == 1.0
    ctx.point_size = 2.0
    assert ctx.point_size == 2.0


def test_primitive_restart(ctx):
    """Get or set primitive restart"""
    assert ctx.primitive_restart_index == -1
    ctx.primitive_restart_index = -2
    assert ctx.primitive_restart_index == -2


def test_enable_disable(ctx):
    """Try enable and disable states manually"""
    assert ctx.is_enabled(ctx.BLEND)
    ctx.enable_only()
    assert len(ctx._flags) == 0

    ctx.enable(ctx.BLEND)
    ctx.enable(ctx.BLEND, ctx.DEPTH_TEST, ctx.CULL_FACE)
    assert ctx.is_enabled(ctx.BLEND)
    assert ctx.is_enabled(ctx.DEPTH_TEST)
    assert ctx.is_enabled(ctx.CULL_FACE)

    ctx.disable(ctx.BLEND)
    assert ctx.is_enabled(ctx.BLEND) is False
    assert len(ctx._flags) == 2

    ctx.enable_only(ctx.BLEND, ctx.CULL_FACE, ctx.DEPTH_TEST, ctx.PROGRAM_POINT_SIZE)


def test_enabled(ctx):
    """Enabled only context manager"""    
    assert ctx.is_enabled(ctx.BLEND)
    assert not ctx.is_enabled(ctx.DEPTH_TEST)

    with ctx.enabled(ctx.DEPTH_TEST):
        assert ctx.is_enabled(ctx.BLEND)
        assert ctx.is_enabled(ctx.DEPTH_TEST)

    assert ctx.is_enabled(ctx.BLEND)
    assert not ctx.is_enabled(ctx.DEPTH_TEST)


def test_enabled_only(ctx):
    """Enabled only context manager"""    
    assert ctx.is_enabled(ctx.BLEND)

    with ctx.enabled_only(ctx.DEPTH_TEST):
        assert not ctx.is_enabled(ctx.BLEND)
        assert ctx.is_enabled(ctx.DEPTH_TEST)

    assert ctx.is_enabled(ctx.BLEND)
    assert not ctx.is_enabled(ctx.DEPTH_TEST)


def test_load_texture(ctx):
    # Default flipped and read value of corner pixel
    texture = ctx.load_texture(":resources:images/test_textures/test_texture.png", build_mipmaps=True)
    assert texture.read()[:4] == b'\x00\x00\xff\xff'  # Blue

    # Don't flip the texture
    texture = ctx.load_texture(":resources:images/test_textures/test_texture.png", flip=False, build_mipmaps=True)
    assert texture.read()[:4] == b'\xff\x00\x00\xff'  # Red
