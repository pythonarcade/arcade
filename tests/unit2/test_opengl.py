"""
Low level tests for OpenGL 3.3 wrappers.
"""
import array
import pytest
import arcade
from arcade import shader

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class OpenGLTest(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.test_ctx()
        self.test_buffer()
        self.test_vertex_array()
        self.test_program()
        self.test_texture()
        self.test_framebuffer()
        self.err_check()

    def err_check(self):
        error = self.ctx.error
        if error:
            raise ValueError("Error", error)

    def test_ctx(self):
        assert self.ctx.gl_version == (3, 3)

    def test_buffer(self):
        """Testing OpenGL buffers"""
        buffer = self.ctx.buffer(b'Hello world')
        assert buffer.glo.value > 0
        assert buffer.ctx == self.ctx
        assert buffer.read() == b'Hello world'
        assert buffer.read(size=5) == b'Hello'
        assert buffer.read(size=5, offset=6) == b'world'

        # Reading outside buffer by 1 byte
        with pytest.raises(ValueError):
            buffer.read(size=12)

        # Reading outside buffer by 1 byte with offset
        with pytest.raises(ValueError):
            buffer.read(size=6, offset=6)

        # Read with zero or negative size
        with pytest.raises(ValueError):
            buffer.read(0)

        buffer.orphan(size=20)
        assert buffer.size == 20
        assert len(buffer.read()) == 20

        buffer.write(b'Testing')
        assert buffer.read(size=7) == b'Testing'
        buffer.write(b'Testing', offset=10)
        assert buffer.read(offset=10, size=7) == b'Testing'

        # Copy buffer
        source = self.ctx.buffer(reserve=20)
        buffer.copy_from_buffer(source, size=10, offset=0)
        # Copy out of bounds in the source buffer
        with pytest.raises(ValueError):
            buffer.copy_from_buffer(source, size=10, source_offset=15)

        # Copy out of bounds in the destination buffer
        with pytest.raises(ValueError):
            buffer.copy_from_buffer(source, size=10, offset=15)

    def test_vertex_array(self):
        """Test vertex_array"""
        program = self.ctx.load_program(
            self.ctx.resource_root / 'shaders/line_vertex_shader_vs.glsl',
            self.ctx.resource_root / 'shaders/line_vertex_shader_fs.glsl',
        )
        num_vertices = 100
        content = [
            shader.BufferDescription(
                self.ctx.buffer(reserve=4 * num_vertices),
                '4B',
                ['in_color'],
                normalized=['in_color'],
            ),
            shader.BufferDescription(
                self.ctx.buffer(reserve=8 * num_vertices),
                '2f',
                ['in_vert']
            ),
        ]
        vao = self.ctx.vertex_array(program, content)
        assert vao.ctx == self.ctx
        assert vao.glo.value > 0
        assert vao.program == program
        assert vao.num_vertices == num_vertices
        assert vao.ibo is None
        vao.render(self.ctx.TRIANGLES)
        vao.render(self.ctx.POINTS)
        vao.render(self.ctx.LINES)

    def test_program(self):
        """Test program"""
        program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform vec2 pos_offset;

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 v_uv;

            void main() {
                gl_Position = vec4(in_vert + pos_offset, 0.0, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            out vec4 f_color;
            in vec2 v_uv;

            void main() {
                f_color = vec4(v_uv, 0.0, 1.0);
            }
            """,
        )
        assert program.ctx == self.ctx
        assert program.glo > 0
        program.use()
        assert self.ctx.active_program == program

        # TODO: Test all uniform types
        program['pos_offset'] = 1, 2
        assert program['pos_offset'] == [1.0, 2.0]
        with pytest.raises(shader.ShaderException):
            program['this_uniform_do_not_exist'] = 0

        # TODO: Test attributes

    def test_texture(self):
        """Test textures"""
        texture = self.ctx.texture(
            (100, 200), 4,
            texture_filter=(self.ctx.NEAREST, self.ctx.NEAREST),
            wrap_x=self.ctx.CLAMP_TO_EDGE,
            wrap_y=self.ctx.REPEAT,
        )
        assert texture.ctx == self.ctx
        assert texture.glo.value > 0
        assert texture.components == 4
        assert texture.width == 100
        assert texture.height == 200
        assert texture.size == (100, 200)
        assert texture.filter == (self.ctx.NEAREST, self.ctx.NEAREST)
        assert texture.wrap_x == self.ctx.CLAMP_TO_EDGE
        assert texture.wrap_y == self.ctx.REPEAT
        texture.use(0)
        texture.use(1)
        texture.use(2)

        # Make an unreasonable texture
        with pytest.raises(Exception):
            self.ctx.texture((100_000, 1), 1)

        # Create textures of different components
        c1 = self.ctx.texture((10, 10), 1)
        c2 = self.ctx.texture((10, 10), 2)
        c3 = self.ctx.texture((10, 10), 3)
        c4 = self.ctx.texture((10, 10), 4)
        assert c1.components == 1
        assert c2.components == 2
        assert c3.components == 3
        assert c4.components == 4

        # Wrong number of components
        with pytest.raises(ValueError):
            self.ctx.texture((10, 10), 5)

        # Create textures using different formats
        def test_texture_format(dtype):
            for components in range(1, 5):
                texture = self.ctx.texture((10, 10), components=components, dtype=dtype)
                assert texture.ctx == self.ctx
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

        # Writing to texture
        data = array.array('f', list(range(10))).tobytes()
        texture = self.ctx.texture((10, 1), components=1, dtype='f4')
        texture.write(data)
        self.err_check()

        buffer = self.ctx.buffer(data=data)
        texture.write(buffer)
        self.err_check()

    def test_framebuffer(self):
        """Test framebuffers"""
        fb = self.ctx.framebuffer(
            color_attachments=[
                self.ctx.texture((10, 20), 4),
                self.ctx.texture((10, 20), 4)])
        assert fb.ctx == self.ctx
        assert fb.width == 10
        assert fb.height == 20
        assert fb.size == (10, 20)
        assert fb.samples == 0
        assert fb.viewport == (0, 0, 10, 20)
        assert len(fb.color_attachments) == 2
        assert fb.depth_attachment is None
        assert fb.depth_mask is True
        fb.viewport = (1, 2, 3, 4)
        assert fb.viewport == (1, 2, 3, 4)

        # Ensure bind tracking works
        fb.use()
        assert self.ctx.active_framebuffer == fb
        self.use()
        assert self.ctx.active_framebuffer == self
        fb.clear()
        fb.clear(color=(0, 0, 0, 0))
        fb.clear(color=arcade.csscolor.AZURE)
        assert self.ctx.active_framebuffer == self

        # Varying attachment sizes not supported for now
        with pytest.raises(ValueError):
            self.ctx.framebuffer(
                color_attachments=[
                    self.ctx.texture((10, 10), 4),
                    self.ctx.texture((10, 11), 4)])


def test_opengl():
    window = OpenGLTest(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    window.close()
