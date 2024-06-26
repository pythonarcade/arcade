"""
Creating compressed textures in OpenGL

Simple formats to test:
* DXT1: gl.GL_COMPRESSED_RGBA_S3TC_DXT1_EXT 6:1 compression ratio
* DXT5: gl.GL_COMPRESSED_RGBA_S3TC_DXT5_EXT 4:1 compression ratio

Running this example:
python -m arcade.examples.gl.texture_compression
"""

import PIL.Image
import arcade
import arcade.gl
from pyglet import gl


class CompressedTextures(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "Compressed Textures Example")

        # self.texture = self.create_compressed_manual()
        self.texture = self.create_simple()

        self.geometry = arcade.gl.geometry.quad_2d_fs()
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_vert;
            in vec2 in_uv;

            out vec2 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D tex;

            in vec2 uv;

            out vec4 fragColor;

            void main() {
                fragColor = texture(tex, uv);
            }
            """,
        )

    def create_simple(self):
        """Create a simple texture"""
        return self.ctx.load_texture(
            ":assets:images/backgrounds/abstract_1.jpg",
            internal_format=gl.GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
            compressed=True,
        )

    def create_compressed_manual(self):
        """Manually load and compress a texture"""
        path = arcade.resources.resolve(":assets:images/backgrounds/abstract_1.jpg")
        image = PIL.Image.open(path)
        components = 3 if image.mode == "RGB" else 4
        if components == 3:
            compression_format = gl.GL_COMPRESSED_RGB_S3TC_DXT1_EXT
        elif components == 4:
            compression_format = gl.GL_COMPRESSED_RGBA_S3TC_DXT5_EXT
        else:
            raise Exception(f"Invalid number of components: {components}")

        return self.ctx.texture(
            size=image.size,
            components=components,
            internal_format=compression_format,
            compressed=True,
            data=image.tobytes(),
        )

    def create_from_compressed_data(self):
        """Create data from compressed bytes"""
        # TODO: This is not easy to replicate with only arcade
        # compressed_data = <get compressed data from some source>
        # size = <the with and height of the image when decompressed>
        # components = <1, 3 or 4 depending on the image format>
        # return self.ctx.texture(
        #     size=size,
        #     components=components,
        #     internal_format=gl.GL_COMPRESSED_RGBA_S3TC_DXT5_EXT,  # tweak to match the format
        #     compressed=True,
        #     data=compressed_data,
        # )
        raise NotImplementedError

    def on_draw(self):
        self.clear()
        self.texture.use(0)
        self.geometry.render(self.program)


CompressedTextures().run()
