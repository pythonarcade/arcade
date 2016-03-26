# https://gist.github.com/davidejones/0ba54a9402c5f374564e
import pyglet
from pyglet.gl import *
from ctypes import create_string_buffer, cast, sizeof, c_int, c_char, pointer, byref, POINTER

width = 800
height = 600
ratio = float(width) / float(height)
window = pyglet.window.Window(config=Config(major_version=2, minor_version=2), width=width, height=height, vsync=True)
program = glCreateProgram()
vertex_shader = b'''
    attribute vec2 position;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
    }
'''
fragment_shader = b'''
    void main()
    {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
'''
vertex_data = [
    0.0, 0.5, 0.0,
    -0.5, -0.5, 0.0,
    0.5, -0.5, 0.0
]
vertex_data_gl = (GLfloat * len(vertex_data))(*vertex_data)
vbuf = GLuint(0)
vao = GLuint(0)


@window.event
def on_draw():
    glViewport(0, 0, width, height)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-ratio, ratio, -1.0, 1.0, 1.0, -1.0)
    glMatrixMode(GL_MODELVIEW)

    glUseProgram(program)

    # render the triangle
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glBindVertexArray(0)


def compile_shader(shader_type, shader_source):
    shader_name = glCreateShader(shader_type)
    src_buffer = create_string_buffer(shader_source)
    buf_pointer = cast(pointer(pointer(src_buffer)), POINTER(POINTER(c_char)))
    length = c_int(len(shader_source) + 1)
    glShaderSource(shader_name, 1, buf_pointer, byref(length))
    glCompileShader(shader_name)
    return shader_name


def init():
    # compile + attach
    glAttachShader(program, compile_shader(GL_VERTEX_SHADER, vertex_shader))
    glAttachShader(program, compile_shader(GL_FRAGMENT_SHADER, fragment_shader))
    # link program
    glLinkProgram(program)

    # setup vao
    glBindVertexArray(vao)

    # generate the vert buffer
    glGenBuffers(1, vbuf)
    # use the buffer
    glBindBuffer(GL_ARRAY_BUFFER, vbuf)
    # allocate memory in the buffer and populate with data
    glBufferData(GL_ARRAY_BUFFER, len(vertex_data_gl)*4, vertex_data_gl, GL_STATIC_DRAW)
    # tell opengl how data is packed in buffer
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)
    # enable vertexattrib array at position 0 so shader can read it
    glEnableVertexAttribArray(0)


if __name__ == '__main__':
    init()
    pyglet.app.run()