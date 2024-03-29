import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shader with Textures"


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.center_window()
        self.background_color = arcade.color.ALMOND
        
        # GL geometry that will be used to pass pixel coordinates to the shader
        # It has the same dimensions as the screen
        self.quad_fs = arcade.gl.geometry.quad_2d_fs()

        # Create textures and FBOs
        self.tex_0 = self.ctx.texture((self.width, self.height))
        self.fbo_0 = self.ctx.framebuffer(color_attachments=[self.tex_0])

        self.tex_1 = self.ctx.texture((self.width, self.height))
        self.fbo_1 = self.ctx.framebuffer(color_attachments=[self.tex_1])

        # Fill the textures with solid colours
        self.fbo_0.clear(color_normalized=(0.0, 0.0, 1.0, 1.0))
        self.fbo_1.clear(color_normalized=(1.0, 0.0, 0.0, 1.0))

        # Create a simple shader program
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            // Get normalized coordinates
            in vec2 in_uv;
            out vec2 uv;
            void main()
            {
                gl_Position = vec4(in_vert, 0., 1.);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330
            // Define an input to receive total_time from python
            uniform float time;
            // Define inputs to access textures
            uniform sampler2D t0;
            uniform sampler2D t1;
            in vec2 uv;
            out vec4 fragColor;
            void main()
            {
                // Set pixel color as a combination of the two textures
                fragColor = mix(
                    texture(t0, uv), 
                    texture(t1, uv), 
                    smoothstep(0.0, 1.0, uv.x));
                // Set the alpha based on time
                fragColor.w = sin(time);
            }
            """
        )

        # Register the texture uniforms in the shader program
        self.prog['t0'] = 0
        self.prog['t1'] = 1

        # Create a variable to track program run time
        self.total_time = 0

    def on_update(self, delta_time):
        # Keep tract o total time
        self.total_time += delta_time

    def on_draw(self):
        # Draw a simple circle
        self.clear()
        arcade.draw_circle_filled(
            SCREEN_WIDTH / 2, 
            SCREEN_HEIGHT / 2,
            100,
            arcade.color.AFRICAN_VIOLET
        )

        # Register the uniform in the shader program
        self.prog['time'] = self.total_time

        # Bind our textures to channels
        self.tex_0.use(0)
        self.tex_1.use(1)

        # Run the shader and render to screen
        # The shader code is run once for each pixel coordinate in quad_fs
        # and the fragColor output added to the screen
        self.quad_fs.render(self.prog)


app = MyWindow()
arcade.run()