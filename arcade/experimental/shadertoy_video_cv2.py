"""
Manipulate a cv2 video with shadertoy.

Dependencies:
    pip install opencv-python

"""
import arcade
from arcade.experimental.shadertoy import Shadertoy
import cv2  # type: ignore

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
SCREEN_TITLE = "ShaderToy Video"


class ShadertoyVideo(arcade.Window):

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

                    // Alter texture coordinates to make some waves
                    vec2 pos = uv - vec2(0.5);
                    float dist = length(pos) - iTime / 5.0;
                    vec2 direction = normalize(pos);
                    vec2 uv2 = uv + (direction * (sin(dist * 50.0 - iTime) - 0.5)) * 0.02;

                    fragColor = texture(iChannel0, uv2);
                }
            """,
        )
        # INSERT YOUR OWN VIDEO HERE
        self.video = cv2.VideoCapture("C:/Users/efors/Desktop/BigBuckBunny.mp4")
        width, height = (
            int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        self.video_texture = self.ctx.texture((width, height), components=3)
        self.video_texture.wrap_x = self.ctx.CLAMP_TO_EDGE
        self.video_texture.wrap_y = self.ctx.CLAMP_TO_EDGE
        self.video_texture.swizzle = "BGR1"
        self.shadertoy.channel_0 = self.video_texture
        self.set_size(width, height)

    def on_draw(self):
        self.clear()
        self.shadertoy.render()

    def on_update(self, delta_time: float):
        self.shadertoy.time += delta_time
        self.next_frame()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.shadertoy.resize(self.get_framebuffer_size())

    def next_frame(self):
        exists, frame = self.video.read()
        frame = cv2.flip(frame, 0)
        if exists:
            self.video_texture.write(frame)


if __name__ == "__main__":
    ShadertoyVideo(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
