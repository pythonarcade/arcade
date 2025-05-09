"""
Experimental video player using pyglet.

This requires that you have ffmpeg installed
and you might need to tell pyglet where it's located.
"""

from pathlib import Path

# import sys
import pyglet

import arcade


class VideoPlayer:
    """
    Primitive video player for arcade.

    Args:
        path: Path of the video that is to be played.
        loop: Pass `True` to make the video loop.
    """

    def __init__(self, path: str | Path, loop: bool = False):
        self.player = pyglet.media.Player()
        self.player.loop = loop
        self.player.queue(pyglet.media.load(str(arcade.resources.resolve(path))))
        self.player.play()

        self.ctx = arcade.get_window().ctx

        self._width = arcade.get_window().width
        self._height = arcade.get_window().height

    def draw(self, left: int = 0, bottom: int = 0, size: tuple[int, int] | None = None) -> None:
        """
        Draw the current video frame.

        Args:
            left:
                Window position from the left.
            bottom:
                Window position from the bottom.
            size:
                The size of the video rectangle.
                If `None`, the video will be drawn in its original size.
        """
        if size and len(size) == 2:
            self._width = size[0] or self.width
            self._height = size[1] or self.height

        self.ctx.disable(self.ctx.BLEND)
        video_texture = self.player.texture
        if video_texture:
            video_texture.blit(
                left,
                bottom,
                width=self.width,
                height=self.height,
            )

    @property
    def width(self) -> int:
        """Video width."""
        return self._width

    @property
    def height(self) -> int:
        """Video height."""
        return self._height

    def get_video_size(self) -> tuple[int, int]:
        if not self.player.source or not self.player.source.video_format:
            return 0, 0
        video_format = self.player.source.video_format
        width = video_format.width
        height = video_format.height
        if video_format.sample_aspect > 1:
            width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            height /= video_format.sample_aspect
        return width, height


class VideoPlayerView(arcade.View):
    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self.video_player = VideoPlayer(path)

    def on_draw(self) -> None:
        self.clear()
        self.video_player.draw()


if __name__ == "__main__":
    window = arcade.Window(1280, 720, "Video Player")
    window.show_view(VideoPlayerView(":resources:video/earth.mp4"))
    window.run()
