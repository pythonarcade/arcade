import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "An Empty Program"


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.center_window()
        self.background_color = arcade.color.ALMOND
        
        # GL geometry that will be used to pass pixel coordinates to the shader
        # It has the same dimensions as the screen
        self.quad_fs = arcade.gl.geometry.quad_2d_fs()

        # Create texture and FBO
        self.tex = self.ctx.texture((self.width, self.height))
        self.fbo = self.ctx.framebuffer(color_attachments=[self.tex])

        # Put something in the framebuffer to start
        self.fbo.clear(color=arcade.color.ALMOND)
        with self.fbo:
            arcade.draw_circle_filled(
                SCREEN_WIDTH / 2, 
                SCREEN_HEIGHT / 2,
                100,
                arcade.color.AFRICAN_VIOLET
            )

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
            // Define input to access texture
            uniform sampler2D t0;
            out vec4 fragColor;
            void main()
            {
                // Overwrite this pixel with the colour from its neighbour
                ivec2 pos = ivec2(gl_FragCoord.xy) + ivec2(-1, -1);
                fragColor = texelFetch(t0, pos, 0);
            }
            """
        )

        # Register the texture uniform in the shader program
        self.prog['t0'] = 0

    def on_draw(self):
        # Activate our new framebuffer to render to
        with self.fbo:
            # Bind our texture to the first channel
            self.tex.use(0)

            # Run the shader and render to the framebuffer
            self.quad_fs.render(self.prog)
        
        # Copy the framebuffer to the screen to display
        self.ctx.copy_framebuffer(self.fbo, self.ctx.screen)


app = MyWindow()
arcade.run()