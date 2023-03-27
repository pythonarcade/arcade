"""
Experimental video player using pyglet.

This requires that you have ffmpeg installed
and you might need to tell pyglet where it's located.
"""
from pathlib import Path
from typing import Union

# import sys
import pyglet
import arcade


class VideoPlayer:
    """
    Primitive video player for arcade.
    Can be used to add effects like rain in the background.

    :param path: Path of the video that is to be played.
    :param loop: Pass `True` to make the video loop.
    """

    def __init__(self, path: Union[str, Path], loop=False):
        self.player = pyglet.media.Player()
        self.player.loop = loop
        self.player.queue(pyglet.media.load(str(arcade.resources.resolve_resource_path(path))))
        self.player.play()


    def draw(self, ctx: arcade.ArcadeContext, width, height):
        """
        Call this in `on_draw`.
        
        :param ctx: Pass arcade.Window.ctx as argument.
        :param width: Width of the window.
        :param height: Height of the window.
        """
        with ctx.pyglet_rendering():
            ctx.disable(ctx.BLEND)
            video_texture = self.player.texture
            if video_texture:
                video_texture.blit(
                    0,
                    0,
                    width=width,
                    height=height,
                )

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

        self.video_player.draw(self.window.ctx, self.window.width, self.window.height)


if __name__ == '__main__':
    window = arcade.Window(800, 600, "Video Player")
    window.show_view(VideoPlayerView("/home/user/path/to/project/assets/rain.mp4"))
    window.run()
