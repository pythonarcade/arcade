import arcade
from arcade.experimental.shadertoy import Shadertoy

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ShaderToy Demo"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.shadertoy = Shadertoy(
            self.get_framebuffer_size(),
            """
                void mainImage( out vec4 fragColor, in vec2 fragCoord )
                {
                    // Calculate the texture coordinate of the current fragment.
                    // This interpolates from 0,0 to 1,1 from lower left to upper right
                    vec2 uv = fragCoord.xy / iResolution.xy;
                    // Write the fragment color
                    fragColor = vec4(uv, 0.0, 1.0);	                
                }                    
            """,
        )

    def on_draw(self):
        self.clear()
        self.shadertoy.render()


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
