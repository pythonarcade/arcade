import array
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


def test_default_properties(ctx):
    """Test textures"""
    texture = ctx.texture((100, 200), components=4)
    assert texture.ctx == ctx
    assert texture.glo.value > 0
    assert texture.components == 4
    assert texture.width == 100
    assert texture.height == 200
    assert texture.size == (100, 200)
    assert texture.filter == (ctx.LINEAR, ctx.LINEAR)
    assert texture.wrap_x == ctx.REPEAT
    assert texture.wrap_y == ctx.REPEAT
    assert repr(texture).startswith('<Texture')


def test_properties(ctx):
    texture = ctx.texture((100, 200), components=4)

    texture.filter = ctx.NEAREST_MIPMAP_NEAREST, ctx.NEAREST
    assert texture.filter == (ctx.NEAREST_MIPMAP_NEAREST, ctx.NEAREST)
    with pytest.raises(ValueError):
        texture.filter = None

    texture.wrap_x = ctx.CLAMP_TO_BORDER
    texture.wrap_y = ctx.CLAMP_TO_EDGE
    assert texture.wrap_x == ctx.CLAMP_TO_BORDER
    assert texture.wrap_y == ctx.CLAMP_TO_EDGE


def test_use(ctx):
    texture = ctx.texture((100, 200), components=4)
    texture.use(0)
    texture.use(1)
    texture.use(2)


def test_mipmaps(ctx):
    texture = ctx.texture((100, 200), components=4)
    texture.build_mipmaps(0, 3)
    texture.build_mipmaps()


def test_write_read(ctx):
    # Writing to texture
    in_data = array.array('f', list(range(40))).tobytes()
    texture = ctx.texture((10, 1), components=4, dtype='f4')
    texture.write(in_data)
    out_data = texture.read()
    assert len(out_data) == 40 * 4
    assert out_data == in_data

    # Write buffer
    buffer = ctx.buffer(data=in_data)
    texture.write(buffer)
    assert texture.read() == in_data

    # Write with viewport
    in_data = array.array('f', list(range(20))).tobytes()
    texture.write(in_data, viewport=(5, 1))
    texture.write(in_data, viewport=(0, 0, 5, 1))
    # TODO: Check results
    with pytest.raises(ValueError):
        texture.write(in_data, viewport=(0, 0, 5))
    with pytest.raises(ValueError):
        texture.write(in_data, viewport=(1,))

    with pytest.raises(TypeError):
        texture.write('moo')

    # TODO: Test LODs


def test_creation_failed(ctx):
    # Make an unreasonable texture
    with pytest.raises(Exception):
        ctx.texture((100_000, 1), components=1)

    with pytest.raises(ValueError):
        ctx.texture((10, 10), components=4, dtype='moo')


def test_components(ctx):
    # Create textures of different components
    c1 = ctx.texture((10, 10), components=1)
    c2 = ctx.texture((10, 10), components=2)
    c3 = ctx.texture((10, 10), components=3)
    c4 = ctx.texture((10, 10), components=4)
    assert c1.components == 1
    assert c2.components == 2
    assert c3.components == 3
    assert c4.components == 4

    # Wrong number of components
    with pytest.raises(ValueError):
        ctx.texture((10, 10), components=5)


def test_texture_dtypes(ctx):
    # Create textures using different formats
    def test_texture_format(dtype):
        for components in range(1, 5):
            texture = ctx.texture((10, 10), components=components, dtype=dtype)
            assert texture.ctx == ctx
            assert texture.glo.value > 0
            assert texture.components == components
            assert texture.dtype == dtype

    test_texture_format('f1')
    test_texture_format('f2')
    test_texture_format('f4')

    test_texture_format('i1')
    test_texture_format('i2')
    test_texture_format('i4')

    test_texture_format('u1')
    test_texture_format('u2')
    test_texture_format('u4')
