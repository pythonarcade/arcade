"""
Perspective example using the PerspectiveProjectionCamera

This is definitely in the advanced section, but it can be
a useful tool to learn. Sometimes we want perspective
projection for things like backgrounds. This can be
done very efficiently with shaders.

In this example we render content into a framebuffer /
virtual screen and map that on a texture we can rotate
in 3D.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.perspective
"""

from array import array

import arcade
from arcade.gl import BufferDescription


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        # Simple texture shader for the plane.
        # It support projection and model matrix
        # and a scroll value for texture coordinates
        self.program = self.window.ctx.program(
            vertex_shader="""
            #version 330

            uniform WindowBlock {
                mat4 projection;
                mat4 model;
            } window;

            in vec3 in_pos;
            in vec2 in_uv;

            out vec2 uv;

            void main() {
                gl_Position = window.projection * window.model * vec4(in_pos, 1.0);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D layer;
            uniform vec2 scroll;

            in vec2 uv;
            out vec4 fragColor;

            void main() {
                fragColor = texture(layer, uv + scroll);
            }
            """,
        )

        # Configure and create the perspective projector
        self.perspective_data = arcade.camera.PerspectiveProjectionData(
            self.window.aspect_ratio, # The ratio between window width and height
            75, # The angle  between things at the top of the screen, and the bottom
            0.1, # Anything within 0.1 units of the camera won't be visible
            100.0 # Anything past 100.0 units of the camera won't be visible
        )
        self.projector = arcade.camera.PerspectiveProjector()

        # Framebuffer / virtual screen to render the contents into
        self.fbo = self.window.ctx.framebuffer(
            color_attachments=self.window.ctx.texture(size=(1024, 1024))
        )

        # Set up the geometry buffer for the plane.
        # This is four points with texture coordinates
        # creating a rectangle
        buffer = self.window.ctx.buffer(
            data=array(
                'f',
                [
                    # x  y   z  u  v
                    -1,  1, 0, 0, 1,  # Top Left
                    -1, -1, 0, 0, 0,  # Bottom Left
                     1,  1, 0, 1, 1,  # Top Right
                     1, -1, 0, 1, 0,  # Bottom right
                ]
            )
        )
        # Make this into a geometry object we can draw-
        # Here we describe the contents of the buffer so the shader can understand it
        self.geometry = self.window.ctx.geometry(
            content=[BufferDescription(buffer, "3f 2f", ("in_pos", "in_uv"))],
            mode=arcade.gl.TRIANGLE_STRIP,
        )

        # Create some sprites
        self.spritelist = arcade.SpriteList()
        for y in range(8):
            for x in range(8):
                self.spritelist.append(
                    arcade.Sprite(
                        ":resources:images/tiles/boxCrate_double.png",
                        center_x=64 + x * 128,
                        center_y=64 + y * 128,
                    )
                )

        # Create a 2D camera for rendering to the fbo
        # by setting the camera's render target it will automatically
        # size and position itself correctly
        self.offscreen_cam = arcade.Camera2D(
            render_target=self.fbo
        )

    def on_update(self, delta_time: float):
        # Rotate the perspective camera around the plane
        view_data = self.projector.view
        view_data.position = arcade.math.quaternion_rotation(
            (1.0, 0.0, 0.0), (0, 0, 3), 180 * self.window.time
        )
        view_data.forward, view_data.up = arcade.camera.grips.look_at(view_data, (0.0, 0.0, 0.0))
        # print(view_data)


    def on_draw(self):
        # Every frame we can update the offscreen texture if needed
        self.draw_offscreen()
        # Clear the window
        self.clear()

        with self.projector.activate():
            # Bind the texture containing the offscreen data to channel 0
            self.fbo.color_attachments[0].use(unit=0)

            # Scroll the texture coordinates
            self.program["scroll"] = 0, -self.window.time / 5

            # Draw the plane
            self.geometry.render(self.program)

    def draw_offscreen(self):
        """Render into the texture mapped """
        # Activate the offscreen cam, this also activates it's render target
        with self.offscreen_cam.activate():
            self.fbo.clear()
            self.offscreen_cam.use()
            self.spritelist.draw()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.perspective_data.aspect = height / width


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(1280, 720, "Perspective Example", resizable=True)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
