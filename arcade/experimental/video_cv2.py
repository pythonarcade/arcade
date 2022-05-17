"""
Simple video player with cv2.
This player can be improved a lot, but it does a decent job.

We simply read frames from cv2 and write them into
a texture.

Dependencies:
    pip install opencv-python
"""
from math import floor
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
        # Configure videoFrame sampler to read from texture channel 0
        self.program["videoFrame"] = 0

        # Open the video (can also read from webcam)
        self.video = cv2.VideoCapture("C:/Users/efors/Desktop/BigBuckBunny.mp4")
        # Query video size
        width, height = (
            int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        # Get the framerate of the video
        self.video_frame_rate = self.video.get(cv2.CAP_PROP_FPS)
        # Keep track of the current frame and current time
        # to estimate a reasonable playback speed
        self.current_frame = 0
        self.time = 0

        # Create and configure the OpenGL texture for the video
        self.texture = self.ctx.texture((width, height), components=3)
        # Swap the components in the texture because cv2 returns BGR data
        # Leave the alpha component as always 1
        self.texture.swizzle = "BGR1"
        # Change the window size to the video size
        self.set_size(width, height)

    def on_draw(self):
        self.clear()

        # Bind video texture to texture channel 0 
        self.texture.use(unit=0)
        # Draw a fullscreen quad using our texture program
        self.quad_fs.render(self.program)

    def on_update(self, delta_time: float):
        self.time += delta_time

        # Do we need to read a new frame?
        next_frame = floor(self.time * self.video_frame_rate)
        if next_frame != self.current_frame:
            self.current_frame = next_frame
            # Read new frame from video and update texture
            exists, frame = self.video.read()
            if exists:
                self.texture.write(frame)


CV2Player().run()
