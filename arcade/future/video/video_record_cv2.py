"""
Simple video recorder with cv2.
Records Arcade screen to a video file, with minimal
I/O operations and minimal memory usage.

We read pixels directly from OpenGL framebuffer, then into
a NumPy array that we can hand to OpenCV for the video writing.

The other ways of doing this with built-in arcade.get_image()
function would require either a lot of re-processing of images
on CPU for no real reason, saving/reloading each frame as an image file,
or having rampant memory usage problems.

This attempts to have optimal performance while not increasing memory usage
by having as few steps in between the pixel data in VRAM and the final video
file as possible.

Dependencies:
    pip install opencv-python numpy
"""

import cv2  # type: ignore
import numpy  # type: ignore
import pyglet.gl as gl

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class VideoRecorderCV2(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

        # The video files produced by this are un-compressed and will be massive.
        # Think 1GB+ for even like 15 seconds+ of 1920x1080. If you want compressed
        # video, you can replace the below line with something like this to use H.264
        # encoding(this probably needs ffmpeg available):
        #
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # self.video = cv2.VideoWriter("my_video.mp4", fourcc, 60, (self.width, self.height))
        self.video = cv2.VideoWriter("my_video.avi", 0, 60, (self.width, self.height))

        # This is just used to count frames so we can cut it off at some point
        self.frames = 0

    def on_draw(self):
        self.clear()

    def on_update(self, delta_time):
        self.frames += 1
        img = self.get_image()
        self.video.write(img)
        if self.frames >= 1000:
            self.video.release()
            cv2.destroyAllWindows()
            arcade.exit()

        # make something happen for our video
        arcade.set_background_color(arcade.types.Color(self.frames % 255, 0, 0))

    # This is sort of a re-implementation of arcade.get_image(). Really the only difference
    # is in the last line, where we create a numpy array with the buffer instead of
    # creating a PIL image, and the fact that we are just capturing the whole screen instead
    # of allowing to capture a specific sub-section.
    def get_image(self):
        image_buffer = (gl.GLubyte * (3 * self.width * self.height))(0)
        gl.glReadPixels(0, 0, self.width, self.height, gl.GL_BGR, gl.GL_UNSIGNED_BYTE, image_buffer)
        return numpy.frombuffer(image_buffer, dtype="uint8").reshape(self.height, self.width, 3)  # type: ignore


def main():
    VideoRecorderCV2(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
