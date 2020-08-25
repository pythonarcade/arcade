import pytest

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    window.use()
    window.close()


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
    """Clear framebuffer with different mehtods and ensure binding do not change"""
    ctx.window.use()
    fb = create(ctx, 10, 20, components=4)
    fb.clear()
    fb.clear(color=(0, 0, 0, 0), normalized=True)
    fb.clear(color=(0, 0, 0), normalized=True)
    fb.clear(color=arcade.csscolor.AZURE)
    fb.clear(color=(0, 0, 0))
    fb.clear(color=(0, 0, 0, 0))
    assert ctx.active_framebuffer == ctx.screen


def test_multi_attachment(ctx):
    """Create framebuffers with multiple layers"""
    for i in range(ctx.limits.MAX_COLOR_ATTACHMENTS):
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


def test_read(twm, ctx):
    fb = create(ctx, 2, 2, components=4)
    fb.clear(color=(1, 1, 0, 1), normalized=True)
    data = fb.read(components=4)
    assert len(data) == 16
    if not twm:
        assert data == b'\xff\xff\x00\xff' * 4

    # FIXME: needs read alignment
    # data = fb.read(components=3)
    # assert len(data) == 12
    # assert data == b'\xff\xff\x00' * 4
