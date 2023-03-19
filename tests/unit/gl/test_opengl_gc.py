import gc
import arcade
from arcade.gl import geometry

COMPUTE_SHADER_SOURCE = """
#version 430

layout(local_size_x=16, local_size_y=16) in;

uniform vec2 screen_size;
uniform vec2 force;
uniform float frame_time;

struct Ball
{
    vec4 pos;
    vec4 vel;
    vec4 col;
};

layout(std430, binding=0) buffer balls_in
{
    Ball balls[];
} In;
layout(std430, binding=1) buffer balls_out
{
    Ball balls[];
} Out;

void main()
{
    int x = int(gl_GlobalInvocationID);
    Ball in_ball = In.balls[x];
    Out.balls[x] = in_ball;
}
"""

VERTEX_SRC = """
#version 330

in vec3 in_position;

void main() {
    gl_Position = vec4(in_position, 1.0);
}
"""

FRAGMENT_SRC = """
#version 330

out vec4 fragColor;

void main() {
    fragColor = vec4(1.0);
}
"""


def test_context_gc(ctx):
    ctx.gc_mode = "context_gc"
    gc.collect()
    ctx.gc()
    create_resources(ctx)
    gc.collect()
    ctx.gc()


def test_auto_gc(ctx):
    gc.collect()
    ctx.gc()
    ctx.gc_mode = "auto"
    create_resources(ctx)


def create_resources(ctx: arcade.ArcadeContext):
    # Texture
    created, freed = ctx.stats.texture
    texture = ctx.texture((10, 10))
    assert ctx.stats.texture == (created + 1, freed)
    texture = None
    gc.collect()
    if ctx.gc_mode == "context_gc":
        collected = ctx.gc()
        assert collected == 1
    assert ctx.stats.texture == (created + 1, freed + 1)

    # Buffer
    created, freed = ctx.stats.buffer
    buf = ctx.buffer(reserve=1024)
    assert ctx.stats.buffer == (created + 1, freed)
    buf = None
    gc.collect()
    if ctx.gc_mode == "context_gc":
        collected = ctx.gc()
        assert collected == 1
    assert ctx.stats.buffer == (created + 1, freed + 1)

    # Framebuffer
    created, freed = ctx.stats.framebuffer
    fb = ctx.framebuffer(
        color_attachments=[ctx.texture((1024, 1024))],
        depth_attachment=ctx.depth_texture((1024, 1024)),
    )
    assert ctx.stats.framebuffer == (created + 1, freed)
    fb = None
    gc.collect()
    if ctx.gc_mode == "context_gc":
        collected = ctx.gc()
        assert collected > 0
    assert ctx.stats.framebuffer == (created + 1, freed + 1)

    # Program
    created, freed = ctx.stats.program
    prog = ctx.program(vertex_shader=VERTEX_SRC, fragment_shader=FRAGMENT_SRC)
    assert ctx.stats.program == (created + 1, freed)
    prog = None
    gc.collect()
    if ctx.gc_mode == "context_gc":
        collected = ctx.gc()
        assert collected > 1
    assert ctx.stats.program == (created + 1, freed + 1)

    # Vertex arrays
    created, freed = ctx.stats.vertex_array
    geo = geometry.cube()
    geo.instance(ctx.program(vertex_shader=VERTEX_SRC, fragment_shader=FRAGMENT_SRC))
    assert ctx.stats.vertex_array == (created + 1, freed)
    geo = None
    gc.collect()
    if ctx.gc_mode == "context_gc":
        collected = ctx.gc()
        assert collected == 1
    assert ctx.stats.vertex_array == (created + 1, freed + 1)

    # Compute shader
    if ctx.gl_version >= (4, 3):
        created, freed = ctx.stats.compute_shader
        compute_shader =  ctx.compute_shader(source=COMPUTE_SHADER_SOURCE)
        assert ctx.stats.compute_shader == (created + 1, freed)
        compute_shader = None
        gc.collect()
        if ctx.gc_mode == "context_gc":
            collected = ctx.gc()
            assert collected > 0
        assert ctx.stats.compute_shader == (created + 1, freed + 1)    

    # query
    created, freed = ctx.stats.query
    query = ctx.query()
    assert ctx.stats.query == (created + 1, freed)
    query = None
    gc.collect()
    if ctx.gc_mode == "context_gc":
        collected = ctx.gc()
        assert collected > 0
    assert ctx.stats.query == (created + 1, freed + 1)
