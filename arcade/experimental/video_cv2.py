"""
Simple video player with cv2.

We simply read frames from cv2 and write them into
a texture.

Dependencies:
    pip install opencv-python
"""
import arcade
from arcade.gl.geometry import quad_2d_fs
import cv2  # type: ignore


class CV2Player(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "OpenCV Video Player", resizable=True)
        self.quad_fs = quad_2d_fs()
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D videoFrame;
            out vec4 fragColor;
            in vec2 uv;

            void main() {
                fragColor = texture(videoFrame, vec2(uv.x, 1.0 - uv.y));
            }
            """,
        )
        self.video = cv2.VideoCapture("C:/Users/efors/Desktop/BigBuckBunny.mp4")
        width, height = (
            int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        self.texture = self.ctx.texture((width, height), components=3)
        # Swap the components in the texture because cv2 returns BGR data
        # Leave the alpha component as always 1
        self.texture.swizzle = "BGR1"
        self.set_size(width, height)

    def on_draw(self):
        self.clear()
        self.texture.use()
        self.quad_fs.render(self.program)

    def on_update(self, delta_time: float):
        exists, frame = self.video.read()
        if exists:
            self.texture.write(frame)


CV2Player().run()
