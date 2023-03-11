import array
import pytest


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
    """poke some texture properties"""
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
    """Writing to texture"""
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
    assert isinstance(texture.read(), bytes)

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

    # Supply too little data
    texture = ctx.texture((2, 2), components=4, dtype='f1')
    with pytest.raises(ValueError):
        texture.write(b'\x00\x00', viewport=(0, 0, 1, 1))

    # Supply too much data
    texture = ctx.texture((2, 2), components=4, dtype='f1')
    with pytest.raises(ValueError):
        texture.write(b'\x00' * 5, viewport=(0, 0, 1, 1))

    # TODO: Test LODs


def test_write_buffer_protocol(ctx):
    """Test creating texture from data using buffer protocol"""
    # In constructor
    data = array.array('B', [0, 0, 255, 255])
    texture = ctx.texture((2, 2), components=1, data=data)
    assert texture.read() == data.tobytes()
    # Using write()
    texture = ctx.texture((2, 2), components=1)
    texture.write(data)
    assert texture.read() == data.tobytes()


def test_creation_failed(ctx):
    """Make an unreasonable texture"""
    with pytest.raises(Exception):
        ctx.texture((100_000, 1), components=1)

    with pytest.raises(ValueError):
        ctx.texture((10, 10), components=4, dtype='moo')


def test_components(ctx):
    """Create textures of different components"""
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
    """Create textures using different formats"""
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


def test_depth(ctx):
    """Create depth texture"""
    tex = ctx.depth_texture((100, 100))
    assert tex.size == (100, 100)
    assert tex.compare_func == '<='


def test_byte_size(ctx):
    """Ensure texture byte size is properly reported"""
    # RBGA8
    texture = ctx.texture((4, 4), components=1)
    assert texture.byte_size == 16
    texture = ctx.texture((4, 4), components=2)
    assert texture.byte_size == 32
    texture = ctx.texture((4, 4), components=3)
    assert texture.byte_size == 48
    texture = ctx.texture((4, 4), components=4)
    assert texture.byte_size == 64

    # 16 bit float
    texture = ctx.texture((4, 4), components=1, dtype='f2')
    assert texture.byte_size == 32
    texture = ctx.texture((4, 4), components=4, dtype='f2')
    assert texture.byte_size == 128

    # 32 bit float
    texture = ctx.texture((4, 4), components=1, dtype='f4')
    assert texture.byte_size == 64
    texture = ctx.texture((4, 4), components=4, dtype='f4')
    assert texture.byte_size == 256

    # 16 bit integer
    texture = ctx.texture((4, 4), components=1, dtype='i2')
    assert texture.byte_size == 32
    texture = ctx.texture((4, 4), components=4, dtype='i2')
    assert texture.byte_size == 128

    # 32 bit float
    texture = ctx.texture((4, 4), components=1, dtype='i4')
    assert texture.byte_size == 64
    texture = ctx.texture((4, 4), components=4, dtype='i4')
    assert texture.byte_size == 256

def test_resize(ctx):
    tex = ctx.texture((100, 100), components=4)
    assert tex.size == (100, 100)
    assert len(tex.read()) == 100 * 100 * 4

    tex.resize((200, 200))
    assert tex.size == (200, 200)
    assert len(tex.read()) == 200 * 200 * 4


def test_swizzle(ctx):
    tex = ctx.texture((10, 10), components=4)
    assert tex.swizzle == "RGBA"

    tex.swizzle = "ABGR"
    assert tex.swizzle == "ABGR"
    tex.swizzle = "0000"
    assert tex.swizzle == "0000"
    tex.swizzle = "1111"
    assert tex.swizzle == "1111"
    tex.swizzle = "RGBA"
    assert tex.swizzle == "RGBA"

    # Set swizzle with wrong size
    with pytest.raises(ValueError):
        tex.swizzle = "AAAAA"

    # Set sizzle with non-string type
    with pytest.raises(ValueError):
        tex.swizzle = 0
