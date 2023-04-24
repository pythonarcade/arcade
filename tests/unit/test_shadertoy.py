import pytest
from arcade.experimental import Shadertoy, ShadertoyBuffer
from arcade.gl import Program, Texture2D

def glsl(inner: str):
    return (
        "void mainImage(out vec4 fragColor, in vec2 fragCoord)\n"
        "{\n"
        f"{inner}\n"
        "}\n"
    )


def test_create_from_file(ctx):
    st = Shadertoy.create_from_file((100, 200), ":resources:shaders/shadertoy/crt_monitor_filter.glsl")
    check_internals(st)

    with pytest.raises(FileNotFoundError):
        st = Shadertoy.create_from_file((100, 200), "something.glsl")

def test_create(ctx):
    st = Shadertoy((120, 130), glsl("fragColor = vec4(1.0, 1.0, 1.0, 1.0);"))
    check_internals(st)

def test_buffers(ctx):
    st = Shadertoy((120, 130), glsl("fragColor = vec4(1.0, 1.0, 1.0, 1.0);"))
    buffer_a = st.create_buffer(glsl("fragColor = vec4(1.0, 0.0, 0.0, 1.0);"))
    buffer_b = st.create_buffer(glsl("fragColor = vec4(0.0, 1.0, 0.0, 1.0);"))
    buffer_c = st.create_buffer(glsl("fragColor = vec4(0.0, 0.0, 1.0, 1.0);"))
    buffer_d = st.create_buffer(glsl("fragColor = vec4(0.0, 0.0, 0.0, 1.0);"))
    st.buffer_a = buffer_a
    st.buffer_b = buffer_b
    st.buffer_c = buffer_c
    st.buffer_d = buffer_d
    assert st.buffer_a == buffer_a
    assert st.buffer_b == buffer_b
    assert st.buffer_c == buffer_c
    assert st.buffer_d == buffer_d

    buffer_a = ShadertoyBuffer(st.size, glsl("fragColor = vec4(1.0, 0.0, 0.0, 1.0);"))
    buffer_b = ShadertoyBuffer(st.size, glsl("fragColor = vec4(0.0, 1.0, 0.0, 1.0);"))
    buffer_c = ShadertoyBuffer(st.size, glsl("fragColor = vec4(0.0, 0.0, 1.0, 1.0);"))
    buffer_d = ShadertoyBuffer(st.size, glsl("fragColor = vec4(0.0, 0.0, 0.0, 1.0);"))
    st.buffer_a = buffer_a
    st.buffer_b = buffer_b
    st.buffer_c = buffer_c
    st.buffer_d = buffer_d
    assert st.buffer_a == buffer_a
    assert st.buffer_b == buffer_b
    assert st.buffer_c == buffer_c
    assert st.buffer_d == buffer_d

def test_getters_setters(ctx):
    st = Shadertoy((120, 130), glsl("fragColor = vec4(1.0, 1.0, 1.0, 1.0);"))
    assert st.size == (120, 130)
    st.mouse_position = 10, 20
    assert st.mouse_position == (10, 20)
    st.mouse_buttons = 1, 2
    assert st.mouse_buttons == (1, 2)
    st.frame = 22
    assert st.frame == 22
    st.time_delta = 0.1
    assert st.time_delta == 0.1
    st.delta_time = 0.2
    assert st.delta_time == 0.2
    st.time = 100.0
    assert st.time == 100.0
    st.frame_rate = 60.0
    assert st.frame_rate == 60.0
    st.channel_time[0] = 1.0
    st.channel_time[1] = 2.0
    st.channel_time[2] = 3.0
    st.channel_time[3] = 4.0
    assert st.channel_time == [1.0, 2.0, 3.0, 4.0]

    # Channel resolution
    tx1 = ctx.texture((10, 11))
    tx2 = ctx.texture((12, 13))
    tx3 = ctx.texture((14, 15))
    tx4 = ctx.texture((16, 17))
    st.channel_0 = tx1
    st.channel_1 = tx2
    st.channel_2 = tx3
    st.channel_3 = tx4
    assert st._channel_resolution == [
        10, 11, 1,
        12, 13, 1,
        14, 15, 1,
        16, 17, 1,
    ]


def check_internals(st: Shadertoy):
    assert isinstance(st.program, Program)
    assert isinstance(st.size, tuple)
    assert len(st.size) == 2

    # Default values
    assert st.time == 0
    assert st.time_delta == 0
    assert st.frame == 0
    assert st.mouse_position == (0, 0)
    assert st.mouse_buttons == (0, 0)

    # Types assigned to channels
    assert st.channel_0 is None or isinstance(st.channel_0, Texture2D)
    assert st.channel_1 is None or isinstance(st.channel_1, Texture2D)
    assert st.channel_2 is None or isinstance(st.channel_2, Texture2D)
    assert st.channel_3 is None or isinstance(st.channel_3, Texture2D)
