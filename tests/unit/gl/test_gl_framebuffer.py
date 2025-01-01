import pytest
import arcade


def create(ctx, width, height, components=4, layers=1, dtype='f1'):
    layers = [ctx.texture((width, height), components=components, dtype=dtype) for _ in range(layers)]
    return ctx.framebuffer(color_attachments=layers)


def test_properties(ctx):
    """Test framebuffers"""
    fb = create(ctx, 10, 20, components=4)
    assert fb.ctx == ctx
    assert fb.width == 10
    assert fb.height == 20
    assert fb.size == (10, 20)
    assert fb.samples == 0
    assert fb.viewport == (0, 0, 10, 20)
    assert fb.depth_attachment is None
    assert fb.depth_mask is True
    assert repr(fb).startswith('<Framebuffer')


def test_viewport(ctx):
    """Test viewport"""
    fb = create(ctx, 10, 20, components=4)
    fb.use()
    fb.viewport = (1, 2, 3, 4)
    assert fb.viewport == (1, 2, 3, 4)

    with pytest.raises(ValueError):
        fb.viewport = 0

    with pytest.raises(ValueError):
        fb.viewport = 0, 0, 0

    with pytest.raises(ValueError):
        fb.viewport = 0, 0, 0, 0, 0


def test_binding(ctx):
    """Ensure bind tracking works"""
    ctx.window.use()
    fb = create(ctx, 10, 20, components=4)
    fb.use()
    fb.use()
    assert ctx.active_framebuffer == fb
    ctx.window.use()
    ctx.window.use()  # Twice to trigger bind check
    assert ctx.active_framebuffer == ctx.screen


def test_clear(ctx):
    """Clear framebuffer with different methods and ensure binding do not change"""
    ctx.window.use()
    fb = create(ctx, 10, 20, components=4)
    fb.clear()
    fb.clear(color_normalized=(0, 0, 0, 0))
    fb.clear(color_normalized=(0, 0, 0))
    fb.clear(color=arcade.csscolor.AZURE)
    fb.clear(color=(0, 0, 0))
    fb.clear(color=(0, 0, 0, 0))
    assert ctx.active_framebuffer == ctx.screen


def test_clear_viewport(ctx):
    fb = create(ctx, 4, 4, components=1)
    fb.clear(color=(64, 64, 64, 64))
    assert fb.read(components=1) == b'\x40' * 16

    # Clear only the center pixels and verify that the rest is unchanged
    fb.clear()
    fb.clear(color=(255, 255, 255, 255), viewport=(1, 1, 2, 2))
    expected = (
        b'\x00\x00\x00\x00'
        b'\x00\xff\xff\x00'
        b'\x00\xff\xff\x00'
        b'\x00\x00\x00\x00'
    )
    assert bytes(fb.read(components=1)) == expected


def test_clear_with_scissor(ctx):
    fb = create(ctx, 4, 4, components=1)
    fb.clear()
    fb.scissor = 1, 1, 2, 2
    fb.clear(color=(255, 255, 255, 255))
    assert bytes(fb.read(components=1)) == b'\xff' * 16


def test_multi_attachment(ctx):
    """Create framebuffers with multiple layers"""
    for i in range(ctx.info.MAX_COLOR_ATTACHMENTS):
        fb = create(ctx, 10, 10, components=4, layers=i + 1)
        assert len(fb.color_attachments) == i + 1
        assert fb.glo.value > 0


def test_depth_mask(ctx):
    fb = create(ctx, 10, 10)
    fb.use()
    assert fb.depth_mask is True
    fb.depth_mask = False
    assert fb.depth_mask is False


def test_incomplete(ctx):
    """Create empty framebuffer. This might be possible in the future?"""
    with pytest.raises(ValueError):
        ctx.framebuffer()


def test_varying_attachment_size(ctx):
    """Varying attachment sizes not supported for now"""
    fb = create(ctx, 10, 20, components=4)
    with pytest.raises(ValueError):
        ctx.framebuffer(
            color_attachments=[
                ctx.texture((10, 10), components=4),
                ctx.texture((10, 11), components=4)])


def test_read(ctx):
    fb = create(ctx, 2, 2, components=4)
    fb.clear(color=(255, 255, 0, 255))
    data = fb.read(components=4)
    assert len(data) == 16
    assert isinstance(fb.read(), bytes)

    # Read 3 components
    data = fb.read(components=3)
    assert len(data) == 12
    assert data == b'\xff\xff\x00' * 4

    # Read from f2 texture
    fb = create(ctx, 2, 2, components=1, layers=1, dtype="f2")
    data = fb.read(components=1, dtype="f2")
    assert len(data) == 2 * 2 * 2

    # Read from f4 texture
    fb = create(ctx, 2, 2, components=1, layers=1, dtype="f4")
    data = fb.read(components=1, dtype="f4")
    assert len(data) == 2 * 2 * 4

    # Read from i2 texture
    fb = create(ctx, 2, 2, components=1, layers=1, dtype="i2")
    data = fb.read(components=1, dtype="i2")
    assert len(data) == 2 * 2 * 2

def test_resize(ctx):
    tex = ctx.texture((100, 100), components=4)
    fbo = ctx.framebuffer(color_attachments=[tex])
    assert fbo.size == tex.size
    tex.resize((200, 200))
    assert tex.size == (200, 200)
    fbo.resize()
    assert fbo.size == tex.size
    assert fbo.viewport == (0, 0, *fbo.size)

def test_read_screen_framebuffer(window):
    components = 3
    data = window.ctx.screen.read(components=components)
    assert isinstance(data, bytes)
    w, h = window.get_framebuffer_size()
    assert len(data) == w * h * components
