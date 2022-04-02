"""
A very simple example rendering a textured fullscreen rectangle.
"""
import arcade
from arcade.gl import geometry

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shader Setup"


class ShaderSetup(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.time = 0
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            // The vertex shader will run for every vertex of the input geometry
            // and set the final position of a vertex.
            // In this example the rectangle geometry we are rendering
            // consists of two triangles.

            // The expected inputs names the geomtry module are using
            in vec2 in_vert;
            in vec2 in_uv;

            // Texture coordinate output to the fragment shader
            out vec2 v_uv;

            void main() {
                // Set the vertex position. This is a special out variable for positions.s
                gl_Position = vec4(in_vert, 0.0, 1.0);
                // Send the texture coordinates to the fragment shader
                v_uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            // The fragment shader will run for every pixel it needs
            // two fill in the two triangles we are rendering.
            // The texture coordinate passed in will be an interpolated
            // value between the texture coordinate specified in each vertex.
            // It interpolates based on location of the current pixel in the triangle.

            // A sampler that can read a texture from a channel
            uniform sampler2D background;

            // Texture coordinate from the vertex shader
            in vec2 v_uv;

            // The final pixel value that will be written to the screen
            out vec4 out_color;

            void main() {
                // Read a pixel from current texture coordinate and write that to the screen.
                out_color = texture(background, v_uv);
            }
            """
        )
        # Configure the sampler to read from texture channel 0.
        # Sampler uniforms are simply intergers containing what
        # texture channel to read from. Most hardware have 8 to 16 channels.
        self.program["background"] = 0
        # Create geometry for a fullscreen rectangle in normalized device coordinates
        self.quad = geometry.screen_rectangle(-1, -1, 2, 2)
        # Load a texture we want to manipulate. This is an OpenGL texture, not an arcade.Texture
        self.texture = self.ctx.load_texture(":resources:images/backgrounds/abstract_1.jpg")

    def on_draw(self):
        self.clear()
        # Bind the texture channel 0 (we configured the sampler to use channel 0)
        self.texture.use(0)
        # Draw the geometry using the program
        self.quad.render(self.program)


ShaderSetup().run()
