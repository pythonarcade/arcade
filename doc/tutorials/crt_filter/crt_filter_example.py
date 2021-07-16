import arcade
from arcade.experimental.shadertoy import ShaderToy

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.time = 0

        # Read in the program
        file_name = "crt_monitor_filter.glsl"
        file = open(file_name)
        shader_sourcecode = file.read()

        # Create the frame buffer
        self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((width, height), components=4)])

        # Create the shader toy
        self.shadertoy = ShaderToy(shader_sourcecode)

        # Bind channel 0 to frame buffer
        self.fbo.color_attachments[0].use(0)

    def on_draw(self):
        self.fbo.use()
        arcade.draw_circle_filled(30, 30, 30, arcade.color.BLUE)

        self.use()
        arcade.start_render()
        self.shadertoy.draw(time=self.time)

    def on_update(self, dt):
        # Keep track of elapsed time
        self.time += dt

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.shadertoy.mouse_pos = x, y


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
