import pytest
from arcade.gl import BufferDescription


def test_buffer_description(ctx):
    # TODO: components > 4
    # TODO: padding
    buffer = ctx.buffer(reserve=4 * 8)
    attribute_names = ['in_vert', 'in_uv']
    descr = BufferDescription(
        buffer,
        '2f 2f',
        attribute_names,
    )
    assert descr.num_vertices == 2
    assert descr.buffer == buffer
    assert descr.attributes == attribute_names
    assert descr.instanced is False
    assert len(descr.formats) == 2
    assert descr.stride == 16

    # Buffer parameter not a buffer
    with pytest.raises(ValueError):
        BufferDescription("test", "2f", ["pos"])

    # Different lengths of attribute names and formats
    with pytest.raises(ValueError):
        BufferDescription(buffer, "2f", ["pos", "uv"])

    # Different lengths when padding is used
    with pytest.raises(ValueError):
        BufferDescription(buffer, "2x", ["pos"])

    # Invalid format
    with pytest.raises(ValueError):
        BufferDescription(buffer, "2g", ["pos"])
