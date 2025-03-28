"""
Use texture layers with shadertoy.
We simply mix the two texture layers.
"""

import arcade
from arcade.experimental.shadertoy import Shadertoy

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "ShaderToy Texture Layers"


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
                    vec4 layer_0 = texture(iChannel0, uv);
                    vec4 layer_1 = texture(iChannel1, uv);
                    float value = (sin((iTime + uv.x) * 3.0) + 1.0) / 2.0;
                    fragColor = mix(layer_0, layer_1, value);
                }
            """,
        )
        # Add two OpenGL textures to different channels
        self.shadertoy.channel_0 = self.ctx.load_texture(
            ":resources:images/backgrounds/abstract_1.jpg"
        )
        self.shadertoy.channel_1 = self.ctx.load_texture(
            ":resources:images/backgrounds/abstract_2.jpg"
        )

    def on_draw(self):
        self.clear()
        self.shadertoy.render()

    def on_update(self, delta_time: float):
        self.shadertoy.time += delta_time

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.shadertoy.resize(self.get_framebuffer_size())


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
