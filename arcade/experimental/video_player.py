"""
Experimental video player using pyglet.

This requires that you have ffmpeg installed
and you might need to tell pyglet where it's located.
"""
from pathlib import Path
from typing import Optional, Tuple, Union

# import sys
import pyglet
import arcade


class VideoPlayer:
    """
    Primitive video player for arcade.

    :param path: Path of the video that is to be played.
    :param loop: Pass `True` to make the video loop.
    """

    def __init__(self, path: Union[str, Path], loop=False):
        self.player = pyglet.media.Player()
        self.player.loop = loop
        self.player.queue(pyglet.media.load(str(arcade.resources.resolve_resource_path(path))))
        self.player.play()

        self.ctx = arcade.get_window().ctx

        self._width = arcade.get_window().width
        self._height = arcade.get_window().height

    def draw(self, left: int = 0, bottom: int = 0, size: Optional[Tuple[int, int]] = None):
        """
        Call this in `on_draw`.

        :param size: Pass None as one of the elements if you want to use the dimension(width, height) attribute.
        """
        if size and len(size) == 2:
            self._width = size[0] or self.width
            self._height = size[1] or self.height

        with self.ctx.pyglet_rendering():
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
    def width(self):
        """Video width."""
        return self._width

    @property
    def height(self):
        """Video height."""
        return self._height

    def get_video_size(self):
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
    def __init__(self, path) -> None:
        super().__init__()

        self.video_player = VideoPlayer(path)

    def on_draw(self):
        self.clear()

        self.video_player.draw()


if __name__ == '__main__':
    window = arcade.Window(800, 600, "Video Player")
    window.show_view(VideoPlayerView("/home/ibrahim/PycharmProjects/pyweek/35/Tetris-in-Ohio/assets/rain.mp4"))
    window.run()
