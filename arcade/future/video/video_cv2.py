"""
Simple video player with cv2.
This player can be improved a lot, but it does a decent job.

We simply read frames from cv2 and write them into
a texture.

Dependencies:
    pip install opencv-python
"""

from math import floor
from pathlib import Path

import cv2  # type: ignore

import arcade
from arcade.gl.geometry import quad_2d_fs


class VideoPlayerCV2:
    """
    Primitive video player for Arcade with cv2.
    Renders to the entire screen. Use VideoPlayer to render to specific coordinate.

    Args:
        path: Path of the video that is to be played.
    """

    def __init__(self, path: str | Path, loop: bool = False):
        self.loop = loop

        self.ctx = arcade.get_window().ctx

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

        self.video = cv2.VideoCapture(str(arcade.resources.resolve(path)))

        # Query video size
        self._width, self._height = (
            int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

        # Get the framerate of the video
        self.video_frame_rate = self.video.get(cv2.CAP_PROP_FPS)
        # Keep track of the current frame and current time
        # to estimate a reasonable playback speed
        self.current_frame = 0
        self.time: float = 0.0

        # Get the number of frames in the video
        self.frames: int = self.video.get(cv2.CAP_PROP_FRAME_COUNT)  # type: ignore

        # Create and configure the OpenGL texture for the video
        self.texture = self.ctx.texture((self._width, self._height), components=3)
        # Swap the components in the texture because cv2 returns BGR data
        # Leave the alpha component as always 1
        self.texture.swizzle = "BGR1"

    @property
    def width(self) -> int:
        """Video width."""
        return self._width

    @property
    def height(self) -> int:
        """Video height."""
        return self._height

    def draw(self) -> None:
        """Call this in `on_draw`."""

        # Bind video texture to texture channel 0
        self.texture.use(unit=0)
        # Draw a fullscreen quad using our texture program
        self.quad_fs.render(self.program)

    def update(self, delta_time: float) -> None:
        """Move the frame forward."""
        self.time += delta_time

        # Do we need to read a new frame?
        next_frame = floor(self.time * self.video_frame_rate)
        if next_frame != self.current_frame:
            self.current_frame = next_frame
            # Read new frame from video and update texture
            exists, frame = self.video.read()
            if exists:
                self.texture.write(frame)
            # loop if we are at the end of the video
            elif self.loop:
                self.time = 0.0
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)


class CV2PlayerView(arcade.View):
    """
    A simple view to hold a video player using cv2.

    Requires the opencv-python module to be installed.

    Args:
        path: Path of the video that is to be played.
        resize: Change the window size to the video size
    """

    def __init__(self, path: str | Path, loop: bool = False, resize: bool = False):
        super().__init__()

        self.video_player = VideoPlayerCV2(path, loop)

        if resize:
            self.window.set_size(self.video_player.width, self.video_player.height)

    def on_draw(self) -> None:
        self.clear()
        self.video_player.draw()

    def on_update(self, delta_time: float) -> None:
        self.video_player.update(delta_time)


if __name__ == "__main__":
    window = arcade.Window(1280, 720, "Video Player")
    window.show_view(CV2PlayerView(":resources:video/earth.mp4", loop=True, resize=False))
    window.run()
