"""
A very simple example rendering a fullscreen rectangle
with a texture doing some simple pixel manipulations.
"""
import arcade
from arcade.gl import geometry

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shader Setup With Pixel Manipulation"


class ShaderSetup(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
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
            uniform float time;

            // Texture coordinate from the vertex shader
            in vec2 v_uv;

            // The final pixel value that will be written to the screen
            out vec4 out_color;

            void main() {
                // Let's manipulate the texture coordinates to make some distortion
                // We are trying to make some waves moving from the center.
                // It's too important that you understand the details of this distortion.
                vec2 pos = v_uv - vec2(0.5);
                float dist = length(pos);
                vec2 direction = normalize(pos);
                vec2 uv = v_uv + (direction * (sin(dist * 50 - time) - 0.5)) * 0.25;

                // Read a pixel using the distorted texture coordinates and write to screen
                out_color = texture(background, uv);
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
        # Update the current time in the shader uniform
        self.program["time"] = self.time * 3
        # Bind the texture channel 0 (we configured the sampler to use channel 0)
        self.texture.use(0)
        # Draw the geometry using the program
        self.quad.render(self.program)

    def on_update(self, dt):
        self.time += dt


ShaderSetup(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE).run()
