import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Basic Vertex and Fragment Shader"


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.center_window()
        self.background_color = arcade.color.ALMOND
        
        # GL geometry that will be used to pass pixel coordinates to the shader
        # It has the same dimensions as the screen
        self.quad_fs = arcade.gl.geometry.quad_2d_fs()

        # Create a simple shader program
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            void main()
            {
                gl_Position = vec4(in_vert, 0., 1.);
            }
            """,
            fragment_shader="""
            #version 330
            out vec4 fragColor;
            void main()
            {
                // Set the pixel colour and alpha based on x position
                fragColor = vec4(0.9, 0.5, 0.5, sin(gl_FragCoord.x / 50));
            }
            """
        )

    def on_draw(self):
        # Draw a simple circle
        self.clear()
        arcade.draw_circle_filled(
            SCREEN_WIDTH / 2, 
            SCREEN_HEIGHT / 2,
            100,
            arcade.color.AFRICAN_VIOLET
        )

        # Run the shader and render to screen
        # The shader code is run once for each pixel coordinate in quad_fs
        # and the fragColor output added to the screen
        self.quad_fs.render(self.prog)


app = MyWindow()
arcade.run()